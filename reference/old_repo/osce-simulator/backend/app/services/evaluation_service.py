from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .base_service import BaseLangChainService
from .models import EvaluationOutput, LlmRubricOutput
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class EvaluationService(BaseLangChainService):
    """Service for evaluation and rubric functionality."""

    def __init__(self):
        super().__init__()
        self.evaluation_parser = JsonOutputParser(pydantic_object=EvaluationOutput)
        self.rubric_parser = JsonOutputParser(pydantic_object=LlmRubricOutput)

    async def evaluate_response(self, case_id: str, response: str) -> Dict[str, Any]:
        """Evaluate a student's response to a patient case."""
        try:
            case = None
            if case_id in self.patient_cases:
                case = self._ensure_complete_case(self.patient_cases[case_id])
            
            prompt = ChatPromptTemplate.from_template("""
            Evaluate the following OSCE response based on these criteria:
            1. History taking completeness
            2. Communication effectiveness
            3. Clinical reasoning
            4. Professionalism
            5. Time efficiency

            {case_details}
            
            Student's Response:
            {response}

            Provide a detailed evaluation with scores (0-5) for each criterion and specific feedback.
            
            {format_instructions}
            """)

            chain = prompt | self.llm | self.evaluation_parser
            result = await chain.ainvoke({
                "case_details": f"Case details: {json.dumps(case)}" if case else "No case details available",
                "response": response,
                "format_instructions": self.evaluation_parser.get_format_instructions()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in evaluate_response: {str(e)}")
            raise Exception(f"Failed to evaluate response: {str(e)}")

    async def evaluate_performance(self, *, case: Optional[dict], conversation: dict, notes: Optional[str]) -> Dict[str, Any]:
        """LLM-based rubric evaluation using conversation transcript and optional notes."""
        try:
            messages = conversation.get("messages", [])
            lines: List[str] = []
            for m in messages:
                role = m.get("role")
                content = m.get("content", "")
                if role == "user":
                    lines.append(f"Doctor: {content}")
                elif role == "assistant":
                    lines.append(f"Patient: {content}")
            transcript = "\n".join(lines)

            prompt = ChatPromptTemplate.from_template(
                """
                You are an OSCE examiner evaluating a nursing student's health history assessment.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Notes (may be empty):
                {notes}

                Provide JSON only that matches this schema exactly:
                {format_instructions}
                """
            )

            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case) if case else "null",
                transcript=transcript,
                notes=notes or "",
                format_instructions=self.rubric_parser.get_format_instructions(),
            ))
            
            content = llm_response.content
            logger.debug("Raw LLM response: %s", content)
            
            import re
            content = re.sub(r'""([^"]+)""', r'"\1"', content)
            content = re.sub(r'(\w+):"([^"]*)"', r'"\1":"\2"', content)
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            try:
                result: Dict[str, Any] = self.rubric_parser.parse(content)
                return result
            except Exception as parse_error:
                logger.error("Failed to parse LLM response: %s", parse_error)
                return self._get_default_evaluation()
        except Exception as e:
            logger.error("Error in evaluate_performance: %s", str(e), exc_info=True)
            raise

    def _get_default_evaluation(self) -> Dict[str, Any]:
        """Return a default evaluation when parsing fails."""
        return {
            "scores": {
                "introduction_collaboration": 0,
                "past_medical_history_part2": 0,
                "family_history": 0,
                "functional_assessment_part1": 0,
                "functional_assessment_part2": 0,
                "review_of_systems": 0,
                "health_promotion_opportunities": 0,
                "quality_health_promotion": 0,
                "patient_centered_care": 0,
                "interview_style": 0,
                "organization": 0,
                "clinical_judgment": 0,
                "professionalism": 0
            },
            "feedback": {
                "introduction_collaboration": "Evaluation parsing failed",
                "past_medical_history_part2": "Evaluation parsing failed",
                "family_history": "Evaluation parsing failed",
                "functional_assessment_part1": "Evaluation parsing failed",
                "functional_assessment_part2": "Evaluation parsing failed",
                "review_of_systems": "Evaluation parsing failed",
                "health_promotion_opportunities": "Evaluation parsing failed",
                "quality_health_promotion": "Evaluation parsing failed",
                "patient_centered_care": "Evaluation parsing failed",
                "interview_style": "Evaluation parsing failed",
                "organization": "Evaluation parsing failed",
                "clinical_judgment": "Evaluation parsing failed",
                "professionalism": "Evaluation parsing failed",
                "overall": "Evaluation parsing failed due to malformed JSON response"
            }
        }