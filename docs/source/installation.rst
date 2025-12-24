Installation and Setup
======================

Mythril can be setup using different methods.

**************
PyPI on Windows
**************

**Prerequisites**

Before installing Mythril on Windows, ensure you have:

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
   
   # Install mythril
   pip install mythril
   
   # Verify installation
   myth version

**Troubleshooting Windows Installation**

- **Error: Microsoft Visual C++ 14.0 is required**
  
  Install Microsoft C++ Build Tools as mentioned in prerequisites.

- **Error: 'solc' is not recognized**
  
  Ensure Solidity compiler is installed and added to your PATH.

- **Permission errors during installation**
  
  Run Command Prompt as Administrator or use virtual environments:
  
  .. code-block:: batch
  
     python -m venv mythril_env
     mythril_env\Scripts\activate
     pip install mythril

**************
PyPI on Mac OS
**************

.. code-block:: bash

   brew update
   brew upgrade
   brew tap ethereum/ethereum
   brew install solidity
   pip3 install mythril


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

   # Install mythril
   pip3 install mythril
   myth version


******
Docker
******

All Mythril releases, starting from v0.18.3, are published to DockerHub as Docker images under the :code:`mythril/myth` name.

After installing `Docker CE <https://docs.docker.com/install/>`_:

   .. code-block:: bash

      # Pull the latest release of mythril/myth
      $ docker pull mythril/myth

Use :code:`docker run mythril/myth` the same way you would use the :code:`myth` command

   .. code-block:: bash

      docker run mythril/myth --help
      docker run mythril/myth disassemble -c "0x6060"

To pass a file from your host machine to the dockerized Mythril, you must mount its containing folder to the container properly. For :code:`contract.sol` in the current working directory, do:

   **Linux/macOS:**
   
    .. code-block:: bash

       docker run -v $(pwd):/tmp mythril/myth analyze /tmp/contract.sol
   
   **Windows (Command Prompt):**
   
   .. code-block:: batch

      docker run -v %cd%:/tmp mythril/myth analyze /tmp/contract.sol
   
   **Windows (PowerShell):**
   
   .. code-block:: powershell

      docker run -v ${PWD}:/tmp mythril/myth analyze /tmp/contract.sol

********************
Development Setup
********************

For development on Windows:

.. code-block:: batch

   # Clone the repository
   git clone https://github.com/ConsenSys/mythril.git
   cd mythril
   
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
