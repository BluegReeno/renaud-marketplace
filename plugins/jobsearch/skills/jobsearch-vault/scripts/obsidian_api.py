"""Obsidian vault client — FILESYSTEM-ONLY (no network, no API key).

This is the job-search slice of the vault I/O, carved out of the global
`obsidian-crm` skill. The REST/Local-REST-API backend has been removed on
purpose: editing local `.md` files needs no server and no key, and if Obsidian
is open it auto-reloads externally-changed files.

Pure stdlib. The public interface:
  - read_note(path)   → dict with frontmatter, content, path, tags
  - read_raw(path)    → raw markdown string
  - create_note(path, content, overwrite=False)
  - append_body(path, content)
  - delete_note(path)
  - update_field(path, field, value)
  - list_directory(folder)   → list of .md filenames
  - search_simple(query)     → list of matches
  - search_dql(dql)          → list of results (basic TABLE...FROM...WHERE...SORT)
  - note_exists(path)        → bool
  - status()                 → dict

VAULT PATH RESOLUTION (no secret — the path is not sensitive):
  1. OBSIDIAN_VAULT_PATH env var (required in Cowork, where the vault is mounted
     at a session path)
  2. Known macOS path fallback
  3. Last resort: vault_path from ~/.claude/skills/obsidian-crm/scripts/config.json
"""

import json
import os
import re
import unicodedata
from pathlib import Path

# Known macOS location of the SecondLife vault (fallback #2).
DEFAULT_VAULT_PATH = (
    "/Users/renaud/Library/CloudStorage/SynologyDrive-MyAssistant/"
    "SecondLife-vault/SecondLife"
)

# Last-resort config (fallback #3) — we read ONLY its vault_path, never any key.
LEGACY_CONFIG_PATH = (
    Path.home() / ".claude" / "skills" / "obsidian-crm" / "scripts" / "config.json"
)


def resolve_vault_path() -> str:
    """Resolve the vault folder path. Filesystem-only — the path is not a secret.

    Order: OBSIDIAN_VAULT_PATH env → known macOS path → obsidian-crm config.json.
    """
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env:
        return env
    if Path(DEFAULT_VAULT_PATH).is_dir():
        return DEFAULT_VAULT_PATH
    if LEGACY_CONFIG_PATH.exists():
        try:
            with open(LEGACY_CONFIG_PATH) as f:
                cfg = json.load(f)
            if cfg.get("vault_path"):
                return cfg["vault_path"]
        except (json.JSONDecodeError, OSError):
            pass
    # Return the default even if it doesn't resolve, so the error message below
    # names a concrete path.
    return DEFAULT_VAULT_PATH


class ObsidianAPI:
    """Direct filesystem client for the SecondLife Obsidian vault.

    Reads/writes Markdown files. Frontmatter is parsed and serialized manually
    (never PyYAML) to preserve Obsidian's exact formatting and emoji enums.
    """

    def __init__(self, vault_path: str | None = None):
        self.backend_name = "file"
        vault_path = vault_path or resolve_vault_path()
        self.vault = Path(vault_path)
        if not self.vault.is_dir():
            raise FileNotFoundError(
                f"Vault not found: {vault_path}. "
                f"Set OBSIDIAN_VAULT_PATH to the vault folder."
            )

    def _resolve(self, path: str) -> Path:
        """Resolve vault-relative path to absolute, with NFC normalization."""
        normalized = unicodedata.normalize("NFC", path)
        return self.vault / normalized

    # --- Frontmatter parsing (no PyYAML — manual, safe) ---

    @staticmethod
    def _split_frontmatter(text: str) -> tuple:
        """Split markdown into (frontmatter_str, body_str).

        Returns ("", full_text) if no frontmatter block found.
        """
        if not text.startswith("---"):
            return "", text
        end = text.find("\n---", 3)
        if end == -1:
            return "", text
        fm_str = text[4:end]  # skip opening "---\n"
        body = text[end + 4:]  # skip closing "\n---"
        if body.startswith("\n"):
            body = body[1:]
        return fm_str, body

    @staticmethod
    def _parse_frontmatter(fm_str: str) -> dict:
        """Minimal YAML parser for Obsidian frontmatter.

        Handles: strings, numbers, booleans, lists (inline and indented),
        wikilinks in double quotes. Does NOT handle nested objects.
        """
        if not fm_str.strip():
            return {}

        result = {}
        lines = fm_str.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            if not line.strip() or line.strip().startswith("#"):
                i += 1
                continue

            m = re.match(r'^([A-Za-z_][\w_-]*)\s*:\s*(.*)', line)
            if not m:
                i += 1
                continue

            key = m.group(1)
            raw_value = m.group(2).strip()

            # Indented list on following lines
            if raw_value == "" or raw_value == "|":
                list_items = []
                j = i + 1
                while j < len(lines) and lines[j].startswith("  "):
                    item_line = lines[j].strip()
                    if item_line.startswith("- "):
                        list_items.append(ObsidianAPI._parse_scalar(item_line[2:].strip()))
                    j += 1
                if list_items:
                    result[key] = list_items
                    i = j
                    continue
                elif raw_value == "":
                    result[key] = None
                    i += 1
                    continue

            # Inline list: [a, b, c]
            if raw_value.startswith("[") and raw_value.endswith("]"):
                inner = raw_value[1:-1].strip()
                if not inner:
                    result[key] = []
                else:
                    items = ObsidianAPI._split_inline_list(inner)
                    result[key] = [ObsidianAPI._parse_scalar(it.strip()) for it in items]
                i += 1
                continue

            result[key] = ObsidianAPI._parse_scalar(raw_value)
            i += 1

        return result

    @staticmethod
    def _split_inline_list(s: str) -> list:
        """Split 'a, "b, c", d' respecting quotes."""
        items = []
        current = ""
        in_quotes = False
        quote_char = None
        for ch in s:
            if ch in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = ch
                current += ch
            elif ch == quote_char and in_quotes:
                in_quotes = False
                current += ch
                quote_char = None
            elif ch == "," and not in_quotes:
                items.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            items.append(current.strip())
        return items

    @staticmethod
    def _parse_scalar(s: str):
        """Parse a YAML scalar value."""
        if not s:
            return None
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1].replace('\\"', '"').replace("\\'", "'")
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
        if s.lower() == "null":
            return None
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            pass
        return s

    @staticmethod
    def _serialize_frontmatter(fm: dict) -> str:
        """Serialize dict to YAML frontmatter (no PyYAML)."""
        lines = []
        for key, value in fm.items():
            formatted = ObsidianAPI._yaml_value(value)
            if formatted.startswith("\n"):
                lines.append(f"{key}:{formatted}")
            else:
                lines.append(f"{key}: {formatted}")
        return "\n".join(lines)

    @staticmethod
    def _yaml_value(value) -> str:
        """Format a Python value as safe YAML (double-quoted strings)."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            if not value:
                return "[]"
            items = [f"  - {ObsidianAPI._yaml_value(v)}" for v in value]
            return "\n" + "\n".join(items)
        s = str(value)
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{s}"'

    @staticmethod
    def _extract_tags(text: str) -> list:
        """Extract #tags from markdown body (not frontmatter)."""
        return re.findall(r'(?<!\w)#([A-Za-z_][\w/-]*)', text)

    # --- Public interface ---

    def read_note(self, path: str) -> dict:
        fp = self._resolve(path)
        if not fp.exists():
            raise FileNotFoundError(f"Note not found: {path}")
        text = fp.read_text(encoding="utf-8")
        fm_str, body = self._split_frontmatter(text)
        fm = self._parse_frontmatter(fm_str)
        stat = fp.stat()
        return {
            "frontmatter": fm,
            "content": body,
            "path": path,
            "tags": fm.get("tags", []) or self._extract_tags(body),
            "stat": {
                "ctime": int(stat.st_ctime * 1000),
                "mtime": int(stat.st_mtime * 1000),
                "size": stat.st_size,
            },
        }

    def read_raw(self, path: str) -> str:
        fp = self._resolve(path)
        if not fp.exists():
            raise FileNotFoundError(f"Note not found: {path}")
        return fp.read_text(encoding="utf-8")

    def create_note(self, path: str, content: str, overwrite: bool = False) -> None:
        fp = self._resolve(path)
        # APFS collision check: macOS APFS is case-insensitive, so fp.exists()
        # already catches case-variant filenames (e.g. "Deal.md" vs "deal.md").
        # This guard is load-bearing for idempotent re-applies — do not weaken it.
        if not overwrite and fp.exists():
            raise FileExistsError(f"Note already exists: {path}")
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")

    def append_body(self, path: str, content: str) -> None:
        fp = self._resolve(path)
        if not fp.exists():
            raise FileNotFoundError(f"Note not found: {path}")
        with open(fp, "a", encoding="utf-8") as f:
            f.write(content)

    def delete_note(self, path: str) -> None:
        fp = self._resolve(path)
        if not fp.exists():
            raise FileNotFoundError(f"Note not found: {path}")
        fp.unlink()

    def update_field(self, path: str, field: str, value) -> None:
        fp = self._resolve(path)
        if not fp.exists():
            raise FileNotFoundError(f"Note not found: {path}")

        text = fp.read_text(encoding="utf-8")
        fm_str, body = self._split_frontmatter(text)
        fm = self._parse_frontmatter(fm_str)

        fm[field] = value

        new_fm = self._serialize_frontmatter(fm)
        new_content = f"---\n{new_fm}\n---\n{body}"
        fp.write_text(new_content, encoding="utf-8")

    def list_directory(self, folder: str) -> list:
        dp = self._resolve(folder)
        if not dp.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder}")
        return sorted([f.name for f in dp.iterdir() if f.suffix == ".md"])

    def search_simple(self, query: str, context_length: int = 200) -> list:
        """Full-text search across all .md files in the vault."""
        query_lower = query.lower()
        results = []
        for fp in self.vault.rglob("*.md"):
            parts = fp.relative_to(self.vault).parts
            if any(p.startswith(".") for p in parts):
                continue

            try:
                text = fp.read_text(encoding="utf-8")
            except Exception:
                continue

            if query_lower in text.lower():
                rel = str(fp.relative_to(self.vault))
                matches = []
                idx = 0
                text_lower = text.lower()
                while True:
                    pos = text_lower.find(query_lower, idx)
                    if pos == -1:
                        break
                    start = max(0, pos - context_length // 2)
                    end = min(len(text), pos + len(query) + context_length // 2)
                    matches.append({
                        "context": text[start:end],
                        "offset": pos,
                    })
                    idx = pos + 1
                    if len(matches) >= 5:
                        break

                results.append({
                    "filename": rel,
                    "score": len(matches),
                    "matches": matches,
                })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def search_dql(self, dql: str) -> list:
        """Parse a subset of DQL (TABLE ... FROM ... WHERE ... SORT).

        Supports basic TABLE queries common in CRM usage. Raises a helpful error
        for unsupported syntax (no Dataview API in filesystem mode).
        """
        m = re.match(
            r'TABLE\s+(.*?)\s+FROM\s+"([^"]+)"'
            r'(?:\s+WHERE\s+(.*?))?'
            r'(?:\s+SORT\s+([\w_]+)\s*(ASC|DESC)?)?'
            r'\s*$',
            dql.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise ValueError(
                "DQL not supported in filesystem mode. "
                "Use search_simple() or list_directory() + read_note() instead."
            )

        columns = [c.strip() for c in m.group(1).split(",")]
        folder = m.group(2)
        where_clause = m.group(3)
        sort_field = m.group(4)
        sort_dir = (m.group(5) or "ASC").upper()

        dp = self._resolve(folder)
        if not dp.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder}")

        rows = []
        for fp in sorted(dp.glob("*.md")):
            try:
                text = fp.read_text(encoding="utf-8")
            except Exception:
                continue

            fm_str, _ = self._split_frontmatter(text)
            fm = self._parse_frontmatter(fm_str)
            name = fp.stem

            if where_clause and not self._eval_where(fm, where_clause):
                continue

            row = {"file": {"name": name, "path": str(fp.relative_to(self.vault))}}
            for col in columns:
                row[col] = fm.get(col)
            rows.append(row)

        if sort_field:
            reverse = sort_dir == "DESC"
            rows.sort(
                key=lambda r: (r.get(sort_field) is None, str(r.get(sort_field, ""))),
                reverse=reverse,
            )

        return rows

    @staticmethod
    def _eval_where(fm: dict, clause: str) -> bool:
        """Evaluate a simple WHERE clause (field = / != / contains, AND-joined)."""
        parts = re.split(r'\s+AND\s+', clause, flags=re.IGNORECASE)
        for part in parts:
            part = part.strip()
            if not ObsidianAPI._eval_condition(fm, part):
                return False
        return True

    @staticmethod
    def _eval_condition(fm: dict, cond: str) -> bool:
        """Evaluate a single condition."""
        cond = cond.replace("\\!", "!")

        m = re.match(r'contains\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)', cond)
        if m:
            field_val = fm.get(m.group(1))
            target = m.group(2)
            if isinstance(field_val, list):
                return target in field_val
            if isinstance(field_val, str):
                return target in field_val
            return False

        m = re.match(r'(\w+)\s*!=\s*"([^"]*)"', cond)
        if m:
            return str(fm.get(m.group(1), "")) != m.group(2)

        m = re.match(r'(\w+)\s*=\s*"([^"]*)"', cond)
        if m:
            return str(fm.get(m.group(1), "")) == m.group(2)

        return True

    def note_exists(self, path: str) -> bool:
        return self._resolve(path).exists()

    def status(self) -> dict:
        return {
            "status": "ok",
            "backend": "filesystem",
            "vault_path": str(self.vault),
            "note_count": sum(1 for _ in self.vault.rglob("*.md")),
        }


if __name__ == "__main__":
    api = ObsidianAPI()
    print(f"Backend: {api.backend_name}")
    s = api.status()
    for k, v in s.items():
        print(f"  {k}: {v}")
