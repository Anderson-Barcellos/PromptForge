"""
Anthropic API client with retry logic and error handling
"""
import time
from typing import Optional, Dict, Any, List
from anthropic import Anthropic, APIError, RateLimitError
from src.config import config


class AnthropicClient:
    """Enhanced Anthropic API client with retry logic"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic client

        Args:
            api_key: Anthropic API key. If None, uses config value
        """
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY

    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function

        Returns:
            Function result

        Raises:
            APIError: If all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise
            except APIError as e:
                last_error = e
                if attempt < self.max_retries - 1 and e.status_code >= 500:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise

        raise last_error

    def create_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Create a message using Claude

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            model: Model to use (defaults to config)
            max_tokens: Maximum tokens (defaults to config)
            temperature: Temperature (defaults to config)

        Returns:
            Response text from Claude
        """
        model = model or config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE

        def _create():
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)
            return response.content[0].text

        return self._retry_with_backoff(_create)

    def analyze_prompt(
        self,
        prompt_to_analyze: str,
        analysis_type: str = "general"
    ) -> str:
        """
        Analyze a prompt using Claude with specialized meta-prompts

        Args:
            prompt_to_analyze: The prompt to analyze
            analysis_type: Type of analysis ('clarity', 'completeness', 'efficiency', 'safety', 'general')

        Returns:
            Analysis result
        """
        meta_prompts = {
            "clarity": """You are an expert in prompt engineering. Analyze the following system prompt for CLARITY and AMBIGUITY.

Evaluate:
1. Are instructions clear and unambiguous?
2. Could any part be misinterpreted?
3. Is the language precise and specific?
4. Are there any vague terms that need definition?

Provide:
- Clarity Score (0-100)
- Specific issues found
- Concrete suggestions for improvement

System prompt to analyze:
---
{prompt}
---

Respond in this format:
CLARITY SCORE: [0-100]

ISSUES FOUND:
[List specific ambiguities and unclear instructions]

SUGGESTIONS:
[Concrete recommendations to improve clarity]
""",
            "completeness": """You are an expert in prompt engineering. Analyze the following system prompt for COMPLETENESS and ROBUSTNESS.

Evaluate:
1. Are edge cases handled?
2. Are there gaps in logic or instructions?
3. Does it handle malformed or unexpected inputs?
4. Are all necessary constraints specified?

Provide:
- Completeness Score (0-100)
- Missing elements
- Edge cases not covered

System prompt to analyze:
---
{prompt}
---

Respond in this format:
COMPLETENESS SCORE: [0-100]

MISSING ELEMENTS:
[List gaps in coverage]

EDGE CASES NOT HANDLED:
[List specific edge cases]

SUGGESTIONS:
[Concrete recommendations to improve completeness]
""",
            "efficiency": """You are an expert in prompt engineering. Analyze the following system prompt for EFFICIENCY and TOKEN USAGE.

Evaluate:
1. Is there unnecessary verbosity?
2. Can instructions be more concise without losing meaning?
3. Are there redundant statements?
4. Is the structure optimal?

Provide:
- Efficiency Score (0-100)
- Redundancies found
- Optimization suggestions

System prompt to analyze:
---
{prompt}
---

Respond in this format:
EFFICIENCY SCORE: [0-100]

REDUNDANCIES:
[List verbose or redundant parts]

OPTIMIZATION OPPORTUNITIES:
[Specific ways to reduce tokens while maintaining effectiveness]
""",
            "safety": """You are an expert in AI safety and prompt engineering. Analyze the following system prompt for SAFETY and ETHICAL CONSIDERATIONS.

Evaluate:
1. Are there potential misuse vectors?
2. Does it include appropriate safety guardrails?
3. Are there concerning biases?
4. Does it handle harmful requests appropriately?

Provide:
- Safety Score (0-100)
- Potential risks
- Recommended safeguards

System prompt to analyze:
---
{prompt}
---

Respond in this format:
SAFETY SCORE: [0-100]

POTENTIAL RISKS:
[List safety concerns]

MISSING SAFEGUARDS:
[What safety measures should be added]

SUGGESTIONS:
[Concrete recommendations to improve safety]
""",
            "general": """You are an expert in prompt engineering. Provide a comprehensive analysis of the following system prompt.

Evaluate across multiple dimensions:
1. Clarity and precision
2. Completeness and robustness
3. Efficiency and token usage
4. Safety and ethics

Provide:
- Overall quality score (0-100)
- Strengths
- Weaknesses
- Prioritized recommendations

System prompt to analyze:
---
{prompt}
---

Respond in this format:
OVERALL SCORE: [0-100]

STRENGTHS:
[What works well]

WEAKNESSES:
[What needs improvement]

PRIORITY RECOMMENDATIONS:
1. [Most important improvement]
2. [Second priority]
3. [Third priority]
"""
        }

        meta_prompt = meta_prompts.get(analysis_type, meta_prompts["general"])
        analysis_prompt = meta_prompt.format(prompt=prompt_to_analyze)

        return self.create_message(
            prompt=analysis_prompt,
            model=config.ANALYSIS_MODEL
        )

    def generate_variants(
        self,
        original_prompt: str,
        optimization_focus: str = "balanced",
        num_variants: int = 3
    ) -> List[str]:
        """
        Generate optimized variants of a prompt

        Args:
            original_prompt: Original prompt to optimize
            optimization_focus: What to optimize for ('clarity', 'conciseness', 'robustness', 'balanced')
            num_variants: Number of variants to generate

        Returns:
            List of variant prompts
        """
        variant_prompt = f"""You are an expert in prompt engineering. Generate {num_variants} improved variants of the following system prompt.

Optimization focus: {optimization_focus}

Original prompt:
---
{original_prompt}
---

Generate {num_variants} variants, each optimizing for {optimization_focus} while maintaining the core intent.

Respond with each variant clearly separated:

VARIANT 1:
---
[First variant]
---

VARIANT 2:
---
[Second variant]
---

VARIANT 3:
---
[Third variant]
---
"""

        response = self.create_message(prompt=variant_prompt)

        # Parse variants from response
        variants = []
        lines = response.split('\n')
        current_variant = []
        in_variant = False

        for line in lines:
            if line.startswith('VARIANT'):
                if current_variant and in_variant:
                    variants.append('\n'.join(current_variant).strip())
                current_variant = []
                in_variant = False
            elif line.strip() == '---':
                if in_variant:
                    in_variant = False
                else:
                    in_variant = True
            elif in_variant:
                current_variant.append(line)

        if current_variant and in_variant:
            variants.append('\n'.join(current_variant).strip())

        return variants[:num_variants]

    def test_prompt(
        self,
        system_prompt: str,
        test_input: str,
        model: Optional[str] = None
    ) -> str:
        """
        Test a prompt with a specific input

        Args:
            system_prompt: The system prompt to test
            test_input: Test input to send
            model: Model to use (optional)

        Returns:
            Model response
        """
        return self.create_message(
            prompt=test_input,
            system_prompt=system_prompt,
            model=model
        )

    def compare_responses(
        self,
        responses: List[Dict[str, str]],
        evaluation_criteria: str
    ) -> str:
        """
        Use Claude as a judge to compare multiple responses

        Args:
            responses: List of dicts with 'name' and 'response' keys
            evaluation_criteria: Criteria for evaluation

        Returns:
            Comparison analysis
        """
        comparison_prompt = f"""You are an expert evaluator. Compare the following responses based on these criteria:

{evaluation_criteria}

"""
        for i, resp in enumerate(responses, 1):
            comparison_prompt += f"""
RESPONSE {i} ({resp['name']}):
---
{resp['response']}
---

"""

        comparison_prompt += """
Provide:
1. Ranking from best to worst
2. Specific strengths and weaknesses of each
3. Overall recommendation

Format:
RANKING:
1. [Name] - [Brief reason]
2. [Name] - [Brief reason]
...

DETAILED ANALYSIS:
[Response name]: [Strengths] | [Weaknesses]
...

RECOMMENDATION:
[Which response is best and why]
"""

        return self.create_message(prompt=comparison_prompt)
