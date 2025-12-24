@echo off
REM Cross-platform test runner for Windows
REM Equivalent to run_tests.py for Windows environments

echo Running Mythril2 tests on Windows...
echo.

REM Set environment variables
if not defined MYTHRIL2_DIR (
    set MYTHRIL2_DIR=%CD%
)

if not defined INFURA_ID (
    echo Warning: INFURA_ID environment variable not set
    echo Some tests may fail without proper RPC endpoint
    echo.
)

REM Check if virtual environment is active
python -c "import sys; print('Virtual environment active:' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'Virtual environment not active - consider activating one')"

echo.
echo Installing test dependencies...
python -m pip install --upgrade pip
pip install pytest pytest-mock pytest-cov coverage

echo.
echo Running unit tests...
python -m pytest tests/ -v --tb=short --cov=mythril2 --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml

if %ERRORLEVEL% neq 0 (
    echo.
    echo Tests failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo Running integration tests...
python -m pytest tests/integration_tests/ -v --tb=short

if %ERRORLEVEL% neq 0 (
    echo.
    echo Integration tests failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo All tests completed successfully!
echo.
echo Test coverage report generated in htmlcov/index.html
echo.

REM Run specific Windows-specific tests if they exist
if exist "tests\windows_tests\" (
    echo Running Windows-specific tests...
    python -m pytest tests/windows_tests/ -v --tb=short
)

echo.
echo Test run completed. Check the output above for any failures.
