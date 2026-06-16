import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required. \nInstall it with: uv add pymupdf")

# -------------- Color mapping --------------------
# Each entry: (R, G, B) normalized 0-1 -> (emoji, label)
# Tweak thresholds or add entries to match your reader's palette.


def classify_color(
    rgb: list[float],
) -> tuple[str, str]:  # FIX 1: was "clasify_color" (typo)
    """Map an RGB triple (0-1 floats) to an emoji + label."""
    if not rgb:
        return "⬜", "Other"

    r, g, b = rgb

    # Dominant channel heuristics
    if r > 0.7 and g > 0.7 and b < 0.4:  # Yellow
        return "🟡", "Key Idea"
    if g > 0.6 and r < 0.5 and b < 0.5:  # Green
        return "🟢", "Important"
    if r > 0.7 and g < 0.4 and b < 0.4:  # Red
        return "🔴", "Question"
    if b > 0.6 and r < 0.4 and g < 0.5:  # Blue
        return "🔵", "Reference"
    if r > 0.5 and b > 0.5 and g < 0.4:  # Purple / Magenta
        return "🟣", "Vocabulary"
    if r > 0.7 and g > 0.4 and b < 0.3:  # Orange
        return "🟠", "Action"
    return "⬜", "Other"


#  ---------- Core extraction -------------
def extract_highlights(pdf_path: Path) -> list[dict]:
    """Return a list of highlight dicts sorted by page then position."""
    doc = fitz.open(str(pdf_path))
    highlights = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_num += 1  # convert to 1-based
        for annot in page.annots():
            # Type 8 = Highlight, also accept Underline (9), Squiggly (10), StrikeOut (11)
            if annot.type[0] not in (8, 9, 10, 11):
                continue

            # ----------- Extract text covered by the annotation -----------------
            annot_rect = annot.rect
            words = page.get_text("words")  # (x0, y0, x1, y1, text, block, line, word)

            highlighted_words = [
                w[4] for w in words if fitz.Rect(w[:4]).intersects(annot_rect)
            ]
            text = " ".join(highlighted_words).strip()

            if not text:
                # Fallback: grab all text in the rect region
                text = page.get_text("text", clip=annot_rect).strip()

                if not text:
                    continue  # skip empty annotations

            # ------------ Colour -------------  # FIX 2: moved inside the for annot loop
            colors = annot.colors
            stroke = list(colors.get("stroke") or colors.get("fill") or [])
            emoji, label = classify_color(stroke)

            # ------------ Author / note (if the reader added a comment)  # FIX 3: moved inside loop
            note = annot.info.get("content", "").strip()

            highlights.append(
                {  # FIX 4: moved inside the for annot loop
                    "page": page_num,
                    "y": annot_rect.y0,  # for secondary sort within page
                    "text": text,
                    "emoji": emoji,
                    "label": label,
                    "note": note,
                    "rgb": stroke,
                }
            )

    doc.close()  # FIX 5: moved outside both for loops
    highlights.sort(
        key=lambda h: (h["page"], h["y"])
    )  # FIX 6: moved outside both for loops
    return highlights  # FIX 7: moved outside both for loops


# --------------- Markdown generation -----------------------
def build_markdown(book_title: str, pdf_path: Path, highlights: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(highlights)

    # YAML front-matter (Obsidian-friendly)
    lines = [
        "---",
        f'title: "Highlights - {book_title}"',
        f'source: "{pdf_path.name}"',
        f'created: "{now}"',
        f"total_highlights: {total}",
        "tags: [book-highlights]",
        "---",
        "",
        f"# 📚 {book_title}",
        f"> Extracted **{total}** highlight(s) on {now}",
        f"> Source: `{pdf_path.name}`",
        "",
        "---",
        "",
        "## Colour legend",
        "| Emoji | Category |",
        "|-------|----------|",
        "| 🟡 | Key Idea |",
        "| 🟢 | Important |",
        "| 🔴 | Question |",
        "| 🔵 | Reference |",
        "| 🟣 | Vocabulary |",
        "| 🟠 | Action |",
        "| ⬜ | Other |",
        "",
        "---",
        "",
        "## Highlights",
        "",
    ]
    current_page = None
    for h in highlights:  # FIX 8: loop body was dedented out of the loop
        if h["page"] != current_page:
            current_page = h["page"]
            lines.append(f"### Page {current_page}")
            lines.append("")

        # Blockquote for the highlighted text
        quoted = re.sub(r"\n+", " ", h["text"])  # collapse newlines
        lines.append(f"> {h['emoji']} **{h['label']}** — *p. {h['page']}*")
        lines.append(f"> {quoted}")

        if h["note"]:
            lines.append(f">\n> 💬 *{h['note']}*")

        lines.append("")

    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────  # FIX 9: unindented out of build_markdown


def slugify(text: str) -> str:
    """Turn a book title into a safe filename."""
    text = re.sub(r"[^\w\s-]", "", text).strip()
    return re.sub(r"[\s]+", "_", text)


def main():
    parser = argparse.ArgumentParser(
        description="Extract PDF highlights → Obsidian Markdown note"
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("vault", help="Path to your Obsidian vault root")
    parser.add_argument(
        "--folder",
        default="Book Highlights",
        help="Sub-folder inside the vault (default: 'Book Highlights')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the note to stdout; do not write to disk",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    vault_path = Path(args.vault).expanduser().resolve()

    if not pdf_path.exists():
        sys.exit(f"❌  PDF not found: {pdf_path}")
    if not vault_path.exists() and not args.dry_run:
        sys.exit(f"❌  Vault path not found: {vault_path}")

    # Use the PDF stem as the book title (Calibre usually names files well)
    book_title = pdf_path.stem.replace("_", " ").replace("-", " ").title()

    print(f"📖  Book   : {book_title}")
    print(f"📄  PDF    : {pdf_path}")
    print(f"🗂️   Vault  : {vault_path}")
    print()

    print("⏳  Extracting highlights …")
    highlights = extract_highlights(pdf_path)
    print(f"✅  Found {len(highlights)} highlight(s)")

    if not highlights:
        print("ℹ️   Nothing to write — make sure the PDF has annotation highlights.")
        return

    # ── Colour breakdown ────────────────────────────────────────────────────
    from collections import Counter

    counts = Counter(h["label"] for h in highlights)
    for label, n in sorted(counts.items()):
        print(f"   {n:>3}×  {label}")
    print()

    markdown = build_markdown(book_title, pdf_path, highlights)

    if args.dry_run:
        print("─" * 60)
        print(markdown)
        return

    # ── Write to vault ──────────────────────────────────────────────────────
    output_dir = vault_path / args.folder
    output_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix} – {slugify(book_title)}.md"
    output_file = output_dir / filename

    output_file.write_text(markdown, encoding="utf-8")
    print(f"📝  Note saved to:\n    {output_file}")


if __name__ == "__main__":
    main()
