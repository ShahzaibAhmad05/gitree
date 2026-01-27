# gitree 🌴

**An upgrade from "ls" for developers. An open-source tool to analyze folder structures and to provide code context to LLMs. Published on PyPi**

<br>

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/shahzaibahmad05/gitree?logo=github)](https://github.com/shahzaibahmad05/gitree/stargazers)
[![PyPI](https://img.shields.io/pypi/v/gitree?logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/gitree/)
[![GitHub forks](https://img.shields.io/github/forks/shahzaibahmad05/gitree?color=blue)](https://github.com/shahzaibahmad05/gitree/network/members)
[![Contributors](https://img.shields.io/github/contributors/shahzaibahmad05/gitree)](https://github.com/shahzaibahmad05/gitree/graphs/contributors)
[![Issues closed](https://img.shields.io/github/issues-closed/shahzaibahmad05/gitree?color=orange)](https://github.com/shahzaibahmad05/gitree/issues)
[![PRs closed](https://img.shields.io/github/issues-pr-closed/shahzaibahmad05/gitree?color=yellow)](https://github.com/shahzaibahmad05/gitree/pulls)

</div>


> [!NOTE]
> Instead of the full-name "gitree", you may use "gt" to call this tool

---

## 📦 Installation

Install using **pip** (python package manager):

```bash
# Install the latest version using pip
pip install gitree

# Alternatively, use pipx
pipx install gitree

# to update gitree
pip install -U gitree
```

---

### 💡 Getting Started

Open a terminal in any project and run:

```bash
# This should print the structure of the current working directory
gitree

# OR use this short alias
gt
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/default.jpg"
  alt="gitree demo"
  width="600"
/>

Now try using `--full` for printing full directory structure:

```bash
gt --full

# OR -f as alias for --full
gt -f
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/full_output.jpg"
  alt="gitree demo"
  width="600"
/>

Try using `--emoji` for better visuals:

```
gt --full --emoji

# You can also use -f and -e together like this
gt -fe
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/full_output_emoji.jpg"
  alt="gitree demo"
  width="600"
/>

### 🧠 This is where it gets useful

For copying all code files in your project, with interactive selection:

```bash
gt --code --copy --interactive

# OR alternaitvely, using short aliases
# -i for interactive, -c for copy, -f for full, -t for types
gt --code -ci
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/interactive.jpg"
  alt="gitree demo"
  width="600"
/>

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/copy_code_interactive.jpg"
  alt="gitree demo"
  width="600"
/>

For zipping the whole project (use `-g` to respect gitignore):

```bash
# creates project.zip in the same directory
gt --zip project

# OR alternatively, using alias
gt -z project

# To respect gitignore rules when zipping, add -g flag
gt -gz project

# To zip only the code files use --code
gt -z project --code
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/zipping.jpg"
  alt="gitree demo"
  width="600"
/>

For dumping the whole project into a single file:

```bash
# Creates project.txt in the directory from where gt is run
# Default format for export is tree
gt --export project --format tree

# OR using aliases
gt -x project --format tree

# OR use other formats
gt -fx project --format json
gt -fx project --format md

# OR using --fmt alias
gt -fx project --fmt json
```

<img
  src="https://raw.githubusercontent.com/shahzaibahmad05/shahzaibahmad05/main/gallery/gitree/export.jpg"
  alt="gitree demo"
  width="600"
/>

---

## 🧩 How it works

```
    ╭────────────────────────────╮
    │           Start            │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │      Argument Parsing      │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │  Files/Folders Selection   │
    ╰────────────────────────────╯
                  │
                  ▼
    ╭────────────────────────────╮
    │   Interactive Selection    │
    │      (only if used)        │
    ╰────────────────────────────╯
            │
            ├─────────────────────────┐
            │                         │
            ▼                         ▼
    ╭─────────────────╮    ╭─────────────────────╮
    │ Zipping Service │    │   Drawing Service   │
    ╰─────────────────╯    ╰─────────────────────╯
            │                  │
            │                  ├────────────────────┐
            │                  │                    │
            │                  ▼                    ▼
            │         ╭─────────────────╮  ╭──────────────────╮
            │         │  Copy Service   │  │  Export Service  │
            │         ╰─────────────────╯  ╰──────────────────╯
            │                  │                    │
            │                  └──────────┬─────────┘
            │                             │
            └─────────────────────────────┘
                           │
                           ▼
               ╭────────────────────────╮
               │    Output & Finish     │
               ╰────────────────────────╯

```


---

## ✨ Overall Features

| Feature                           | Description                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------- |
| **Tree Visualization** | Generate a structure for any directory for visualizing and understanding the codebase |
| **Smart File Selection** | Control what's selected by the tool with custom ignore patterns, depth limits, and item caps |
| **Interactive Selection** | Gain full control of the output by reviewing what's selected by the file selection service |
| **Copy Your Codebase** | Instantly copy the whole codebase file contents to your clipboard to paste into LLMs |
| **Multiple Export Formats** | Export your codebase contents to files using tree, json and markdown formats |
| **Zipping the Whole Project** | Create project archives (optionally respecting `.gitignore` with `-g` flag) |
| **Large/Binary Files Handling** | Automatically detects binary and large files and marks or skips them during export |


---

## ⚙️ Common Arguments

### General Options

| Argument          | Description                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `-h`, `--help`    | Show the **help message** with all available options and exit.                                                  |
| `-v`, `--version` | Display the **version number** of the tool.                                                                       |
| `--verbose`       | Enable **logger output** to the console. Helpful for **debugging**.                                             |
| `--config-user`   | Create a **default config.json** file in the current directory and open it in the **default editor**.           |
| `--no-config`     | Ignore both **user-level and global-level** `config.json` and use **default and CLI values** for configuration. |

### Semantic Flags (Quick Actions)

| Argument          | Description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `-f`, `--full`    | **Shortcut** for `--max-depth 5` - show full directory tree up to 5 levels deep.              |
| `-e`, `--emoji`   | Show **emojis** in the output for better visual clarity.                                      |
| `-i`, `--interactive` | Use **interactive mode** for manual file selection after automatic filtering.            |
| `-c`, `--copy`    | **Copy** file contents and project structure to **clipboard** (great for LLM prompts).        |
| `--code` | Include **only code extensions**            |

### Output & Export Options

| Argument          | Description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `-z`, `--zip`     | Create a **zip archive** of the given directory (respects gitignore if `-g` is used).              |
| `-x`, `--export`        | Save **project structure** along with its **contents** to a file with the format specified using `--format`. |
| `--format`, `--fmt`      | **Format output** only. Options: `tree`, `json`, `md`. Default: `tree`.                      |

<details>
<summary><h3>Full CLI Arguments List (Click to expand)</h3></summary>

### Listing Options

| Argument                     | Description                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `--max-items`                | Limit **items to be selected** per directory.                                           |
| `--max-entries`              | Limit **entries (files/dirs)** to be selected for the overall output.                   |
| `--max-depth`                | **Maximum depth** to traverse when selecting files.                                     |
| `--gitignore-depth`          | Limit depth to look for during **`.gitignore` processing**.                             |
| `-a`, `--hidden-items`, `--all`     | Show **hidden files and directories**.                                                  |
| `--exclude [pattern ...]`    | **Patterns of files** to specifically exclude.                                          |
| `--exclude-depth`            | Limit depth for **exclude patterns**.                                                   |
| `--include [pattern ...]`    | **Patterns of files** to specifically include.                                          |
| `--include-file-types`       | Include files of **certain types**.                                                     |
| `--files-first`              | Print **files before directories**.                                                     |
| `--no-color`                 | Disable **colored output**.                                                             |
| `--no-contents`              | Don't include **file contents** in export/copy.                                         |
| `--no-contents-for [path ...]` | Exclude **contents for specific files** for export/copy.                              |
| `--max-file-size`            | **Maximum file size** in MB to include in exports (default: 1.0).                       |
| `--override-files`           | **Override existing files**.                                                            |
| `-s`, `--size`                | Show **file sizes** in the output.                                                       |

### Listing Override Options

| Argument           | Description                                |
| ------------------ | ------------------------------------------ |
| `--no-max-entries` | Disable **`--max-entries` limit**.             |
| `--no-max-items`   | Disable **`--max-items` limit**.               |
| `-g`, `--gitignore`   | Enable **`.gitignore` rules** (respects .gitignore files).             |
| `--no-files`       | Hide files (show only **directories**).        |

</details>

---


## Installation (for Contributors)

Clone the **repository**:

```bash
git clone https://github.com/ShahzaibAhmad05/gitree
```

Move into the **project directory**:

```bash
cd gitree
```

Setup a **Virtual Environment** (to avoid package conflicts):

```bash
python -m venv .venv
```

Activate the **virtual environment**:

```bash
.venv/Scripts/Activate      # on windows
.venv/bin/activate          # on linux/macOS
```

> [!WARNING]
> If you get an **execution policy error** on windows, run this:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

Install **dependencies** in the virtual environment:

```bash
pip install -r requirements.txt
```

The tool is now available as a **Python CLI** in your virtual environment.

For running the tool, type (**venv should be activated**):

```bash
gt
```

For running **unit tests** after making changes:

```bash
python -m tests
```

---

## Contributions

> [!TIP]
> This is **YOUR** tool. Issues and pull requests are always welcome.

Gitree is kept intentionally small and readable, so contributions that preserve **simplicity** and follow [Contributing Guidelines](https://github.com/ShahzaibAhmad05/gitree?tab=contributing-ov-file) are especially appreciated.
