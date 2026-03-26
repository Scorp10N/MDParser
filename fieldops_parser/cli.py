"""
CLI for fieldops_parser.

Commands:
  parse  <file.md> [...]       Parse markdown → JSON (stdout or --out)
  build  <manifest.json>       Build markdown from JSON (stdout or --out)
  batch  [dir]                 Parse every .md in dir → one .json per file
"""

import argparse
import json
import os
import sys

from . import parser as p


def cmd_parse(args):
    docs = []
    for path in args.files:
        doc = p.parse(path)
        doc["_source"] = os.path.basename(path)
        docs.append(doc)

    output = json.dumps(docs if len(docs) > 1 else docs[0], ensure_ascii=False, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(output)


def cmd_build(args):
    doc = p.parse_json(args.manifest)

    # Support single doc or list
    docs = doc if isinstance(doc, list) else [doc]

    for d in docs:
        md = p.serialize(d)
        if args.out:
            out_path = args.out if len(docs) == 1 else args.out.replace(".md", f"_{d.get('_source','doc')}.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Written to {out_path}", file=sys.stderr)
        else:
            print(md)


def cmd_batch(args):
    directory = args.dir or "."
    out_dir = args.out_dir or directory
    os.makedirs(out_dir, exist_ok=True)

    md_files = [f for f in os.listdir(directory) if f.endswith(".md")]
    if not md_files:
        print("No .md files found.", file=sys.stderr)
        return

    for filename in sorted(md_files):
        src = os.path.join(directory, filename)
        stem = filename[:-3]
        doc = p.parse(src)
        doc["_source"] = filename

        json_dst = os.path.join(out_dir, stem + ".json")
        with open(json_dst, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        md_dst = os.path.join(out_dir, stem + ".md")
        with open(md_dst, "w", encoding="utf-8") as f:
            f.write(p.serialize(doc))

        print(f"{filename} → {os.path.relpath(json_dst)}, {os.path.relpath(md_dst)}")


def main():
    ap = argparse.ArgumentParser(prog="fieldops_parser")
    sub = ap.add_subparsers(dest="command", required=True)

    # parse
    sp = sub.add_parser("parse", help="Parse .md files → JSON")
    sp.add_argument("files", nargs="+", metavar="file.md")
    sp.add_argument("--out", metavar="out.json", help="Write output to file instead of stdout")

    # build
    sb = sub.add_parser("build", help="Build .md from JSON manifest")
    sb.add_argument("manifest", metavar="manifest.json")
    sb.add_argument("--out", metavar="out.md", help="Write output to file instead of stdout")

    # batch
    sc = sub.add_parser("batch", help="Parse all .md files in a directory")
    sc.add_argument("dir", nargs="?", default=".", metavar="dir")
    sc.add_argument("--out-dir", metavar="dir", help="Write outputs to this directory (default: same as source)")

    args = ap.parse_args()
    {"parse": cmd_parse, "build": cmd_build, "batch": cmd_batch}[args.command](args)


if __name__ == "__main__":
    main()
