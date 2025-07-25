# SmartTestAI

SmartTestAI is a comprehensive AI-powered automated testing framework for REST APIs. It combines the power of AI (OpenAI's GPT models) with traditional testing approaches to generate, execute, and maintain API tests.

## 🎯 Key Features

- **AI-Powered Test Generation**: Create test cases from natural language prompts or API specifications
- **Automated Test Execution**: Run tests in parallel with comprehensive reporting
- **Test Maintenance**: AI-assisted test fixing and debugging
- **Rich Reporting**: Generate HTML, JSON, Markdown, and JUnit XML reports
- **Notifications**: Send test results to Slack or email
- **CI/CD Integration**: Ready-to-use Jenkinsfile and CI/CD setup

## 📋 Requirements

- Python 3.8+
- OpenAI API key for AI features

## 🚀 Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/SmartTestAI-AI-Test-Automation-Framework.git
cd SmartTestAI
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your environment variables:

```bash
cp .env.example .env
# Edit .env file to add your OpenAI API key and other settings
```

## 📁 Project Structure

```
SmartTestAI/
├── ai/
│   ├── prompt_generator.py   # AI test generation
│   └── fixer.py             # AI test fixing
├── config/
│   ├── config_loader.py     # Configuration loader
│   └── test_config.yaml     # Test configuration
├── tests/
│   ├── api/                 # Manual test cases
│   └── generated/           # AI-generated tests
├── utils/
│   ├── schema_validator.py  # JSON Schema validation
│   ├── notifications.py     # Notification handlers
│   └── report_generator.py  # Report generation
├── reports/                 # Generated test reports
├── runner.py               # Test runner CLI
├── Jenkinsfile             # CI/CD integration
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

Edit `config/test_config.yaml` to set your API endpoints, authentication, and test execution settings.

Key configuration sections:
- **api**: Base URL and request settings
- **auth**: Authentication type and credentials
- **endpoints**: API endpoints for testing
- **execution**: Test execution settings (parallel/sequential)
- **reporting**: Report formats and output directory
- **notifications**: Slack and email notification settings
- **openai**: AI model configuration

## 📝 Usage

### Running Tests

Run all tests:

```bash
python runner.py --all
```

Run a specific test file:

```bash
python runner.py --test-file tests/api/test_login_api.py
```

Run tests in parallel:

```bash
python runner.py --all --parallel
```

### Generating Reports

Generate reports in multiple formats:

```bash
python runner.py --all --report-formats html json markdown
```

### Sending Notifications

Send test results via configured notification channels:

```bash
python runner.py --all --notify
```

For detailed notifications:

```bash
python runner.py --all --notify --detailed-notify
```

### AI Test Generation

Generate a test case from a natural language prompt:

```bash
python runner.py --generate --prompt "Test that creating a user with missing email returns a 400 error" --endpoint "/users" --method POST
```

## 🤖 AI Features

### Test Generation

SmartTestAI can generate test cases from:

1. Natural language prompts:
   ```bash
   python runner.py --generate --prompt "Verify login with invalid credentials returns 401" --endpoint "/login" --method POST
   ```

2. OpenAPI/Swagger specifications:
   ```bash
   # Feature available through the API but not exposed in CLI yet
   ```

### Test Fixing

When tests fail, you can use the AI fixer to analyze and fix issues:

```python
from ai.fixer import TestFixer

fixer = TestFixer()
fixer.apply_fix('tests/api/failing_test.py', error_log)
```

## 🔄 CI/CD Integration

SmartTestAI includes a sample Jenkinsfile for CI/CD integration. To use it:

1. Configure your Jenkins pipeline to use the provided Jenkinsfile
2. Make sure your Jenkins instance has the required dependencies installed
3. Set up appropriate credentials for API authentication and notifications

## 📊 Reports

SmartTestAI generates rich, detailed reports in multiple formats:

- **HTML**: Interactive reports with test details and statistics
- **JSON**: Machine-readable format for further processing
- **Markdown**: GitHub-friendly format for documentation
- **JUnit XML**: Compatible with CI/CD systems

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
