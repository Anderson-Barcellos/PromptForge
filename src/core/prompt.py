"""
Prompt data models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PromptVersion(BaseModel):
    """Individual version of a prompt"""
    id: Optional[int] = None
    prompt_id: int
    version: int
    content: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Result of prompt analysis"""
    id: Optional[int] = None
    version_id: int
    analysis_type: str  # 'clarity', 'completeness', 'efficiency', 'safety', 'general'
    score: Optional[int] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.now)


class TestCase(BaseModel):
    """Test case for prompt evaluation"""
    id: Optional[int] = None
    prompt_id: int
    name: str
    input_text: str
    expected_output: Optional[str] = None
    evaluation_criteria: str
    created_at: datetime = Field(default_factory=datetime.now)


class TestResult(BaseModel):
    """Result of running a test case"""
    id: Optional[int] = None
    test_case_id: int
    version_id: int
    output: str
    score: Optional[float] = None
    evaluation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Prompt(BaseModel):
    """Main prompt entity"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    current_version: int = 1
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
