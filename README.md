# PrintStruct

**PrintStruct** is a clean, lightweight Python CLI that prints a clean directory tree of your project **while respecting `.gitignore`** with optional zipping.

The problems it solves:

- sharing project structure in issues or pull requests
- generating clean trees for documentation
- pasting project layouts into ChatGPT / LLMs
- creating zip files for LLMs using gitignore directions.

<br>

## Quick Start (10 seconds) 

### Installation using pip (recommended):

- Run this command in your terminal:

````
pip install printstruct
````


### Usage:

- Open a terminal in any project (any time) and run:

````
prst
````

This will print the whole structure of the repository as shown. In fact, You can also just type:
 
````
prst <directory_path>
````

in any terminal to get the structure of the directory printed.

- Example usage (on windows powershell):

````
PS C:/Users/Projects/PrintStruct> prst .
````

outputs:

````
PrintStruct
├─ LICENSE
├─ pyproject.toml
├─ README.md
├─ requirements.txt
└─ structure.py
````

### For Updates:

To update the tool simply reinstall it with pip, but with the latest release version. Pip will automatically handle old version removal.


### Installation (for Contributors):

- Clone the repository (main branch):

````
git clone https://github.com/ShahzaibAhmad05/PrintStruct
````

- Move your terminal to the project

````
cd PrintStruct
````

- Install the project on your system (globally) using pip:

````
pip install -r requirements.txt
````

and Done! The tool is installed as a python script on your system.

<br>

## Useful CLI args

*Other than the directory path*, here are some CLI args you can use with this script:

**--version** or **-v**

Displays the version of the tool installed on the system.

**--zip**

Zips the project, respecting gitignores. For example, `--zip a` should create `a.zip` in the same directory having the directory contents. If zip name is not given, it defaults to a random ID.

**--max-depth**

Limits how deep the directory recursion gets. For example, `--max-depth 1` should print the files and folders directly visible from the project root.

**--all** or **-a**

Includes hidden files and folders in the results. This does not override gitignore directives.

**--ignore** 

Adds further files or folders to ignore.

**--gitignore-depth**

Controls how deep the script looks for gitignore files. For example, `--gitignore-depth 0` should include only the gitignore present at the project root.

**--no-gitignore** 

Does not respect gitignore files if this flag is given.

**--max-items**

Max number of files/folders to display in each folder, the rest is shown as `... and x more items`. For example `--max-items 5` should display only 5 items per directory. 

Default for max items is 20.

**--no-limit**

Remove the `--max-items` limiter on printing files. 

<br>

## Contributions

Please feel free to open issues or submit pull requests to improve formatting, add features (e.g. colorized output), or add tests.
