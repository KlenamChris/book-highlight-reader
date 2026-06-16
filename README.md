# 🔮 Boo Lighter (Calibre, Acrobat & Preview to Obsidian Sync)

An automated Python synchronization pipeline that extracts your book highlights from **Calibre** (EPUB/MOBI), **Acrobat Reader** and **macOS Preview** (PDFs), safely exporting them as formatted markdown notes straight into your Obsidian Vault.

---

## 🏛️ Vault Folder Target
All highlights are automatically formatted, tagged, and delivered to your designated Obsidian research folder:
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/{OBSIDIAN_VAULT_FOLDER}`

---

## 🛠️ Project Structure & Architecture

The project splits the sync engines because of how different e-book formats save annotation metadata:

1. **`cali_to_obsidian.py`**: Extracts native highlights, notes, and bookmarks written inside the built-in **Calibre E-book Viewer**. Run this using Calibre's internal Python engine.
2. **`mac_preview_to_obsidian.py`**: Directly scans binary PDF files to extract text highlights added via **Mac's native Preview app**. Run this using your system's standard Python engine.
3. **`adobe_to_obsidian.py`**: same as the `mac_preview_to_obsidian.py`
---

## ⚙️ Prerequisites & Setup

### 1. Python Libraries (System Environment)
The PDF scanner requires the `PyMuPDF` framework to look underneath the highlight bounding coordinates of macOS Preview files. Install it using terminal:
```bash
uv add pymupdf
```

### 2. Configure Your System Paths
Open both Python scripts and verify the variables at the top map correctly to your machine:
```python
CALIBRE_LIBRARY = os.path.expanduser("~/Calibre Library")
OBSIDIAN_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/{OBSIDIAN_VAULT_FOLDER}"
)
```

---

## 🚀 Execution Instructions

⚠️ **Crucial Rule:** Always completely quit the Calibre Desktop App and close open Preview windows before running sync tasks to prevent database locking errors.

### Syncing EPUB/MOBI Highlights (Calibre Viewer)
Because Calibre stores its application engine inside a closed container, you must call the internal `calibre-debug` binary instead of standard system Python:

```bash
/Applications/calibre.app/Contents/MacOS/calibre-debug -e cali_to_obsidian.py
```

### Syncing PDF Highlights (Mac Preview)
Since this script acts as a localized file crawler targeting the metadata records embedded directly inside document binaries, run it through your regular Mac system shell:

```bash
uv run python3 mac_preview_to_obsidian.py
```

---

## 📦 Output Markdown Format
Each book generates a distinct note containing interactive frontmatter layout configurations designed to interact seamlessly with Obsidian plugins like Dataview:

```markdown
---
title: "The Book Title"
author: "Author Name"
type: preview-highlights
tags: [pdf-highlights]
---

# The Book Title
**Author:** Author Name

## Highlights from Preview

> This is a captured piece of wisdom from your reading session.
```

---

## 📝 Troubleshooting & Validation Tips
* **Duplicate Folder Created:** If running the script spawns a new folder instead of writing inside your live vault, ensure the path string strictly includes the `/Documents/` sub-folder configuration masked by Apple's iCloud cloud container.
* **Command Not Found:** If pointing directly to the `/Applications/...` line throws paths errors, ensure Calibre is installed inside your default macOS applications storage directory.
* **Command Not Found:** If pointing directly to the `/Applications/...` line throws paths errors, ensure Calibre is installed inside your default macOS applications storage directory.

---

## 🏎️ Optimized Unified Sync Engine (`sync.sh`)

Instead of running three separate terminal commands every time you finish a reading session, you can execute the master orchestration shell script `sync.sh`. This script sequentially runs all three engines while safely validating background processes.

### 1. Make the Script Executable
Before firing up the script for the first time, give your macOS shell explicit permission to run it:
```bash
chmod +x sync.sh
```

### 2. Run the Complete Pipeline
Simply call the script from your project root directory:
```bash
./sync.sh
```

---

## 🧪 Advanced `uv` Integration (PEP 723)

To ensure this project remains completely self-contained and reproducible without altering your global Mac environment, both `mac_preview_to_obsidian.py` and `adobe_to_obsidian.py` contain inline PEP 723 dependency metadata headers:

```python
# /// script
# dependencies = [
#   "pymupdf",
# ]
# ///
```

When you execute commands like `uv run adobe_to_obsidian.py`, `uv` instantly provisions an isolated, transient environment, downloads `PyMuPDF`, caches it, and executes your code instantly without needing local python virtual environments (`.venv`).

---

## 📄 License
This project is open-source and available under the terms of the [MIT License](LICENSE).
