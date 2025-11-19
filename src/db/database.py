"""
Database management using SQLAlchemy
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from src.config import config

Base = declarative_base()


class PromptModel(Base):
    """SQLAlchemy model for Prompt"""
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    metadata = Column(JSON, default=dict)

    # Relationships
    versions = relationship("PromptVersionModel", back_populates="prompt", cascade="all, delete-orphan")
    test_cases = relationship("TestCaseModel", back_populates="prompt", cascade="all, delete-orphan")


class PromptVersionModel(Base):
    """SQLAlchemy model for PromptVersion"""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    tags = Column(JSON, default=list)

    # Relationships
    prompt = relationship("PromptModel", back_populates="versions")
    analyses = relationship("AnalysisResultModel", back_populates="version", cascade="all, delete-orphan")
    test_results = relationship("TestResultModel", back_populates="version", cascade="all, delete-orphan")


class AnalysisResultModel(Base):
    """SQLAlchemy model for AnalysisResult"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    score = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    version = relationship("PromptVersionModel", back_populates="analyses")


class TestCaseModel(Base):
    """SQLAlchemy model for TestCase"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    input_text = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=True)
    evaluation_criteria = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    prompt = relationship("PromptModel", back_populates="test_cases")
    test_results = relationship("TestResultModel", back_populates="test_case", cascade="all, delete-orphan")


class TestResultModel(Base):
    """SQLAlchemy model for TestResult"""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False)
    output = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    evaluation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    test_case = relationship("TestCaseModel", back_populates="test_results")
    version = relationship("PromptVersionModel", back_populates="test_results")


class Database:
    """Database manager"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or config.DATABASE_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    # Prompt operations
    def create_prompt(self, name: str, description: Optional[str] = None, content: str = "") -> int:
        """
        Create a new prompt

        Args:
            name: Prompt name
            description: Prompt description
            content: Initial prompt content

        Returns:
            Prompt ID
        """
        session = self.get_session()
        try:
            prompt = PromptModel(name=name, description=description)
            session.add(prompt)
            session.flush()

            # Create initial version
            version = PromptVersionModel(
                prompt_id=prompt.id,
                version=1,
                content=content
            )
            session.add(version)
            session.commit()

            return prompt.id
        finally:
            session.close()

    def get_prompt(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """Get prompt by ID"""
        session = self.get_session()
        try:
            prompt = session.query(PromptModel).filter_by(id=prompt_id).first()
            if not prompt:
                return None

            return {
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "current_version": prompt.current_version,
                "created_at": prompt.created_at,
                "updated_at": prompt.updated_at,
                "metadata": prompt.metadata
            }
        finally:
            session.close()

    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all prompts"""
        session = self.get_session()
        try:
            prompts = session.query(PromptModel).order_by(PromptModel.updated_at.desc()).all()
            return [{
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "current_version": p.current_version,
                "created_at": p.created_at,
                "updated_at": p.updated_at
            } for p in prompts]
        finally:
            session.close()

    def update_prompt(self, prompt_id: int, **kwargs):
        """Update prompt metadata"""
        session = self.get_session()
        try:
            prompt = session.query(PromptModel).filter_by(id=prompt_id).first()
            if prompt:
                for key, value in kwargs.items():
                    if hasattr(prompt, key):
                        setattr(prompt, key, value)
                prompt.updated_at = datetime.now()
                session.commit()
        finally:
            session.close()

    def delete_prompt(self, prompt_id: int):
        """Delete a prompt and all related data"""
        session = self.get_session()
        try:
            prompt = session.query(PromptModel).filter_by(id=prompt_id).first()
            if prompt:
                session.delete(prompt)
                session.commit()
        finally:
            session.close()

    # Version operations
    def create_version(self, prompt_id: int, content: str, notes: Optional[str] = None) -> int:
        """Create a new version of a prompt"""
        session = self.get_session()
        try:
            prompt = session.query(PromptModel).filter_by(id=prompt_id).first()
            if not prompt:
                raise ValueError(f"Prompt {prompt_id} not found")

            new_version_num = prompt.current_version + 1
            version = PromptVersionModel(
                prompt_id=prompt_id,
                version=new_version_num,
                content=content,
                notes=notes
            )
            session.add(version)

            prompt.current_version = new_version_num
            prompt.updated_at = datetime.now()

            session.commit()
            return version.id
        finally:
            session.close()

    def get_version(self, version_id: int) -> Optional[Dict[str, Any]]:
        """Get specific version"""
        session = self.get_session()
        try:
            version = session.query(PromptVersionModel).filter_by(id=version_id).first()
            if not version:
                return None

            return {
                "id": version.id,
                "prompt_id": version.prompt_id,
                "version": version.version,
                "content": version.content,
                "notes": version.notes,
                "created_at": version.created_at,
                "tags": version.tags or []
            }
        finally:
            session.close()

    def get_current_version(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """Get current version of a prompt"""
        session = self.get_session()
        try:
            prompt = session.query(PromptModel).filter_by(id=prompt_id).first()
            if not prompt:
                return None

            version = session.query(PromptVersionModel).filter_by(
                prompt_id=prompt_id,
                version=prompt.current_version
            ).first()

            if not version:
                return None

            return {
                "id": version.id,
                "prompt_id": version.prompt_id,
                "version": version.version,
                "content": version.content,
                "notes": version.notes,
                "created_at": version.created_at,
                "tags": version.tags or []
            }
        finally:
            session.close()

    def list_versions(self, prompt_id: int) -> List[Dict[str, Any]]:
        """List all versions of a prompt"""
        session = self.get_session()
        try:
            versions = session.query(PromptVersionModel).filter_by(
                prompt_id=prompt_id
            ).order_by(PromptVersionModel.version.desc()).all()

            return [{
                "id": v.id,
                "version": v.version,
                "content": v.content[:100] + "..." if len(v.content) > 100 else v.content,
                "notes": v.notes,
                "created_at": v.created_at
            } for v in versions]
        finally:
            session.close()

    # Analysis operations
    def save_analysis(self, version_id: int, analysis_type: str, content: str, score: Optional[int] = None) -> int:
        """Save analysis result"""
        session = self.get_session()
        try:
            analysis = AnalysisResultModel(
                version_id=version_id,
                analysis_type=analysis_type,
                score=score,
                content=content
            )
            session.add(analysis)
            session.commit()
            return analysis.id
        finally:
            session.close()

    def get_analyses(self, version_id: int) -> List[Dict[str, Any]]:
        """Get all analyses for a version"""
        session = self.get_session()
        try:
            analyses = session.query(AnalysisResultModel).filter_by(
                version_id=version_id
            ).order_by(AnalysisResultModel.created_at.desc()).all()

            return [{
                "id": a.id,
                "analysis_type": a.analysis_type,
                "score": a.score,
                "content": a.content,
                "created_at": a.created_at
            } for a in analyses]
        finally:
            session.close()

    # Test case operations
    def create_test_case(
        self,
        prompt_id: int,
        name: str,
        input_text: str,
        evaluation_criteria: str,
        expected_output: Optional[str] = None
    ) -> int:
        """Create a test case"""
        session = self.get_session()
        try:
            test_case = TestCaseModel(
                prompt_id=prompt_id,
                name=name,
                input_text=input_text,
                expected_output=expected_output,
                evaluation_criteria=evaluation_criteria
            )
            session.add(test_case)
            session.commit()
            return test_case.id
        finally:
            session.close()

    def get_test_cases(self, prompt_id: int) -> List[Dict[str, Any]]:
        """Get all test cases for a prompt"""
        session = self.get_session()
        try:
            test_cases = session.query(TestCaseModel).filter_by(
                prompt_id=prompt_id
            ).all()

            return [{
                "id": tc.id,
                "name": tc.name,
                "input_text": tc.input_text,
                "expected_output": tc.expected_output,
                "evaluation_criteria": tc.evaluation_criteria,
                "created_at": tc.created_at
            } for tc in test_cases]
        finally:
            session.close()

    def delete_test_case(self, test_case_id: int):
        """Delete a test case"""
        session = self.get_session()
        try:
            test_case = session.query(TestCaseModel).filter_by(id=test_case_id).first()
            if test_case:
                session.delete(test_case)
                session.commit()
        finally:
            session.close()

    # Test result operations
    def save_test_result(
        self,
        test_case_id: int,
        version_id: int,
        output: str,
        score: Optional[float] = None,
        evaluation: Optional[str] = None
    ) -> int:
        """Save test result"""
        session = self.get_session()
        try:
            result = TestResultModel(
                test_case_id=test_case_id,
                version_id=version_id,
                output=output,
                score=score,
                evaluation=evaluation
            )
            session.add(result)
            session.commit()
            return result.id
        finally:
            session.close()

    def get_test_results(self, version_id: int) -> List[Dict[str, Any]]:
        """Get all test results for a version"""
        session = self.get_session()
        try:
            results = session.query(TestResultModel).filter_by(
                version_id=version_id
            ).all()

            return [{
                "id": r.id,
                "test_case_id": r.test_case_id,
                "output": r.output,
                "score": r.score,
                "evaluation": r.evaluation,
                "created_at": r.created_at
            } for r in results]
        finally:
            session.close()
