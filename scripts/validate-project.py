#!/usr/bin/env python3
"""Contrôles locaux Markdown, scripts et absence de secrets dans Git."""
import configparser
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(ok, message):
    if not ok:
        errors.append(message)


for path in ROOT.rglob("*.md"):
    if any(part in (".git", ".secrets", "downloads", "node_modules") for part in path.parts):
        continue
    content = path.read_text()
    check(content.startswith("# "), f"Titre manquant : {path.relative_to(ROOT)}")
    check(len(re.findall(r"^```", content, re.M)) % 2 == 0, f"Bloc de code non fermé : {path.name}")
    tokens = MarkdownIt("commonmark").enable("table").parse(content)
    for token in tokens:
        for child in token.children or []:
            if child.type not in ("link_open", "image"):
                continue
            target = child.attrGet("href") or child.attrGet("src") or ""
            if not target or target.startswith("#") or urlparse(target).scheme:
                continue
            linked = path.parent / unquote(target.split("#", 1)[0])
            check(linked.exists(), f"Lien local absent dans {path.name} : {target}")

for path in (ROOT / "policies").glob("*.json"):
    json.loads(path.read_text())
for path in (ROOT / "scripts").glob("*.sh"):
    check(subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0, f"Syntaxe Bash : {path.name}")
check(subprocess.run(["fish", "-n", str(ROOT / "scripts/use-lab-env.fish")], capture_output=True).returncode == 0, "Syntaxe Fish")

result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True)
check(result.returncode == 0, "Git doit être initialisé pour l'audit des fichiers suivables")
paths = sorted(set(p.decode() for p in result.stdout.split(b"\0") if p))
patterns = [
    re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(rb"\barn:aws[^\s]*:\d{12}:"),
    re.compile(rb"\b\d{12}\b"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?im)^\s*(?:aws_secret_access_key|aws_session_token|aws_access_key_id)\s*=\s*\S+"),
]
known_secrets = []
credentials = ROOT / ".secrets/credentials"
if credentials.is_file():
    private_config = configparser.RawConfigParser()
    try:
        private_config.read(credentials)
        for section in private_config.sections():
            for key in ("aws_access_key_id", "aws_secret_access_key", "aws_session_token"):
                value = private_config.get(section, key, fallback="").strip()
                if value:
                    known_secrets.append(value.encode())
    except configparser.Error:
        check(False, "Fichier credentials non analysable ; contenu jamais affiché")
for name in paths:
    path = ROOT / name
    check(not name.startswith((".secrets/", "downloads/", ".aws/")) and path.suffix != ".csv", f"Fichier privé suivable : {name}")
    if path.is_file():
        content = path.read_bytes()
        check(not any(pattern.search(content) for pattern in patterns), f"Secret ou identifiant de compte potentiel : {name} (valeur non affichée)")
        check(not any(secret in content for secret in known_secrets), f"Secret local présent dans un fichier suivable : {name} (valeur non affichée)")

for required in (".secrets/config", ".secrets/credentials", "downloads/test.txt", "example.csv", ".env", ".env.local", "node_modules/x", "__pycache__/x", "playwright-report/x", "test-results/x"):
    result = subprocess.run(["git", "check-ignore", "-q", "--no-index", required], cwd=ROOT)
    check(result.returncode == 0, f"Exclusion manquante : {required}")
check(subprocess.run(["git", "check-ignore", "-q", "--no-index", "preuves/01-table-created.png"], cwd=ROOT).returncode == 1, "Les preuves PNG doivent rester suivables")
if errors:
    raise SystemExit("\n".join(errors))
print(f"CONTRÔLES LOCAUX OK — Markdown analysé, liens, JSON, Bash/Fish, exclusions et {len(paths)} fichiers suivables audités. Les images exigent une revue visuelle. Aucun test AWS effectué par ce contrôle.")
