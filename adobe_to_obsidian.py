import os
import re
import sqlite3

import fitz  # This is PyMuPDF

# ==================== CONFIGURATION ====================
# Path to your Calibre Library folder
CALIBRE_LIBRARY = os.path.expanduser("~/Calibre Library")

# Path to your Obsidian Vault
OBSIDIAN_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/STUDENT VAULT/Grimoire✍🏼"
)
# =======================================================


def sanitize_filename(filename):
    return re.sub(r'[\/*?:"<>|]', "", filename).strip()


def get_calibre_books():
    """Reads Calibre's metadata.db to find all PDF books."""
    db_path = os.path.join(CALIBRE_LIBRARY, "metadata.db")
    if not os.path.exists(db_path):
        print(f"❌ Error: Could not find metadata.db at {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get Book ID, Title, Author, Path, and Filename for all PDFs
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


def extract_highlights_from_pdf(pdf_path):
    """Opens a PDF and extracts text that has been highlighted."""
    highlights = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            # Loop through all annotations on the page
            annot = page.first_annot
            while annot:
                if annot.type[0] == 8:  # 8 is the code for 'Highlight'
                    # Extract the text under the highlight area
                    text = page.get_text("text", clip=annot.rect).strip()
                    if text:
                        highlights.append(text)
                annot = annot.next
        doc.close()
    except Exception as e:
        print(f"   ⚠️ Error reading PDF: {e}")

    return highlights


def main():
    if not os.path.exists(OBSIDIAN_VAULT):
        os.makedirs(OBSIDIAN_VAULT)

    print("🔍 Scanning Calibre Library for PDFs...")
    books = get_calibre_books()
    print(f"📚 Found {len(books)} PDF books. Checking for highlights...\n")

    for book_id, title, author, relative_path, filename in books:
        # Construct the full path to the PDF file
        pdf_path = os.path.join(CALIBRE_LIBRARY, relative_path, filename + ".pdf")

        if not os.path.exists(pdf_path):
            continue

        # Extract highlights
        highlights = extract_highlights_from_pdf(pdf_path)

        if highlights:
            # Create Markdown Content
            safe_title = sanitize_filename(title)
            md_filename = f"{safe_title}.md"
            md_filepath = os.path.join(OBSIDIAN_VAULT, md_filename)

            content = []
            content.append("---")
            content.append(f'title: "{title}"')
            content.append(f'author: "{author}"')
            content.append("type: pdf-highlights")
            content.append("---")
            content.append(f"# {title}")
            content.append(f"**Author:** {author}\n")
            content.append("## PDF Highlights\n")

            for hl in highlights:
                content.append(f"> {hl}\n")

            # Write to Obsidian
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(content))

            print(f"✅ Synced: {title} ({len(highlights)} highlights)")

    print("\n✨ All Done!")


if __name__ == "__main__":
    main()
