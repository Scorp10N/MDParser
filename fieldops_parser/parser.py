"""
Bidirectional Markdown <-> JSON parser for FieldOps documents.

Schema:
{
  "title": str,
  "description": str | None,   # prose between H1 and first H2
  "sections": [
    {
      "heading": str,
      "prose": str | None,      # prose between H2 and its list
      "items": [
        {"type": "bullet" | "ordered", "text": str}
      ],
      "footer": str | None      # prose after the section's list
    }
  ],
  "footer": str | None          # trailing prose after all sections
}
"""

import re
import json


def parse(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    doc = {"title": None, "description": None, "sections": [], "footer": None}
    current_section = None
    prose_buf = []
    section_footer_buf = []
    doc_footer_buf = []
    in_section_footer = False

    def flush_prose(target: dict, key: str):
        text = "\n".join(prose_buf).strip()
        if text:
            target[key] = text
        prose_buf.clear()

    def flush_section_footer():
        if current_section is not None and section_footer_buf:
            text = "\n".join(section_footer_buf).strip()
            if text:
                current_section["footer"] = text
            section_footer_buf.clear()

    for raw in lines:
        line = raw.rstrip("\n")

        # H1 — document title
        m = re.match(r"^# (.+)$", line)
        if m:
            doc["title"] = m.group(1).strip()
            continue

        # H2 — new section
        m = re.match(r"^## (.+)$", line)
        if m:
            flush_section_footer()
            if current_section is not None:
                flush_prose(current_section, "prose")
            else:
                flush_prose(doc, "description")
            current_section = {"heading": m.group(1).strip(), "prose": None, "items": [], "footer": None}
            doc["sections"].append(current_section)
            in_section_footer = False
            continue

        # Ordered list item: "1. text" or "12. text"
        m = re.match(r"^\d+\. (.+)$", line)
        if m and current_section is not None and not in_section_footer:
            flush_prose(current_section, "prose")
            current_section["items"].append({"type": "ordered", "text": m.group(1).strip()})
            continue

        # Bullet list item: "- text" or "* text"
        m = re.match(r"^[-*] (.+)$", line)
        if m and current_section is not None and not in_section_footer:
            flush_prose(current_section, "prose")
            current_section["items"].append({"type": "bullet", "text": m.group(1).strip()})
            continue

        # Blank line
        if line.strip() == "":
            if in_section_footer:
                section_footer_buf.append("")
            elif current_section is None:
                # preserve blank lines in doc description
                prose_buf.append("")
            # blank lines between list items or before list: discard
            continue

        # Prose line
        if current_section is None:
            prose_buf.append(line)
        elif not current_section["items"]:
            prose_buf.append(line)
        else:
            in_section_footer = True
            section_footer_buf.append(line)

    # Flush remaining buffers
    flush_section_footer()
    if current_section is not None:
        flush_prose(current_section, "prose")
    else:
        flush_prose(doc, "description")

    footer = "\n".join(doc_footer_buf).strip()
    if footer:
        doc["footer"] = footer

    return doc


def serialize(doc: dict) -> str:
    parts = []

    if doc.get("title"):
        parts.append(f"# {doc['title']}")

    if doc.get("description"):
        parts.append("")
        parts.append(doc["description"].strip())

    for section in doc.get("sections", []):
        parts.append("")
        parts.append(f"## {section['heading']}")

        if section.get("prose"):
            parts.append(section["prose"])

        items = section.get("items", [])
        ordered_counter = 1
        for item in items:
            if item["type"] == "ordered":
                parts.append(f"{ordered_counter}. {item['text']}")
                ordered_counter += 1
            else:
                parts.append(f"- {item['text']}")
                ordered_counter = 1

        if section.get("footer"):
            parts.append("")
            parts.append(section["footer"])

    if doc.get("footer"):
        parts.append("")
        parts.append(doc["footer"])

    parts.append("")  # trailing newline
    return "\n".join(parts)


def parse_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
