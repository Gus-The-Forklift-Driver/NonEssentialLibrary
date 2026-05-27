# clanker code
# create a list of templates in the given files

import argparse
import re
from pathlib import Path


def _extract_block(text: str, start: int) -> str:
    brace_start = text.index("{", start)
    depth = 0
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1: i]
    raise ValueError("Unbalanced braces")


def _first_description_line(body: str) -> str:
    desc_match = re.search(r"Description\s*=\s*\{([^}]*)\}", body, re.DOTALL)
    if not desc_match:
        return ""
    first_string = re.search(r'"([^"]*)"', desc_match.group(1))
    if not first_string:
        return ""
    raw = first_string.group(1)
    line = re.split(r"\\n|\\r|\r\n|\n|\r", raw, maxsplit=1)[0]
    line = re.sub(r"\\+$", "", line)
    return re.sub(r"^@\w+:", "", line).strip()


def fetch_templates(pkfx_path: Path) -> list[tuple[str, str]]:
    text = pkfx_path.read_text(encoding="utf-8")

    effect_match = re.search(r"CParticleEffect\s+\$[0-9A-Fa-f]+", text)
    if not effect_match:
        return []
    effect_body = _extract_block(text, effect_match.end())

    templates_match = re.search(r"Templates\s*=\s*\{([^}]*)\}", effect_body)
    if not templates_match:
        return []
    template_ids = re.findall(r"\$([0-9A-Fa-f]+)", templates_match.group(1))

    results: list[tuple[str, str]] = []
    for tid in template_ids:
        graph_match = re.search(
            rf"CParticleNodeGraph\s+\${tid}\b", text
        )
        if not graph_match:
            continue
        body = _extract_block(text, graph_match.end())
        name_match = re.search(r'CustomName\s*=\s*"([^"]*)"', body)
        if not name_match:
            continue
        results.append((name_match.group(1), _first_description_line(body)))

    return results


def collect_pkfx_paths(args: argparse.Namespace) -> list[Path]:
    if args.file:
        return [args.file]
    if args.folder:
        return sorted(args.folder.rglob("*.pkfx"))
    if args.filelist:
        return [
            Path(line.strip())
            for line in args.filelist.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List template names in PopcornFX .pkfx files.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--file", type=Path, help="Path to a single .pkfx file."
    )
    source.add_argument(
        "--filelist",
        type=Path,
        help="Path to a text file listing .pkfx paths (one per line).",
    )
    source.add_argument(
        "--folder",
        type=Path,
        help="Folder to scan recursively for .pkfx files.",
    )
    args = parser.parse_args()

    for pkfx in collect_pkfx_paths(args):
        templates = fetch_templates(pkfx)

        print(f"## {pkfx.name}")
        for name, description in templates:
            print(f"- {name} : {description}")
