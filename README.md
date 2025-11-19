# 🔨 Prompt Forge Studio

**An advanced prompt engineering laboratory powered by Claude**

Prompt Forge Studio is a desktop/web application that transforms prompt engineering from trial-and-error into a systematic, data-driven process. Using Claude's meta-cognitive capabilities, it analyzes, optimizes, tests, and refines system prompts through intelligent feedback loops.

## 🌟 Features

### Core Functionality

- **Intelligent Prompt Editor**: Full-featured editor with version control and history tracking
- **Multi-Dimensional Quality Analysis**: Automated analysis across clarity, completeness, efficiency, and safety dimensions
- **Automated Testing Suite**: Create test cases and run A/B comparisons between prompt versions
- **Version Management**: Git-like versioning system with diff visualization and rollback capabilities
- **Variant Generation**: AI-powered generation of optimized prompt variants
- **Performance Metrics**: Track quality scores and test performance across iterations

### Analysis Dimensions

The system analyzes prompts across multiple dimensions:

1. **Clarity**: Identifies ambiguities and unclear instructions
2. **Completeness**: Detects missing edge cases and logical gaps
3. **Efficiency**: Finds redundancies and optimization opportunities
4. **Safety**: Evaluates ethical considerations and potential risks
5. **Comprehensive**: Overall quality assessment with prioritized recommendations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PromptForge.git
cd PromptForge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### Running the Application

```bash
python run.py
```

Or directly with Streamlit:
```bash
streamlit run src/ui/app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Creating Your First Prompt

1. **Start the Application**: Launch Prompt Forge Studio
2. **Configure API**: Enter your Anthropic API key in the sidebar
3. **Create New Prompt**: Click "➕ New Prompt" in the sidebar
4. **Write Your Prompt**: Use the editor to craft your system prompt
5. **Analyze Quality**: Click "📊 Analyze Quality" to get comprehensive feedback
6. **Iterate and Improve**: Use the insights to refine your prompt

### Running Quality Analysis

The Analysis page offers multiple analysis types:

- **Comprehensive**: Runs all analysis dimensions and shows a quality radar chart
- **Clarity**: Focuses on ambiguity and precision
- **Completeness**: Identifies missing edge cases
- **Efficiency**: Suggests token optimizations
- **Safety**: Evaluates ethical and safety concerns

Each analysis provides:
- Numeric quality score (0-100)
- Specific issues found
- Concrete improvement suggestions

### Testing Prompts

1. **Create Test Cases**: Define inputs and evaluation criteria
2. **Run Tests**: Execute all test cases against your prompt
3. **Review Results**: See scores, outputs, and AI evaluations
4. **Compare Versions**: Test multiple prompt versions side-by-side

### Version Management

- **Save Versions**: Create new versions with descriptive notes
- **View History**: Browse all previous versions
- **Load Versions**: Restore any previous version
- **Compare**: See what changed between versions

## 🏗️ Architecture

```
PromptForge/
├── src/
│   ├── api/
│   │   └── anthropic_client.py    # API client with retry logic
│   ├── core/
│   │   ├── analyzer.py            # Quality analysis engine
│   │   ├── prompt.py              # Data models
│   │   └── tester.py              # Testing system
│   ├── db/
│   │   └── database.py            # SQLite database manager
│   ├── ui/
│   │   └── app.py                 # Streamlit interface
│   └── config.py                  # Configuration management
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

### Technology Stack

- **Backend**: Python 3.8+, SQLAlchemy, Pydantic
- **Frontend**: Streamlit, Plotly
- **AI**: Anthropic Claude API (Sonnet 4.5)
- **Database**: SQLite

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# Default Model Settings
DEFAULT_MODEL=claude-sonnet-4-5-20250929
ANALYSIS_MODEL=claude-sonnet-4-5-20250929

# API Limits
MAX_TOKENS=4096
TEMPERATURE=1.0

# Database
DATABASE_PATH=./promptforge.db

# App Settings
DEBUG=false
```

### Advanced Configuration

Edit `src/config.py` to customize:
- Retry logic parameters
- Model selections
- Token limits
- Database location

## 💡 Use Cases

### 1. System Prompt Development
Create and refine system prompts for production AI applications with confidence.

### 2. Prompt Optimization
Systematically improve existing prompts by identifying and fixing weaknesses.

### 3. Quality Assurance
Ensure prompts meet quality standards before deployment.

### 4. A/B Testing
Compare different prompt approaches with quantitative metrics.

### 5. Education
Learn prompt engineering best practices through AI-powered feedback.

## 🎯 Workflow Example

**Scenario**: Creating a medical report analyzer

1. **Initial Creation**
   - Create new prompt "Medical Report Analyzer v1"
   - Write initial system prompt with basic instructions
   - Add medical ethics component from library

2. **Quality Analysis**
   - Run comprehensive analysis
   - Discover missing edge case handling
   - Get suggestions for improving clarity

3. **Generate Variants**
   - Request robustness-focused variants
   - Review 3 AI-generated alternatives
   - Select most promising variant

4. **Testing**
   - Create test cases with sample reports
   - Include edge cases (incomplete data, ambiguous results)
   - Run tests across all variants

5. **Selection and Refinement**
   - Compare test results
   - Select best-performing variant (23% better on edge cases)
   - Make final tweaks
   - Save as v2

6. **Export**
   - Export finalized prompt for production use
   - Document test results and decisions

## 📊 Features in Detail

### Prompt Analysis

The analyzer uses specialized meta-prompts to evaluate your prompts:

- **Automated Scoring**: Each dimension receives a 0-100 score
- **Issue Detection**: Specific problems are identified with examples
- **Actionable Suggestions**: Concrete recommendations for improvement
- **Historical Tracking**: All analyses are saved for longitudinal comparison

### Test System

- **Flexible Test Cases**: Define inputs with expected outputs or evaluation criteria
- **AI-as-Judge**: Claude evaluates outputs based on your criteria
- **Batch Testing**: Run all tests with one click
- **Comparative Analysis**: Side-by-side comparison of different prompts
- **Score Tracking**: Historical performance metrics

### Variant Generation

Generate optimized variants focusing on:
- **Clarity**: Maximum precision and explicitness
- **Conciseness**: Token-optimized versions
- **Robustness**: Edge case handling
- **Balanced**: Overall quality improvement

## 🔐 Security & Privacy

- API keys are stored securely in environment variables
- Local SQLite database keeps all data on your machine
- No data is sent to third parties except Anthropic API
- Prompts may contain sensitive information - ensure proper API key security

## 🛣️ Roadmap

### Upcoming Features

- [ ] Component library with reusable prompt blocks
- [ ] Evolutionary optimization mode (genetic algorithms)
- [ ] Multi-model testing (GPT-4, Gemini comparison)
- [ ] Export to multiple formats (Python, TypeScript, etc.)
- [ ] Collaborative features and prompt sharing
- [ ] Advanced visualization and analytics
- [ ] CI/CD integration for automated testing
- [ ] Production monitoring integration

## 🤝 Contributing

Contributions are welcome! Areas of interest:

- Additional analysis dimensions
- New testing capabilities
- UI/UX improvements
- Documentation
- Example prompts and use cases

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- UI powered by [Streamlit](https://streamlit.io/)
- Inspired by the prompt engineering community

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🎓 Learn More

### Resources

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Best Practices for System Prompts](https://docs.anthropic.com/claude/docs/system-prompts)
- [Testing and Evaluation Strategies](https://docs.anthropic.com/claude/docs/evaluations)

---

**Built with ❤️ using Claude to improve Claude**

*Meta-recursion at its finest*
