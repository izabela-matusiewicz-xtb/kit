#!/usr/bin/env python3
"""Compare the full kit PR reviewer with the simple reviewer."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import click

from kit.pr_review.agentic_reviewer import AgenticPRReviewer
from kit.pr_review.config import LLMProvider, ReviewConfig
from kit.pr_review.cost_tracker import CostTracker
from kit.pr_review.reviewer import PRReviewer
from kit.pr_review.simple_reviewer import SimplePRReviewer


class ReviewJudge:
    """LLM-based judge to evaluate and compare review quality."""

    def __init__(self, config: ReviewConfig):
        self.config = config
        self._llm_client = None
        self.cost_tracker = CostTracker(config.custom_pricing)

    def judge_reviews(self, pr_url: str, pr_title: str, simple_review: str, full_review: str) -> str:
        """Use LLM to judge and compare the two reviews."""
        judge_prompt = f"""You are an expert code review evaluator. Compare these two PR reviews for the same pull request and provide a detailed assessment.

**Pull Request**: {pr_url}
**Title**: {pr_title}

**REVIEW 1 (Simple Reviewer - No Repository Context)**:
{simple_review}

**REVIEW 2 (Full Kit Reviewer - With Repository Context)**:
{full_review}

Please evaluate both reviews and provide:

1. **Overall Quality Score** (1-10) for each review
2. **Strengths** of each review
3. **Weaknesses** of each review
4. **Unique Insights** that each review provided
5. **Missing Elements** that a good review should have included
6. **Recommendation**: Which review is more helpful and why
7. **Improvement Suggestions** for each reviewer

Be specific and objective in your assessment. Consider factors like:
- Accuracy and relevance of the feedback
- Depth of analysis
- Actionability of suggestions
- Understanding of the code changes
- Identification of potential issues
- Overall helpfulness to the PR author

Format your response clearly with headers for each section."""

        if self.config.llm.provider == LLMProvider.ANTHROPIC:
            return self._judge_with_anthropic(judge_prompt)
        else:
            return self._judge_with_openai(judge_prompt)

    def judge_three_reviews(self, pr_url: str, pr_title: str, simple_review: str, full_review: str, agentic_review: str) -> str:
        """Use LLM to judge and compare three reviews."""
        judge_prompt = f"""You are an expert code review evaluator. Compare these three PR reviews for the same pull request and provide a detailed assessment.

**Pull Request**: {pr_url}
**Title**: {pr_title}

**REVIEW 1 (Simple Reviewer - File Contents Only)**:
{simple_review}

**REVIEW 2 (Full Kit Reviewer - Repository Context)**:
{full_review}

**REVIEW 3 (Agentic Reviewer - Multi-turn Tool-based Analysis)**:
{agentic_review}

Please evaluate all three reviews and provide:

1. **Overall Quality Score** (1-10) for each review
2. **Strengths** of each review approach
3. **Weaknesses** of each review approach
4. **Unique Insights** that each review provided
5. **Cost vs Value Analysis** - which approaches provide the best value for their cost
6. **Recommendation**: Rank the reviews by overall helpfulness and explain why
7. **Improvement Suggestions** for each reviewer approach

Consider factors like:
- Accuracy and relevance of the feedback
- Depth and breadth of analysis
- Actionability of suggestions
- Understanding of the code changes and their implications
- Identification of potential issues
- Overall helpfulness to the PR author
- Cost efficiency (simple < full kit < agentic in terms of cost)

Format your response clearly with headers for each section. Pay special attention to whether the more expensive agentic approach provides proportionally better value.
"""

        if self.config.llm.provider == LLMProvider.ANTHROPIC:
            return self._judge_with_anthropic(judge_prompt)
        else:
            return self._judge_with_openai(judge_prompt)

    def _judge_with_anthropic(self, prompt: str) -> str:
        """Judge using Anthropic Claude."""
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

        if not self._llm_client:
            self._llm_client = anthropic.Anthropic(api_key=self.config.llm.api_key)

        response = self._llm_client.messages.create(
            model=self.config.llm.model,
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent judging
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

    def _judge_with_openai(self, prompt: str) -> str:
        """Judge using OpenAI GPT."""
        try:
            import openai
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        if not self._llm_client:
            self._llm_client = openai.OpenAI(api_key=self.config.llm.api_key)

        response = self._llm_client.chat.completions.create(
            model=self.config.llm.model,
            max_tokens=2000,
            temperature=0.3,
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


def extract_review_content(full_comment: str) -> str:
    """Extract just the review content without the header/footer."""
    lines = full_comment.split('\n')
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if line.strip().startswith('## 🛠️ Kit'):
            start_idx = i + 1
        elif line.strip().startswith('---'):
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        return '\n'.join(lines[start_idx:end_idx]).strip()
    return full_comment


def save_comparison_results(pr_url: str, results: Dict, output_dir: str = "review_comparisons"):
    """Save comparison results to a file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create filename from PR URL
    pr_parts = pr_url.replace("https://github.com/", "").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pr_parts}_{timestamp}.json"

    filepath = output_path / filename
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)

    return filepath


@click.command()
@click.argument('pr_url')
@click.option('--judge/--no-judge', default=True, help='Run LLM judge to evaluate reviews')
@click.option('--save/--no-save', default=True, help='Save comparison results to file')
@click.option('--output-dir', default='review_comparisons', help='Directory to save results')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
@click.option('--include-agentic/--no-agentic', default=False, help='Include agentic reviewer (more expensive)')
@click.option('--agentic-turns', type=int, default=20, help='Maximum turns for agentic reviewer')
@click.option('--agentic-finalize-at', type=int, default=15, help='Turn to start encouraging finalization')
def main(pr_url: str, judge: bool, save: bool, output_dir: str, config: Optional[str], include_agentic: bool, agentic_turns: int, agentic_finalize_at: int):
    """Compare full kit PR reviewer with simple reviewer."""

    # Load config from environment
    review_config = ReviewConfig.from_file(config)
    review_config.post_as_comment = False  # Dry run

    click.echo("=" * 80)
    click.echo(click.style("PR REVIEW COMPARISON TOOL", fg='green', bold=True))
    click.echo("=" * 80)
    click.echo(f"Analyzing PR: {pr_url}")
    click.echo()

    # Track total costs
    # Note: Individual reviewers track their own costs

    # Run simple reviewer
    click.echo(click.style("1. Running Simple Reviewer (no kit features)...", fg='yellow'))
    simple_reviewer = SimplePRReviewer(review_config)
    simple_comment = simple_reviewer.review_pr_simple(pr_url)
    simple_cost = simple_reviewer.cost_tracker.breakdown.llm_cost_usd

    # Extract PR details for later use
    owner, repo, pr_number = simple_reviewer.parse_pr_url(pr_url)
    pr_details = simple_reviewer.get_pr_details(owner, repo, pr_number)
    pr_title = pr_details['title']

    click.echo(click.style("✓ Simple review complete", fg='green'))
    click.echo()

    # Run full reviewer
    click.echo(click.style("2. Running Full Kit Reviewer (with repository context)...", fg='yellow'))
    full_reviewer = PRReviewer(review_config)
    full_comment = full_reviewer.review_pr(pr_url)
    full_cost = full_reviewer.cost_tracker.breakdown.llm_cost_usd

    click.echo(click.style("✓ Full review complete", fg='green'))
    click.echo()

    # Run agentic reviewer if requested
    agentic_comment = None
    agentic_cost = 0
    if include_agentic:
        click.echo(click.style("3. Running Agentic Reviewer (multi-turn analysis)...", fg='yellow'))

        # Configure agentic settings
        agentic_config = review_config
        agentic_config.agentic_max_turns = agentic_turns
        agentic_config.agentic_finalize_threshold = agentic_finalize_at

        click.echo(f"   Max turns: {agentic_turns}, Finalize threshold: {agentic_finalize_at}")

        agentic_reviewer = AgenticPRReviewer(agentic_config)
        agentic_comment = agentic_reviewer.review_pr_agentic(pr_url)
        agentic_cost = agentic_reviewer.cost_tracker.breakdown.llm_cost_usd

        click.echo(click.style("✓ Agentic review complete", fg='green'))
        click.echo()

    # Display reviews side by side
    click.echo("=" * 80)
    click.echo(click.style("REVIEW COMPARISON", fg='green', bold=True))
    click.echo("=" * 80)

    # Extract content without headers/footers for cleaner comparison
    simple_content = extract_review_content(simple_comment)
    full_content = extract_review_content(full_comment)

    click.echo(click.style("\n--- SIMPLE REVIEW ---", fg='cyan', bold=True))
    click.echo(simple_content)

    click.echo(click.style("\n--- FULL KIT REVIEW ---", fg='cyan', bold=True))
    click.echo(full_content)

    if include_agentic and agentic_comment:
        agentic_content = extract_review_content(agentic_comment)
        click.echo(click.style("\n--- AGENTIC REVIEW ---", fg='magenta', bold=True))
        click.echo(agentic_content)

    # Statistics
    click.echo("\n" + "=" * 80)
    click.echo(click.style("STATISTICS", fg='green', bold=True))
    click.echo("=" * 80)

    stats = {
        "Simple Review": {
            "Length": f"{len(simple_comment)} characters",
            "Cost": f"${simple_cost:.4f}",
            "Tokens": simple_reviewer.cost_tracker.get_cost_summary().split("(")[1].split(")")[0] if "(" in simple_reviewer.cost_tracker.get_cost_summary() else "N/A"
        },
        "Full Kit Review": {
            "Length": f"{len(full_comment)} characters",
            "Cost": f"${full_cost:.4f}",
            "Tokens": full_reviewer.cost_tracker.get_cost_summary().split("(")[1].split(")")[0] if "(" in full_reviewer.cost_tracker.get_cost_summary() else "N/A"
        }
    }

    if include_agentic and agentic_comment:
        stats["Agentic Review"] = {
            "Length": f"{len(agentic_comment)} characters",
            "Cost": f"${agentic_cost:.4f}",
            "Tokens": agentic_reviewer.cost_tracker.get_cost_summary().split("(")[1].split(")")[0] if "(" in agentic_reviewer.cost_tracker.get_cost_summary() else "N/A"
        }

    stats["Comparison"] = {
        "Length Ratio (Full/Simple)": f"{len(full_comment) / len(simple_comment):.2f}x" if len(simple_comment) > 0 else "N/A",
        "Cost Ratio (Full/Simple)": f"{full_cost / simple_cost:.2f}x" if simple_cost > 0 else "N/A",
        "Cost Savings (Simple-Full)": f"${simple_cost - full_cost:.4f}" if simple_cost > 0 and full_cost > 0 and full_cost < simple_cost else f"-${full_cost - simple_cost:.4f}" if simple_cost > 0 and full_cost > 0 else "N/A"
    }

    if include_agentic and agentic_comment:
        if full_cost > 0:
            stats["Comparison"]["Agentic vs Full Cost Ratio"] = f"{agentic_cost / full_cost:.2f}x"
        else:
            stats["Comparison"]["Agentic vs Full Cost Ratio"] = "N/A"

        if simple_cost > 0:
            stats["Comparison"]["Agentic vs Simple Cost Ratio"] = f"{agentic_cost / simple_cost:.2f}x"
        else:
            stats["Comparison"]["Agentic vs Simple Cost Ratio"] = "N/A"

    for category, metrics in stats.items():
        click.echo(f"\n{category}:")
        for metric, value in metrics.items():
            click.echo(f"  {metric}: {value}")

    # Judge reviews if requested
    judge_assessment = None
    judge_cost = 0
    if judge:
        click.echo("\n" + "=" * 80)
        click.echo(click.style("LLM JUDGE ASSESSMENT", fg='green', bold=True))
        click.echo("=" * 80)
        click.echo(click.style("Running LLM judge to evaluate review quality...", fg='yellow'))

        judge_instance = ReviewJudge(review_config)
        if include_agentic and agentic_comment:
            # Judge all three reviewers
            agentic_content = extract_review_content(agentic_comment)
            judge_assessment = judge_instance.judge_three_reviews(pr_url, pr_title, simple_content, full_content, agentic_content)
        else:
            # Judge just simple and full
            judge_assessment = judge_instance.judge_reviews(pr_url, pr_title, simple_content, full_content)
        judge_cost = judge_instance.cost_tracker.breakdown.llm_cost_usd

        click.echo(click.style("✓ Judge assessment complete", fg='green'))
        click.echo()
        click.echo(judge_assessment)

        click.echo(f"\nJudge Cost: ${judge_cost:.4f}")
        total_cost = simple_cost + full_cost + (agentic_cost if include_agentic else 0) + judge_cost
        click.echo(f"Total Comparison Cost: ${total_cost:.4f}")
    else:
        # Handle case where judge wasn't run or failed
        total_cost = simple_cost + full_cost + (agentic_cost if include_agentic else 0)
        if total_cost > 0:
            click.echo(f"Total Comparison Cost: ${total_cost:.4f}")
        else:
            click.echo("Total Comparison Cost: N/A (API failures)")

    # Check for API failures and provide helpful message
    if simple_cost == 0 and full_cost == 0 and (not include_agentic or agentic_cost == 0):
        click.echo("\n⚠️  All reviewers failed due to API issues (likely overloaded).")
        click.echo("💡 Try again in a few minutes or check your API keys and rate limits.")

    # Save results if requested
    if save:
        results = {
            "pr_url": pr_url,
            "pr_title": pr_title,
            "timestamp": datetime.now().isoformat(),
            "reviews": {
                "simple": {
                    "content": simple_comment,
                    "cost": simple_cost,
                    "stats": stats["Simple Review"]
                },
                "full": {
                    "content": full_comment,
                    "cost": full_cost,
                    "stats": stats["Full Kit Review"]
                }
            },
            "comparison": stats["Comparison"],
            "judge_assessment": judge_assessment if judge else None,
            "total_cost": simple_cost + full_cost + (agentic_cost if include_agentic else 0) + (judge_cost if judge else 0)
        }

        if include_agentic and agentic_comment:
            results["reviews"]["agentic"] = {
                "content": agentic_comment,
                "cost": agentic_cost,
                "stats": stats["Agentic Review"]
            }

        filepath = save_comparison_results(pr_url, results, output_dir)
        click.echo(f"\n✓ Results saved to: {filepath}")

    click.echo("\n" + "=" * 80)
    click.echo(click.style("COMPARISON COMPLETE", fg='green', bold=True))
    click.echo("=" * 80)


if __name__ == "__main__":
    main()
