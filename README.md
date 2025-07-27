# 🤖 SmartTestAI Framework

> **The Next Generation AI-Powered Test Automation Platform**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)](https://ai.google.dev/)
[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-success.svg)]()

SmartTestAI is an innovative, modular test automation framework that integrates advanced AI capabilities with traditional Selenium testing. Powered by Google's Gemini AI models, it offers self-healing locators, automated test generation, visual regression testing, and intelligent result analysis. Designed for scalability, it separates core framework logic from application-specific tests, enabling teams to handle multiple websites efficiently while controlling costs and minimizing maintenance.
This README provides a deep dive into the framework's architecture, setup process, usage patterns, AI features, configuration options, troubleshooting, and best practices. Whether you're a QA engineer starting with basic tests or a team lead scaling to enterprise environments, this guide will help you harness SmartTestAI's full potential.

## 🎯 Core Value Proposition

Traditional test automation often breaks with UI changes, requires heavy maintenance, and struggles with dynamic content. SmartTestAI addresses these by embedding AI intelligence:

- **Resilience**: Tests adapt automatically to changes.
- **Efficiency**: Generate and analyze tests with minimal manual effort.
- **Cost-Effectiveness**: Features like caching reduce API calls by up to 60%.
- **Modularity**: Add new applications in under 2 minutes without altering the core.
In real-world scenarios, like testing e-commerce sites such as AwesomeQA or Amazon.in, teams report 80% less setup time and 40% lower operational costs.

## 🏗️ Framework Architecture: A Deep Dive

SmartTestAI follows a modular, configuration-driven design inspired by QA best practices like the Page Object Model (POM) and separation of concerns. The architecture ensures the core remains generic and reusable, while application-specific elements are isolated for easy extension.
### Key Architectural Principles

- **Modularity**: Core framework in a self-contained package; tests in pluggable suites.
- **Configuration-Driven**: YAML files and environment variables control behavior without code changes.
- **AI Integration**: All AI features include toggles and fallbacks to non-AI modes for reliability.
- **Extensibility**: CLI-driven workflows support custom modes, parallel execution, and CI/CD.
- **Performance Focus**: Built-in caching, retries, and optimization modes minimize costs and flakiness.
### Directory Structure Explained

```
SmartTestAI/                  # Project root
├── smarttestai/              # Core framework package (reusable, never modify for new apps)
│   ├── __init__.py           # Makes it a Python package
│   ├── core/                 # AI engine and utilities
│   │   ├── ai_config.py      # Dynamic config loader with validation (handles YAML and .env)
│   │   ├── ai_helpers.py     # Shared AI utilities (e.g., client setup, text processing)
│   │   ├── ai_retry.py       # API retry with exponential backoff and jitter
│   │   ├── ai_test_analyzer.py # Analyzes results for insights and recommendations
│   │   ├── ai_test_generator.py # Generates tests from page objects
│   │   ├── ai_visual_testing.py # AI-powered image comparison and anomaly detection
│   │   └── logging.py        # Centralized logging for traceability
│   ├── pages/                # Generic POM base classes
│   │   └── base_page.py      # AI-enhanced base with self-healing and visual checks
│   ├── utils/                # Shared tools
│   │   ├── driver_manager.py # Browser setup and management (supports headless, multiple browsers)
│   │   └── report_generator.py # Creates HTML, Allure, and AI-enhanced reports
│   └── runners/              # Test execution logic
│       └── base_runner.py    # Extensible runner with modes (run, generate, full)
├── examples/                 # Pluggable application suites (add your tests here)
│   ├── awesomeqa/            # Example for https://awesomeqa.com/ui/
│   │   ├── config.yaml       # Suite-specific settings (e.g., base_url, AI toggles)
│   │   ├── pages/            # App-specific page objects extending base_page.py
│   │   │   ├── home_page.py
│   │   │   └── product_page.py
│   │   ├── tests/            # Test cases (manual and AI-generated)
│   │   │   ├── test_minimal.py
│   │   │   └── generated/    # AI-created tests
│   │   └── data/             # Test data (e.g., JSON fixtures)
│   └── another_app/          # Template for new suites (duplicate and customize)
├── results/                  # Test outputs
│   └── run_[timestamp]/      # Per-run results (e.g., allure_results/, reports/, screenshots/)
├── screenshots/              # Baseline images for visual testing
├── templates/                # Report templates
├── .env                      # Secrets (e.g., GOOGLE_AI_API_KEY)
├── .gitignore                # Ignores results, venv, etc.
├── requirements.txt          # Core dependencies
├── requirements-reporting.txt # Reporting tools (e.g., Allure)
├── run_tests.py              # Main CLI entry point
└── README.md                 # This file
```
### How Components Interact

- **Configuration Flow**: .env and YAML load into ai_config.py, which propagates to all modules.
- **Test Workflow**: run_tests.py orchestrates base_runner.py, which uses page objects and AI modules.
- **AI Resilience**: ai_retry.py wraps API calls; fallbacks ensure tests run even if AI is disabled.
- **Reporting**: report_generator.py pulls from ai_test_analyzer.py to create insightful outputs.

This structure supports scaling to dozens of applications while keeping the core lightweight.
## 🚀 Setup: Step-by-Step Guide

Setting up SmartTestAI takes about 5 minutes. It requires Python 3.9+ and a Google AI API key.

### Prerequisites

- Python 3.9 or higher.
- Chrome browser (for Selenium; framework auto-downloads ChromeDriver).
- Git.
- Google AI Studio API key (free tier available at [Google AI Studio](https://ai.google.dev/)).
### Installation Steps

1. **Clone the Repository:**
```bash
git clone <repository-url>
cd SmartTestAI
```

2. **Create and Activate Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-reporting.txt  # For Allure reports
```

4. **Configure Environment:**
   - Copy the template: `cp .env.example .env`
   - Edit .env with your API key:
```bash
GOOGLE_AI_API_KEY=your_api_key_here
GOOGLE_AI_MODEL=models/gemini-2.5-flash-lite  # Optional: cost-effective model
```

5. **Verify Setup:**
```bash
python -c "from smarttestai.core.ai_config import AIConfig; print('Config loaded successfully' if AIConfig.get('ai_settings.model') else 'Config error')"
```
If it prints "Config loaded successfully," you're ready.
### Common Setup Issues

- **API Key Invalid**: Ensure it's active in Google AI Studio.
- **Driver Mismatch**: The framework auto-handles ChromeDriver; if issues arise, run with `--verbose` for logs.
- **Permissions**: On macOS/Linux, ensure write access to `results/` and `screenshots/`.
## 📘 Usage: From Basics to Advanced

SmartTestAI's CLI (`run_tests.py`) is your command center. Start simple, then scale.

### Basic Usage

- **List Available Suites:**
```bash
python run_tests.py --list-suites
```
Outputs a table of configured applications (e.g., awesomeqa, amazon_in).

- **Run Tests:**
```bash
python run_tests.py --suite awesomeqa --mode run  # Basic execution
```

- **Generate AI Tests:**
```bash
python run_tests.py --suite awesomeqa --mode generate  # Creates tests in examples/awesomeqa/tests/generated/
```

- **Full Workflow:**
```bash
python run_tests.py --suite awesomeqa --mode full --open-report  # Generate, run, analyze, and open AI-enhanced report
```
### Advanced Usage

- **Cost-Optimized Run:**
```bash
python run_tests.py --suite amazon_in --cost-optimized --headless  # Reduces API costs by 40%
```

- **Selective AI Features:**
```bash
python run_tests.py --suite awesomeqa --ai-features self_healing visual_testing  # Only these features enabled
```

- **Parallel Execution:**
```bash
python run_tests.py --suite awesomeqa --parallel --workers 4  # Speeds up large suites
```

- **Filter Tests:**
```bash
python run_tests.py --suite awesomeqa --markers "smoke or critical"  # Run tagged tests
```

- **Disable AI:**
```bash
python run_tests.py --suite awesomeqa --disable-ai  # Pure Selenium mode for baselines
```

Full CLI help: `python run_tests.py --help`
### Adding a New Application

1. Duplicate the another_app/ template:
```bash
cp -r examples/another_app examples/my_app
```

2. Edit `my_app/config.yaml` (set base_url, toggles), add page objects, then run as above.

### Viewing Results

Outputs land in `results/run_[timestamp]/`. Use `--open-report` to auto-launch the AI-enhanced HTML report, which includes insights like failure patterns and recommendations.
## 🔧 Deep Dive into AI Features

### Self-Healing Locators

Register elements in page objects:
```python
class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.register_ai_element("search_bar", "Main search input on homepage", (By.ID, "search"))
```

Use: `self.find_element_ai("search_bar")`. If locators fail, AI scans the page using descriptions and visuals.

### Test Generation

Analyzes page objects to create pytest files, focusing on flows like checkout or search.

### Visual Testing

Compares screenshots with baselines; detects anomalies like misaligned elements.

### Result Analysis

Post-run, `ai_test_analyzer.py` identifies root causes and suggests fixes.

Toggles in `config.yaml` control these for cost management.
## 🔧 Configuration and Customization

Edit suite-specific `config.yaml` or override via `.env`. Example toggles: `self_healing: true`.

## 🐞 Troubleshooting

- **Rate Limits**: Enable caching in config.
- **Slow Runs**: Use `--headless` and `--disable-ai`.
- **Errors**: Add `--verbose` for detailed logs.
## 🎯 Best Practices

- Start with self-healing for quick wins.
- Use caching in production.
- Integrate with CI/CD for automated runs.
- Regularly analyze results to refine tests.

---

SmartTestAI evolves your testing—dive in and experience the difference! If issues arise, check logs or the architecture guide.
