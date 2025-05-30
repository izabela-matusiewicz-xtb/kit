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
| **Standard** | $0.025-0.045 | 15-30 sec | Daily development - best value |
| **Agentic Budget** (8 turns) | $0.20-0.30 | 1-2 min | Complex PRs, budget-conscious |
| **Agentic Thorough** (15+ turns) | $0.35-0.50 | 2-4 min | Critical PRs, maximum depth |

### **Real-World Monthly Costs**

**Small Team (20 PRs/month)**:
- All Standard: $0.50-1.00/month  
- Mixed approach: $2.50-4.00/month

**Medium Team (100 PRs/month)**:
- All Standard: $2.50-4.50/month
- Mixed approach: $8.00-12.00/month  

**Enterprise (500 PRs/month)**:
- All Standard: $12.50-22.50/month
- Mixed approach: $40.00-60.00/month

**Key advantages**:
- No per-seat licensing - costs scale with usage, not team size
- No vendor lock-in - open source, you control deployment
- Complete cost transparency - see exact LLM costs with no markup

## 🎯 Review Modes Deep Dive

### Standard Mode (Recommended)

**How it works**: Leverages kit's repository intelligence for comprehensive reviews with symbol analysis and cross-codebase impact assessment.

**Performance Profile**:
```
Cost: $0.025-0.045 (typical PR)
Speed: 15-30 seconds  
Quality Score: 8.5/10
```

**Strengths**:
- Excellent quality-to-cost ratio
- Repository context and symbol analysis
- Identifies impact on functions/classes used elsewhere
- Fast single-pass execution
- Professional, actionable feedback

**Example capabilities**:
- Identifies that a function is used in 23 other places
- Suggests specific code improvements with examples
- Analyzes dependency changes and their implications
- Provides architectural guidance based on repository structure

### Agentic Mode (Multi-turn Analysis)

**How it works**: Uses multi-turn analysis where the AI strategically investigates the PR using kit's tools, building deep understanding through iterative exploration.

**Performance Profiles**:

#### Budget Configuration (8 turns)
```
Cost: $0.20-0.30 (typical PR)
Speed: 45-90 seconds
Quality Score: 8.8/10
```

#### Thorough Configuration (15 turns)  
```
Cost: $0.35-0.50 (typical PR)
Speed: 2-4 minutes
Quality Score: 9.2/10
```

**Unique capabilities**:
- Investigative approach like a human reviewer
- Deep context building across multiple files
- Adaptive analysis focusing on important areas
- Strategic tool usage leveraging all kit capabilities

**Example investigation pattern**:
1. Get repository structure overview
2. Analyze main implementation changes
3. Search for related patterns and dependencies
4. Examine test coverage
5. Check for cross-file impacts
6. Finalize comprehensive review

**Best for**:
- Complex architectural changes
- Security-critical modifications  
- Large PRs with interconnected files
- Critical production systems

### Mode Comparison

| Aspect | Standard | Agentic Budget | Agentic Thorough |
|--------|----------|----------------|------------------|
| **Cost** | $0.025-0.045 | $0.20-0.30 | $0.35-0.50 |
| **Speed** | 15-30 sec | 1-2 min | 2-4 min |
| **Quality** | 8.5/10 | 8.8/10 | 9.2/10 |
| **Best For** | Daily workflow | Complex PRs | Critical changes |

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

# Agentic budget mode (8 turns)
kit review --agentic --agentic-turns 8 https://github.com/owner/repo/pull/123

# Agentic thorough mode (15 turns)
kit review --agentic --agentic-turns 15 https://github.com/owner/repo/pull/123
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
- `claude-opus-4-20250514` - **Most capable model**, world's best coding model, superior for complex analysis
- `claude-sonnet-4-20250514` - **Optimal balance**, high performance with excellent reasoning

**Previous Generation (Claude 3.x)**  
- `claude-3-7-sonnet-20250219` - Extended thinking capabilities, solid performance
- `claude-3-5-sonnet-20241022` - Proven reliable option, good balance
- `claude-3-5-haiku-20241022` - Fastest responses, budget option

#### OpenAI Models
- `gpt-4o` - Strong reasoning capabilities
- `gpt-4o-mini` - Cost-effective option

### Cost Optimization Tips

1. **Use Standard mode** for 80% of daily PRs
2. **Agentic Budget mode** for complex features  
3. **Agentic Thorough mode** for critical/security changes
4. **Monitor costs** with dry runs first
5. **Enable caching** for faster subsequent reviews

## 🎯 Accuracy Validation

Kit provides several approaches to validate review accuracy without relying on LLM self-assessment:

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
📊 Review Quality Score: 0.85/1.0
📈 Metrics: {'file_references': 3, 'specific_issues': 5, 'github_links': 4}
```

### Validation Strategies

1. **Comparative Analysis**
   ```bash
   # Compare different modes on same PR
   kit review --dry-run --simple <pr-url>
   kit review --dry-run <pr-url>
   kit review --dry-run --agentic --agentic-turns 8 <pr-url>
   ```

2. **Historical Tracking**
   - Track quality scores over time
   - Monitor for degradation patterns
   - Compare across different PR types

3. **Spot Checking**
   - Manually validate 5-10% of reviews
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
📱 SIMPLE MODE: $0.025 | 1,234 chars
🛠️  STANDARD MODE: $0.045 | 2,856 chars  
🤖 AGENTIC MODE: $0.28 | 4,102 chars

📊 Quality Scores: Simple: 0.72 | Standard: 0.89 | Agentic: 0.94
```