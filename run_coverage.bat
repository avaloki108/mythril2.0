@echo off
REM Cross-platform coverage runner for Windows
REM Equivalent to run_coverage.py for Windows environments

echo Running Mythril2 coverage analysis on Windows...
echo.

REM Set environment variables
if not defined MYTHRIL2_DIR (
    set MYTHRIL2_DIR=%CD%
)

if not defined INFURA_ID (
    echo Warning: INFURA_ID environment variable not set
    echo Some coverage may be incomplete without proper RPC endpoint
    echo.
)

REM Check if virtual environment is active
python -c "import sys; print('Virtual environment active:' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'Virtual environment not active - consider activating one')"

echo.
echo Installing coverage dependencies...
python -m pip install --upgrade pip
pip install coverage pytest pytest-cov

echo.
echo Cleaning previous coverage data...
coverage erase

echo.
echo Running coverage analysis...
coverage run -m pytest tests/ -v --tb=short
coverage run -a -m pytest tests/integration_tests/ -v --tb=short

if %ERRORLEVEL% neq 0 (
    echo.
    echo Coverage analysis failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo Generating coverage reports...
coverage report -m
coverage html
coverage xml

echo.
echo Coverage analysis completed!
echo.
echo Reports generated:
echo - Terminal coverage report (shown above)
echo - HTML coverage report: htmlcov/index.html
echo - XML coverage report: coverage.xml
echo.

REM Check coverage threshold
coverage report | findstr /C:"TOTAL" > temp_coverage.txt
set /p COVERAGE_LINE=<temp_coverage.txt
del temp_coverage.txt

echo %COVERAGE_LINE%
echo.
echo Target coverage: 80%
echo Current coverage: Check the percentage above

REM Optional: Fail if coverage is below threshold
for /f "tokens=2" %%i in ("%COVERAGE_LINE%") do set COVERAGE_PCT=%%i
set COVERAGE_PCT=%COVERAGE_PCT:~0,-1%

if %COVERAGE_PCT% lss 80 (
    echo Warning: Coverage is below 80%% threshold
    echo Consider adding more tests to improve coverage
) else (
    echo Coverage threshold met! Good job!
)

echo.
echo Coverage analysis completed successfully!
