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
Don't just say *"LGTM"* and approve.

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

#### In the terminal
1. Go to the `docs/` directory
2. Run `$ pdflatex -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory=./build final-report.tex`

## Name
Avonic SP

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Izzy van der Giessen, Petr Khartskhaev, Yehor Kozyr, Borislav Semerdzhiev, Ivan Smilenov
