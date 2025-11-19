"""
Prompt testing and comparison system
"""
import re
from typing import List, Dict, Any, Optional
from src.api.anthropic_client import AnthropicClient
from src.db.database import Database


class PromptTester:
    """System for testing and comparing prompts"""

    def __init__(self, client: AnthropicClient, db: Database):
        """
        Initialize tester

        Args:
            client: Anthropic API client
            db: Database instance
        """
        self.client = client
        self.db = db

    def run_test(
        self,
        version_id: int,
        test_case_id: int,
        system_prompt: str,
        save_result: bool = True
    ) -> Dict[str, Any]:
        """
        Run a single test case against a prompt version

        Args:
            version_id: Version ID being tested
            test_case_id: Test case ID
            system_prompt: System prompt to test
            save_result: Whether to save result to database

        Returns:
            Test result dictionary
        """
        # Get test case
        session = self.db.get_session()
        try:
            from src.db.database import TestCaseModel
            test_case = session.query(TestCaseModel).filter_by(id=test_case_id).first()

            if not test_case:
                raise ValueError(f"Test case {test_case_id} not found")

            # Run the test
            output = self.client.test_prompt(
                system_prompt=system_prompt,
                test_input=test_case.input_text
            )

            # Evaluate the output
            evaluation = self._evaluate_output(
                output=output,
                expected=test_case.expected_output,
                criteria=test_case.evaluation_criteria
            )

            score = self._extract_score_from_evaluation(evaluation)

            result = {
                "test_case_id": test_case_id,
                "test_name": test_case.name,
                "output": output,
                "score": score,
                "evaluation": evaluation
            }

            if save_result:
                self.db.save_test_result(
                    test_case_id=test_case_id,
                    version_id=version_id,
                    output=output,
                    score=score,
                    evaluation=evaluation
                )

            return result

        finally:
            session.close()

    def _evaluate_output(
        self,
        output: str,
        expected: Optional[str],
        criteria: str
    ) -> str:
        """
        Evaluate test output using Claude as judge

        Args:
            output: Model output to evaluate
            expected: Expected output (optional)
            criteria: Evaluation criteria

        Returns:
            Evaluation text
        """
        eval_prompt = f"""You are an expert evaluator. Evaluate the following output based on the criteria provided.

Evaluation Criteria:
{criteria}

"""
        if expected:
            eval_prompt += f"""Expected Output:
---
{expected}
---

"""

        eval_prompt += f"""Actual Output:
---
{output}
---

Provide:
1. Score from 0-100
2. What was done well
3. What could be improved
4. Whether it meets the criteria

Format:
SCORE: [0-100]

STRENGTHS:
[What was done well]

WEAKNESSES:
[What could be improved]

VERDICT:
[Does it meet the criteria? Yes/No and why]
"""

        return self.client.create_message(prompt=eval_prompt)

    def _extract_score_from_evaluation(self, evaluation: str) -> Optional[float]:
        """Extract numeric score from evaluation text"""
        match = re.search(r"SCORE:\s*(\d+)", evaluation)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def run_all_tests(
        self,
        prompt_id: int,
        version_id: int,
        system_prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Run all test cases for a prompt

        Args:
            prompt_id: Prompt ID
            version_id: Version ID being tested
            system_prompt: System prompt to test

        Returns:
            List of test results
        """
        test_cases = self.db.get_test_cases(prompt_id)
        results = []

        for test_case in test_cases:
            result = self.run_test(
                version_id=version_id,
                test_case_id=test_case["id"],
                system_prompt=system_prompt,
                save_result=True
            )
            results.append(result)

        return results

    def compare_versions(
        self,
        version_ids: List[int],
        test_case_id: int
    ) -> Dict[str, Any]:
        """
        Compare multiple prompt versions on a single test case

        Args:
            version_ids: List of version IDs to compare
            test_case_id: Test case to run

        Returns:
            Comparison result
        """
        responses = []

        for version_id in version_ids:
            version = self.db.get_version(version_id)
            if not version:
                continue

            # Get test case
            session = self.db.get_session()
            try:
                from src.db.database import TestCaseModel
                test_case = session.query(TestCaseModel).filter_by(id=test_case_id).first()

                if not test_case:
                    continue

                # Run test
                output = self.client.test_prompt(
                    system_prompt=version["content"],
                    test_input=test_case.input_text
                )

                responses.append({
                    "name": f"Version {version['version']}",
                    "response": output,
                    "version_id": version_id
                })

            finally:
                session.close()

        if not responses:
            return {"error": "No valid versions to compare"}

        # Get evaluation criteria
        session = self.db.get_session()
        try:
            from src.db.database import TestCaseModel
            test_case = session.query(TestCaseModel).filter_by(id=test_case_id).first()
            criteria = test_case.evaluation_criteria if test_case else "Quality and correctness"
        finally:
            session.close()

        # Compare using Claude
        comparison = self.client.compare_responses(
            responses=responses,
            evaluation_criteria=criteria
        )

        return {
            "test_case_id": test_case_id,
            "responses": responses,
            "comparison": comparison
        }

    def get_test_summary(self, version_id: int) -> Dict[str, Any]:
        """
        Get summary of test results for a version

        Args:
            version_id: Version ID

        Returns:
            Summary dictionary
        """
        results = self.db.get_test_results(version_id)

        if not results:
            return {
                "total_tests": 0,
                "average_score": None,
                "passed": 0,
                "failed": 0
            }

        scores = [r["score"] for r in results if r["score"] is not None]
        average_score = sum(scores) / len(scores) if scores else None

        # Consider >= 70 as passing
        passed = sum(1 for s in scores if s >= 70)
        failed = len(scores) - passed

        return {
            "total_tests": len(results),
            "average_score": average_score,
            "passed": passed,
            "failed": failed,
            "results": results
        }

    def generate_test_report(self, prompt_id: int, version_id: int) -> str:
        """
        Generate a comprehensive test report

        Args:
            prompt_id: Prompt ID
            version_id: Version ID

        Returns:
            Formatted report string
        """
        summary = self.get_test_summary(version_id)
        version = self.db.get_version(version_id)

        report = f"""# Test Report

## Version Information
- Version: {version['version'] if version else 'Unknown'}
- Tested at: {summary['results'][0]['created_at'] if summary['results'] else 'N/A'}

## Summary
- Total Tests: {summary['total_tests']}
- Average Score: {summary['average_score']:.2f if summary['average_score'] else 'N/A'}
- Passed: {summary['passed']}
- Failed: {summary['failed']}

## Individual Test Results

"""
        for i, result in enumerate(summary.get('results', []), 1):
            report += f"""### Test {i}
- Score: {result['score'] if result['score'] else 'N/A'}
- Output Preview: {result['output'][:100]}...

"""

        return report
