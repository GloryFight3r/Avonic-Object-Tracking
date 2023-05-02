# 11C - Avonic

## Rules

### Use Conventional Commits
[Reference here](https://www.conventionalcommits.org/en/v1.0.0/)

## The Report

### Editing
Create a new chapter in `chapters` and end it with `.tex`. Edit that file (no need to do headers/boilerplate, that's already done).

### Compiling (Linux or maybe MacOS)

#### In IntelliJ/PyCharm
1. Go to Configurations -> Edit configurations
2. Add New Configuration -> LaTeX
3. Configure it similar to this (obviously you can choose your own pdf viewer)
   [configuration](https://cdn.discordapp.com/attachments/1100381425674506282/1100404222769516626/image.png)
4. Click Apply/Ok
5. Run this configuration

#### In the terminal
1. Go to the `docs/` directory
2. Run `$ pdflatex -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory=./build final-report.tex`

## Installing the project

### Using `build`

1. `$ python -m build`
2. `$ pip install dist/avonic_speaker_tracker-<version and other info>.whl`

### Without `build`

To install the base package:

`$ pip install .`

To install the test packages, too:

`$ pip install -e '.[test]'`

## Running

`$ flask -app avonic-speaker-tracker run`