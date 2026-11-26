#!/usr/bin/env python3
"""Validation structurelle locale stricte. Aucune simulation AWS."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/NovaUsersTP2A"


def validate(policy, phase, arn=None, template=False):
    actions = ["dynamodb:GetItem", "dynamodb:Query"]
    if phase == "attributes":
        actions.append("dynamodb:Scan")
    resource = policy.get("Statement", [{}])[0].get("Resource")
    expected_arn = TEMPLATE if template else arn
    if not expected_arn or resource != expected_arn:
        raise ValueError("ARN différent de la table vérifiée, ou ARN non lié")
    if not template and not re.fullmatch(
        r"arn:aws:dynamodb:[a-z0-9-]+:\d{12}:table/NovaUsersTP2A", resource
    ):
        raise ValueError("ARN exact invalide")
    condition = {
        "ForAllValues:StringEquals": {"dynamodb:Attributes": ["id", "username", "email"]},
        "StringEqualsIfExists": {"dynamodb:Select": "SPECIFIC_ATTRIBUTES"},
        "Null": {"dynamodb:Attributes": "false"},
    }
    if phase == "leadingkeys":
        condition["ForAllValues:StringEquals"]["dynamodb:LeadingKeys"] = ["001"]
        condition["Null"]["dynamodb:LeadingKeys"] = "false"
    statements = policy.get("Statement")
    if policy.get("Version") != "2012-10-17" or not isinstance(statements, list) or len(statements) != 1:
        raise ValueError("Version ou nombre de statements inattendu")
    statement = {k: v for k, v in statements[0].items() if k != "Sid"}
    expected = {"Effect": "Allow", "Action": actions, "Resource": expected_arn, "Condition": condition}
    if statement != expected or set(policy) != {"Version", "Statement"}:
        raise ValueError("Actions, conditions ou permissions inattendues")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", action="store_true")
    args = parser.parse_args()
    try:
        manifest = {} if args.templates else json.loads((ROOT / ".secrets/manifest.json").read_text())
        for phase in ("attributes", "leadingkeys"):
            folder = ROOT / ("policies" if args.templates else ".secrets/policies")
            validate(json.loads((folder / f"fgac-{phase}.json").read_text()), phase,
                     manifest.get("table_arn"), args.templates)
        print("VALIDATION LOCALE OK — " + ("modèles non déployables" if args.templates else "ARN lié"))
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"VALIDATION LOCALE ÉCHOUÉE : {exc}")
