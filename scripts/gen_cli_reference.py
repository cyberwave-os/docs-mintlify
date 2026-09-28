#!/usr/bin/env python3
"""Regenerate the command tables in overview/tools/cli.mdx from the Click source.

The CLI reference page mixes hand-written prose with generated tables. Each
generated table sits between two MDX comments:

    {/* cli-gen:begin <kind> <arg> */}
    ...generated content, overwritten on every run...
    {/* cli-gen:end */}

Block kinds:

    group <path>         One row per direct subcommand of the group at <path>
                         (for example "edge" or "edge driver"): command, what
                         it does, options.
    options <path>       One row per option of the single command at <path>
                         (for example "pair" or "twin create").
    commands <a>,<b>     One row per listed command, like "group" but for an
                         explicit list of paths (for example "login,logout").

Everything outside the markers is left untouched, so edit prose freely.

Usage:

    python3 -m venv .venv
    .venv/bin/pip install -e <path-to>/cyberwave-clis/cyberwave-python-cli
    .venv/bin/python scripts/gen_cli_reference.py            # rewrite the page
    .venv/bin/python scripts/gen_cli_reference.py --check    # exit 1 if stale
    .venv/bin/python scripts/gen_cli_reference.py --dump     # print the tree

The script also reports any visible command that no block covers, so new CLI
commands are not silently missing from the page.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # don't litter the CLI checkout with __pycache__

try:
    import click
    from cyberwave_cli import __version__ as CLI_VERSION
    from cyberwave_cli.main import cli as ROOT
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    sys.exit(
        f"Cannot import the Cyberwave CLI ({exc}).\n"
        "Install it first: pip install -e <path-to>/cyberwave-python-cli"
    )

PAGE = Path(__file__).resolve().parent.parent / "overview" / "tools" / "cli.mdx"
PROG = "cyberwave"

# Docstrings that read badly as a one-line summary. Keep this list short and
# prefer fixing the docstring in the CLI repo.
SUMMARY_OVERRIDES = {
    "edge health": "Deprecated. Edge Core now runs this health check itself.",
    "edge remote-status": "Deprecated. Edge Core now runs this check itself. "
    "Reads the last heartbeat stored in twin metadata.",
}

# Options that exist for Cyberwave staff only and would confuse readers.
# Keyed by command path, values are Click parameter names.
INTERNAL_OPTIONS = {
    "configure": {"internal_deb_read_token", "internal_python_read_token"},
}

BEGIN_RE = re.compile(r"\{/\* cli-gen:begin (\w+) (.+?) \*/\}")
END_MARK = "{/* cli-gen:end */}"


# --------------------------------------------------------------------------- #
# Click tree helpers
# --------------------------------------------------------------------------- #


def _ctx_chain(path: list[str]) -> tuple[click.Command, click.Context]:
    """Resolve a command path like ["edge", "driver"] to (command, context)."""
    ctx = click.Context(ROOT, info_name=PROG)
    cmd: click.Command = ROOT
    for name in path:
        if not isinstance(cmd, click.Group):
            raise KeyError(f"'{' '.join(path)}': '{cmd.name}' is not a group")
        sub = cmd.get_command(ctx, name)
        if sub is None:
            raise KeyError(f"unknown command: {PROG} {' '.join(path)}")
        ctx = click.Context(sub, info_name=name, parent=ctx)
        cmd = sub
    return cmd, ctx


def _children(group: click.Group, ctx: click.Context) -> list[tuple[str, click.Command]]:
    out = []
    for name in group.list_commands(ctx):
        sub = group.get_command(ctx, name)
        if sub is not None and not getattr(sub, "hidden", False):
            out.append((name, sub))
    return out


def walk(path: list[str] | None = None):
    """Yield (path, command) for every visible command, depth first."""
    path = path or []
    cmd, ctx = _ctx_chain(path)
    if path:
        yield path, cmd
    if isinstance(cmd, click.Group):
        for name, _ in _children(cmd, ctx):
            yield from walk(path + [name])


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #


def _escape_text(text: str) -> str:
    """Escape prose for an MDX table cell, leaving `code spans` intact."""
    text = text.replace("``", "`")  # reST literals -> Markdown code
    # Put bare --flags in code spans so they render as typed.
    parts = text.split("`")
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<![\w/`-])(--[a-z][a-z0-9-]*)", r"`\1`", parts[i])
    text = "`".join(parts)
    parts = text.split("`")
    for i, part in enumerate(parts):
        if i % 2 == 0:  # outside a code span
            part = (
                part.replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("{", "&#123;")
                .replace("}", "&#125;")
                .replace("*", "\\*")
                .replace("_", "\\_")
                .replace("~", "\\~")
            )
        parts[i] = part.replace("|", "\\|")
    return "`".join(parts)


def _first_sentence(text: str) -> str:
    text = " ".join((text or "").split())
    # Split only where a new sentence starts with a capital letter, so
    # abbreviations such as "e.g. http://..." stay intact.
    m = re.match(r"(.+?\.)(?=\s+[A-Z]|$)", text)
    return m.group(1) if m else text


def summary(path: list[str], cmd: click.Command) -> str:
    key = " ".join(path)
    if key in SUMMARY_OVERRIDES:
        return SUMMARY_OVERRIDES[key]
    text = cmd.get_short_help_str(limit=200)
    text = re.sub(r"^DEPRECATED:\s*", "Deprecated. ", text)
    return text if text.endswith(".") else text + "."


def usage(path: list[str], cmd: click.Command) -> str:
    pieces = [PROG, *path]
    for p in cmd.params:
        if isinstance(p, click.Argument):
            meta = p.human_readable_name.upper()
            pieces.append(meta if p.required else f"[{meta}]")
    return " ".join(pieces)


def _flags(opt: click.Option) -> str:
    shorts = [o for o in opt.opts if not o.startswith("--")]
    longs = [o for o in opt.opts if o.startswith("--")]
    names = ", ".join(shorts + longs)
    if opt.secondary_opts:
        names += " / " + ", ".join(opt.secondary_opts)
    return names


def _default(opt: click.Option) -> str | None:
    d = opt.default
    if callable(d) or d is None or type(d).__name__ == "Sentinel":
        return None
    if opt.is_flag:
        # Only worth saying when a flag is on by default.
        return "on" if d is True else None
    if d is False or d == "" or (isinstance(d, (list, tuple)) and not d):
        return None
    return str(d)


def option_help(opt: click.Option, *, full: bool) -> str:
    text = " ".join((opt.help or "").split())
    if not full:
        text = _first_sentence(text)
    text = _escape_text(text.rstrip(".")) if text else ""
    extras = []
    if isinstance(opt.type, click.Choice):
        extras.append("one of " + ", ".join(f"`{c}`" for c in opt.type.choices))
    default = _default(opt)
    if default is not None and "default" not in (opt.help or "").lower():
        extras.append(f"default `{default}`")
    if opt.required:
        extras.append("required")
    if opt.multiple:
        extras.append("repeatable")
    if extras:
        text = f"{text} ({'; '.join(extras)})" if text else "; ".join(extras).capitalize()
    return text


def visible_options(cmd: click.Command, path: list[str] | None = None) -> list[click.Option]:
    internal = INTERNAL_OPTIONS.get(" ".join(path or []), set())
    return [
        p
        for p in cmd.params
        if isinstance(p, click.Option)
        and not p.hidden
        and p.name != "help"
        and p.name not in internal
    ]


def options_cell(cmd: click.Command, path: list[str], skip: set[str]) -> str:
    rows = []
    for opt in visible_options(cmd, path):
        if opt.name in skip:
            continue
        rows.append(f"`{_flags(opt)}` {option_help(opt, full=False)}".strip())
    return "<br/>".join(rows) if rows else "None"


# --------------------------------------------------------------------------- #
# Block renderers
# --------------------------------------------------------------------------- #


def _command_rows(paths: list[list[str]], skip_common: set[str]) -> list[str]:
    lines = [
        "| Command | What it does | Options |",
        "|---|---|---|",
    ]
    for path in paths:
        cmd, _ = _ctx_chain(path)
        desc = _escape_text(summary(path, cmd))
        if isinstance(cmd, click.Group):
            cell = "Subcommands, see the table below."
            name = f"`{PROG} {' '.join(path)} …`"
        else:
            cell = options_cell(cmd, path, skip_common)
            name = f"`{usage(path, cmd)}`"
        lines.append(f"| {name} | {desc} | {cell} |")
    return lines


def render_group(arg: str) -> str:
    path = arg.split()
    group, ctx = _ctx_chain(path)
    if not isinstance(group, click.Group):
        raise KeyError(f"'{arg}' is not a group")
    kids = _children(group, ctx)
    paths = [path + [name] for name, _ in kids]
    leaves = [c for _, c in kids if not isinstance(c, click.Group)]

    # Options shared by most leaf subcommands are listed once, under the table,
    # instead of on every row. An option counts as shared when at least three
    # leaves and at least two thirds of them accept it.
    by_name: dict[str, tuple[click.Option, list[str]]] = {}
    for name, cmd in kids:
        if isinstance(cmd, click.Group):
            continue
        for opt in visible_options(cmd, path + [name]):
            by_name.setdefault(opt.name, (opt, []))[1].append(name)
    leaf_names = [n for n, c in kids if not isinstance(c, click.Group)]
    common = {
        k: v
        for k, v in by_name.items()
        if len(v[1]) >= 3 and len(v[1]) * 3 >= len(leaf_names) * 2
    }
    lines = _command_rows(paths, set(common))
    for opt, having in common.values():
        missing = [n for n in leaf_names if n not in having]
        scope = f"Every `{PROG} {arg}` subcommand"
        if missing:
            scope += " except " + ", ".join(f"`{n}`" for n in missing)
        lines += ["", f"{scope} also accepts `{_flags(opt)}`: {option_help(opt, full=True)}."]
    return "\n".join(lines)


def render_commands(arg: str) -> str:
    paths = [p.strip().split() for p in arg.split(",") if p.strip()]
    return "\n".join(_command_rows(paths, set()))


def render_options(arg: str) -> str:
    path = arg.split()
    cmd, _ = _ctx_chain(path)
    lines = [f"`{usage(path, cmd)}`", "", "| Option | What it does |", "|---|---|"]
    for opt in visible_options(cmd, path):
        lines.append(f"| `{_flags(opt)}` | {option_help(opt, full=True)} |")
    return "\n".join(lines)


RENDERERS = {"group": render_group, "commands": render_commands, "options": render_options}


def covered_paths(kind: str, arg: str) -> set[str]:
    if kind == "group":
        path = arg.split()
        group, ctx = _ctx_chain(path)
        return {" ".join(path + [n]) for n, _ in _children(group, ctx)} | {arg}
    if kind == "commands":
        return {p.strip() for p in arg.split(",") if p.strip()}
    return {arg}


# --------------------------------------------------------------------------- #
# Page rewrite
# --------------------------------------------------------------------------- #


def regenerate(text: str) -> tuple[str, set[str]]:
    out: list[str] = []
    covered: set[str] = set()
    pos = 0
    for m in BEGIN_RE.finditer(text):
        if m.start() < pos:
            continue
        end = text.find(END_MARK, m.end())
        if end == -1:
            raise SystemExit(f"Unclosed block: {m.group(0)}")
        kind, arg = m.group(1), m.group(2).strip()
        if kind not in RENDERERS:
            raise SystemExit(f"Unknown block kind '{kind}' in {m.group(0)}")
        out.append(text[pos : m.end()])
        out.append("\n\n" + RENDERERS[kind](arg) + "\n\n")
        covered |= covered_paths(kind, arg)
        pos = end
    out.append(text[pos:])
    new = "".join(out)
    new = re.sub(
        r"\{/\* cli-version: .*? \*/\}",
        f"{{/* cli-version: generated from cyberwave-cli {CLI_VERSION} */}}",
        new,
    )
    return new, covered


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--page", type=Path, default=PAGE, help="MDX page to rewrite")
    ap.add_argument("--check", action="store_true", help="exit 1 if the page is stale")
    ap.add_argument("--dump", action="store_true", help="print the command tree and exit")
    args = ap.parse_args()

    if args.dump:
        for path, cmd in walk():
            print(f"{usage(path, cmd):50s} {summary(path, cmd)}")
        return 0

    text = args.page.read_text(encoding="utf-8")
    new, covered = regenerate(text)

    missing = [" ".join(p) for p, _ in walk() if " ".join(p) not in covered]
    for name in missing:
        print(f"warning: `{PROG} {name}` is not covered by any cli-gen block", file=sys.stderr)

    if args.check:
        if new != text:
            print(f"{args.page} is out of date; run {Path(__file__).name}", file=sys.stderr)
            return 1
        return 0

    if new != text:
        args.page.write_text(new, encoding="utf-8")
        print(f"updated {args.page}")
    else:
        print(f"{args.page} already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
