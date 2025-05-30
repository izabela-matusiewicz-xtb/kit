#!/usr/bin/env python3
"""Cross-model comparison test for PR reviews."""

import os

from src.kit.pr_review.config import GitHubConfig, LLMConfig, LLMProvider, ReviewConfig
from src.kit.pr_review.simple_reviewer import SimplePRReviewer
from src.kit.pr_review.validator import validate_review_quality


def create_config(provider: LLMProvider, model: str) -> ReviewConfig:
    """Create a config for the given provider and model."""
    github_config = GitHubConfig(
        token=os.getenv("KIT_GITHUB_TOKEN", "dummy_token")
    )

    if provider == LLMProvider.ANTHROPIC:
        api_key = os.getenv("KIT_ANTHROPIC_TOKEN", "dummy_key")
    else:
        api_key = os.getenv("KIT_OPENAI_TOKEN", "dummy_key")

    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key
    )

    return ReviewConfig(
        github=github_config,
        llm=llm_config,
        post_as_comment=False  # Don't actually post
    )

def compare_models_on_pr(pr_url: str):
    """Compare different models on the same PR."""
    print("🔬 Cross-Model Comparison Test")
    print(f"PR: {pr_url}")
    print("=" * 60)

    # Define models to test
    models = [
        (LLMProvider.ANTHROPIC, "claude-3-5-sonnet-20241022"),
        (LLMProvider.ANTHROPIC, "claude-3-5-haiku-20241022"),
        (LLMProvider.OPENAI, "gpt-4o"),
        (LLMProvider.OPENAI, "gpt-4o-mini"),
    ]

    results = []

    for provider, model in models:
        print(f"\n🤖 Testing: {provider.value} - {model}")
        print("-" * 40)

        try:
            config = create_config(provider, model)
            reviewer = SimplePRReviewer(config)

            # Check if we have API keys
            if config.llm.api_key == "dummy_key":
                print(f"⚠️  Skipping {provider.value} - no API key")
                results.append({
                    'provider': provider.value,
                    'model': model,
                    'skipped': True,
                    'reason': 'No API key'
                })
                continue

            # Run review
            import time
            start_time = time.time()

            review = reviewer.review_pr_simple(pr_url)

            end_time = time.time()
            duration = end_time - start_time

            # Get validation metrics
            try:
                owner, repo, pr_number = reviewer.parse_pr_url(pr_url)
                files = reviewer.get_pr_files(owner, repo, pr_number)
                pr_diff = reviewer.get_pr_diff(owner, repo, pr_number)
                changed_files = [f['filename'] for f in files]
                validation = validate_review_quality(review, pr_diff, changed_files)

                result = {
                    'provider': provider.value,
                    'model': model,
                    'skipped': False,
                    'cost': reviewer.cost_tracker.breakdown.llm_cost_usd,
                    'quality_score': validation.score,
                    'issues': validation.issues,
                    'metrics': validation.metrics,
                    'review_length': len(review),
                    'duration': duration,
                    'review': review
                }

                print(f"✅ Quality Score: {validation.score:.2f}/1.0")
                print(f"💰 Cost: ${result['cost']:.3f}")
                print(f"📏 Length: {result['review_length']:,} chars")
                if validation.issues:
                    print(f"⚠️  Issues: {len(validation.issues)} found")

            except Exception as e:
                result = {
                    'provider': provider.value,
                    'model': model,
                    'skipped': False,
                    'error': str(e),
                    'cost': reviewer.cost_tracker.breakdown.llm_cost_usd,
                }
                print(f"❌ Validation failed: {e}")

            results.append(result)

        except Exception as e:
            print(f"❌ Review failed: {e}")
            results.append({
                'provider': provider.value,
                'model': model,
                'skipped': True,
                'reason': str(e)
            })

    # Summary comparison
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 60)

    successful_results = [r for r in results if not r.get('skipped') and 'quality_score' in r]

    if not successful_results:
        print("❌ No successful reviews to compare")
        print("\n💡 To run real comparisons:")
        print("   export KIT_GITHUB_TOKEN='your_token'")
        print("   export KIT_ANTHROPIC_TOKEN='your_anthropic_key'")
        print("   export KIT_OPENAI_TOKEN='your_openai_key'")
        return results

    print(f"{'Provider':<15} {'Model':<25} {'Quality':<8} {'Cost':<8} {'Length':<8} {'Issues'}")
    print("-" * 75)

    for result in successful_results:
        provider = result['provider']
        model = result['model'][:20] + "..." if len(result['model']) > 20 else result['model']
        quality = f"{result['quality_score']:.2f}"
        cost = f"${result['cost']:.3f}"
        length = f"{result['review_length']:,}"
        issues = len(result.get('issues', []))

        print(f"{provider:<15} {model:<25} {quality:<8} {cost:<8} {length:<8} {issues}")

    # Analysis
    if len(successful_results) > 1:
        print("\n🏆 ANALYSIS")
        print("-" * 20)

        best_quality = max(successful_results, key=lambda x: x['quality_score'])
        best_value = min(successful_results, key=lambda x: x['cost'] / max(x['quality_score'], 0.1))

        print(f"🥇 Best Quality: {best_quality['provider']} {best_quality['model']} ({best_quality['quality_score']:.2f})")
        print(f"💎 Best Value: {best_value['provider']} {best_value['model']} (${best_value['cost']:.3f} for {best_value['quality_score']:.2f})")

        avg_quality = sum(r['quality_score'] for r in successful_results) / len(successful_results)
        avg_cost = sum(r['cost'] for r in successful_results) / len(successful_results)

        print(f"📈 Average Quality: {avg_quality:.2f}")
        print(f"📉 Average Cost: ${avg_cost:.3f}")

    return results

def test_with_sample_data():
    """Test the comparison system with sample data when no API keys available."""
    print("🧪 Testing Cross-Model Comparison System (Sample Data)")
    print("=" * 60)

    # Simulate different model outputs
    sample_reviews = {
        'claude-sonnet': """## Priority Issues
- High priority: Missing input validation in [auth.py:45](https://github.com/test/repo/blob/abc123/auth.py#L45)
- Medium priority: Consider using environment variables for configuration

## Summary
This PR implements user authentication with JWT tokens and session management.

## Recommendations
- Add rate limiting for login attempts
- Implement secure password hashing with bcrypt
- Consider adding request logging for security monitoring
""",

        'claude-haiku': """## Summary
PR adds authentication features with JWT implementation.

## Issues Found
- Missing validation in auth.py:45
- Configuration should use env vars
- Add rate limiting

## Recommendations
Add proper input checks and rate limiting.
""",

        'gpt-4o': """## Priority Issues
- High: Input validation missing at [auth.py:45](https://github.com/test/repo/blob/abc123/auth.py#L45)
- Medium: Hardcoded configuration values

## Summary
This PR introduces JWT-based authentication system with session handling.

## Recommendations
- Implement input sanitization for user credentials
- Move configuration to environment variables
- Add comprehensive error handling for edge cases
- Consider implementing CSRF protection
""",

        'gpt-4o-mini': """## Summary
Authentication PR looks good overall.

## Issues
Some validation missing.

## Recommendations
Add input checks and use env vars.
"""
    }

    # Sample diff and files
    pr_diff = """@@ -20,6 +20,25 @@ class AuthService:
+    def authenticate(self, username, password):
+        if not username or not password:
+            return None
+        user = self.get_user(username)
+        if user and self.verify_password(password, user.password_hash):
+            return self.generate_jwt_token(user)
+        return None
+
+    def generate_jwt_token(self, user):
+        payload = {'user_id': user.id, 'exp': time.time() + 3600}
+        return jwt.encode(payload, 'secret_key', algorithm='HS256')
"""

    changed_files = ['auth.py', 'models.py']

    print("🔍 Validating Sample Reviews:")
    print("-" * 30)

    model_results = []

    for model_name, review in sample_reviews.items():
        validation = validate_review_quality(review, pr_diff, changed_files)

        result = {
            'model': model_name,
            'quality_score': validation.score,
            'issues': validation.issues,
            'metrics': validation.metrics,
            'review_length': len(review)
        }

        model_results.append(result)

        print(f"{model_name:<15}: Quality {validation.score:.2f}, Length {len(review):,} chars")
        if validation.issues:
            print(f"                 Issues: {len(validation.issues)} found")

    print("\n📊 Sample Comparison Results:")
    print("-" * 40)

    best = max(model_results, key=lambda x: x['quality_score'])
    worst = min(model_results, key=lambda x: x['quality_score'])

    print(f"🥇 Best: {best['model']} (Quality: {best['quality_score']:.2f})")
    print(f"🥉 Worst: {worst['model']} (Quality: {worst['quality_score']:.2f})")

    print("\n✅ Cross-model comparison system working!")
    return model_results

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pr_url = sys.argv[1]
        results = compare_models_on_pr(pr_url)
    else:
        print("💡 Usage: python cross_model_test.py <pr_url>")
        print("📝 Running with sample data instead...\n")
        test_with_sample_data()
