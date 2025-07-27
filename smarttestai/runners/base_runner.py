"""
Base runner class for executing test suites with AI-enhanced capabilities.
This class provides the core orchestration logic for test execution, generation,
and reporting.
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseRunner:
    """
    Base class for running test suites with AI capabilities.
    
    This runner orchestrates:
    - Test discovery and execution
    - AI-powered test generation
    - Result analysis and reporting
    - Integration with various test frameworks (pytest, etc.)
    """
    
    def __init__(self, suite_name: str, config: Dict[str, Any], runtime_overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize the runner for a specific test suite.
        
        Args:
            suite_name: Name of the test suite to run
            config: Configuration dictionary for the suite
        """
        self.suite_name = suite_name
        self.config = config.copy()  # Don't modify original config
        self.runtime_overrides = runtime_overrides or {}
        self.logger = logging.getLogger(f"{__name__}.{suite_name}")
        
        # Apply runtime overrides to config
        self._apply_runtime_overrides()
        
        self.project_root = Path(__file__).parent.parent.parent
        self.suite_path = self.project_root / "examples" / suite_name
        
        # Execution options (set via set_options)
        self.mode = "run"
        self.tests = None
        self.markers = None
        self.report_formats = ["html"]
        self.open_report = False
        
        # Create results directory
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = self.project_root / "results" / f"run_{self.timestamp}"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized runner for suite: {suite_name}")
        logger.info(f"Results will be saved to: {self.results_dir}")
    
    def _apply_runtime_overrides(self):
        """Apply runtime configuration overrides using dot notation"""
        for key, value in self.runtime_overrides.items():
            self._set_nested_config(self.config, key, value)
            self.logger.debug(f"Applied runtime override: {key} = {value}")
    
    def _set_nested_config(self, config: Dict, key_path: str, value: Any):
        """Set a nested configuration value using dot notation"""
        keys = key_path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def set_options(self, **kwargs):
        """Set execution options for the runner"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                logger.debug(f"Set option {key} = {value}")
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution method that orchestrates the test run.
        
        Returns:
            Dictionary containing execution results and metadata
        """
        try:
            result = {
                "suite": self.suite_name,
                "timestamp": self.timestamp,
                "results_dir": str(self.results_dir),
                "success": False
            }
            
            if self.mode in ["generate", "full"]:
                logger.info("Starting test generation phase")
                generation_result = self._generate_tests()
                result["generation"] = generation_result
                
                if not generation_result.get("success", False):
                    logger.error("Test generation failed")
                    return result
            
            if self.mode in ["run", "full"]:
                logger.info("Starting test execution phase")
                execution_result = self._execute_tests()
                result["execution"] = execution_result
                
                if not execution_result.get("success", False):
                    logger.error("Test execution failed")
                    return result
                
                logger.info("Starting test analysis phase")
                analysis_result = self._analyze_results(execution_result)
                result["analysis"] = analysis_result
                
                logger.info("Starting report generation phase")
                reporting_result = self._generate_reports(execution_result, analysis_result)
                result["reporting"] = reporting_result
                result["report_path"] = reporting_result.get("main_report_path")
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Runner execution failed: {e}", exc_info=True)
            return {
                "suite": self.suite_name,
                "success": False,
                "error": str(e)
            }
    
    def _generate_tests(self) -> Dict[str, Any]:
        """Generate test cases using AI"""
        try:
            # Import here to avoid circular dependencies
            from smarttestai.core.ai_test_generator import AITestGenerator
            
            if not self.config.get("ai_features", {}).get("test_generation", False):
                logger.info("Test generation is disabled in configuration")
                return {"success": True, "message": "Test generation disabled"}
            
            generator = AITestGenerator(self.suite_name, self.config)
            
            # Discover page objects
            page_objects = generator.discover_page_objects(self.suite_path / "pages")
            logger.info(f"Discovered {len(page_objects)} page objects")
            
            # Generate test cases
            test_cases = generator.generate_test_cases(page_objects)
            logger.info(f"Generated {len(test_cases)} test cases")
            
            # Save generated tests
            generated_dir = self.suite_path / "tests" / "generated"
            generated_dir.mkdir(exist_ok=True)
            
            saved_files = generator.save_generated_tests(test_cases, generated_dir)
            
            return {
                "success": True,
                "page_objects_count": len(page_objects),
                "test_cases_count": len(test_cases),
                "saved_files": saved_files
            }
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _execute_tests(self) -> Dict[str, Any]:
        """Execute tests using pytest"""
        try:
            # Prepare pytest command
            cmd = ["python", "-m", "pytest"]
            
            # Test path
            test_path = self.suite_path / "tests"
            if self.tests:
                if "/" in self.tests or "\\" in self.tests:
                    # Full path provided
                    test_path = Path(self.tests)
                else:
                    # Relative to tests directory
                    test_path = test_path / self.tests
            
            cmd.append(str(test_path))
            
            # Add markers
            if self.markers:
                cmd.extend(["-m", self.markers])
            
            # Add parallel execution
            if self.config.get("test_execution", {}).get("parallel", False):
                workers = self.config.get("test_execution", {}).get("max_workers", 4)
                cmd.extend(["-n", str(workers)])
            
            # Add reporting options
            allure_dir = self.results_dir / "allure_results"
            allure_dir.mkdir(exist_ok=True)
            cmd.extend(["--alluredir", str(allure_dir)])
            
            # Add JUnit XML output
            junit_file = self.results_dir / "junit.xml"
            cmd.extend(["--junitxml", str(junit_file)])
            
            # Add verbose output
            cmd.append("-v")
            
            # Set environment variables
            env = os.environ.copy()
            env["SMARTTESTAI_SUITE"] = self.suite_name
            env["SMARTTESTAI_CONFIG"] = str(self.suite_path / "config.yaml")
            env["SMARTTESTAI_RESULTS_DIR"] = str(self.results_dir)
            
            # Execute pytest
            logger.info(f"Executing command: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.get("test_execution", {}).get("timeout", 300)
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "junit_file": str(junit_file),
                "allure_dir": str(allure_dir)
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            return {"success": False, "error": "Execution timeout"}
        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _analyze_results(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results using AI"""
        try:
            if not self.config.get("ai_features", {}).get("test_analysis", False):
                logger.info("Test analysis is disabled in configuration")
                return {"success": True, "message": "Test analysis disabled"}
            
            # Import here to avoid circular dependencies
            from smarttestai.core.ai_test_analyzer import AITestAnalyzer
            
            analyzer = AITestAnalyzer(self.config)
            
            # Create test run data from execution results
            test_run_data = {
                "suite": self.suite_name,
                "timestamp": self.timestamp,
                "execution_time": execution_result.get("execution_time", 0),
                "return_code": execution_result.get("return_code", -1),
                "stdout": execution_result.get("stdout", ""),
                "stderr": execution_result.get("stderr", ""),
                "junit_file": execution_result.get("junit_file")
            }
            
            # Perform analysis
            insights = analyzer.analyze_test_run(test_run_data)
            
            # Save analysis results
            analysis_file = self.results_dir / "ai_analysis.json"
            import json
            with open(analysis_file, 'w') as f:
                json.dump(insights, f, indent=2)
            
            return {
                "success": True,
                "insights": insights,
                "analysis_file": str(analysis_file)
            }
            
        except Exception as e:
            logger.error(f"Test analysis failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _generate_reports(self, execution_result: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test reports in multiple formats"""
        try:
            reports_dir = self.results_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            generated_reports = []
            main_report_path = None
            
            # Generate HTML report
            if "html" in self.report_formats:
                from smarttestai.utils.report_generator import HTMLReportGenerator
                
                html_generator = HTMLReportGenerator(self.config)
                html_report = reports_dir / "test_report.html"
                
                html_generator.generate(
                    execution_result,
                    analysis_result.get("insights", {}),
                    str(html_report)
                )
                
                generated_reports.append(str(html_report))
                if not main_report_path:
                    main_report_path = str(html_report)
            
            # Generate Allure report
            if "allure" in self.report_formats:
                allure_report_dir = reports_dir / "allure_report"
                allure_results_dir = execution_result.get("allure_dir")
                
                if allure_results_dir and Path(allure_results_dir).exists():
                    cmd = ["allure", "generate", allure_results_dir, "-o", str(allure_report_dir), "--clean"]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        generated_reports.append(str(allure_report_dir))
                        logger.info("Allure report generated successfully")
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"Allure report generation failed: {e}")
                    except FileNotFoundError:
                        logger.warning("Allure command not found. Install Allure to generate reports.")
            
            # Generate JSON report
            if "json" in self.report_formats:
                json_report = reports_dir / "test_results.json"
                report_data = {
                    "suite": self.suite_name,
                    "timestamp": self.timestamp,
                    "execution": execution_result,
                    "analysis": analysis_result,
                    "config": self.config
                }
                
                import json
                with open(json_report, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
                
                generated_reports.append(str(json_report))
            
            return {
                "success": True,
                "generated_reports": generated_reports,
                "main_report_path": main_report_path,
                "reports_dir": str(reports_dir)
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
