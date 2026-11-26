#!/usr/bin/env python3
"""Affiche des réponses AWS réelles limitées aux données fictives, pour capture écran."""
import argparse
import json
import sys

import lab


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subject", choices=["table", "items"])
    args = parser.parse_args()
    try:
        manifest = lab.state()
        lab.guard(manifest)
        print("TP4 NOVA SERVICES — PREUVE AWS CLI RÉELLE", flush=True)
        print(f"Date UTC : {lab.now()}\nProfil : tp2a-admin | Région : {manifest['region']}", flush=True)
        print("Compte et principal STS vérifiés ; identifiants masqués.\n", flush=True)
        if args.subject == "table":
            result = lab.aws("tp2a-admin", "dynamodb", "describe-table", "--table-name", lab.TABLE)
            value = lab.parse(result)["Table"]
            lab.require(value["TableArn"] == manifest["table_arn"] and value["TableId"] == manifest["table_id"], "Table différente du manifest")
            fields = ["TableName", "TableStatus", "KeySchema", "AttributeDefinitions", "BillingModeSummary", "TableClassSummary"]
            safe = {key: value[key] for key in fields if key in value}
            print("DescribeTable — NovaUsersTP2A | code réel :", result.returncode)
            print(json.dumps(safe, ensure_ascii=False, indent=2))
        else:
            for key in ("001", "002"):
                result = lab.aws("tp2a-admin", "dynamodb", "get-item", "--table-name", lab.TABLE,
                                 "--key", lab.key_json(key), "--consistent-read")
                value = lab.parse(result)
                lab.require(value.get("Item") == lab.item(key), "Item différent des données fictives approuvées")
                print(f"GetItem id={key} avec consistent-read | code réel : {result.returncode}")
                # Affichage compact des valeurs réelles, dont les cinq types String.
                for name, attribute in sorted(value["Item"].items()):
                    print(f"  {name} (String) = {attribute['S']}")
                print()
        print("\nFin de la réponse réelle. Aucun test reader n'est démontré ici.", flush=True)
        return 0
    except (lab.Stop, KeyError, OSError, ValueError) as exc:
        print("ARRÊT : " + lab.redact(str(exc)), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
