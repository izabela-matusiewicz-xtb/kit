"""Fast PR Reviewer - focused file-level analysis without repository context."""

import asyncio
import re
from typing import Any, Dict, List

import requests

from .config import LLMProvider, ReviewConfig
from .cost_tracker import CostTracker
from .file_prioritizer import FilePrioritizer
from .validator import validate_review_quality


class SimplePRReviewer:
    """Fast PR reviewer that focuses on file-level analysis without repository context."""

    def __init__(self, config: ReviewConfig):
        self.config = config
        self.github_session = requests.Session()
        self.github_session.headers.update({
            "Authorization": f"token {config.github.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "kit-simple-reviewer/0.1.0"
        })
        self._llm_client = None
        self.cost_tracker = CostTracker(config.custom_pricing)

    def parse_pr_url(self, pr_input: str) -> tuple[str, str, int]:
        """Parse PR URL to extract owner, repo, and PR number."""
        url_pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.match(url_pattern, pr_input)

        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {pr_input}")

        owner, repo, pr_number = match.groups()
        return owner, repo, int(pr_number)

    def get_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get PR details from GitHub API."""
        url = f"{self.config.github.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = self.github_session.get(url)
        response.raise_for_status()
        return response.json()

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[Dict[str, Any]]:
        """Get list of files changed in the PR."""
        url = f"{self.config.github.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = self.github_session.get(url)
        response.raise_for_status()
        return response.json()

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Get the full diff for the PR."""
        url = f"{self.config.github.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self.github_session.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"

        response = self.github_session.get(url, headers=headers)
        response.raise_for_status()

        return response.text

    async def analyze_pr_simple(self, pr_details: Dict[str, Any], files: List[Dict[str, Any]]) -> str:
        """Simple PR analysis with intelligent file prioritization."""

        # Basic PR info
        total_additions = sum(f['additions'] for f in files)
        total_deletions = sum(f['deletions'] for f in files)

        # GET THE ACTUAL DIFF WITH CORRECT LINE NUMBERS
        owner, repo = pr_details["head"]["repo"]["owner"]["login"], pr_details["head"]["repo"]["name"]
        pr_number = pr_details["number"]
        try:
            pr_diff = self.get_pr_diff(owner, repo, pr_number)
        except Exception as e:
            pr_diff = f"Error retrieving diff: {e}"

        # Prioritize files for analysis (basic prioritization for Simple reviewer)
        priority_files, skipped_count = FilePrioritizer.basic_priority(files, max_files=8)

        # Generate analysis summary for transparency
        analysis_summary = FilePrioritizer.get_analysis_summary(files, priority_files)

        # Simple analysis prompt - no symbols, dependencies, or advanced context
        pr_status = "WIP" if "WIP" in pr_details['title'].upper() or "WORK IN PROGRESS" in pr_details['title'].upper() else "Ready for Review"

        analysis_prompt = f"""You are an expert code reviewer. Analyze this GitHub PR based on the diff content.

**PR Information:**
- Title: {pr_details['title']}
- Author: {pr_details['user']['login']}
- Files: {len(files)} changed (+{total_additions} -{total_deletions})
- Status: {pr_status}

{analysis_summary}

**Diff:**
```diff
{pr_diff}
```

**Review Format:**

## Priority Issues
- [High/Medium/Low priority] findings with [file.py:123](https://github.com/{owner}/{repo}/blob/{pr_details["head"]["sha"]}/file.py#L123) links

## Summary
- What this PR does
- Key changes

## Recommendations
- Security, logic, or quality issues with specific fixes
- Missing error handling or edge cases
- Testing needs

**Guidelines:** Be specific, actionable, and professional. Reference actual diff content. Focus on issues worth fixing."""

        # Use LLM for analysis
        if self.config.llm.provider == LLMProvider.ANTHROPIC:
            return await self._analyze_with_anthropic_simple(analysis_prompt)
        else:
            return await self._analyze_with_openai_simple(analysis_prompt)

    async def _analyze_with_anthropic_simple(self, prompt: str) -> str:
        """Simple Anthropic analysis."""
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

        if not self._llm_client:
            self._llm_client = anthropic.Anthropic(api_key=self.config.llm.api_key)

        try:
            response = self._llm_client.messages.create(
                model=self.config.llm.model,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track cost
            input_tokens, output_tokens = self.cost_tracker.extract_anthropic_usage(response)
            self.cost_tracker.track_llm_usage(
                self.config.llm.provider,
                self.config.llm.model,
                input_tokens,
                output_tokens
            )

            return response.content[0].text

        except Exception as e:
            return f"Error during simple LLM analysis: {e}"

    async def _analyze_with_openai_simple(self, prompt: str) -> str:
        """Simple OpenAI analysis."""
        try:
            import openai
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        if not self._llm_client:
            self._llm_client = openai.OpenAI(api_key=self.config.llm.api_key)

        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.llm.model,
                max_tokens=self.config.llm.max_tokens,
                temperature=self.config.llm.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track cost
            input_tokens, output_tokens = self.cost_tracker.extract_openai_usage(response)
            self.cost_tracker.track_llm_usage(
                self.config.llm.provider,
                self.config.llm.model,
                input_tokens,
                output_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error during simple LLM analysis: {e}"

    def review_pr_simple(self, pr_input: str) -> str:
        """Simple PR review without kit features."""
        try:
            # Parse PR input
            owner, repo, pr_number = self.parse_pr_url(pr_input)
            print(f"⚡ Reviewing PR #{pr_number} in {owner}/{repo} [SIMPLE MODE]")

            # Get PR details
            pr_details = self.get_pr_details(owner, repo, pr_number)
            print(f"PR Title: {pr_details['title']}")
            print(f"PR Author: {pr_details['user']['login']}")

            # Get changed files
            files = self.get_pr_files(owner, repo, pr_number)
            print(f"Changed files: {len(files)}")

            # Simple analysis
            analysis = asyncio.run(self.analyze_pr_simple(pr_details, files))

            # Validate review quality
            try:
                pr_diff = self.get_pr_diff(owner, repo, pr_number)
                changed_files = [f['filename'] for f in files]
                validation = validate_review_quality(analysis, pr_diff, changed_files)

                print(f"📊 Review Quality Score: {validation.score:.2f}/1.0")
                if validation.issues:
                    print(f"⚠️  Quality Issues: {', '.join(validation.issues)}")
                print(f"📈 Metrics: {validation.metrics}")

                # If quality is poor, warn the user
                if validation.score < 0.6:
                    print("⚠️  LOW QUALITY REVIEW DETECTED - Consider using standard mode for better results")

            except Exception as e:
                print(f"⚠️  Could not validate review quality: {e}")

            review_comment = self._generate_review_comment(pr_details, files, analysis)

            # Display cost summary
            print(self.cost_tracker.get_cost_summary())

            return review_comment

        except requests.RequestException as e:
            raise RuntimeError(f"GitHub API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Simple review failed: {e}")

    def _generate_review_comment(self, pr_details: Dict[str, Any], files: list[Dict[str, Any]], analysis: str) -> str:
        """Generate a GitHub comment for the review."""
        comment = f"""## 🛠️ Kit Code Review

{analysis}

---
*Generated by [cased kit](https://github.com/cased/kit) v{self._get_kit_version()} using {self.config.llm.provider.value}*
"""
        return comment

    def _get_kit_version(self) -> str:
        """Get kit version for review attribution."""
        try:
            import kit
            return getattr(kit, '__version__', 'dev')
        except Exception:
            return 'dev'
