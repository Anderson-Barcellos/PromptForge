"""
Multi-dimensional prompt quality analyzer
"""
import re
from typing import Dict, List, Optional, Any
from src.api.anthropic_client import AnthropicClient
from src.db.database import Database


class PromptAnalyzer:
    """Analyzer for prompt quality across multiple dimensions"""

    def __init__(self, client: AnthropicClient, db: Database):
        """
        Initialize analyzer

        Args:
            client: Anthropic API client
            db: Database instance
        """
        self.client = client
        self.db = db

    def _extract_score(self, analysis_text: str, score_pattern: str = r"SCORE:\s*(\d+)") -> Optional[int]:
        """
        Extract numeric score from analysis text

        Args:
            analysis_text: Text containing score
            score_pattern: Regex pattern to extract score

        Returns:
            Extracted score or None
        """
        match = re.search(score_pattern, analysis_text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def analyze_clarity(self, prompt: str, version_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze prompt for clarity and ambiguity

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analysis to (optional)

        Returns:
            Analysis result dictionary
        """
        analysis = self.client.analyze_prompt(prompt, analysis_type="clarity")
        score = self._extract_score(analysis, r"CLARITY SCORE:\s*(\d+)")

        result = {
            "type": "clarity",
            "score": score,
            "content": analysis
        }

        if version_id:
            self.db.save_analysis(
                version_id=version_id,
                analysis_type="clarity",
                content=analysis,
                score=score
            )

        return result

    def analyze_completeness(self, prompt: str, version_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze prompt for completeness and robustness

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analysis to (optional)

        Returns:
            Analysis result dictionary
        """
        analysis = self.client.analyze_prompt(prompt, analysis_type="completeness")
        score = self._extract_score(analysis, r"COMPLETENESS SCORE:\s*(\d+)")

        result = {
            "type": "completeness",
            "score": score,
            "content": analysis
        }

        if version_id:
            self.db.save_analysis(
                version_id=version_id,
                analysis_type="completeness",
                content=analysis,
                score=score
            )

        return result

    def analyze_efficiency(self, prompt: str, version_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze prompt for efficiency and token usage

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analysis to (optional)

        Returns:
            Analysis result dictionary
        """
        analysis = self.client.analyze_prompt(prompt, analysis_type="efficiency")
        score = self._extract_score(analysis, r"EFFICIENCY SCORE:\s*(\d+)")

        result = {
            "type": "efficiency",
            "score": score,
            "content": analysis
        }

        if version_id:
            self.db.save_analysis(
                version_id=version_id,
                analysis_type="efficiency",
                content=analysis,
                score=score
            )

        return result

    def analyze_safety(self, prompt: str, version_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze prompt for safety and ethical considerations

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analysis to (optional)

        Returns:
            Analysis result dictionary
        """
        analysis = self.client.analyze_prompt(prompt, analysis_type="safety")
        score = self._extract_score(analysis, r"SAFETY SCORE:\s*(\d+)")

        result = {
            "type": "safety",
            "score": score,
            "content": analysis
        }

        if version_id:
            self.db.save_analysis(
                version_id=version_id,
                analysis_type="safety",
                content=analysis,
                score=score
            )

        return result

    def analyze_comprehensive(self, prompt: str, version_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis across all dimensions

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analysis to (optional)

        Returns:
            Analysis result dictionary with overall score and recommendations
        """
        analysis = self.client.analyze_prompt(prompt, analysis_type="general")
        score = self._extract_score(analysis, r"OVERALL SCORE:\s*(\d+)")

        result = {
            "type": "general",
            "score": score,
            "content": analysis
        }

        if version_id:
            self.db.save_analysis(
                version_id=version_id,
                analysis_type="general",
                content=analysis,
                score=score
            )

        return result

    def analyze_all_dimensions(self, prompt: str, version_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Analyze prompt across all dimensions

        Args:
            prompt: Prompt to analyze
            version_id: Version ID to save analyses to (optional)

        Returns:
            List of analysis results
        """
        results = []

        # Run all analyses
        results.append(self.analyze_clarity(prompt, version_id))
        results.append(self.analyze_completeness(prompt, version_id))
        results.append(self.analyze_efficiency(prompt, version_id))
        results.append(self.analyze_safety(prompt, version_id))
        results.append(self.analyze_comprehensive(prompt, version_id))

        return results

    def get_quality_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate quality summary from multiple analyses

        Args:
            analyses: List of analysis results

        Returns:
            Summary dictionary with average score and dimension scores
        """
        dimension_scores = {}
        total_score = 0
        count = 0

        for analysis in analyses:
            if analysis["score"] is not None:
                dimension_scores[analysis["type"]] = analysis["score"]
                if analysis["type"] != "general":  # Don't double count general
                    total_score += analysis["score"]
                    count += 1

        average_score = total_score / count if count > 0 else None

        return {
            "average_score": average_score,
            "dimension_scores": dimension_scores,
            "total_analyses": len(analyses)
        }
