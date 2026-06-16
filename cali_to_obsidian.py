import json
import os
import re

from calibre.library import db

# ==================== CONFIGURATION ====================
# Use absolute paths to your library and Obsidian vault
CALIBRE_LIBRARY = os.path.expanduser("~/Calibre Library")
OBSIDIAN_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/STUDENT VAULT/Grimoire✍🏼"
)
# =======================================================
# Mobile\ Documents/iCloud\~md\~obsidian/Documents/STUDENT\ VAULT


def sanitize_filename(filename):
    """Removes invalid characters to prevent file system errors."""
    return re.sub(r'[\/*?:"<>|]', "", filename).strip()


def export_highlights():
    # Ensure the Obsidian output folder exists
    if not os.path.exists(OBSIDIAN_VAULT):
        os.makedirs(OBSIDIAN_VAULT)
        print(f"Created directory: {OBSIDIAN_VAULT}")

    # Connect to the Calibre Database API
    print("Connecting to Calibre library...")
    cache = db(CALIBRE_LIBRARY).new_api

    # Fetch all native viewer annotations (highlights, notes, bookmarks)
    # This retrieves standard JSON dictionaries containing highlight data
    all_annots = cache.all_annotations(annotation_type="highlight")

    if not all_annots:
        print("No highlights found in your Calibre viewer database.")
        return

    # Group highlights by Book ID first
    books_with_highlights = {}
    for entry in all_annots:
        book_id = entry.get("book_id")
        if book_id:
            if book_id not in books_with_highlights:
                books_with_highlights[book_id] = []
            books_with_highlights[book_id].append(entry)

    print(f"Processing highlights for {len(books_with_highlights)} books...")

    for book_id, annots in books_with_highlights.items():
        # Grab metadata safely via Calibre database cache
        title = cache.field_for("title", book_id) or f"Unknown Title (ID {book_id})"
        authors = cache.field_for("authors", book_id) or ["Unknown Author"]
        author_str = ", ".join(authors)

        # Structure markdown file name and frontmatter metadata
        safe_title = sanitize_filename(title)
        md_filename = f"{safe_title}.md"
        md_filepath = os.path.join(OBSIDIAN_VAULT, md_filename)

        markdown_content = []
        markdown_content.append("---")
        markdown_content.append(f'title: "{title}"')
        markdown_content.append(f'author: "{author_str}"')
        markdown_content.append(f"calibre_id: {book_id}")
        markdown_content.append("tags: [book-highlights]")
        markdown_content.append("---\n")
        markdown_content.append(f"# {title}")
        markdown_content.append(f"**Author:** {author_str}\n")
        markdown_content.append("## Highlights\n")

        # Sort highlights by their physical location in the book (using the CFI path)
        annots.sort(key=lambda x: x.get("annotation", {}).get("epubcfi", ""))

        for annot in annots:
            annotation_data = annot.get("annotation", {})
            highlighted_text = annotation_data.get("highlighted_text", "").strip()
            user_note = annotation_data.get("notes", "").strip()

            if highlighted_text:
                # Add blockquote format for the highlight text
                markdown_content.append(f"> {highlighted_text}")

                # Append user notes underneath the highlight if they exist
                if user_note:
                    markdown_content.append(f"\n**Note:** {user_note}")

                markdown_content.append("")  # Spacer line

        # Write out to your Obsidian vault path
        with open(md_filepath, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_content))

        print(f"Successfully synced: '{title}' -> Obsidian")

    print("\n✅ Sync Complete! Open Obsidian to review your notes.")


if __name__ == "__main__":
    export_highlights()
