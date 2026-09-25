#!/usr/bin/env python3
"""按句子长度规则扫描中文文案。

- 整句（按 。！？ 切分）不超过 100 个汉字。
- 句内被逗号、顿号、冒号、分号分开的每一截不超过 30 个汉字。

只报告，不改文件。Python 3.7 以上，无第三方依赖。

用法：
    python check_clauses.py <文件或目录>...
    python check_clauses.py docs/ --max-clause 30
    python check_clauses.py . --quiet
"""

import argparse
import io
import os
import re
import sys

CJK = "\u4e00-\u9fff"
CJK_CLS = "[%s]" % CJK
SENT_SPLIT = re.compile(r"[。！？]")
CLAUSE_SPLIT = re.compile(r"[，、：；]")

DEFAULT_EXT = (".md", ".kt", ".kts", ".java", ".xml", ".properties", ".yml", ".yaml",
               ".txt", ".py", ".js", ".ts", ".html", ".cs", ".axaml", ".xaml")
SKIP_DIR = {".git", ".gradle", ".kotlin", ".idea", "build", ".workbuddy", "node_modules",
            "target", "dist", "out", "venv", ".venv", "__pycache__", "Pods", "DerivedData",
            ".next", ".nuxt", "bin", "obj", "vendor"}


def cjk_len(text):
    return len(re.findall(CJK_CLS, text))


def scan(path, root, max_sentence, max_clause):
    rel = os.path.relpath(path, root).replace("\\", "/")
    try:
        text = io.open(path, encoding="utf-8").read()
    except (IOError, UnicodeDecodeError):
        return []
    if not re.search(CJK_CLS, text):
        return []

    rows = []
    in_fence = False
    in_front_matter = False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if i == 1 and s == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if s == "---":
                in_front_matter = False
            continue
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or "http://" in line or "https://" in line:
            continue
        if s.startswith("//") or s.startswith("*") or s.startswith("|"):
            continue
        # 行内代码与链接文字不参与计数
        body = re.sub(r"`[^`]*`", "X", line)
        body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)
        for sent in SENT_SPLIT.split(body):
            n = cjk_len(sent)
            if n > max_sentence:
                rows.append((rel, i, "整句%d字" % n, sent.strip()[:90]))
            for clause in CLAUSE_SPLIT.split(sent):
                cn = cjk_len(clause)
                if cn > max_clause:
                    rows.append((rel, i, "分截%d字" % cn, clause.strip()[:90]))
    return rows


def collect_files(paths, exts):
    files = []
    for item in paths:
        if os.path.isfile(item):
            if os.path.splitext(item)[1].lower() in exts:
                files.append(item)
            continue
        for dirpath, dirnames, filenames in os.walk(item):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR)
            for fn in sorted(filenames):
                if os.path.splitext(fn)[1].lower() in exts:
                    files.append(os.path.join(dirpath, fn))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--ext", help="comma separated extension list, overrides the default")
    parser.add_argument("--max-sentence", type=int, default=100, help="max CJK chars per sentence")
    parser.add_argument("--max-clause", type=int, default=30, help="max CJK chars per clause")
    parser.add_argument("--quiet", action="store_true", help="print a single summary line")
    args = parser.parse_args()

    if args.ext:
        exts = {("." + e.strip().lstrip(".")).lower() for e in args.ext.split(",") if e.strip()}
    else:
        exts = set(DEFAULT_EXT)

    paths = args.paths or ["."]
    for p in paths:
        if not os.path.exists(p):
            print("path does not exist: %s" % p, file=sys.stderr)
            return 2

    root = paths[0] if len(paths) == 1 else os.path.commonpath(
        [os.path.abspath(p) for p in paths])
    if os.path.isfile(root):
        root = os.path.dirname(root)

    rows = []
    for path in collect_files(paths, exts):
        rows.extend(scan(path, root, args.max_sentence, args.max_clause))

    if args.quiet:
        print("%d hit(s)" % len(rows))
        return 0

    print("%d hit(s)" % len(rows))
    by_file = {}
    for r in rows:
        by_file[r[0]] = by_file.get(r[0], 0) + 1
    for name, count in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0])):
        print("  %-58s %d" % (name, count))
    print()
    for r in rows:
        print("%s:%d [%s] %s" % (r[0], r[1], r[2], r[3]))
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
