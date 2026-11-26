from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ..schemas.patient import PatientCase
from .base_service import BaseLangChainService
from .models import PatientCaseOutput
from typing import Dict, Any
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class PatientService(BaseLangChainService):
    """Service for patient case generation and management."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize output parser
        self.patient_parser = JsonOutputParser(pydantic_object=PatientCaseOutput)
        
        # In-memory storage for patient cases during development
        self.patient_cases = {}

    def _ensure_complete_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill any missing PatientCase required fields with sensible defaults."""
        # Normalize incoming structure (dict or Pydantic model)
        if data is None:
            out: Dict[str, Any] = {}
        elif isinstance(data, dict):
            out = dict(data)
        elif hasattr(data, "dict"):
            try:
                out = data.dict()
            except Exception:
                out = dict(data.__dict__)
        elif hasattr(data, "model_dump"):
            out = data.model_dump()  # type: ignore[attr-defined]
        else:
            try:
                out = json.loads(json.dumps(data, default=lambda o: getattr(o, "__dict__", str(o))))
            except Exception:
                out = {}
        
        def _values_to_strings(obj: Dict[str, Any]) -> Dict[str, str]:
            result: Dict[str, str] = {}
            if not isinstance(obj, dict):
                return {}
            for key, value in obj.items():
                if isinstance(value, str):
                    result[key] = value
                elif isinstance(value, (int, float)):
                    result[key] = str(value)
                elif isinstance(value, (list, dict)):
                    try:
                        # Prefer human-friendly summarization for common lab/imaging nests
                        if isinstance(value, dict):
                            flat = "; ".join(f"{k}: {v}" for k, v in value.items())
                            result[key] = flat
                        else:
                            result[key] = ", ".join(map(str, value))
                    except Exception:
                        result[key] = json.dumps(value, ensure_ascii=False)
                else:
                    result[key] = str(value)
            return result
        # Required simple fields
        out.setdefault("labs", {})
        out["labs"] = _values_to_strings(out.get("labs", {}))
        out.setdefault("imaging", {})
        out["imaging"] = _values_to_strings(out.get("imaging", {}))
        out.setdefault("difficulty", "simple")
        out.setdefault("age", 30)
        out.setdefault("gender", "female")
        # Personality / behavior
        if not isinstance(out.get("personality_traits"), dict):
            out["personality_traits"] = {"shy": False, "introverted": False, "anxious": True, "talkative": True, "defensive": False, "friendly": True}
        else:
            for k in ["shy","introverted","anxious","talkative","defensive","friendly"]:
                out["personality_traits"].setdefault(k, False)
        if not isinstance(out.get("behavioral_settings"), dict):
            out["behavioral_settings"] = {"cooperative": True, "provides_complete_answers": True, "emotional": False}
        else:
            for k, v in {"cooperative": True, "provides_complete_answers": True, "emotional": False}.items():
                out["behavioral_settings"].setdefault(k, v)
        # Vitals presence
        out.setdefault("vital_signs", {})
        if isinstance(out["vital_signs"], dict):
            out["vital_signs"] = _values_to_strings(out["vital_signs"]) or {}
        # Name/ID defaults
        out.setdefault("id", str(uuid.uuid4()))
        out.setdefault("name", out.get("name", "Patient"))
        out.setdefault("chief_complaint", out.get("chief_complaint", "Unknown"))
        out.setdefault("history_of_present_illness", out.get("history_of_present_illness", "Unknown"))
        out.setdefault("past_medical_history", out.get("past_medical_history", "Unknown"))
        out.setdefault("medications", out.get("medications", []))
        out.setdefault("allergies", out.get("allergies", []))
        out.setdefault("social_history", out.get("social_history", "Unknown"))
        out.setdefault("family_history", out.get("family_history", "Unknown"))
        out.setdefault("physical_examination", out.get("physical_examination", "Unremarkable"))
        return out

    async def generate_patient_case(self, difficulty: str, age: int, gender: str, personality_traits: list, behavioral_settings: dict) -> PatientCase:
        try:
            logger.debug("Generating patient case with parameters: %s", {
                "difficulty": difficulty,
                "age": age,
                "gender": gender,
                "personality_traits": personality_traits,
                "behavioral_settings": behavioral_settings
            })

            # Create prompt template
            prompt = ChatPromptTemplate.from_template("""
            Generate a detailed OSCE patient case with the following specifications:
            Difficulty: {difficulty}
            Age: {age}
            Gender: {gender}
            Personality Traits: {personality_traits}
            Behavioral Settings: {behavioral_settings}

            Generate a realistic and educational patient case that medical students can practice with.
            The case should be appropriate for the specified difficulty level and include all required fields.
            
            IMPORTANT: Generate a realistic full name for the patient (e.g., "Sarah Johnson", "Michael Chen", "Maria Rodriguez").
            The name should be appropriate for the patient's age, gender, and cultural background.
            
            {format_instructions}
            """)

            # Create the chain
            chain = prompt | self.llm | self.patient_parser

            # Prepare personality traits dict
            personality_dict = {trait: trait in personality_traits for trait in [
                "shy", "introverted", "anxious", "talkative", "defensive", "friendly"
            ]}

            # Run the chain
            result = await chain.ainvoke({
                "difficulty": difficulty,
                "age": age,
                "gender": gender,
                "personality_traits": ", ".join(personality_traits),
                "behavioral_settings": json.dumps(behavioral_settings),
                "format_instructions": self.patient_parser.get_format_instructions()
            })
            
            # Ensure ID is set
            if not result.get("id"):
                result["id"] = str(uuid.uuid4())
            
            # Ensure completeness and store
            result = self._ensure_complete_case(result)
            # Final defensive coercion for nested dicts in labs/imaging/vitals
            for field in ("labs", "imaging", "vital_signs"):
                try:
                    if isinstance(result.get(field), dict):
                        coerced = {}
                        for k, v in result[field].items():
                            if isinstance(v, str):
                                coerced[k] = v
                            elif isinstance(v, (int, float)):
                                coerced[k] = str(v)
                            elif isinstance(v, dict):
                                coerced[k] = "; ".join(f"{ik}: {iv}" for ik, iv in v.items())
                            elif isinstance(v, list):
                                coerced[k] = ", ".join(map(str, v))
                            else:
                                coerced[k] = json.dumps(v, ensure_ascii=False)
                        result[field] = coerced
                except Exception:
                    pass
            self.patient_cases[result["id"]] = result
            
            # Initialize memory for this case
            self._get_or_create_memory(result["id"])
            
            logger.debug("Generated case data: %s", result)
            return PatientCase(**self._ensure_complete_case(result))

        except Exception as e:
            logger.error("Error generating patient case: %s", str(e), exc_info=True)
            raise

    async def get_patient_case(self, case_id: str) -> PatientCase:
        """Retrieve a patient case by ID."""
        try:
            if case_id in self.patient_cases:
                complete = self._ensure_complete_case(self.patient_cases[case_id])
                return PatientCase(**complete)
            raise Exception(f"Patient case with ID {case_id} not found")
        except Exception as e:
            logger.error(f"Error retrieving patient case: {str(e)}")
            raise
