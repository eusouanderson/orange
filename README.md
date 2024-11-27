# Orange A Program to Optimize Windows 10 for Gaming

## Overview

Orange is a program that optimizes the Windows 10 operating system for gaming by helping disable unnecessary processes while gaming.

---

#### -- Development Version 0.1.1 --

---

## Features

### Buttons

#### Investigate

Used to investigate your operating system by reading all active processes on your computer.

#### Graph

Used to open a real-time performance graph showing the resource consumption of your system.

Still under development.

#### Optimize

Optimizes your operating system by closing unnecessary processes for gaming.

#### ForceFPS

Used to force the maximum performance of your computer.

Still under development.

#### Internet Control

Provides a small control panel where you can optimize your internet connection and make some adjustments.

Still under development.

#### Brute Ping

Used to calculate the ping.

Still under development.

---

## Tools

1. Language: [Python](https://www.python.org/)



---

## Get Started

1. Download the orange folder along with its code.
2. Add the necessary libraries for your project in the [requirements.txt](./requirements.txt) file.
3. I'm using Linux Ubuntu 22.04.2 LTS.

---

## Test Locally

To test locally, execute the following command in the directory:

### On Linux or Windows:

```bash
./start.sh
```

Running Scripts
There are .sh scripts available to help with running and building the project for both Linux and Windows systems.

Running the Project
Linux: Use the start.sh script to run the project on Linux.

Run the following command:

bash
Copiar código
./start.sh
Windows: A similar script can be executed for Windows systems (e.g., start_windows.bat) to launch the project.

Building the Project
You can build the project for both Linux and Windows using the build.sh script, which will create a packaged version of the program.

For Linux:
To build for Linux, use the following command:

bash
Copiar código
./build.sh linux
This will create a build suitable for deployment on Linux systems.

For Windows:
To build for Windows, use the following command:

bash
Copiar código
./build.sh windows
This will generate a build suitable for deployment on Windows systems.

Poetry as Dependency Manager
The project uses Poetry as a package manager to handle dependencies.

Installing Poetry
To install Poetry, follow these steps:

## Install Poetry by running the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Make sure to add Poetry to your system's PATH.

Installing Dependencies with Poetry
After setting up Poetry, you can install all the necessary dependencies by running the following command:

```bash
poetry install
```

Note
Once I finish creating all the buttons, I will create the compiled file.





Developed by Anderson B.O.B

## Directory Tree

```bash
.
├── Dockerfile
├── Docs
│   └── style_docs
│       └── styles.md
├── LICENSE
├── README.md
├── build.sh
├── config.json
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── assets
│   │   └── images
│   │       ├── background
│   │       │   ├── 1.jpg
│   │       │   ├── 2.jpg
│   │       │   ├── 3.jpg
│   │       │   ├── 4.jpg
│   │       │   └── 5.jpg
│   │       ├── orange.png
│   │       └── screenshots
│   │           ├── orange.png
│   │           ├── screenshot1.png
│   │           ├── screenshot2.png
│   │           ├── screenshot3.png
│   │           ├── screenshot4.png
│   │           ├── screenshot7.png
│   │           └── screenshot8.png
│   ├── build
│   │   ├── build
│   │   │   ├── Orange
│   │   │   │   ├── Analysis-00.toc
│   │   │   │   ├── EXE-00.toc
│   │   │   │   ├── Orange.pkg
│   │   │   │   ├── PKG-00.toc
│   │   │   │   ├── PYZ-00.pyz
│   │   │   │   ├── PYZ-00.toc
│   │   │   │   ├── base_library.zip
│   │   │   │   ├── localpycs
│   │   │   │   │   ├── pyimod01_archive.pyc
│   │   │   │   │   ├── pyimod02_importers.pyc
│   │   │   │   │   ├── pyimod03_ctypes.pyc
│   │   │   │   │   └── struct.pyc
│   │   │   │   ├── warn-Orange.txt
│   │   │   │   └── xref-Orange.html
│   │   │   └── main
│   │   │       ├── Analysis-00.toc
│   │   │       ├── EXE-00.toc
│   │   │       ├── PKG-00.toc
│   │   │       ├── PYZ-00.pyz
│   │   │       ├── PYZ-00.toc
│   │   │       ├── base_library.zip
│   │   │       ├── localpycs
│   │   │       │   ├── pyimod01_archive.pyc
│   │   │       │   ├── pyimod02_importers.pyc
│   │   │       │   ├── pyimod03_ctypes.pyc
│   │   │       │   └── struct.pyc
│   │   │       ├── main.pkg
│   │   │       ├── warn-main.txt
│   │   │       └── xref-main.html
│   │   ├── build.py
│   │   ├── dist
│   │   │   └── Orange
│   │   └── specs
│   │       ├── Orange.spec
│   │       └── main.spec
│   ├── collor.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── background.cpython-312.pyc
│   │   │   ├── choose.cpython-312.pyc
│   │   │   ├── clean.cpython-312.pyc
│   │   │   ├── save.cpython-312.pyc
│   │   │   ├── save_user_config.cpython-312.pyc
│   │   │   └── themes.cpython-312.pyc
│   │   ├── background.py
│   │   ├── choose.py
│   │   ├── clean.py
│   │   ├── config.json
│   │   ├── save_user_config.py
│   │   └── themes.py
│   ├── core
│   │   ├── __pycache__
│   │   │   └── reload.cpython-312.pyc
│   │   ├── main.py
│   │   └── reload.py
│   ├── data
│   │   └── __init__.py
│   ├── graphic
│   │   └── __init__.py
│   ├── test.py
│   └── theme
│       └── __init__.py
└── start.sh

```