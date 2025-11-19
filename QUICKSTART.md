# 🚀 Prompt Forge Studio - Quick Start Guide

Get up and running with Prompt Forge Studio in 5 minutes!

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure API key**:
```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

3. **Launch the application**:
```bash
python run.py
```

The app will open at `http://localhost:8501`

## First Steps

### 1. Configure API Key in UI

If you didn't set the `.env` file, you can configure your API key directly in the app:
- Click the **⚙️ API Configuration** section in the sidebar
- Paste your Anthropic API key
- Click **Save API Key**

### 2. Create Your First Prompt

- Click **➕ New Prompt** in the sidebar
- Enter a name (e.g., "My First Prompt")
- Add a description (optional)
- Write your initial prompt content
- Click **Create**

### 3. Analyze Quality

- Navigate to **📊 Analysis** tab
- Select **Comprehensive** analysis type
- Click **🔍 Run Analysis**
- Review your quality scores and recommendations

### 4. Create Test Cases

- Navigate to **🧪 Testing** tab
- Click **➕ Create New Test Case**
- Add a test name and input
- Define evaluation criteria
- Click **Create Test Case**

### 5. Run Tests

- In the **Run Tests** tab
- Click **▶️ Run All Tests**
- Review outputs and scores

## Example Workflow

Let's create a simple code review assistant:

1. **Create prompt**:
```
You are an expert code reviewer. Review the provided code for:
- Code quality and best practices
- Potential bugs or issues
- Performance concerns
- Security vulnerabilities

Provide constructive feedback in a friendly tone.
```

2. **Analyze it**:
   - Run Comprehensive analysis
   - Check clarity, completeness, safety scores

3. **Create test cases**:
   - **Test 1**: Submit a simple Python function
   - **Test 2**: Submit code with a security issue
   - **Test 3**: Submit poorly formatted code

4. **Run tests and iterate**:
   - Review how the prompt handles each case
   - Refine based on test results
   - Save new versions as you improve

## Tips

- **Version Control**: Save new versions after significant changes
- **Test Early**: Create test cases early in development
- **Iterate**: Use analysis feedback to guide improvements
- **Compare**: Test multiple variants to find the best approach

## Common Tasks

### Generate Variants
In the Editor, click **🔄 Generate Variants** to get AI-powered alternatives optimized for different aspects.

### View History
Click **📜 Version History** to see all versions and restore previous ones.

### Compare Versions
Create multiple versions and run the same test cases against each to compare performance.

## Next Steps

- Explore the **📚 Library** for managing multiple prompts
- Experiment with different analysis types
- Build a comprehensive test suite
- Save successful prompt patterns for reuse

## Troubleshooting

**API Key Error**: Ensure your API key is valid and properly configured in Settings or `.env`

**Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Database Issues**: Delete `promptforge.db` to reset the database if needed

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review code comments for implementation details
- Open an issue if you encounter bugs

Happy prompt engineering! 🔨
