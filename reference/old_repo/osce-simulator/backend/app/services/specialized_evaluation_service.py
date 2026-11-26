#!/usr/bin/env python3
"""
Specialized Evaluation Service for OSCE
Handles individual category evaluation using specialized prompts.
"""

from typing import Dict, Any, Optional, Tuple, List, Union
from collections import defaultdict
import logging
import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from ..core.config import get_settings

# Read API key directly from file for reliability
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
settings = get_settings()
if not api_key:
    api_key = settings.OPENAI_API_KEY
    print(f"DEBUG: Using API key from settings: {api_key[:8] if api_key else 'None'}...")

logger = logging.getLogger(__name__)

class SpecializedEvaluationService:
    """Service for specialized OSCE evaluation using individual prompts for each category."""
    
    def __init__(self, llm=None):
        self.logger = logger
        self._evaluations = {}  # In-memory store for evaluations
        
        # Validate API key
        if not api_key:
            logger.error("No OpenAI API key found. Please set OPENAI_API_KEY in your .env file.")
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize LangChain ChatOpenAI if no LLM provided
        self.llm = llm or ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,  # Lower temperature for more consistent scoring
            api_key=api_key,
            max_tokens=1024,
            presence_penalty=0.0,  # Neutral presence penalty for scoring
            frequency_penalty=0.0,  # Neutral frequency penalty for scoring
        )
    
    def persist(self, conversation_id: str, evaluation_data: Dict[str, Any]) -> None:
        """Store evaluation data for a conversation."""
        self._evaluations[conversation_id] = evaluation_data
    
    def load(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load evaluation data for a conversation."""
        return self._evaluations.get(conversation_id)
    
    def list_for_user(self, user_conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """List evaluations for the given conversations."""
        evaluations = []
        for conv in user_conversations:
            conv_id = conv.get("conversation_id")
            if conv_id and conv_id in self._evaluations:
                eval_data = dict(self._evaluations[conv_id])
                eval_data["conversation_id"] = conv_id
                evaluations.append(eval_data)
        return evaluations
    


    def _prepare_transcript(self, transcript: Optional[Union[str, Dict]]) -> str:
        """Helper method to prepare transcript text from either string or conversation dict.
        
        Args:
            transcript: Either a string containing the transcript, a dict with messages, or None
            
        Returns:
            Formatted transcript text with "Doctor:" and "Patient:" prefixes, or "None" for None input
        """
        if transcript is None:
            return "None"
        if isinstance(transcript, dict) and "messages" in transcript:
            messages = transcript.get("messages", [])
            lines: List[str] = []
            for m in messages:
                role = m.get("role")
                content = m.get("content", "")
                if role == "user":
                    lines.append(f"Doctor: {content}")
                elif role == "assistant":
                    lines.append(f"Patient: {content}")
            return "\n".join(lines)
        return str(transcript)

    async def evaluate_introduction_collaboration(self, transcript_text: Optional[str], case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Introduction & Collaboration category (0-5 points)."""
        if transcript_text is None or transcript_text.strip() == "":
            return 0, "No transcript provided"
        try:

            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Introduction & Collaboration / Biographic Data (Score: 0–5)**

                Evaluate the following student interview based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 according to the scoring rubric. If the student fails to explicitly obtain consent, assign a score of 0 regardless of the other elements.

                **Required elements (9 total):**

                1. Self-introduction and role
                2. Greeting and explicit consent
                3. Reason for visit (chief complaint)
                4. Preferred name and/or pronouns
                5. Demographics (e.g., age, gender)
                6. Occupational status
                7. Relationship or marital status
                8. Living situation or address
                9. Language or cultural background

                **Scoring rubric:**

                * 5 = 8 or more elements addressed
                * 4 = 7 elements addressed
                * 3 = 5–6 elements addressed
                * 1 = 1–4 elements addressed
                * 0 = Consent not explicitly obtained

                **Instructions:**

                * Check how many of the required elements are clearly and explicitly addressed in the interview.
                * Use the scoring rubric to assign a single integer score (0–5).
                * Do not infer or assume information unless it is clearly stated.
                * If consent is missing or not clearly obtained, assign a score of 0.

                **Example:**
                If the student introduced themselves, obtained consent, asked for the reason for visit, and inquired about the patient's living situation, but did not ask about age, pronouns, occupation, or marital status, assign a score of 3 (Developing) for addressing 5–6 elements.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which elements were found/missing and why that score was given
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating introduction_collaboration: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_past_medical_history_part1(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Past Medical History Part 1 category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Past Medical History: Part 1 (Score: 0–5)**

                Evaluate the following student interview based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 according to the scoring rubric. The student must **ask at least one question related to sexual health** and **include at least one specific example of past medical history** to receive a score of 5.

                **Required elements (9 total):**

                1. Chronic conditions
                2. Past illnesses or infections
                3. Hospitalisations
                4. Surgeries
                5. Immunisations and preventive care
                6. Mental health history
                7. Obstetric or gynecologic history
                8. Sexual health (mandatory)
                9. Past allergies

                **Scoring rubric:**

                * 5 = 7 or more elements addressed, including at least one sexual health question and at least one example of a specific past medical condition
                * 4 = 6 elements addressed
                * 3 = 4–5 elements addressed
                * 1 = 1–3 elements addressed
                * 0 = Past medical history not covered at all

                **Instructions:**

                * Count the number of required elements explicitly addressed in the interview.
                * Do not infer or assume content; elements must be clearly stated.
                * Sexual health must be asked about to qualify for a 5.
                * One or more concrete examples of past medical history (e.g., "the patient had asthma as a child") must also be included for a score of 5.
                * Assign a single integer score (0–5) using the rubric above.

                **Example:**
                If the student asks about chronic conditions, hospitalisations, allergies, and mental health, and includes a patient history example, but omits sexual health, assign a score of 3 (Developing). A score of 5 is only appropriate if 7 or more elements are addressed, **sexual health is explicitly covered**, and at least one medical history **example** is given.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which elements were found/missing and why that score was given
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating past_medical_history_part1: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"

    async def evaluate_past_medical_history_part2(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Past Medical History Part 2 (Medications & Allergies) category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Past Medical History: Part 2 (Medications & Allergies) (Score: 0–5)**

                Evaluate the student's performance based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 using the rubric provided. **All medication-related elements must include both dose and frequency** to be counted. If the student does not explicitly address consent or skips this section entirely, assign a score of 0.

                **Required elements (8 total):**

                1. Prescription medications (must include dose and frequency)
                2. Over-the-counter (OTC) medications (must include dose and frequency)
                3. Herbal remedies or supplements (must include dose and frequency)
                4. Recreational drug use (must include dose and frequency if applicable)
                5. Dose and frequency explicitly addressed for each medication (if any medications are mentioned)
                6. Drug allergies
                7. Food or other allergies
                8. Adverse reactions

                **Scoring rubric:**

                * 5 = 8 or more elements addressed
                * 4 = 7 elements addressed
                * 3 = 5–6 elements addressed
                * 1 = 1–4 elements addressed
                * 0 = Section not covered

                **Instructions:**

                * Count how many of the 8 elements are clearly and explicitly addressed.
                * Medication entries (items 1–4) only count if **dose and frequency** are included.
                * If a student fails to include dose/frequency for a mentioned medication, do **not** count it.
                * If consent was not explicitly obtained, assign a score of 0 regardless of other elements.
                * Assign a single integer score (0–5) using the rubric above.

                **Example:**
                If the student asked about prescription and OTC medications (but did **not** include dose/frequency), supplements (without dose/frequency), and food allergies, they addressed only 4 valid elements → Score = 1 (Unsatisfactory).
                If they included all four medication types **with dose/frequency**, asked about drug and food allergies, and adverse reactions → Score = 5 (Excellent).

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which elements were found/missing and why that score was given. For medications, specify if dose/frequency were properly addressed.
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating past_medical_history_part2: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_family_history(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Family History category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Family History (Score: 0–5)**

                Evaluate the student's performance based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 using the scoring rubric. Full points require that **all three core generations** (parents, siblings/children, grandparents) are addressed **and** at least two examples of hereditary illnesses are explicitly discussed.

                **Required elements (6 total):**

                1. Parents' health
                2. Siblings' health
                3. Children's health
                4. Grandparents' health
                5. Extended family health (e.g., aunts, uncles, cousins)
                6. Specific hereditary illnesses (e.g., diabetes, heart disease, cancer, genetic disorders)

                **Scoring rubric:**

                * 5 = 5 or more elements addressed (must cover all three generations and include at least two examples of hereditary illness)
                * 4 = 4 elements addressed
                * 3 = 3 elements addressed
                * 1 = 1–2 elements addressed
                * 0 = Section not covered

                **Instructions:**

                * Count the number of elements explicitly addressed.
                * One element is awarded per **generation** covered (parents, siblings/children, grandparents, extended family).
                * Each explicitly discussed hereditary illness counts as an additional element.
                * Do not infer or assume content unless the student explicitly asks about it.
                * Assign a single integer score (0–5) based on the rubric.

                **Example:**
                If the student asked about parents' health, siblings' health, grandparents' health, and asked specifically about diabetes and heart disease, they addressed 5 valid elements → **Score = 5 (Excellent)**.
                If they only asked about parents' health, siblings' health, and one hereditary illness, they addressed 3 elements → **Score = 3 (Developing)**.
                If they did not ask any family history questions, assign **Score = 0 (Unsatisfactory)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which generations and hereditary illnesses were covered/missing and why that score was given
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating family_history: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_functional_assessment_part1(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Functional Assessment Part 1 category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Functional Assessment: Part 1 (Score: 0–5)**

                Evaluate the student's performance based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 using the rubric. To count an element, the student must meet the stated requirements.

                **Required elements (6 total):**

                1. Activity and exercise (**must be quantified** by frequency, duration, or intensity)
                2. Mobility and assistive devices
                3. Sleep patterns (**must explicitly elicit if daytime naps are taken**)
                4. Nutrition (**minimum one nutrition-related question required for the point**)
                5. Elimination (**minimum one elimination-related question required for the point**)
                6. Activities of daily living (ADLs)

                **Scoring rubric:**

                * 5 = 6 or more elements addressed (**Excellent**)
                * 4 = 5 elements addressed (**Proficient**)
                * 3 = 4 elements addressed (**Developing**)
                * 1 = 1–3 elements addressed (**Unsatisfactory**)
                * 0 = Section not covered (**Not Applicable**)

                **Instructions:**

                * Count the number of elements explicitly addressed by the student.
                * Do not award credit for **activity/exercise** unless the student quantifies it.
                * Do not award credit for **sleep patterns** unless the student explicitly asks about daytime naps.
                * For **nutrition** and **elimination**, a minimum of one relevant question per domain is required for the point to count.
                * Do not infer or assume details unless explicitly elicited.
                * Assign a single integer score (0–5) based on the rubric.

                **Example:**
                If the student asked about exercise (**partly quantified**) and diet but **did not ask** about mobility, sleep, elimination, or ADLs, they addressed only 2 valid elements → **Score = 1 (Unsatisfactory)**.
                If the student addressed exercise (**fully quantified**), mobility, sleep (including naps), nutrition, and elimination but missed ADLs, they addressed 5 elements → **Score = 4 (Proficient)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which elements were covered/missing and whether they met the specific requirements (e.g., if exercise was quantified, if naps were asked about)
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating functional_assessment_part1: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_functional_assessment_part2(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Functional Assessment Part 2 (0-5 points)."""
        if transcript_text is None or transcript_text.strip() == "":
            return 0, "No transcript provided"
        try:
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Functional Assessment: Part 2 (Score: 0–5)**

                Evaluate the student's performance based on how many of the required elements below are explicitly covered. Assign a score from 0 to 5 using the rubric. To count an element, the student must meet the stated requirements. **Two coping/stress questions and an advance-care planning question are mandatory for full points.** If advance-care planning is not explicitly asked, apply a **−1 point override** to the score.

                **Required elements (7 total):**

                1. Coping and stress management (**must ask at least two distinct coping/stress questions for full credit**)
                2. Smoking or vaping (**must include both pack count and years to earn the element point**)
                3. Alcohol consumption
                4. Recreational or illicit drug use
                5. Social support
                6. Mental health and mood
                7. Advance-care planning (**mandatory for full points**)

                **Scoring rubric:**

                * 5 = 7 or more elements addressed **and** includes two coping/stress questions **and** advance-care planning (**Excellent**)
                * 4 = 6 elements addressed (**Proficient**)
                * 3 = 4–5 elements addressed (**Developing**)
                * 1 = 1–3 elements addressed (**Unsatisfactory**)
                * 0 = Section not covered

                **Instructions:**

                * Count how many of the required elements were explicitly addressed.
                * For **coping and stress management**, two separate questions are required for full credit; one question counts as one element, but the student cannot receive a score of 5 without asking two.
                * For **smoking/vaping**, the student must explicitly ask about **both pack quantity and duration (years)** for the point to count.
                * If **advance-care planning** is missing, apply a **−1 point override** even if other elements are fully covered.
                * Do not infer or assume information; only count explicitly elicited responses.
                * Assign a single integer score (0–5) based on the rubric and override rule.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which elements were found/missing and why that score was given
                """
            )
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                self.logger.error("Raw response: %s", llm_response.content)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"
        except Exception as e:
            self.logger.error(f"Error evaluating functional_assessment_part2: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_review_of_systems(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Review of Systems (ROS) category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Review of Systems (ROS) (Score: 0–5)**

                Evaluate the student's performance based on how many relevant body systems were explicitly reviewed. Assign a score from 0 to 5 using the rubric. Each body system counts as one element **only if** the questions are relevant to the patient's past medical history (PMHx) or family history.

                **Required criteria:**

                * The student must review **specific body systems** by asking targeted questions.
                * Only systems **clinically relevant** to the patient's PMHx or family history count as valid elements.
                * General or unrelated ROS questions do **not** count toward the score.

                **Examples of valid systems (each counts as one element if relevant):**

                * Cardiovascular — chest pain, palpitations, shortness of breath
                * Respiratory — cough, wheezing, sputum
                * Endocrine — thirst, urination, weight changes
                * Neurological — headaches, dizziness, neuropathy
                * Gastrointestinal — nausea, abdominal pain, bowel changes
                * Genitourinary, musculoskeletal, integumentary, ocular/vision, and others if relevant

                **Scoring rubric:**

                * 5 = 5 or more relevant systems reviewed (**Excellent**)
                * 4 = 4 relevant systems reviewed (**Proficient**)
                * 3 = 3 relevant systems reviewed (**Developing**)
                * 1 = 1–2 relevant systems reviewed (**Unsatisfactory**)
                * 0 = Section not covered

                **Instructions:**

                * Count only the number of **relevant** systems explicitly reviewed.
                * For each system, there must be at least one targeted, symptom-based question.
                * If the system asked about is **not connected** to the patient's PMHx or family history, **do not award credit** for that element.
                * Assign a single integer score (0–5) using the rubric.

                **Example:**
                If the patient has diabetes and hyperlipidemia, relevant systems would include **endocrine** (polydipsia, polyuria), **cardiovascular** (chest pain, palpitations), **neurological** (neuropathy), and **integumentary** (foot ulcers).

                * If the student asks about five relevant systems → **Score = 5 (Excellent)**.
                * If they only ask about cardiovascular and respiratory symptoms unrelated to the patient's PMHx → **Score = 1 (Unsatisfactory)**.
                * If no ROS questions are asked → **Score = 0 (Not Covered)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which systems were reviewed, whether they were relevant to the patient's history, and why that score was given
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating review_of_systems: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_health_promotion_opportunities(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Opportunities for Health Promotion category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Opportunities for Health Promotion (Score: 0–5)**

                Evaluate the student's performance based on how many distinct health promotion or nursing intervention elements were explicitly provided. Assign a score from 0 to 5 using the rubric. Each unique intervention counts as one element.

                **Required elements (examples of valid interventions):**

                1. **Allergy preparedness** — e.g., advising the patient to carry an EpiPen for severe allergies
                2. **Chronic disease management** — e.g., recommending ≥150 minutes/week of exercise, dietary changes, or glucose monitoring for diabetes
                3. **Lifestyle risk reduction** — e.g., counselling on smoking/vaping cessation, safe alcohol limits, or drug cessation
                4. **Stress management** — e.g., suggesting journaling, mindfulness, or coping strategies
                5. **Routine screening** — e.g., recommending vaccinations, cholesterol checks, or blood-pressure monitoring
                6. **Safety measures** — e.g., encouraging seat belts, sun protection, condom use, helmet use, etc.

                **Scoring rubric:**

                * 5 = 3 or more distinct health promotion or nursing intervention elements (**Excellent**)
                * 4 = 2 elements addressed (**Proficient**)
                * 3 = 1 element addressed (**Developing**)
                * 1 = Attempted but incomplete intervention (**Unsatisfactory**)
                * 0 = Section not covered (**Not Applicable**)

                **Instructions:**

                * Count the number of **explicit and distinct** health promotion or nursing intervention elements addressed.
                * Each **unique teaching point** or intervention counts as one element.
                * Incomplete or vague advice (e.g., "You should be healthier") does **not** count as a valid element unless specific actions are described.
                * Assign a single integer score (0–5) based on the rubric.

                **Example:**
                If the student:

                * Advises carrying an EpiPen for a peanut allergy (**allergy preparedness**)
                * Recommends 150 minutes/week of moderate exercise for diabetes (**chronic disease management**)
                * Counsels on vaping and alcohol reduction (**lifestyle risk reduction**)
                  These three interventions = **Score = 5 (Excellent)**.

                If the student only recommends mindfulness for stress → **Score = 3 (Developing)**.
                If the student vaguely says "try to live healthier" without giving specifics → **Score = 1 (Unsatisfactory)**.
                If no health promotion advice is provided → **Score = 0 (Not Covered)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining which health promotion elements were provided, whether they were specific enough to count, and why that score was given
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating health_promotion_opportunities: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_quality_health_promotion(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Quality of Health Promotion category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Quality of Health Promotion (Score: 0–5)**

                Evaluate **how** the student delivers health promotion and patient education, not just the number of interventions. Focus on clarity, tailoring, verification of understanding, and evidence-based recommendations. Assign a score from 0 to 5 using the rubric.

                **Scoring rubric:**

                * **5 = Excellent** — Information is delivered in **short, clear, and understandable statements**; patient understanding is **consistently verified**; **all recommendations are evidence-based** and **tailored** to the patient's conditions.
                * **4 = Proficient** — Information is mostly provided in **short statements** with occasional longer explanations; **some verification** of patient understanding; most recommendations are **evidence-based and tailored**, but one may be less so.
                * **3 = Developing** — Information is delivered in **long monologues** without breaking content into manageable pieces; **no verification** of understanding; advice is mostly **evidence-based** but not tailored well.
                * **1 = Unsatisfactory** — Explanations are **confusing, vague, or not simplified**; recommendations are **non-evidence-based** or **irrelevant**; patient understanding is not checked.
                * **0 = Not Applicable** — No health promotion or patient education provided.

                **Instructions:**

                * Evaluate **quality**, not quantity.
                * Prioritize clarity, evidence basis, and patient-centered tailoring.
                * Deduct points if:

                  * The student fails to verify understanding (e.g., does not ask "Does this make sense?").
                  * Advice is generic rather than tailored.
                  * Recommendations are unsupported or contradictory to clinical guidelines.
                * Assign a single integer score (0–5) based on the rubric.

                **Example:**
                If the student says:
                *"Since you're allergic to peanuts, carrying an EpiPen at all times can be lifesaving. Would you like me to help you get a prescription?"*
                — and verifies understanding → **Score = 5 (Excellent)**.

                If the student offers tailored advice but **does not always check patient understanding** → **Score = 4 (Proficient)**.

                If the student provides long, dense explanations without interaction → **Score = 3 (Developing)**.

                If the student gives vague or non-evidence-based recommendations → **Score = 1 (Unsatisfactory)**.

                If no health promotion occurs → **Score = 0 (Not Applicable)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining how the health promotion was delivered, focusing on clarity, verification of understanding, evidence basis, and tailoring to the patient
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating quality_health_promotion: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_interview_style(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Global Appreciation (Interview Style) category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Global Appreciation (Interview Style) (Score: 0–5)**

                Evaluate the student's **overall questioning style** during the interview. Focus on whether the student uses open-ended questions, guides the conversation purposefully, and avoids negatively phrased or leading questions. Assign a score from 0 to 5 using the rubric below.

                **Scoring rubric:**

                * **5 = Excellent** — Consistently uses **open-ended questions** to determine the reason for visit and gather information; guides the interview smoothly and purposefully; **avoids negatively phrased questions**.
                * **4 = Proficient** — Confirms the reason for the visit using a **statement** rather than an open-ended question; guides **most** of the interview effectively; uses few negatively phrased questions.
                * **3 = Developing** — Relies more on **statements** than questions; guides only **part** of the interview; includes some negatively phrased or leading questions (e.g., *"You don't smoke, do you?"*).
                * **1 = Unsatisfactory** — Does **not** use open-ended questions; fails to guide the interview; frequently uses negative or biased phrasing.
                * **0 = Not Applicable** — Cannot assess due to insufficient interaction or missing questioning.

                **Instructions:**

                * Evaluate the **global quality** of the student's questioning style.
                * Prioritize:

                  * Use of **open-ended vs. closed** questions
                  * Ability to **guide the conversation purposefully**
                  * Avoidance of **negatively phrased or biased** questions
                * Do **not** evaluate specific content here — only the **style** and **flow** of questioning.
                * Assign a single integer score (0–5) using the rubric.

                **Example:**

                * If the student asks, *"What brings you in today?"*, follows up with open-ended, purposeful questions, and avoids negative phrasing → **Score = 5 (Excellent)**.
                * If the student uses a statement like, *"So you're here for a checkup,"* but otherwise guides the conversation well → **Score = 4 (Proficient)**.
                * If the student mixes statements with a few negative or leading questions and only partially guides the interview → **Score = 3 (Developing)**.
                * If the student does not use open-ended questions and fails to guide the interview effectively → **Score = 1 (Unsatisfactory)**.
                * If there is not enough questioning to assess → **Score = 0 (Not Applicable)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining the student's questioning style, focusing on open-ended questions, interview guidance, and avoidance of negative phrasing
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating interview_style: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_organization(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Organization category (0-5 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Organization (Score: 0–5)**

                Evaluate the **overall organization and sequencing** of the student's interview. Focus on whether the topics follow a logical flow and whether transitions between sections are smooth. Assign a score from 0 to 5 using the rubric below.

                **Scoring rubric:**

                * **5 = Excellent** — Interview follows a **clear, logical sequence** from start to finish (e.g., **introduction → presenting problem → past history → functional assessment → review of systems → health promotion**). Minimal redundancy or topic-hopping.
                * **4 = Proficient** — Interview is mostly well-organized and orderly; **minor lapses** in sequencing but overall flow is maintained.
                * **3 = Developing** — Some structure is present but there is **noticeable disorganization**, missed transitions, or incomplete sections.
                * **1 = Unsatisfactory** — Interview is **disorganized**, jumps between unrelated topics, frequently repeats questions, and lacks a coherent flow.
                * **0 = Not Applicable** — Cannot assess due to insufficient information or incomplete interview.

                **Instructions:**

                * Evaluate the **sequence and flow** of the interview, not the content of individual answers.
                * Prioritize:

                  * Logical progression between sections
                  * Smooth transitions
                  * Avoidance of unnecessary repetition or abrupt topic changes
                * Deduct points for missing sections that disrupt the logical sequence.
                * Assign a single integer score (0–5) using the rubric.

                **Example:**

                * If the student introduces themselves, obtains the presenting problem, explores past history, performs functional assessments, conducts a review of systems, and ends with health promotion → **Score = 5 (Excellent)**.
                * If the student maintains an overall logical flow but skips one minor section → **Score = 4 (Proficient)**.
                * If the student partially follows a structure but misses key sections (e.g., **family history** or **ROS**) and makes abrupt jumps between topics → **Score = 3 (Developing)**.
                * If the interview feels disorganized and repetitive → **Score = 1 (Unsatisfactory)**.
                * If organization cannot be assessed → **Score = 0 (Not Applicable)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-5
                2. "feedback": detailed string explaining the interview's organization, focusing on sequence, transitions, and any issues with flow or missing sections
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating organization: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_clinical_judgment(self, transcript_text: str, case_details: Optional[dict] = None) -> Tuple[int, str]:
        """Evaluate Professionalism & Clinical Judgement category (0-10 points)."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                **Grading Prompt – Professionalism & Clinical Judgement (Score: 0–10)**

                Evaluate the student's **overall clinical knowledge, reasoning, professionalism, and demeanor** during the interview. Consider their ability to provide respectful, empathetic, and tailored care while demonstrating appropriate clinical understanding. Assign a score from **0 to 10** using the rubric below.

                **Scoring rubric:**

                * **10 = Excellent** — Demonstrates **comprehensive clinical knowledge** relevant to the patient's conditions; uses **respectful, empathetic language**; tailors advice to the patient's context; maintains a **non-judgmental tone** throughout.
                * **7 = Proficient** — Demonstrates **good knowledge** but misses some nuances or subtleties; generally maintains professionalism and empathy.
                * **5 = Developing** — Shows **partial knowledge gaps** and occasional lapses in professionalism, empathy, or clinical reasoning.
                * **3 = Unsatisfactory** — Demonstrates **minimal knowledge**, makes frequent clinical errors, or exhibits significant professionalism concerns (e.g., judgmental tone, dismissive attitude).
                * **0 = Not Applicable** — Cannot assess due to insufficient interaction.

                **Instructions:**

                * Evaluate **knowledge, reasoning, and demeanor** holistically.
                * Consider the following dimensions:

                  * **Clinical knowledge:** Are recommendations accurate and appropriate for the patient's conditions?
                  * **Professionalism:** Is communication respectful, supportive, and free from judgment?
                  * **Empathy:** Does the student demonstrate understanding of the patient's concerns?
                  * **Tailoring:** Are recommendations individualized based on the patient's history and needs?
                * Assign a single score (0–10) based on the overall impression.

                **Example:**

                * If the student demonstrates **strong knowledge** of diabetes, smoking cessation, and allergy management; provides empathetic, tailored advice; and maintains a professional tone → **Score = 10 (Excellent)**.
                * If the student shows **good knowledge** but misses important nuances (e.g., fails to address sexual history, family history, or ROS) → **Score = 7 (Proficient)**.
                * If the student exhibits **knowledge gaps** and occasional lapses in respectful communication → **Score = 5 (Developing)**.
                * If the student demonstrates **limited knowledge** and uses dismissive or judgmental language → **Score = 3 (Unsatisfactory)**.
                * If insufficient information is available to assess → **Score = 0 (Not Applicable)**.

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Provide your evaluation in JSON format with two fields:
                1. "score": integer between 0-10
                2. "feedback": detailed string explaining the student's clinical knowledge, professionalism, empathy, and ability to tailor recommendations
                """
            )

            # Get LLM response
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case_details) if case_details else "null",
                transcript=transcript_text
            ))

            # Parse response
            try:
                result = json.loads(llm_response.content)
                return result["score"], result["feedback"]
            except Exception as parse_error:
                self.logger.error("Failed to parse LLM response: %s", parse_error)
                return 0, f"Evaluation parsing failed: {str(parse_error)}"

        except Exception as e:
            self.logger.error(f"Error evaluating clinical_judgment: {str(e)}")
            return 0, f"Evaluation error: {str(e)}"
    
    async def evaluate_all_categories(self, transcript: Union[str, Dict], case_details: Optional[dict] = None) -> Dict[str, Any]:
        """Evaluate all OSCE categories and return comprehensive results."""
        if transcript is None or (isinstance(transcript, str) and not transcript.strip()):
            return {
                "scores": {},
                "feedback": {},
                "total_score": 0,
                "max_possible": 65
            }
        try:
            # Prepare transcript once for all evaluations
            transcript_text = self._prepare_transcript(transcript)
            
            # Evaluate each category with prepared transcript
            try:
                intro_score, intro_feedback = await self.evaluate_introduction_collaboration(transcript_text, case_details)
                self.logger.debug("Introduction & Collaboration evaluated: %d", intro_score)
            except Exception as e:
                self.logger.error("Error evaluating introduction_collaboration: %s", str(e))
                intro_score, intro_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                pmh1_score, pmh1_feedback = await self.evaluate_past_medical_history_part1(transcript_text, case_details)
                self.logger.debug("Past Medical History Part 1 evaluated: %d", pmh1_score)
            except Exception as e:
                self.logger.error("Error evaluating past_medical_history_part1: %s", str(e))
                pmh1_score, pmh1_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                pmh2_score, pmh2_feedback = await self.evaluate_past_medical_history_part2(transcript_text, case_details)
                self.logger.debug("Past Medical History Part 2 evaluated: %d", pmh2_score)
            except Exception as e:
                self.logger.error("Error evaluating past_medical_history_part2: %s", str(e))
                pmh2_score, pmh2_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                family_score, family_feedback = await self.evaluate_family_history(transcript_text, case_details)
                self.logger.debug("Family History evaluated: %d", family_score)
            except Exception as e:
                self.logger.error("Error evaluating family_history: %s", str(e))
                family_score, family_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                func1_score, func1_feedback = await self.evaluate_functional_assessment_part1(transcript_text, case_details)
                self.logger.debug("Functional Assessment Part 1 evaluated: %d", func1_score)
            except Exception as e:
                self.logger.error("Error evaluating functional_assessment_part1: %s", str(e))
                func1_score, func1_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                func2_score, func2_feedback = await self.evaluate_functional_assessment_part2(transcript_text, case_details)
                self.logger.debug("Functional Assessment Part 2 evaluated: %d", func2_score)
            except Exception as e:
                self.logger.error("Error evaluating functional_assessment_part2: %s", str(e))
                func2_score, func2_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                ros_score, ros_feedback = await self.evaluate_review_of_systems(transcript_text, case_details)
                self.logger.debug("Review of Systems evaluated: %d", ros_score)
            except Exception as e:
                self.logger.error("Error evaluating review_of_systems: %s", str(e))
                ros_score, ros_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                hpo_score, hpo_feedback = await self.evaluate_health_promotion_opportunities(transcript_text, case_details)
                self.logger.debug("Health Promotion Opportunities evaluated: %d", hpo_score)
            except Exception as e:
                self.logger.error("Error evaluating health_promotion_opportunities: %s", str(e))
                hpo_score, hpo_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                qhp_score, qhp_feedback = await self.evaluate_quality_health_promotion(transcript_text, case_details)
                self.logger.debug("Quality Health Promotion evaluated: %d", qhp_score)
            except Exception as e:
                self.logger.error("Error evaluating quality_health_promotion: %s", str(e))
                qhp_score, qhp_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                style_score, style_feedback = await self.evaluate_interview_style(transcript_text, case_details)
                self.logger.debug("Interview Style evaluated: %d", style_score)
            except Exception as e:
                self.logger.error("Error evaluating interview_style: %s", str(e))
                style_score, style_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                org_score, org_feedback = await self.evaluate_organization(transcript_text, case_details)
                self.logger.debug("Organization evaluated: %d", org_score)
            except Exception as e:
                self.logger.error("Error evaluating organization: %s", str(e))
                org_score, org_feedback = 0, f"Evaluation error: {str(e)}"

            try:
                cj_score, cj_feedback = await self.evaluate_clinical_judgment(transcript_text, case_details)
                self.logger.debug("Clinical Judgment evaluated: %d", cj_score)
            except Exception as e:
                self.logger.error("Error evaluating clinical_judgment: %s", str(e))
                cj_score, cj_feedback = 0, f"Evaluation error: {str(e)}"
            
            # Calculate total score
            total_score = (intro_score + pmh1_score + pmh2_score + family_score + func1_score + func2_score + 
                          ros_score + hpo_score + qhp_score + style_score + 
                          org_score + cj_score)
            
            # Generate overall feedback
            overall_feedback = f"Total score: {total_score}/65. Evaluation completed."
            
            return {
                "scores": {
                    "introduction_collaboration": intro_score,
                    "past_medical_history_part1": pmh1_score,
                    "past_medical_history_part2": pmh2_score,
                    "family_history": family_score,
                    "functional_assessment_part1": func1_score,
                    "functional_assessment_part2": func2_score,
                    "review_of_systems": ros_score,
                    "health_promotion_opportunities": hpo_score,
                    "quality_health_promotion": qhp_score,
                    "interview_style": style_score,
                    "organization": org_score,
                    "clinical_judgment": cj_score
                },
                "feedback": {
                    "introduction_collaboration": intro_feedback,
                    "past_medical_history_part1": pmh1_feedback,
                    "past_medical_history_part2": pmh2_feedback,
                    "family_history": family_feedback,
                    "functional_assessment_part1": func1_feedback,
                    "functional_assessment_part2": func2_feedback,
                    "review_of_systems": ros_feedback,
                    "health_promotion_opportunities": hpo_feedback,
                    "quality_health_promotion": qhp_feedback,
                    "interview_style": style_feedback,
                    "organization": org_feedback,
                    "clinical_judgment": cj_feedback,
                    "overall": overall_feedback
                },
                "total_score": total_score,
                "max_possible": 65
            }
            
        except Exception as e:
            self.logger.error(f"Error in specialized evaluation: {str(e)}")
            return {
                "error": f"Evaluation failed: {str(e)}",
                "scores": {},
                "feedback": {},
                "total_score": 0,
                "max_possible": 65
            }
