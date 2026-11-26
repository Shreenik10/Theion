from pydantic import BaseModel
from typing import Dict, Optional

class SpecializedEvaluationScores(BaseModel):
    introduction_collaboration: int
    past_medical_history_part1: int
    past_medical_history_part2: int
    family_history: int
    functional_assessment_part1: int
    functional_assessment_part2: int
    review_of_systems: int
    health_promotion_opportunities: int
    quality_health_promotion: int
    interview_style: int
    organization: int
    clinical_judgment: int

class SpecializedEvaluationFeedback(BaseModel):
    introduction_collaboration: str
    past_medical_history_part1: str
    past_medical_history_part2: str
    family_history: str
    functional_assessment_part1: str
    functional_assessment_part2: str
    review_of_systems: str
    health_promotion_opportunities: str
    quality_health_promotion: str
    interview_style: str
    organization: str
    clinical_judgment: str
    overall: str

class SpecializedEvaluationResponse(BaseModel):
    case_id: str
    conversation_id: str
    scores: SpecializedEvaluationScores
    feedback: SpecializedEvaluationFeedback
    total_score: int
    max_possible: int = 65
    time_taken: Optional[int] = None
    details: Optional[Dict] = None
