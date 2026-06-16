## pdf_highlights_to_obsidian.py
─────────────────────────────
Extracts highlighted annotations from a Calibre PDF and writes a
structured Markdown note to your Obsidian vault.
 
### Usage:
    python3 pdf_highlights_to_obsidian.py <path/to/book.pdf> <path/to/obsidian/vault>
 
### Optional flags:
    --folder FOLDER   Sub-folder inside vault (default: "Book Highlights")
    --dry-run         Print the note to stdout without writing to disk
 
Highlight colour tags (customisable at the bottom of this file):
    🟡 Yellow  – Key idea
    🟢 Green   – Agree / Important
    🔴 Red     – Disagree / Question
    🔵 Blue    – Reference / Citation
    🟣 Purple  – Vocabulary / Definition
    🟠 Orange  – Action item
    ⬜ Other   – Uncategorised
