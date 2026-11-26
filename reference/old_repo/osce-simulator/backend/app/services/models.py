from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Pydantic models for structured output
class PatientCaseOutput(BaseModel):
    id: str = Field(description="Unique case identifier")
    name: str = Field(description="Patient's full name (e.g., 'Sarah Johnson', 'Michael Chen')")
    chief_complaint: str = Field(description="Main complaint")
    history_of_present_illness: str = Field(description="Detailed history")
    past_medical_history: str = Field(description="Relevant past medical history")
    medications: List[str] = Field(description="List of medications")
    allergies: List[str] = Field(description="List of allergies")
    social_history: str = Field(description="Relevant social history")
    family_history: str = Field(description="Relevant family history")
    vital_signs: Dict[str, str] = Field(description="Vital signs")
    physical_examination: str = Field(description="Physical examination findings")
    labs: Dict[str, str] = Field(description="Laboratory results")
    imaging: Dict[str, str] = Field(description="Imaging results")
    difficulty: str = Field(description="Case difficulty level")
    age: int = Field(description="Patient age")
    gender: str = Field(description="Patient gender")
    personality_traits: Dict[str, bool] = Field(description="Personality traits")
    behavioral_settings: Dict[str, bool] = Field(description="Behavioral settings")

class EvaluationOutput(BaseModel):
    history_taking_score: int = Field(description="Score for history taking (0-5)")
    communication_score: int = Field(description="Score for communication (0-5)")
    clinical_reasoning_score: int = Field(description="Score for clinical reasoning (0-5)")
    professionalism_score: int = Field(description="Score for professionalism (0-5)")
    time_efficiency_score: int = Field(description="Score for time efficiency (0-5)")
    feedback: str = Field(description="Detailed feedback")

# LLM rubric aligned to OSCE rubric structure
class LlmRubricScores(BaseModel):
    # Core Assessment Categories (0-6 each)
    introduction_collaboration: int = Field(description="0-6: Introduction & collaboration with patient, biographical data, PMH Part 1")
    past_medical_history_part2: int = Field(description="0-6: Past Medical History Part 2 - medications and allergies")
    family_history: int = Field(description="0-6: Family History - 3 generations and hereditary conditions")
    functional_assessment_part1: int = Field(description="0-6: Functional Assessment Part 1 - activity, mobility, sleep, nutrition, elimination")
    functional_assessment_part2: int = Field(description="0-6: Functional Assessment Part 2 - coping, smoking/vaping, advanced care planning")
    review_of_systems: int = Field(description="0-6: Review of Systems - must be related to PMHx or Family Hx")
    health_promotion_opportunities: int = Field(description="0-6: Opportunities for Health Promotion - 3 health promotion items")
    quality_health_promotion: int = Field(description="0-6: Quality of Health Promotion - communication style and evidence-based recommendations")
    
    # Global Appreciation Categories
    patient_centered_care: int = Field(description="0-6: Global Appreciation - Patient Centered Care")
    interview_style: int = Field(description="0-6: Global Appreciation - Interview Style")
    organization: int = Field(description="0-6: Global Appreciation - Organization")
    clinical_judgment: int = Field(description="0-10: Global Appreciation - Clinical Judgment, Reasoning and Knowledge")
    professionalism: int = Field(description="0-6: Global Appreciation - Professionalism")

class LlmRubricFeedback(BaseModel):
    # Core Assessment Categories
    introduction_collaboration: str
    past_medical_history_part2: str
    family_history: str
    functional_assessment_part1: str
    functional_assessment_part2: str
    review_of_systems: str
    health_promotion_opportunities: str
    quality_health_promotion: str
    
    # Global Appreciation Categories
    patient_centered_care: str
    interview_style: str
    organization: str
    clinical_judgment: str
    professionalism: str
    overall: str

class LlmRubricOutput(BaseModel):
    scores: LlmRubricScores
    feedback: LlmRubricFeedback

# Chat output with emotion
class ChatEmotionOutput(BaseModel):
    reply: str = Field(description="Patient reply text without speaker labels")
    emotion: str = Field(description="Short description of the patient's emotional state (3-10 words)")
