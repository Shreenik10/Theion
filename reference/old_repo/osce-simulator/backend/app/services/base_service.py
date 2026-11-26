from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List, Optional
from ..core.config import get_settings
import os
import uuid
import json
import logging
import re
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class BaseLangChainService:
    """Base service class with shared LLM initialization and utilities."""
    
    def __init__(self):
        # Read API key directly from file for reliability
        self.api_key = self._get_api_key()
        
        # Validate API key
        if not self.api_key:
            logger.error("No OpenAI API key found. Please set OPENAI_API_KEY in your .env file.")
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=self.api_key,
            max_tokens=2048,  # Increased for detailed feedback
            presence_penalty=0.2,  # encourage new content
            frequency_penalty=0.5, # reduce verbatim repetition
        )
        
        # Initialize conversation memories for each case
        self.conversation_memories: Dict[str, ConversationBufferMemory] = {}
        
        logger.info(f"LangChain service initialized with model: gpt-3.5-turbo, API key starting with: {self.api_key[:8]}...")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from file or settings."""
        api_key = None
        try:
            dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            if os.path.exists(dotenv_path):
                with open(dotenv_path, 'r') as f:
                    env_content = f.read()
                    for line in env_content.strip().split('\n'):
                        if line.startswith('OPENAI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            print(f"DEBUG: API Key read directly from file: {api_key[:8]}...")
                            break
        except Exception as e:
            print(f"Error reading API key from file: {str(e)}")
        
        # Still try the regular method as fallback
        if not api_key:
            settings = get_settings()
            api_key = settings.OPENAI_API_KEY
            print(f"DEBUG: Using API key from settings: {api_key[:8] if api_key else 'None'}...")
        
        return api_key

    def _get_or_create_memory(self, memory_key: str) -> ConversationBufferMemory:
        """Get or create a conversation memory for a specific key (conversation/session or case)."""
        if memory_key not in self.conversation_memories:
            self.conversation_memories[memory_key] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        return self.conversation_memories[memory_key]

    def _add_to_memory(self, memory_key: str, human_message: str, ai_message: str):
        """Add a conversation exchange to the memory."""
        memory = self._get_or_create_memory(memory_key)
        memory.chat_memory.add_user_message(human_message)
        memory.chat_memory.add_ai_message(ai_message)

    def _is_repetitive(self, previous: str, current: str) -> bool:
        """Detect if current reply largely repeats the previous one."""
        try:
            if not previous or not current:
                return False
            prev = re.sub(r"\s+", " ", previous.strip().lower())
            cur = re.sub(r"\s+", " ", current.strip().lower())
            if prev == cur:
                return True
            # Token overlap ratio
            prev_tokens = set(re.findall(r"\w+", prev))
            cur_tokens = set(re.findall(r"\w+", cur))
            if not prev_tokens or not cur_tokens:
                return False
            overlap = len(prev_tokens & cur_tokens) / max(1, len(cur_tokens))
            # If more than 80% of current tokens are in previous, consider repetitive
            return overlap > 0.8
        except Exception:
            return False

    def _rewrite_direct_answer(self, case: Dict[str, Any], question: str, current_reply: str, style_instructions: str) -> str:
        """Ask LLM to rewrite the reply to directly answer the doctor's question without restating background."""
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            pmh = case.get("past_medical_history", "Unknown")
            meds = ", ".join(case.get("medications", []) or []) or "None"
            allergies = ", ".join(case.get("allergies", []) or []) or "None"
            prompt = ChatPromptTemplate.from_template(
                """
                Rewrite the patient's reply to directly answer the doctor's question ONLY.
                - Do NOT restate background/profile unless asked explicitly.
                - If the question asks for info not in profile (e.g., height/weight) and the patient wouldn't know, say you are not sure or don't recall; do not invent data.
                - Keep it aligned with style rules: {style_instructions}
                - Output ONLY the patient reply (no labels, no JSON).

                Profile quick facts (for consistency only):
                PMH: {pmh}; Meds: {meds}; Allergies: {allergies}

                Doctor's question:
                {question}

                Original reply:
                {reply}
                """
            )
            chain = prompt | self.llm
            out = chain.invoke({
                "style_instructions": style_instructions,
                "pmh": pmh,
                "meds": meds,
                "allergies": allergies,
                "question": question,
                "reply": current_reply,
            })
            text = getattr(out, "content", out) or ""
            return re.sub(r"^(?:Patient|Doctor|Assistant)\s*:\s*", "", text, flags=re.IGNORECASE).strip() or current_reply
        except Exception:
            return current_reply

    def _try_factoid_answer(self, case: Dict[str, Any], question: str) -> Optional[str]:
        """Return a concise first-person answer for simple fact questions without calling the LLM.

        Covers: age, name, gender, medications, allergies, PMH/social/family when explicitly asked.
        """
        try:
            q = (question or "").strip().lower()
            if not q:
                return None
            # Age
            if re.search(r"\b(how old|age)\b", q):
                age = case.get("age")
                if age is not None:
                    return f"I'm {age} years old."
            # Name
            if re.search(r"\b(name|what's your name|what is your name)\b", q):
                name = case.get("name") or ""
                if name:
                    return f"My name is {name}."
            # Gender/sex
            if re.search(r"\b(gender|sex)\b", q):
                gender = case.get("gender")
                if gender:
                    return f"I'm {gender}."
            # Medications
            if re.search(r"\b(meds?|medications?|medicine|do you take any)\b", q):
                meds = case.get("medications", []) or []
                text = ", ".join(meds) if meds else "I'm not on any medications."
                return text if meds else "I'm not on any medications."
            # Allergies
            if re.search(r"\ballerg(y|ies)\b", q):
                alls = case.get("allergies", []) or []
                return f"I'm allergic to {', '.join(alls)}." if alls else "I don't have any allergies that I know of."
            # PMH
            if re.search(r"\b(past medical|medical history|conditions|illnesses)\b", q):
                pmh = case.get("past_medical_history")
                return f"My past medical history: {pmh}." if pmh else "I don't have any significant past medical history."
            # Social
            if re.search(r"\b(social history|do you smoke|alcohol|drugs|occupation|work)\b", q):
                sh = case.get("social_history")
                return sh if sh else None
            # Family
            if re.search(r"\bfamily history|family|parents|siblings\b", q):
                fh = case.get("family_history")
                return fh if fh else None
            return None
        except Exception:
            return None

    def _enforce_first_person_and_profile_consistency(self, case: Dict[str, Any], reply_text: str, style_instructions: str) -> str:
        """If the reply is in third-person or contradicts key facts, rewrite to first-person with exact profile values."""
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            if not reply_text:
                return reply_text

            text_lower = reply_text.lower()
            # Heuristic triggers for third-person clinical style
            third_person_triggers = [
                "the patient", "presents with", "she ", "he ", "mrs.", "mr.", " ms. ", "patient presents"
            ]
            violates_person = any(t in text_lower for t in third_person_triggers)

            # Detect an age mention in reply, and compare with case age if numeric
            stated_age_match = re.search(r"(\d{1,3})\s*[- ]?year[- ]?old", reply_text, flags=re.IGNORECASE)
            age_mismatch = False
            if isinstance(case.get("age"), int) and stated_age_match:
                try:
                    stated_age = int(stated_age_match.group(1))
                    age_mismatch = stated_age != int(case.get("age"))
                except Exception:
                    age_mismatch = False

            # If no issues detected, return as-is
            if not (violates_person or age_mismatch):
                return reply_text

            # Prepare exact profile facts
            age = case.get("age", "Unknown")
            gender = case.get("gender", "Unknown")
            pmh = case.get("past_medical_history", "Unknown")
            meds = ", ".join(case.get("medications", []) or []) or "None"
            allergies = ", ".join(case.get("allergies", []) or []) or "None"
            name = case.get("name", "")

            prompt = ChatPromptTemplate.from_template(
                """
                Rewrite the patient's reply so it is strictly FIRST-PERSON (I, my, me) and consistent with these facts:
                - Name: {name}
                - Age: {age}
                - Gender: {gender}
                - PMH: {pmh}
                - Meds: {medications}
                - Allergies: {allergies}

                Requirements:
                - Do NOT use phrases like "the patient", "she/he", "presents with"; speak as the patient.
                - Replace any conflicting details with the exact facts above.
                - Keep the same overall meaning and tone, and follow these style rules: {style_instructions}
                - Output ONLY the corrected patient reply text. No JSON, no commentary, no speaker labels.

                Original reply:
                {reply}
                """
            )

            chain = prompt | self.llm
            fixed = chain.invoke({
                "name": name,
                "age": age,
                "gender": gender,
                "pmh": pmh,
                "medications": meds,
                "allergies": allergies,
                "style_instructions": style_instructions,
                "reply": reply_text,
            })
            corrected = getattr(fixed, "content", fixed) or ""
            # Final cleanup: strip speaker labels if any
            corrected = re.sub(r"^(?:Patient|Doctor|Assistant)\s*:\s*", "", corrected, flags=re.IGNORECASE).strip()
            return corrected if corrected else reply_text
        except Exception:
            return reply_text

    def _infer_emotion(self, case: Dict[str, Any], reply_text: str) -> str:
        """Infer a plausible emotion from profile and content without an extra LLM call."""
        try:
            traits = case.get("personality_traits", {}) if isinstance(case.get("personality_traits"), dict) else {}
            behav = case.get("behavioral_settings", {}) if isinstance(case.get("behavioral_settings"), dict) else {}
            cc = (case.get("chief_complaint") or "").lower()
            text = (reply_text or "").lower()

            # Baseline from traits
            candidates: List[str] = []
            if traits.get("anxious"):
                candidates.append("Anxious")
            if traits.get("defensive"):
                candidates.append("Defensive")
            if traits.get("friendly"):
                candidates.append("Warm")
            if traits.get("shy") or traits.get("introverted"):
                candidates.append("Reserved")

            if not candidates:
                candidates.append("Calm")

            # Amplify by complaint/content
            worry_keywords = ["chest pain", "shortness of breath", "sob", "faint", "dizzy", "severe", "sharp", "worse", "bleed", "palpit"]
            discomfort_keywords = ["pain", "nausea", "vomit", "headache", "cramp", "tender", "ache"]
            frustration_keywords = ["why", "again", "tired of", "don\'t want", "stop asking", "annoy"]

            if any(k in cc or k in text for k in worry_keywords):
                candidates.insert(0, "Concerned")
            elif any(k in cc or k in text for k in discomfort_keywords):
                candidates.insert(0, "Uncomfortable")
            if any(k in text for k in frustration_keywords) or traits.get("defensive"):
                candidates.insert(0, "Irritated")

            # Behavioral emotional flag reduces odds of "Neutral"
            if behav.get("emotional") and "Neutral" in candidates:
                candidates = [c for c in candidates if c != "Neutral"]

            # Construct short 3-6 word phrase
            unique = []
            for c in candidates:
                if c not in unique:
                    unique.append(c)
            phrase = ", ".join(unique[:2])
            if not phrase:
                phrase = "Calm"
            return phrase
        except Exception:
            return "Concerned"

    def _reconcile_emotion(self, case: Dict[str, Any], reply_text: str, llm_emotion: Optional[str]) -> str:
        """Prefer model emotion if specific and coherent; otherwise replace with inferred."""
        inferred = self._infer_emotion(case, reply_text)
        if not llm_emotion:
            return inferred
        e = llm_emotion.strip()
        if not e:
            return inferred
        low = e.lower()
        generic = {"neutral", "ok", "okay", "fine", "normal"}
        traits = case.get("personality_traits", {}) if isinstance(case.get("personality_traits"), dict) else {}

        # If anxious/defensive traits, avoid "neutral" outputs
        if (traits.get("anxious") or traits.get("defensive")) and any(g in low for g in generic):
            return inferred
        # Keep short and concise (3-10 words)
        words = re.split(r"\s+", e)
        if len(words) > 10:
            return inferred
        return e

    def clear_conversation_memory(self, key: str):
        """Clear the conversation memory for a specific key (conversation/session or case)."""
        if key in self.conversation_memories:
            del self.conversation_memories[key]
            logger.info(f"Cleared conversation memory for key: {key}")

    def get_conversation_history(self, key: str) -> List[Dict[str, str]]:
        """Get the conversation history for a specific key (conversation/session or case)."""
        if key in self.conversation_memories:
            memory = self.conversation_memories[key]
            return [
                {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else {"role": "assistant", "content": msg.content}
                for msg in memory.chat_memory.messages
            ]
        return []
