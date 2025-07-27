#!/usr/bin/env python3
"""
SmartTestAI Test Runner

Main entry point for running AI-enhanced test suites with support for multiple
applications and configurable execution modes.

Usage Examples:
    # Run all tests for AwesomeQA suite
    python run_tests.py --suite awesomeqa --mode run

    # Generate and run tests for a specific suite in headless mode
    python run_tests.py --suite awesomeqa --mode full --headless

    # Run only critical tests
    python run_tests.py --suite awesomeqa --mode run --markers "critical"

    # List available suites
    python run_tests.py --list-suites
"""

import sys
import argparse
import subprocess
import logging
import yaml
import time
from pathlib import Path
from typing import List, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from smarttestai.core.ai_config import AIConfig
from smarttestai.runners.base_runner import BaseRunner


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the test runner"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"test_run_{int(time.time())}.log")
        ]
    )


def discover_suites():
    """Discover available test suites with validation"""
    examples_dir = Path("examples")
    suites = []
    
    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir.absolute()}")
        return []
    
    for suite_dir in examples_dir.iterdir():
        if suite_dir.is_dir():
            config_file = suite_dir / "config.yaml"
            if config_file.exists():
                try:
                    # Validate config can be loaded
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    if config and 'suite_info' in config:
                        suites.append({
                            'name': suite_dir.name,
                            'display_name': config.get('suite_info', {}).get('name', suite_dir.name),
                            'base_url': config.get('suite_info', {}).get('base_url', 'Not configured')
                        })
                except Exception as e:
                    print(f"⚠️  Invalid config in {suite_dir.name}: {e}")
            else:
                print(f"⚠️  No config.yaml found in {suite_dir.name}")
    
    return sorted(suites, key=lambda x: x['name'])


def validate_suite(suite_name: str) -> bool:
    """Validate that a suite exists and has required structure"""
    suite_path = project_root / "examples" / suite_name
    
    required_files = [
        suite_path / "config.yaml",
        suite_path / "pages",
        suite_path / "tests"
    ]
    
    return all(path.exists() for path in required_files)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="SmartTestAI Test Runner - AI-Enhanced Test Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --suite awesomeqa --mode run
  %(prog)s --suite awesomeqa --mode full --headless --open-report
  %(prog)s --suite awesomeqa --mode generate --tests "test_product"
  %(prog)s --list-suites
        """
    )
    
    # Suite selection
    parser.add_argument(
        "--suite", "-s",
        type=str,
        help="Test suite to run (e.g., 'awesomeqa', 'amazon_in')"
    )
    
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List all available test suites"
    )
    
    parser.add_argument(
        "--disable-ai",
        action="store_true",
        help="Disable all AI features for faster execution"
    )
    
    parser.add_argument(
        "--cost-optimized",
        action="store_true",
        help="Run with cost-optimized AI settings"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Execution mode
    parser.add_argument(
        "--mode", "-m",
        choices=["run", "generate", "full"],
        default="run",
        help="Execution mode: 'run' (run tests), 'generate' (generate tests), 'full' (generate + run)"
    )
    
    # Test selection
    parser.add_argument(
        "--tests", "-t",
        type=str,
        help="Specific test file or pattern to run"
    )
    
    parser.add_argument(
        "--markers",
        type=str,
        help='Pytest markers to filter tests (e.g., "critical", "smoke", "regression")'
    )
    
    # Browser options
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run tests in headless browser mode"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox", "safari", "edge"],
        help="Browser to use for testing"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="Number of parallel workers (default: from config)"
    )
    
    # AI options
    parser.add_argument(
        "--ai-features",
        nargs="+",
        choices=["self_healing", "visual_testing", "test_generation", "test_analysis"],
        help="Enable specific AI features only"
    )
    
    # Reporting
    parser.add_argument(
        "--open-report",
        action="store_true",
        help="Automatically open test report when complete"
    )
    
    parser.add_argument(
        "--report-formats",
        nargs="+",
        choices=["html", "allure", "json"],
        help="Report formats to generate"
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the test runner"""
    args = parse_arguments()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else args.log_level
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting SmartTestAI Test Runner")
    
    # Handle list suites command
    if args.list_suites:
        suites = discover_suites()
        if suites:
            print("\n📋 Available Test Suites:")
            print("-" * 50)
            for suite in suites:
                print(f"  🧪 {suite['name']:15} | {suite['display_name']}")
                print(f"     {'':15} | URL: {suite['base_url']}")
            print("-" * 50)
            print(f"\n✅ Found {len(suites)} test suite(s)")
        else:
            print("❌ No test suites found in examples/ directory")
            print("💡 Create a new suite with: mkdir -p examples/my_app && cp examples/another_app/config.yaml examples/my_app/")
        return 0
    
    # Validate suite argument
    if not args.suite:
        logger.error("No test suite specified. Use --suite <suite_name> or --list-suites")
        return 1
    
    if not validate_suite(args.suite):
        logger.error(f"Invalid or missing test suite: {args.suite}")
        logger.info("Available suites: " + ", ".join(discover_suites()))
        return 1
    
    try:
        # Load suite configuration
        logger.info(f"Loading configuration for suite: {args.suite}")
        config = AIConfig.load_suite_config(args.suite)
        
        # Create runtime overrides based on command line arguments
        runtime_overrides = {}
        
        if args.headless:
            runtime_overrides["browser.headless"] = True
        
        if args.browser:
            runtime_overrides["browser.default"] = args.browser
        
        if args.parallel:
            runtime_overrides["test_execution.parallel"] = True
        
        if args.workers:
            runtime_overrides["test_execution.max_workers"] = args.workers
        
        if args.disable_ai:
            for feature in ["self_healing", "visual_testing", "test_generation", "test_analysis"]:
                runtime_overrides[f"ai_features.{feature}"] = False
        
        if args.ai_features:
            # Disable all features first, then enable specified ones
            for feature in ["self_healing", "visual_testing", "test_generation", "test_analysis"]:
                runtime_overrides[f"ai_features.{feature}"] = False
            for feature in args.ai_features:
                runtime_overrides[f"ai_features.{feature}"] = True
        
        if args.cost_optimized:
            runtime_overrides["ai_settings.model"] = "models/gemini-2.5-flash-lite"
            runtime_overrides["ai_settings.enable_caching"] = True
            runtime_overrides["test_execution.max_workers"] = 1
        
        # Create and configure runner with runtime overrides
        runner = BaseRunner(args.suite, config, runtime_overrides)
        
        # Configure runner options
        runner.set_options(
            mode=args.mode,
            tests=args.tests,
            markers=args.markers,
            report_formats=args.report_formats,
            open_report=args.open_report
        )
        
        # Execute tests
        logger.info(f"Starting test execution in {args.mode} mode")
        result = runner.run()
        
        # Log summary
        if result.get("success", False):
            logger.info("Test execution completed successfully")
            if args.open_report and result.get("report_path"):
                import webbrowser
                webbrowser.open(f"file://{result['report_path']}")
        else:
            logger.error("Test execution failed")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
