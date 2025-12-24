Installation and Setup
======================

Mythril 2.0 can be set up using different methods.

**************
PyPI on Windows
**************

**Prerequisites**

Before installing Mythril 2.0 on Windows, ensure you have:

1. **Python 3.7 or higher**: Download from `python.org <https://www.python.org/downloads/windows/>`_
2. **Microsoft C++ Build Tools**: Required for compiling native dependencies

   - Install `Microsoft C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_
   - Or install Visual Studio with C++ development tools

3. **Solidity Compiler (solc)**: 

   **Option 1: Using npm (Recommended)**
   
   .. code-block:: batch
   
      # Install Node.js from https://nodejs.org/
      npm install -g solc
   
   **Option 2: Using Chocolatey**
   
   .. code-block:: batch
   
      # Install Chocolatey from https://chocolatey.org/install
      choco install solidity
   
   **Option 3: Manual Installation**
   
   - Download solc from `Solidity releases <https://github.com/ethereum/solidity/releases>`_
   - Add the executable to your PATH

**Installation**

.. code-block:: batch

   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install mythril2
   pip install mythril2
   
   # Verify installation
   myth2 version

**Troubleshooting Windows Installation**

- **Error: Microsoft Visual C++ 14.0 is required**
  
  Install Microsoft C++ Build Tools as mentioned in prerequisites.

- **Error: 'solc' is not recognized**
  
  Ensure Solidity compiler is installed and added to your PATH.

- **Permission errors during installation**
  
  Run Command Prompt as Administrator or use virtual environments:
  
  .. code-block:: batch
  
     python -m venv mythril2_env
     mythril2_env\Scripts\activate
     pip install mythril2

**************
PyPI on Mac OS
**************

.. code-block:: bash

   brew update
   brew upgrade
   brew tap ethereum/ethereum
   brew install solidity
   pip3 install mythril2


**************
PyPI on Ubuntu
**************

.. code-block:: bash

   # Update
   sudo apt update

   # Install solc
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:ethereum/ethereum
   sudo apt install solc

   # Install libssl-dev, python3-dev, and python3-pip
   sudo apt install libssl-dev python3-dev python3-pip

   # Install mythril2
   pip3 install mythril2
   myth2 version


******
Docker
******

All Mythril 2.0 releases are published to DockerHub as Docker images under the :code:`mythril2/myth2` name.

After installing `Docker CE <https://docs.docker.com/install/>`_:

   .. code-block:: bash

      # Pull the latest release of mythril2/myth2
      $ docker pull mythril2/myth2

Use :code:`docker run mythril2/myth2` the same way you would use the :code:`myth2` command

   .. code-block:: bash

      docker run mythril2/myth2 --help
      docker run mythril2/myth2 disassemble -c "0x6060"

To pass a file from your host machine to the dockerized Mythril 2.0, you must mount its containing folder to the container properly. For :code:`contract.sol` in the current working directory, do:

   **Linux/macOS:**
   
    .. code-block:: bash

       docker run -v $(pwd):/tmp mythril2/myth2 analyze /tmp/contract.sol
   
   **Windows (Command Prompt):**
   
   .. code-block:: batch

      docker run -v %cd%:/tmp mythril2/myth2 analyze /tmp/contract.sol
   
   **Windows (PowerShell):**
   
   .. code-block:: powershell

      docker run -v ${PWD}:/tmp mythril2/myth2 analyze /tmp/contract.sol

********************
Development Setup
********************

For development on Windows:

.. code-block:: batch

   # Clone the repository
   git clone https://github.com/avaloki108/mythril2.0.git
   cd mythril2.0
   
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   
   # Run tests (cross-platform)
   python run_tests.py
   
   # Or use batch script
   run_tests.bat
   
   # Run coverage
   python run_coverage.py
   
   # Or use batch script
   run_coverage.bat
