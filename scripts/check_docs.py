#!/usr/bin/env python3
"""Structural checks for the Mintlify docs. Run from the docs root: python3 scripts/check_docs.py

Fails (exit 1) when:
  - a page in docs.json navigation has no .mdx file
  - a page appears twice in the navigation
  - an .mdx page is neither in the navigation nor in ALLOWED_UNLISTED
  - a redirect source shadows an existing page
  - an internal link does not resolve to a page directly (broken, or only via a redirect)
  - a visible "stub" marker is published (use {/* TODO(docs): ... */} comments instead)
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Pages that intentionally live outside the sidebar.
ALLOWED_UNLISTED = {"README", "REFACTOR_PLAN"}
SKIP_PREFIXES = ("api-reference/rest/", "snippets/", "scripts/", "node_modules/")

errors = []
docs = json.load(open("docs.json"))

nav = []


def walk(items):
    for it in items:
        if isinstance(it, dict):
            walk(it.get("pages", []))
            for g in it.get("groups", []):
                walk([g])
        else:
            nav.append(it)


for tab in docs["navigation"].get("tabs", []):
    walk(tab.get("pages", []))
    walk(tab.get("groups", []))


def page_exists(p):
    p = p.strip("/")
    if p == "":
        return True
    return any(os.path.isfile(p + ext) for ext in (".mdx", ".md", "/index.mdx", "/index.md"))


for p, c in collections.Counter(nav).items():
    if c > 1:
        errors.append(f"nav: duplicate page {p}")
for p in nav:
    if not page_exists(p):
        errors.append(f"nav: missing file for {p}")

pages = set()
for f in glob.glob("**/*.mdx", recursive=True):
    if f.startswith(SKIP_PREFIXES):
        continue
    pages.add(f[:-4])
navset = set(nav)
for p in sorted(pages):
    if p not in navset and p not in ALLOWED_UNLISTED and not p.startswith("api-reference/rest"):
        errors.append(f"orphan: {p}.mdx is not in the navigation")

# Internal (non-customer) API surfaces must not be published, even if a
# regeneration from openapi.json brings them back. Fix at the source with
# include_in_schema=False (see cyberwave-backend/docs/OPENAPI_PUBLIC_SURFACE.md).
INTERNAL_API = re.compile(r"^(CRM|Contact|Admin|Opportunit)")
for f in glob.glob("api-reference/rest/*.mdx"):
    if INTERNAL_API.match(os.path.basename(f)):
        errors.append(f"internal API page published: {f}")

for r in docs.get("redirects", []):
    src = r["source"]
    if ":" not in src and page_exists(src):
        errors.append(f"redirect: source {src} shadows an existing page")

LINK = re.compile(r'(?:\]\(|href=["\'])(/[^)"\'\s]*)')
redirect_sources = {r["source"] for r in docs.get("redirects", []) if ":" not in r["source"]}
wildcards = [r["source"].split("/:")[0] for r in docs.get("redirects", []) if ":" in r["source"]]
STUB = re.compile(r"(?i)(^|[^a-z_/`-])stub([^a-z_]|$)")
for f in sorted(glob.glob("**/*.mdx", recursive=True)):
    if f.startswith(SKIP_PREFIXES):
        continue
    text = open(f).read()
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose_no_comments = re.sub(r"\{/\*.*?\*/\}", "", prose, flags=re.S)
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not fm:
        errors.append(f"frontmatter: {f} has no frontmatter block")
    else:
        for line in fm.group(1).split("\n"):
            if line.strip() and not re.match(r"^([\w-]+:|\s+|- |#)", line):
                errors.append(f"frontmatter: {f}: stray line {line.strip()!r}")
    for m in LINK.finditer(prose):
        base = m.group(1).split("#")[0].split("?")[0].rstrip("/")
        if not base or re.search(r"\.\w{2,5}$", base):
            continue
        if page_exists(base):
            continue
        if base in redirect_sources or any(base == w or base.startswith(w + "/") for w in wildcards):
            errors.append(f"link: {f} -> {base} only resolves through a redirect; link the final page")
        else:
            errors.append(f"link: {f} -> {base} is broken")
    for i, line in enumerate(prose_no_comments.splitlines(), 1):
        if STUB.search(line) and not re.search(r"(?i)stubs?\b.*(generator|pyi|typing)", line):
            errors.append(f"stub: {f}:{i}: visible stub marker")
            break

for e in errors:
    print(e)
print(f"\n{len(nav)} nav pages, {len(pages)} mdx pages, {len(errors)} problems")
sys.exit(1 if errors else 0)
