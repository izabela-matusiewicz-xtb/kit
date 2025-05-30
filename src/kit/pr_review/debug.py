#!/usr/bin/env python3
"""Debug CLI for PR review testing and comparison."""

import time
from typing import Optional

import typer

app = typer.Typer(help="Debug tools for PR review testing and comparison.")


@app.command("compare")
def compare_reviews(
    pr_url: str,
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    dry_run: bool = typer.Option(True, "--dry-run/--post", help="Run analysis but do not post comments"),
):
    """Compare enhanced vs simple PR review analysis on the same PR."""
    try:
        from .config import ReviewConfig
        from .reviewer import PRReviewer
        from .simple_reviewer import SimplePRReviewer

        # Load configuration
        if config:
            review_config = ReviewConfig.from_file(config)
        else:
            review_config = ReviewConfig.from_file()

        # Override post_as_comment for comparison
        if dry_run:
            review_config.post_as_comment = False

        typer.echo(f"🔍 Comparing PR reviews for: {pr_url}")
        typer.echo("=" * 60)

        # Run enhanced review
        typer.echo("\n🛠️ Running ENHANCED review (with kit features)...")
        start_time = time.time()

        enhanced_reviewer = PRReviewer(review_config)
        enhanced_result = enhanced_reviewer.review_pr(pr_url)
        enhanced_time = time.time() - start_time

        typer.echo(f"Enhanced review completed in {enhanced_time:.1f} seconds")

        # Run simple review
        typer.echo("\n⚡ Running SIMPLE review (no kit features)...")
        start_time = time.time()

        simple_reviewer = SimplePRReviewer(review_config)
        simple_result = simple_reviewer.review_pr_simple(pr_url)
        simple_time = time.time() - start_time

        typer.echo(f"Simple review completed in {simple_time:.1f} seconds")

        # Output comparison
        typer.echo("\n" + "=" * 60)
        typer.echo("📊 COMPARISON RESULTS")
        typer.echo("=" * 60)

        typer.echo("\n⏱️  PERFORMANCE:")
        typer.echo(f"Enhanced: {enhanced_time:.1f}s")
        typer.echo(f"Simple:   {simple_time:.1f}s")
        performance_diff = enhanced_time / simple_time if simple_time > 0 else 1
        typer.echo(f"Ratio:    {performance_diff:.1f}x {'slower' if performance_diff > 1 else 'faster'}")

        typer.echo("\n📏 LENGTH:")
        typer.echo(f"Enhanced: {len(enhanced_result):,} characters")
        typer.echo(f"Simple:   {len(simple_result):,} characters")
        length_diff = len(enhanced_result) / len(simple_result) if len(simple_result) > 0 else 1
        typer.echo(f"Ratio:    {length_diff:.1f}x {'longer' if length_diff > 1 else 'shorter'}")

        typer.echo("\n🛠️ ENHANCED REVIEW OUTPUT:")
        typer.echo("-" * 40)
        typer.echo(enhanced_result)

        typer.echo("\n⚡ SIMPLE REVIEW OUTPUT:")
        typer.echo("-" * 40)
        typer.echo(simple_result)

        typer.echo("\n" + "=" * 60)
        typer.echo("✅ Comparison complete!")

        # Summary
        typer.echo("\n📈 SUMMARY:")
        typer.echo(f"Enhanced review was {performance_diff:.1f}x the time but {length_diff:.1f}x the detail")

    except Exception as e:
        typer.echo(f"❌ Comparison failed: {e}", err=True)
        return


@app.command("simple")
def review_pr_simple(
    pr_url: str,
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    dry_run: bool = typer.Option(True, "--dry-run/--post", help="Run analysis but do not post comment"),
):
    """Review a GitHub PR using simple analysis (no kit features) for comparison."""
    try:
        from .config import ReviewConfig
        from .simple_reviewer import SimplePRReviewer

        # Load configuration
        if config:
            review_config = ReviewConfig.from_file(config)
        else:
            review_config = ReviewConfig.from_file()

        # Override post_as_comment if dry run
        if dry_run:
            review_config.post_as_comment = False

        # Run simple review
        reviewer = SimplePRReviewer(review_config)
        result = reviewer.review_pr_simple(pr_url)

        if dry_run:
            typer.echo("\n" + "="*50)
            typer.echo("SIMPLE REVIEW RESULT (DRY RUN)")
            typer.echo("="*50)
            typer.echo(result)
        else:
            typer.echo("✅ Simple review completed and posted!")

    except Exception as e:
        typer.echo(f"❌ Simple review failed: {e}", err=True)
        return


@app.command("enhanced")
def review_pr_enhanced(
    pr_url: str,
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    dry_run: bool = typer.Option(True, "--dry-run/--post", help="Run analysis but do not post comment"),
):
    """Review a GitHub PR using enhanced analysis (with all kit features) for testing."""
    try:
        from .config import ReviewConfig
        from .reviewer import PRReviewer

        # Load configuration
        if config:
            review_config = ReviewConfig.from_file(config)
        else:
            review_config = ReviewConfig.from_file()

        # Override post_as_comment if dry run
        if dry_run:
            review_config.post_as_comment = False

        # Run enhanced review
        reviewer = PRReviewer(review_config)
        result = reviewer.review_pr(pr_url)

        if dry_run:
            typer.echo("\n" + "="*50)
            typer.echo("ENHANCED REVIEW RESULT (DRY RUN)")
            typer.echo("="*50)
            typer.echo(result)
        else:
            typer.echo("✅ Enhanced review completed and posted!")

    except Exception as e:
        typer.echo(f"❌ Enhanced review failed: {e}", err=True)
        return


@app.command("benchmark")
def benchmark_reviews(
    pr_url: str,
    runs: int = typer.Option(3, "--runs", "-r", help="Number of runs for benchmarking"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Benchmark enhanced vs simple PR review performance."""
    try:
        from .config import ReviewConfig
        from .reviewer import PRReviewer
        from .simple_reviewer import SimplePRReviewer

        # Load configuration (dry run for benchmarking)
        if config:
            review_config = ReviewConfig.from_file(config)
        else:
            review_config = ReviewConfig.from_file()

        review_config.post_as_comment = False  # Always dry run for benchmarking

        typer.echo(f"🏃 Benchmarking PR review performance ({runs} runs each)")
        typer.echo(f"PR: {pr_url}")
        typer.echo("=" * 60)

        # Benchmark enhanced reviewer
        enhanced_times = []
        enhanced_lengths = []

        typer.echo("\n🛠️ Benchmarking ENHANCED reviewer...")
        for i in range(runs):
            typer.echo(f"  Run {i+1}/{runs}...", nl=False)
            start_time = time.time()

            enhanced_reviewer = PRReviewer(review_config)
            result = enhanced_reviewer.review_pr(pr_url)

            duration = time.time() - start_time
            enhanced_times.append(duration)
            enhanced_lengths.append(len(result))
            typer.echo(f" {duration:.1f}s")

        # Benchmark simple reviewer
        simple_times = []
        simple_lengths = []

        typer.echo("\n⚡ Benchmarking SIMPLE reviewer...")
        for i in range(runs):
            typer.echo(f"  Run {i+1}/{runs}...", nl=False)
            start_time = time.time()

            simple_reviewer = SimplePRReviewer(review_config)
            result = simple_reviewer.review_pr_simple(pr_url)

            duration = time.time() - start_time
            simple_times.append(duration)
            simple_lengths.append(len(result))
            typer.echo(f" {duration:.1f}s")

        # Results
        typer.echo("\n" + "=" * 60)
        typer.echo("📊 BENCHMARK RESULTS")
        typer.echo("=" * 60)

        enhanced_avg = sum(enhanced_times) / len(enhanced_times)
        simple_avg = sum(simple_times) / len(simple_times)

        enhanced_len_avg = sum(enhanced_lengths) / len(enhanced_lengths)
        simple_len_avg = sum(simple_lengths) / len(simple_lengths)

        typer.echo("\n⏱️  PERFORMANCE:")
        typer.echo(f"Enhanced: {enhanced_avg:.1f}s avg (min: {min(enhanced_times):.1f}s, max: {max(enhanced_times):.1f}s)")
        typer.echo(f"Simple:   {simple_avg:.1f}s avg (min: {min(simple_times):.1f}s, max: {max(simple_times):.1f}s)")
        typer.echo(f"Ratio:    {enhanced_avg/simple_avg:.1f}x slower")

        typer.echo("\n📏 OUTPUT LENGTH:")
        typer.echo(f"Enhanced: {enhanced_len_avg:,.0f} chars avg")
        typer.echo(f"Simple:   {simple_len_avg:,.0f} chars avg")
        typer.echo(f"Ratio:    {enhanced_len_avg/simple_len_avg:.1f}x longer")

        typer.echo("\n✅ Benchmark complete!")

    except Exception as e:
        typer.echo(f"❌ Benchmark failed: {e}", err=True)
        return


if __name__ == "__main__":
    app()
