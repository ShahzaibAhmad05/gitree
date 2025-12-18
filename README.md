# PrintStruct

A Python CLI tool for printing the structure of your project in a visually easy-to-read format. Respects `.gitignore` files when present so ignored files and folders are omitted from the output.

Example output:
````
PrintStruct
├─ LICENSE
├─ pyproject.toml
├─ README.md
├─ requirements.txt
└─ structure.py
````

<br>

## Quick Setup

- Clone this repository:

````
git clone https://github.com/shahzaibahmad05/printstruct
````

- Install the project on your system using pip:

````
pip install -r requirements.txt
````

- Open a terminal in any project (any time) and run:

````
structure
````

This will print the whole structure of the repository as shown.

**Note:** You can also just type:
 
````
structure <project_directory_path>
````

in any terminal to get the structure of the project printed.

<br>

## Useful CLI args

*Other than the directory path*, here are some CLI args you can use with this script:

**--max-depth**

Limits how deep the directory recursion gets. For example, `--max-depth 1` should print the files and folders directly visible from the project root.

**--all** or **-a**

Includes hidden files and folders in the results. This does not override gitignore directives.

**--ignore** 

Adds further files or folders to ignore.

**--gitignore-depth**

Controls how deep the script looks for gitignore files. For example, `--gitignore-depth 0` should include only the gitignore present at the project root.

<br>

## Contributions

Please feel free to open issues or submit pull requests to improve formatting, add features (e.g. colorized output), or add tests.
