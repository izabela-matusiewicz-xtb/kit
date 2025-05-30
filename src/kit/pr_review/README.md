# Kit AI-Powered PR Reviewer

`kit` includes a production-ready CLI-based pull request reviewer that provides intelligent, comprehensive code reviews using Claude or GPT-4, with complete cost transparency and professional-grade analysis.

## 🚀 Quick Start

```bash
# 1. Install kit
pip install cased-kit

# 2. Initialize configuration
kit review --init-config

# 3. Set your API keys
export KIT_GITHUB_TOKEN="ghp_your_github_token"
export KIT_ANTHROPIC_TOKEN="sk-ant-your_anthropic_key"

# 4. Review any GitHub PR
kit review https://github.com/owner/repo/pull/123

# 5. Test without posting (dry run)
kit review --dry-run https://github.com/owner/repo/pull/123
```

## 💰 Cost Economics

Kit provides **exceptional value** with transparent pricing. Based on real-world testing:

### **Actual Cost Data (Typical 3-6 file PR)**

| Mode | Cost Range | Speed | Use Case |
|------|------------|-------|----------|
| **Simple** | $0.015-0.025 | 5-15 sec | Quick feedback, budget reviews |
| **Standard** | $0.10-0.30 | 15-45 sec | Daily development - **recommended** |
| **Agentic** | $0.56-3.07 | 1-5 min | Research/experimentation |

### **Real-World Monthly Costs**

**Small Team (20 PRs/month)**:
- All Standard: $2.00-6.00/month  
- Mixed approach: $5.00-15.00/month

**Medium Team (100 PRs/month)**:
- All Standard: $10.00-30.00/month
- Mixed approach: $25.00-75.00/month  

**Enterprise (500 PRs/month)**:
- All Standard: $50.00-150.00/month
- Mixed approach: $125.00-375.00/month

**Key advantages**:
- No per-seat licensing - costs scale with usage, not team size
- No vendor lock-in - open source, you control deployment
- Complete cost transparency - see exact LLM costs with no markup

## 🎯 Review Modes Deep Dive

### Simple Mode (Fast & Budget-Friendly)

**How it works**: Fast file-level analysis without repository context - focuses on diff content only.

**Performance Profile**:
```
Cost: $0.015-0.025 (typical PR)
Speed: 5-15 seconds  
Quality: Basic but reliable
```

**Best for**: Quick feedback, budget-conscious workflows, initial PR screening

### Standard Mode (Recommended)

**How it works**: Leverages kit's repository intelligence for comprehensive reviews with symbol analysis and cross-codebase impact assessment.

**Performance Profile**:
```
Cost: $0.10-0.30 (typical PR)
Speed: 15-45 seconds  
Quality: Excellent balance of depth and accuracy
```

**Strengths**:
- Best quality-to-cost ratio
- Repository context and symbol analysis
- Identifies impact on functions/classes used elsewhere
- Fast single-pass execution
- Professional, actionable feedback

**Example capabilities**:
- Identifies that a function is used in 23 other places
- Suggests specific code improvements with examples
- Analyzes dependency changes and their implications
- Provides architectural guidance based on repository structure

### Agentic Mode (Experimental)

**How it works**: Uses multi-turn analysis where the AI investigates the PR using kit's tools through iterative exploration.

**Performance Profile**:
```
Cost: $0.56-3.07 (typical PR)
Speed: 1-5 minutes
Quality: Variable - can produce false positives
```

**Important Notes**:
- **Experimental feature** - currently serves as research artifact
- Can produce overconfident conclusions about non-existent issues
- Significantly more expensive than other modes
- Demonstrates that complex approaches don't always yield better results

**Best for**: Research, experimentation, understanding current AI agent limitations

### Mode Comparison

| Aspect | Standard | Agentic |
|--------|----------|---------|
| **Cost** | $0.10-0.30 | $0.56-3.07 |
| **Speed** | 15-45 sec | 1-5 min |
| **Quality** | Excellent balance of depth and accuracy | Variable - can produce false positives |
| **Best For** | Daily development | Research/experimentation |

## 🎯 Key Features

### Intelligent Analysis
- Deep code understanding using repository cloning and analysis
- Context-aware reviews with full codebase knowledge
- Multi-language support for any language kit supports
- Security and architecture analysis

### Professional Output
- Concise, actionable feedback without unnecessary verbosity
- Priority-based issue ranking (High/Medium/Low)
- Clickable GitHub links for all file references
- Professional tone without dramatic language

### Cost Transparency
- Real-time cost tracking showing exact LLM usage
- Token breakdown (input/output) for understanding cost drivers
- Model information showing which LLM provided the analysis

### Enterprise Features
- Repository caching for faster repeat reviews
- Multiple LLM support (Anthropic Claude, OpenAI GPT-4)
- Configurable analysis depth and turn limits
- GitHub integration with token-based authentication

## 📋 Setup Instructions

### 1. GitHub Token Setup

You need a GitHub token with appropriate permissions:

#### Classic Personal Access Token (Recommended)

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. Select scopes:
   - **Public repos**: `public_repo`
   - **Private repos**: `repo` (includes public access)
4. Copy token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. LLM API Keys

#### Anthropic Claude (Recommended)
1. Get API key from https://console.anthropic.com/
2. Format: `sk-ant-xxxxxxxxxxxxxxxxx`
3. Set: `export KIT_ANTHROPIC_TOKEN="your_key"`

#### OpenAI GPT-4
1. Get API key from https://platform.openai.com/
2. Format: `sk-xxxxxxxxxxxxxxxxx`
3. Set: `export KIT_OPENAI_TOKEN="your_key"`

### 3. Configuration

#### Quick Setup
```bash
kit review --init-config
```

This creates `~/.kit/review-config.yaml` with defaults.

#### Manual Configuration

Edit `~/.kit/review-config.yaml`:

```yaml
github:
  token: ghp_your_token_here
  base_url: https://api.github.com

llm:
  provider: anthropic  # or "openai"
  model: claude-sonnet-4-20250514  # or "gpt-4o"
  api_key: sk-ant-your_key_here
  max_tokens: 4000
  temperature: 0.1

review:
  max_files: 50
  post_as_comment: true
  clone_for_analysis: true
  cache_repos: true
  agentic_max_turns: 15
  agentic_finalize_threshold: 10

# Optional: Custom LLM pricing
custom_pricing:
  anthropic:
    claude-sonnet-4-20250514:
      input_per_million: 3.00
      output_per_million: 15.00
  openai:
    gpt-4o:
      input_per_million: 2.50  
      output_per_million: 10.00
```

## 🔧 Usage Examples

### Basic Review
```bash
# Standard mode (recommended)
kit review https://github.com/owner/repo/pull/123

# Dry run (no posting)
kit review --dry-run https://github.com/owner/repo/pull/123

# Agentic mode (experimental)
kit review --agentic --agentic-turns 8 https://github.com/owner/repo/pull/123
```

### Cache Management
```bash
# Check cache status
kit review-cache status

# Clean up old cached repos
kit review-cache cleanup

# Clear all cache
kit review-cache clear
```

## 🎛️ Advanced Configuration

### Environment Variables

| Purpose | Variable |
|---------|----------|
| GitHub Token | `KIT_GITHUB_TOKEN` |
| Anthropic Key | `KIT_ANTHROPIC_TOKEN` |
| OpenAI Key | `KIT_OPENAI_TOKEN` |

### Model Recommendations

#### Anthropic Models (Recommended)

**Latest Generation (Claude 4)**
- `claude-opus-4-20250514` - Most capable model, best for complex analysis but expensive
- `claude-sonnet-4-20250514` - **Recommended balance** of capability and cost

**Previous Generation (Claude 3.x)**  
- `claude-3-5-sonnet-20241022` - Proven reliable option, good balance
- `claude-3-5-haiku-20241022` - Fastest responses, budget option

#### OpenAI Models
- `gpt-4o` - Strong reasoning capabilities
- `gpt-4o-mini` - Cost-effective option

### Cost Optimization Tips

1. **Use Standard mode** for 90% of daily PRs - best value
2. **Use Simple mode** for quick feedback or budget constraints
3. **Use Agentic mode** sparingly for research/experimentation only
4. **Monitor costs** with dry runs first
5. **Enable caching** for faster subsequent reviews

## 🎯 Accuracy Validation

Kit provides several approaches to validate review accuracy:

### Built-in Quality Metrics

Every review includes objective quality scoring:

- **Reference Validation**: Checks if review references actual changed files
- **Line Number Validation**: Verifies line references are plausible
- **Specificity Analysis**: Counts concrete vs vague feedback
- **GitHub Link Validation**: Ensures links point to changed files
- **Content Relevance**: Measures alignment with actual code changes
- **Change Coverage**: Assesses coverage of major modifications

Example output:
```
📊 Review Quality Score: 0.75/1.0
📈 Metrics: {'file_references': 3, 'specific_issues': 5, 'github_links': 4}
```

### Validation Strategies

1. **Comparative Analysis**
   ```bash
   # Compare different modes on same PR
   kit review --dry-run --simple <pr-url>
   kit review --dry-run <pr-url>
   kit review --dry-run --agentic <pr-url>
   ```

2. **Historical Tracking**
   - Track quality scores over time
   - Monitor for degradation patterns
   - Compare across different PR types

3. **Spot Checking**
   - Manually validate 10-20% of reviews
   - Focus on high-impact or low-scoring reviews
   - Document common failure patterns

4. **Cross-Validation**
   - Test same PR with different models
   - Compare Claude vs GPT-4 outputs
   - Use multiple team members for validation

### Quality Thresholds

Kit automatically warns when quality is low:

- **Score < 0.6**: Warning displayed to user
- **No specific issues**: Suggests using standard mode
- **Broken links**: Reports invalid file references
- **Missing coverage**: Flags unaddressed major changes

### Accuracy Testing Tools

Kit includes tools for systematic accuracy validation:

#### Cross-Mode Testing
```bash
# Test a PR across all modes and compare
python -m kit.pr_review.test_accuracy test --pr-url https://github.com/owner/repo/pull/123
```

#### Review Validation
```bash
# Validate an existing review
echo "## Summary\nThis PR adds..." > review.txt
python -m kit.pr_review.test_accuracy validate --pr-url <pr-url> --review-file review.txt
```

#### Regression Testing
```bash
# Test multiple PRs systematically
echo "https://github.com/owner/repo/pull/123" > pr_list.txt
echo "https://github.com/owner/repo/pull/124" >> pr_list.txt
python -m kit.pr_review.test_accuracy regression --pr-list pr_list.txt
```

Output example:
```
🧪 Testing PR: https://github.com/owner/repo/pull/123
📱 SIMPLE MODE: $0.018 | 1,234 chars
🛠️  STANDARD MODE: $0.15 | 2,856 chars  
🤖 AGENTIC MODE: $1.25 | 4,102 chars

📊 Quality Scores: Simple: 0.72 | Standard: 0.84 | Agentic: 0.71*
*Agentic may produce false positives - use with caution
```