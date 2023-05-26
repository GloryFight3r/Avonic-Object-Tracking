# 11C - Avonic

## Rules

### General, non-technology-related

**PLEASE!!** Be available from 9-17 every workday. This means that you have to be able to read messages from all teammates/the TA/Coach/Client on every platform during these specified hours. You should also reply to the message unless you have something extremely important to do at that moment, but do try to get back ASAP.

### Code

Everyone should follow the Test Driven Development practices - ie. write tests for every method.

### Commits

Do **NOT** commit to `dev` branch directly unless there is some critical bug that needs fixing ASAP.

### Requirements

Each requirement should have one of the MoSCoW labels attached.

### Issues

Each issue MUST have a definiton of done.

Each issue should have a milestone.

Each issue's weight should roughly depict its perceived difficulty/how long it will take. Categories are:

1. Hours
2. Days
3. Weeks
4. Months

### Merge requests

Each merge request (for a feature) should include both tests and documentation for any new code.

### Code review

At least two people should review a merge request. Everyone should try to review everything.

**ALWAYS** look at the entirety of the code, and try to find at least one problem with the code (there will always be at least one).
Don't just say _"LGTM"_ and approve.

A reviewer should always compare the code with the definition of done and see if it meets it.

### Use Conventional Commits

Basically, prepend each commit message with `fix:` for fixes, `feat:` for features, `docs:` for docs, `test:` for tests.
[Reference here](https://www.conventionalcommits.org/en/v1.0.0/).

## The Report

### Editing

Create a new chapter in `chapters` and end it with `.tex`. Edit that file (no need to do headers/boilerplate, that's already done).

### Compiling (Linux or maybe MacOS)

#### In IntelliJ/PyCharm

1. Go to Configurations -> Edit configurations
2. Add New Configuration -> LaTeX
3. Configure it similar to this (obviously you can choose your own pdf viewer)
   ![image](https://cdn.discordapp.com/attachments/1100381425674506282/1100404222769516626/image.png)
4. Click Apply/Ok
5. Run this configuration

## Badges
`dev branch:` ![dev pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/public/badges/pylint.svg?job=pylint) [dev pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/public/badges/pylint.svg?job=pylint)

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
