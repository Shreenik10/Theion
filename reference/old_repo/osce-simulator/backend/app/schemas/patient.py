from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum

class DifficultyLevel(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    HARD = "hard"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class PersonalityTrait(BaseModel):
    shy: bool = False
    introverted: bool = False
    anxious: bool = False
    talkative: bool = False
    defensive: bool = False
    friendly: bool = False

class BehavioralSettings(BaseModel):
    cooperative: bool = True
    provides_complete_answers: bool = True
    emotional: bool = False

class PatientCaseRequest(BaseModel):
    difficulty: DifficultyLevel = Field(..., description="Difficulty level of the case")
    age: int = Field(..., ge=0, le=120, description="Patient's age")
    gender: Gender = Field(..., description="Patient's gender")
    personality_traits: Optional[PersonalityTrait] = Field(default_factory=PersonalityTrait)
    behavioral_settings: Optional[BehavioralSettings] = Field(default_factory=BehavioralSettings)

class PatientCase(BaseModel):
    id: str
    name: str = Field(..., description="Patient's full name")
    chief_complaint: str
    history_of_present_illness: str
    past_medical_history: str
    medications: List[str]
    allergies: List[str]
    social_history: str
    family_history: str
    vital_signs: Dict[str, str]
    physical_examination: str
    labs: Optional[Dict[str, str]]
    imaging: Optional[Dict[str, str]]
    difficulty: DifficultyLevel
    age: int
    gender: Gender
    personality_traits: PersonalityTrait
    behavioral_settings: BehavioralSettings 