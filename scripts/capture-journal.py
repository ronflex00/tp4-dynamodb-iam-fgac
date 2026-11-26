#!/usr/bin/env python3
"""Capture réelle d'un journal AWS expurgé dans une fenêtre de terminal dédiée."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from redact import redact

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "I01": "03-reader-no-permission.png",
    "A01": "04-projection-allowed.png",
    "A02": "05-ssn-denied.png",
    "A03": "06-no-projection-denied.png",
    "A04": "07-query-allowed.png",
    "A05": "08-scan-two-items.png",
    "A07": "09-write-denied.png",
    "B01": "10-leadingkeys-001.png",
    "B02": "11-leadingkeys-002-denied.png",
    "B07": "12-scan-denied.png",
}


def hypr(command):
    result = subprocess.run(["hyprctl", command, "-j"], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=NAMES)
    parser.add_argument("--display", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    journal = ROOT / "preuves" / f"{args.scenario}.txt"
    marker = ROOT / ".secrets" / f"capture-{args.scenario}.ready"
    if not journal.is_file():
        raise SystemExit("Journal réel absent : aucune capture créée")
    if args.display:
        # Bande vide réservée en haut ; le rectangle de capture commence sous
        # les notifications du bureau et conserve l'intégralité du journal.
        print("\n" * 7 + "TP4 — JOURNAL D'UN APPEL AWS RÉEL, EXPURGÉ\n")
        print(redact(journal.read_text()), flush=True)
        marker.touch(mode=0o600)
        return
    marker.unlink(missing_ok=True)
    app = "tp4-proof-" + args.scenario.lower()
    output = ROOT / "downloads/captures" / NAMES[args.scenario]
    output.parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / ".secrets/capture-terminal.stderr").open("a") as log:
        process = subprocess.Popen([
            "foot", "--config=/dev/null", "--hold", "--app-id", app,
            "--title", "TP4 — " + args.scenario, "--font", "monospace:size=11",
            "python3", str(Path(__file__).resolve()), args.scenario, "--display",
        ], cwd=ROOT, stdout=log, stderr=log)
        try:
            for _ in range(120):
                if marker.exists():
                    break
                if process.poll() is not None:
                    raise RuntimeError("Terminal fermé avant affichage du journal")
                time.sleep(0.25)
            else:
                raise RuntimeError("Affichage non confirmé ; aucune capture")
            clients = [c for c in hypr("clients") if c.get("class") == app]
            if len(clients) != 1:
                raise RuntimeError("Fenêtre de preuve non identifiée de façon unique")
            client = clients[0]
            if hypr("activewindow").get("address") != client["address"]:
                raise RuntimeError("Une autre fenêtre est active : capture annulée")
            time.sleep(0.4)
            x, y = client["at"]
            width, height = client["size"]
            if height < 1000:
                raise RuntimeError("Fenêtre trop courte pour conserver tout le journal ; aucune capture")
            subprocess.run(["grim", "-g", f"{x},{y + 120} {width}x{height - 120}", str(output)], check=True, capture_output=True)
            print("Capture réelle à revoir avant copie dans preuves/ :", output)
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
