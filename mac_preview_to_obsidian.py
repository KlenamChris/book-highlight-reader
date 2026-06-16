import os
import re
import sqlite3

import fitz  # PyMuPDF

# ==================== CONFIGURATION ====================
CALIBRE_LIBRARY = os.path.expanduser("~/Calibre Library")

OBSIDIAN_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/STUDENT VAULT/Grimoire✍🏼"
)
# =======================================================


def sanitize_filename(filename):
    return re.sub(r'[\/*?:"<>|]', "", filename).strip()


def get_calibre_pdfs():
    """Queries Calibre's database to safely grab metadata for PDF formats."""
    db_path = os.path.join(CALIBRE_LIBRARY, "metadata.db")
    if not os.path.exists(db_path):
        print(f"❌ Error: Could not find metadata.db at {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT b.id, b.title, group_concat(a.name, ', '), b.path, d.name
    FROM books b
    JOIN data d ON b.id = d.book
    JOIN books_authors_link bal ON b.id = bal.book
    JOIN authors a ON bal.author = a.id
    WHERE d.format = 'PDF'
    GROUP BY b.id
    """
    cursor.execute(query)
    books = cursor.fetchall()
    conn.close()
    return books


def extract_preview_highlights(pdf_path):
    """Scans for highlights saved via macOS Preview's unique annotation metadata."""
    highlights = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            for annot in page.annots():
                # 8 represents a traditional Highlight Annotation block
                if annot.type[0] == 8:
                    # Mac's Preview copies highlighted strings into the content info property
                    text = annot.info.get("content", "").strip()

                    # Fallback fallback mechanism: If Preview didn't write to content,
                    # cross-examine the text coordinates directly on the document canvas.
                    if not text:
                        text = page.get_text("text", clip=annot.rect).strip()

                    if text:
                        highlights.append(text)
        doc.close()
    except Exception as e:
        print(f"   ⚠️ Error processing file: {e}")
    return highlights


def main():
    if not os.path.exists(OBSIDIAN_VAULT):
        os.makedirs(OBSIDIAN_VAULT)

    print("🔮 Opening the Grimoire... Scanning Calibre Library for PDFs...")
    books = get_calibre_pdfs()
    print(f"📚 Found {len(books)} PDF records. Pulling Preview highlights...\n")

    synced_count = 0
    for book_id, title, author, relative_path, filename in books:
        pdf_path = os.path.join(CALIBRE_LIBRARY, relative_path, filename + ".pdf")

        if not os.path.exists(pdf_path):
            continue

        highlights = extract_preview_highlights(pdf_path)

        if highlights:
            safe_title = sanitize_filename(title)
            md_filename = f"{safe_title}.md"
            md_filepath = os.path.join(OBSIDIAN_VAULT, md_filename)

            content = [
                "---",
                f'title: "{title}"',
                f'author: "{author}"',
                "type: preview-highlights",
                "tags: [pdf-highlights]",
                "---",
                f"# {title}",
                f"**Author:** {author}\n",
                "## Highlights from Preview\n",
            ]

            for hl in highlights:
                content.append(f"> {hl}\n")

            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(content))

            print(f'✅ Synced: "{title}" -> {len(highlights)} highlights copied.')
            synced_count += 1

    print(
        f"\n✨ Process complete! {synced_count} books synced directly into your Grimoire."
    )


if __name__ == "__main__":
    main()
