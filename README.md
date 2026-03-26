# mdparser

Bidirectional Markdown ↔ JSON parser. Converts structured markdown documents into a clean JSON schema and back.

## Supported Markdown Structure

```markdown
# Document Title

Optional description prose.

## Section Heading

Optional section prose.

- bullet item
- another item

1. ordered item
2. another ordered item

Optional section footer prose.

## Another Section

...
```

## JSON Schema

```json
{
  "title": "string",
  "description": "string | null",
  "sections": [
    {
      "heading": "string",
      "prose": "string | null",
      "items": [
        { "type": "bullet | ordered", "text": "string" }
      ],
      "footer": "string | null"
    }
  ],
  "footer": "string | null"
}
```

## CLI Usage

### `parse` — Markdown → JSON

```bash
python -m mdparser parse <file.md> [file2.md ...]
python -m mdparser parse <file.md> --out output.json
```

- Multiple files produce a JSON array; a single file produces a JSON object.
- Each result includes a `_source` field with the original filename.

### `build` — JSON → Markdown

```bash
python -m mdparser build <manifest.json>
python -m mdparser build <manifest.json> --out output.md
```

- Accepts a single document object or an array of documents.

### `batch` — Parse all `.md` files in a directory

```bash
python -m mdparser batch [dir]
python -m mdparser batch [dir] --out-dir outputs/
```

- Produces one `.json` and one round-tripped `.md` per input file.
- Defaults to the current directory if `dir` is omitted.

## Python API

```python
from mdparser import parse, serialize, parse_json

# Markdown file → dict
doc = parse("document.md")

# dict → Markdown string
md = serialize(doc)

# JSON file → dict
doc = parse_json("document.json")
```
