from typing import List, Literal, Optional

from pydantic import BaseModel, Field

CONFIDENCE_THRESHOLD = 0.6

TEXT_FIELDS = ["name", "email", "phone", "company", "designation"]
ALL_FIELDS  = TEXT_FIELDS + ["skills"]

ExtractionStatus = Literal["extracted", "extraction_failed"]


class TextField(BaseModel):
    value:      Optional[str] = Field(default=None, description="Extracted value, or null if not found")
    confidence: float         = Field(ge=0, le=1, description="Confidence that this value is correct")


class SkillsField(BaseModel):
    value:      List[str] = Field(default_factory=list, description="List of skills found, empty if none")
    confidence: float     = Field(ge=0, le=1, description="Confidence that this list is correct")


class ResumeExtraction(BaseModel):
    name:        TextField
    email:       TextField
    phone:       TextField
    company:     TextField
    designation: TextField
    skills:      SkillsField
