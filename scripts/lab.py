#!/usr/bin/env python3
"""Orchestration TP4 par AWS CLI, bibliothèque standard Python uniquement."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import time

from redact import redact

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".secrets"
PROOFS = ROOT / "preuves"
TABLE = "NovaUsersTP2A"
READER = "tp2a-dynamo-reader"
POLICY = "TP2AFGAC"
PDF = ROOT / "docs/sources/TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf"
spec = importlib.util.spec_from_file_location("validation", ROOT / "scripts/validate-policies.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class Stop(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise Stop(message)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    if path.is_relative_to(PRIVATE):
        temp.chmod(0o600)
    temp.replace(path)


def state():
    try:
        return json.loads((PRIVATE / "manifest.json").read_text())
    except FileNotFoundError:
        raise Stop("Préflight absent : exécuter preflight après lecture du PDF et connexion.")


def save(value):
    write_json(PRIVATE / "manifest.json", value)


def isolated():
    os.umask(0o077)
    require(not PRIVATE.is_symlink(), ".secrets ne doit pas être un lien symbolique")
    PRIVATE.mkdir(exist_ok=True, mode=0o700)
    PRIVATE.chmod(0o700)
    env = dict(os.environ)
    for name in tuple(env):
        if name.startswith("AWS_"):
            del env[name]
    env.update(AWS_CONFIG_FILE=str(PRIVATE / "config"),
               AWS_SHARED_CREDENTIALS_FILE=str(PRIVATE / "credentials"),
               AWS_LOGIN_CACHE_DIRECTORY=str(PRIVATE / "login-cache"),
               AWS_PAGER="", AWS_CLI_AUTO_PROMPT="off", AWS_EC2_METADATA_DISABLED="true",
               AWS_IGNORE_CONFIGURED_ENDPOINT_URLS="true")
    return env


def aws(profile, service, operation, *args):
    command = ["aws", service, operation, *map(str, args), "--profile", profile, "--region", configured_region(),
               "--output", "json", "--no-cli-pager", "--cli-connect-timeout", "10",
               "--cli-read-timeout", "30"]
    try:
        return subprocess.run(command, env=isolated(), text=True, capture_output=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("AWS CLI indisponible ou délai dépassé ; aucun résultat IAM déduit.")


def error_code(result):
    match = re.search(r"An error occurred \(([^)]+)\) when calling", result.stderr)
    return match.group(1) if match else None


def parse(result):
    require(result.returncode == 0, "AWS CLI rc=" + str(result.returncode) + ": " + redact(result.stderr))
    try:
        return json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        raise Stop("Réponse AWS non JSON ; aucun succès déduit.")


def admin(service, operation, *args):
    return parse(aws("tp2a-admin", service, operation, *args))


def identity(profile, manifest=None):
    value = parse(aws(profile, "sts", "get-caller-identity"))
    require(re.fullmatch(r"\d{12}", value.get("Account", "")), "Compte STS invalide")
    arn = value.get("Arn", "")
    require(arn.startswith("arn:aws:") and not arn.endswith(":root"), "Identité root ou partition inattendue : arrêt")
    if manifest:
        require(value["Account"] == manifest["account"], "Le compte a changé : arrêt")
        if profile == "tp2a-admin":
            require(arn == manifest["admin_arn"], "Le principal administrateur a changé : arrêt")
    if profile == "tp2a-reader":
        require(arn == f"arn:aws:iam::{value['Account']}:user/{READER}", "Le profil reader ne correspond pas à l'utilisateur exact")
    return value


def source_required():
    require(PDF.is_file(), "PDF absent : copier le sujet dans docs/sources/ avant les opérations AWS.")
    require(shutil.which("pdfinfo"), "pdfinfo requis pour contrôler le sujet")
    result = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True)
    require(result.returncode == 0 and re.search(r"Pages:\s+10\b", result.stdout), "Le sujet doit contenir 10 pages : vérifier le PDF")
    digest = hashlib.sha256(PDF.read_bytes()).hexdigest()
    acknowledgement = PRIVATE / "source-reviewed.sha256"
    require(acknowledgement.is_file() and acknowledgement.read_text().strip() == digest,
            "Lire le PDF, rapprocher les exigences et consigner son SHA256 dans .secrets/source-reviewed.sha256 ; voir docs/sources/README.md.")


def configured_region():
    result = subprocess.run(["aws", "configure", "get", "region", "--profile", "tp2a-admin"],
                            env=isolated(), capture_output=True, text=True)
    require(result.returncode == 0 and re.fullmatch(r"[a-z]{2}-[a-z]+-\d+", result.stdout.strip()), "Région admin absente/invalide")
    return result.stdout.strip()


def guard(manifest):
    identity("tp2a-admin", manifest)
    require(configured_region() == manifest["region"], "Région modifiée depuis le préflight")


def absent(service, operation, code, *args):
    result = aws("tp2a-admin", service, operation, *args)
    require(result.returncode != 0 and error_code(result) == code,
            f"Absence de {service}/{operation} non démontrée (rc={result.returncode}, erreur={error_code(result)}). Inspecter ; aucun écrasement.")


def table(manifest):
    value = admin("dynamodb", "describe-table", "--table-name", TABLE)["Table"]
    require(value["TableArn"] == manifest["table_arn"], "ARN de table différent")
    require(value.get("TableId"), "Identifiant unique de table manquant")
    if manifest.get("table_id"):
        require(value["TableId"] == manifest["table_id"], "La table a été remplacée : arrêt")
    require(value["TableStatus"] == "ACTIVE", "Table non ACTIVE")
    require(value["KeySchema"] == [{"AttributeName": "id", "KeyType": "HASH"}], "Clé primaire incorrecte")
    require(value["AttributeDefinitions"] == [{"AttributeName": "id", "AttributeType": "S"}], "Type de clé/index incorrect")
    require(value.get("BillingModeSummary", {}).get("BillingMode") == "PAY_PER_REQUEST", "Mode On-demand requis")
    require(value.get("TableClassSummary", {}).get("TableClass", "STANDARD") == "STANDARD", "Classe Standard requise")
    require(not any(value.get(k) for k in ("GlobalSecondaryIndexes", "LocalSecondaryIndexes", "Replicas")), "Index ou réplication inattendus")
    require(not value.get("StreamSpecification", {}).get("StreamEnabled", False), "Stream inattendu")
    backups = admin("dynamodb", "describe-continuous-backups", "--table-name", TABLE)
    recovery = backups.get("ContinuousBackupsDescription", {}).get("PointInTimeRecoveryDescription", {})
    require(recovery.get("PointInTimeRecoveryStatus", "DISABLED") == "DISABLED", "Sauvegarde PITR supplémentaire active")
    require(not admin("dynamodb", "list-backups", "--table-name", TABLE).get("BackupSummaries"), "Sauvegarde supplémentaire détectée")
    tags = admin("dynamodb", "list-tags-of-resource", "--resource-arn", manifest["table_arn"])["Tags"]
    require({t["Key"]: t["Value"] for t in tags}.get("TP4LabId") == manifest["lab_id"], "Marqueur d'appartenance table absent/différent")
    result = aws("tp2a-admin", "dynamodb", "get-resource-policy", "--resource-arn", manifest["table_arn"])
    if result.returncode == 0:
        require(not parse(result).get("Policy"), "Policy de ressource détectée : analyser avant de poursuivre")
    else:
        require(error_code(result) == "PolicyNotFoundException", "Impossible de vérifier la policy de ressource")
    return value


def audit_login_profile(manifest):
    result = aws("tp2a-admin", "iam", "get-login-profile", "--user-name", READER)
    if result.returncode != 0 and error_code(result) == "NoSuchEntity":
        return "ABSENT"
    restricted = (result.returncode != 0 and error_code(result) == "AccessDenied"
                  and "iam:GetLoginProfile" in result.stderr
                  and "explicit deny in a service control policy" in result.stderr)
    require(restricted, "Profil console présent ou absence non démontrée ; inspecter la réponse AWS")
    # La restriction de lecture n'est ni contournée ni comptée comme un refus reader.
    manifest.setdefault("audit_limitations", {})["get-login-profile"] = {
        "observed_at": now(), "returncode": result.returncode,
        "status": "PARTIAL", "cause": "Explicit deny in a service control policy",
    }
    save(manifest)
    proof("audit-login-profile.txt", f"{now()} Profil administrateur, action iam:GetLoginProfile.\nCode réel : {result.returncode}. Statut d'audit : PARTIAL.\n{result.stderr}\nAucun accès console créé par nos commandes CreateUser. Absence non confirmée par cette API.\nAucune restriction AWS modifiée. Ce résultat ne valide aucun test DynamoDB du reader.\n")
    print("Audit GetLoginProfile : PARTIAL — lecture refusée par une SCP ; restriction conservée.")
    return "UNVERIFIED_SCP_DENY"


def reader(manifest, phase=None, require_key=True):
    value = admin("iam", "get-user", "--user-name", READER)["User"]
    require(value["UserId"] == manifest.get("user_id"), "Utilisateur non enregistré ou remplacé")
    require(value["Arn"] == f"arn:aws:iam::{manifest['account']}:user/{READER}", "ARN utilisateur incorrect")
    tags = {v["Key"]: v["Value"] for v in value.get("Tags", [])}
    require(tags.get("TP4LabId") == manifest["lab_id"], "Marqueur d'appartenance IAM incorrect")
    require(not value.get("PermissionsBoundary"), "Permissions boundary inattendue : inspecter")
    require(not admin("iam", "list-groups-for-user", "--user-name", READER)["Groups"], "Groupe IAM inattendu")
    require(not admin("iam", "list-attached-user-policies", "--user-name", READER)["AttachedPolicies"], "Managed policy inattendue")
    names = admin("iam", "list-user-policies", "--user-name", READER)["PolicyNames"]
    require(sorted(names) == ([] if phase is None else [POLICY]), "Policies inline inattendues")
    if phase:
        document = admin("iam", "get-user-policy", "--user-name", READER, "--policy-name", POLICY)["PolicyDocument"]
        validation.validate(document, phase, manifest["table_arn"])
    audit_login_profile(manifest)
    keys = admin("iam", "list-access-keys", "--user-name", READER)["AccessKeyMetadata"]
    require(len(keys) <= 1, "Plus d'une clé de laboratoire : arrêt")
    if require_key:
        require(len(keys) == 1 and keys[0]["Status"] == "Active", "Une unique clé active est requise")
    return keys


def item(key):
    return {k: {"S": v} for k, v in {
        "id": key, "username": "alice" if key == "001" else "bob",
        "email": "alice@example.com" if key == "001" else "bob@example.com",
        "ssn": f"FICTIF-{key}", "internal_note": "Demonstration interne",
    }.items()}


def key_json(key):
    return json.dumps({"id": {"S": key}})


def public_item(key):
    return {k: v for k, v in item(key).items() if k in ("id", "username", "email")}


def verify_items():
    values = admin("dynamodb", "scan", "--table-name", TABLE, "--consistent-read").get("Items", [])
    require(len(values) == 2 and sorted(values, key=lambda v: v["id"]["S"]) == [item("001"), item("002")], "Les deux items ne correspondent pas exactement aux données fictives")
    for key in ("001", "002"):
        value = admin("dynamodb", "get-item", "--table-name", TABLE, "--key", key_json(key), "--consistent-read")
        require(value.get("Item") == item(key), "GetItem administrateur incorrect")


def bind(manifest):
    for phase in ("attributes", "leadingkeys"):
        document = json.loads((ROOT / f"policies/fgac-{phase}.json").read_text())
        validation.validate(document, phase, template=True)
        document["Statement"][0]["Resource"] = manifest["table_arn"]
        validation.validate(document, phase, manifest["table_arn"])
        write_json(PRIVATE / f"policies/fgac-{phase}.json", document)


def definitions(phase):
    # ID, action, clé, projection (None = absente), succès attendu.
    if phase == "initial":
        return [("I01", "get-item", "001", "allowed", False)]
    if phase == "attributes":
        return [
            ("A01", "get-item", "001", "allowed", True),
            ("A02", "get-item", "001", "ssn", False),
            ("A03", "get-item", "001", None, False),
            ("A04", "query", "001", "allowed", True),
            ("A05", "scan", None, "allowed", True),
            ("A06", "scan", None, "ALL_ATTRIBUTES", False),
            ("A07", "put-item", "999", None, False),
            ("A08", "get-item", "002", "allowed", True),
            ("A09", "get-item", "001", "internal_note", False),
            ("A10", "update-item", "001", None, False),
            ("A11", "delete-item", "001", None, False),
        ]
    return [
        ("B01", "get-item", "001", "allowed", True),
        ("B02", "get-item", "002", "allowed", False),
        ("B03", "get-item", "001", "ssn", False),
        ("B04", "get-item", "001", None, False),
        ("B05", "query", "001", "allowed", True),
        ("B06", "query", "002", "allowed", False),
        ("B07", "scan", None, "allowed", False),
        ("B08", "put-item", "999", None, False),
        ("B09", "get-item", "001", "internal_note", False),
        ("B10", "update-item", "001", None, False),
        ("B11", "delete-item", "001", None, False),
    ]


def arguments(action, key, projection):
    args = ["--table-name", TABLE]
    if action in ("get-item", "update-item", "delete-item"):
        args += ["--key", key_json(key)]
    if action in ("get-item", "query", "scan"):
        args += ["--consistent-read"]
    if action == "query":
        args += ["--key-condition-expression", "#id = :pk", "--expression-attribute-values", json.dumps({":pk": {"S": key}})]
    aliases = {}
    if projection and projection != "ALL_ATTRIBUTES":
        names = ["id", "username", "email"] if projection == "allowed" else ["id", projection]
        aliases = {"#" + name: name for name in names}
        args += ["--projection-expression", ",".join(aliases)]
        if action in ("query", "scan"):
            args += ["--select", "SPECIFIC_ATTRIBUTES"]
    if action == "query":
        aliases["#id"] = "id"
    if aliases:
        args += ["--expression-attribute-names", json.dumps(aliases)]
    if projection == "ALL_ATTRIBUTES":
        args += ["--select", "ALL_ATTRIBUTES"]
    if action == "put-item":
        args += ["--item", json.dumps({"id": {"S": "999"}, "username": {"S": "test-refus"}}),
                 "--condition-expression", "attribute_not_exists(id)"]
    if action == "update-item":
        # Si une permission inattendue existe, aucune modification : condition toujours fausse
        # sur l'item 001 vérifié existant. ConditionFailed est FAIL, jamais EXPECTED DENY.
        args += ["--update-expression", "SET #note = :note", "--expression-attribute-names", '{"#note":"internal_note"}',
                 "--expression-attribute-values", '{":note":{"S":"Demonstration interne"}}',
                 "--condition-expression", "attribute_not_exists(id)"]
    if action == "delete-item":
        args += ["--condition-expression", "attribute_not_exists(id)"]
    return args


def classify(result, action, key, allow):
    if not allow:
        # L'erreur doit provenir de l'opération testée, pas d'un proxy ou STS.
        aws_name = {"get-item": "GetItem", "query": "Query", "scan": "Scan",
                    "put-item": "PutItem", "update-item": "UpdateItem", "delete-item": "DeleteItem"}[action]
        denied = result.returncode != 0 and error_code(result) in ("AccessDeniedException", "AccessDenied")
        denied = denied and f"when calling the {aws_name} operation" in result.stderr
        return "EXPECTED DENY" if denied else "FAIL"
    if result.returncode:
        return "FAIL"
    try:
        value = json.loads(result.stdout)
        if action == "get-item":
            correct = value.get("Item") == public_item(key)
        elif action == "query":
            correct = value.get("Items") == [public_item(key)] and value.get("Count") == 1
        else:
            correct = (sorted(value.get("Items", []), key=lambda v: v.get("id", {}).get("S", "")) ==
                       [public_item("001"), public_item("002")] and value.get("Count") == 2)
        return "PASS" if correct else "FAIL"
    except (ValueError, KeyError, TypeError, AttributeError):
        return "FAIL"


def matrix():
    records = {}
    for phase in ("initial", "attributes", "leadingkeys"):
        path = PROOFS / f"results-{phase}.json"
        if path.exists():
            records.update({r["id"]: r for r in json.loads(path.read_text())})
    text = "# Matrice des tests\n\nRésultats AWS uniquement. `NOT TESTED` signifie aucune observation. Les tests locaux ne valident pas IAM.\n\n"
    text += "| Étape | Identité | Action | Clé | Projection | Attendu | Observé | Statut | Preuve |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    admin_results = PROOFS / "results-admin.json"
    if admin_results.exists():
        for result in json.loads(admin_results.read_text()):
            fields = [result[key] for key in ("step", "identity", "action", "key", "projection", "expected", "observed", "status")]
            fields.append(f"[Preuve](../preuves/{result['proof']})")
            text += "| " + " | ".join(fields) + " |\n"
    for phase in ("initial", "attributes", "leadingkeys"):
        for ident, action, key, projection, allow in definitions(phase):
            record = records.get(ident, {})
            observed = record.get("observed", "Non exécuté")
            evidence = f"[Journal](../preuves/{record['proof']})" if record else "—"
            text += f"| {ident} ({phase}) | tp2a-reader | {action} | {key or '—'} | {projection or 'absente'} | {'SUCCESS' if allow else 'AccessDenied'} | {observed} | {record.get('status', 'NOT TESTED')} | {evidence} |\n"
    text += "\nA01–A07 et B01–B08 reprennent les scénarios de votre demande. A08–A11 et B09–B11 sont des contrôles complémentaires (002, internal_note, UpdateItem, DeleteItem). Les écritures Update/Delete portent une condition fausse pour éviter une altération si les droits sont trop larges ; une erreur ConditionalCheckFailedException est FAIL.\n\nLes retours réels et l'heure UTC sont conservés dans les journaux expurgés. Attendre la propagation IAM, puis relancer une suite si nécessaire : aucun échec n'est converti automatiquement en succès.\n"
    (ROOT / "docs/tests.md").write_text(text)


def proof(name, content):
    PROOFS.mkdir(exist_ok=True)
    path = PROOFS / name
    path.write_text(redact(content).rstrip() + "\n")
    path.chmod(0o644)


def all_passed(phase):
    path = PROOFS / f"results-{phase}.json"
    if not path.exists():
        return False
    records = json.loads(path.read_text())
    expected = {r[0] for r in definitions(phase)}
    return {r["id"] for r in records} == expected and all(r["status"] in ("PASS", "EXPECTED DENY") for r in records)


def run_tests(phase):
    manifest = state()
    guard(manifest)
    table(manifest)
    verify_items()
    require(manifest.get("phase") == phase, "Phase active différente de la suite demandée")
    reader(manifest, None if phase == "initial" else phase)
    identity("tp2a-reader", manifest)
    records = []
    write_json(PROOFS / f"results-{phase}.json", records)
    for ident, action, key, projection, allow in definitions(phase):
        result = aws("tp2a-reader", "dynamodb", action, *arguments(action, key, projection))
        status = classify(result, action, key, allow)
        name = f"{ident}.txt"
        observed = f"rc={result.returncode}, {error_code(result) or ('SUCCESS' if result.returncode == 0 else 'ERREUR CLI')}"
        proof(name, f"Date UTC : {now()}\nÉtape : {ident}\nProfil : tp2a-reader\nAction : {action}\nClé : {key}\nProjection : {projection}\nAttendu : {'SUCCESS' if allow else 'AccessDenied'}\nObservé : {observed}\nStatut : {status}\n\nstdout AWS réel :\n{result.stdout}\nstderr AWS réel :\n{result.stderr}\n")
        records.append(dict(id=ident, observed=observed, status=status, proof=name))
        write_json(PROOFS / f"results-{phase}.json", records)
        matrix()
        print(f"{ident}: {status} ({observed})")
        if action == "put-item" and result.returncode == 0:
            # Remédiation ciblée expressément demandée, avant arrêt définitif.
            guard(manifest)
            table(manifest)
            accidental = admin("dynamodb", "get-item", "--table-name", TABLE, "--key", key_json("999"), "--consistent-read").get("Item")
            expected = {"id": {"S": "999"}, "username": {"S": "test-refus"}}
            require(accidental == expected, "STOP FAIL : item 999 inattendu ; aucune suppression")
            admin("dynamodb", "delete-item", "--table-name", TABLE, "--key", key_json("999"),
                  "--condition-expression", "#u = :u AND attribute_exists(id)", "--expression-attribute-names", '{"#u":"username"}',
                  "--expression-attribute-values", '{":u":{"S":"test-refus"}}')
            require(not admin("dynamodb", "get-item", "--table-name", TABLE, "--key", key_json("999"), "--consistent-read").get("Item"), "Item 999 encore présent")
            proof("incident-999.txt", f"{now()} FAIL PutItem inattendu ; item 999 vérifié, supprimé par admin et absence observée.\n")
            raise Stop("STOP FAIL : PutItem a réussi ; seul l'item 999 de test a été retiré après vérification")
        require(status != "FAIL", f"STOP FAIL : {ident}. Inspecter le journal ; aucune suite automatique.")
    verify_items()


def check_env():
    for command in (["aws", "--version"], ["python3", "--version"], ["git", "--version"]):
        result = subprocess.run(command, text=True, capture_output=True)
        require(result.returncode == 0, f"Outil indisponible : {command[0]}")
        print((result.stdout or result.stderr).strip())
    print("PDF :", "présent (lecture à vérifier)" if PDF.is_file() else "ABSENT — docs/sources/ requis")
    print("Région configurée :", configured_region())
    value = identity("tp2a-admin")
    proof("environment.txt", f"{now()} STS tp2a-admin rc=0 ; compte et ARN vérifiés, masqués dans cette preuve.\nIdentité autre que root. Région : {configured_region()}\n")
    print("STS admin : identité non-root vérifiée ; compte et ARN expurgés dans preuves/environment.txt")


def preflight():
    source_required()
    require(not (PRIVATE / "manifest.json").exists(), "Manifest existant : ne pas réinitialiser l'appartenance")
    value = identity("tp2a-admin")
    region = configured_region()
    require(region == "eu-north-1", "Région différente de celle confirmée : faire confirmer les paramètres")
    absent("dynamodb", "describe-table", "ResourceNotFoundException", "--table-name", TABLE)
    absent("iam", "get-user", "NoSuchEntity", "--user-name", READER)
    manifest = dict(account=value["Account"], admin_arn=value["Arn"], region=region,
                    table_arn=f"arn:aws:dynamodb:{region}:{value['Account']}:table/{TABLE}",
                    lab_id=secrets.token_hex(12), checked_absent_at=now(), phase="initial")
    save(manifest)
    bind(manifest)
    proof("preflight.txt", f"{now()} STS non-root vérifié. Région {region}.\nTable {TABLE} : ResourceNotFoundException.\nUtilisateur {READER} : NoSuchEntity.\nAucune ressource créée.\n")
    print("Absence préalable observée ; manifest privé créé. Créer la table en console avec le tag :")
    print("TP4LabId =", manifest["lab_id"])


def register_table():
    source_required()
    manifest = state()
    guard(manifest)
    require(not manifest.get("table_id"), "Table déjà enregistrée ; utiliser verify-table")
    value = table(manifest)
    created = dt.datetime.fromisoformat(str(value["CreationDateTime"]).replace("Z", "+00:00"))
    checked = dt.datetime.fromisoformat(manifest["checked_absent_at"])
    require(created >= checked, "La table existait avant le préflight : arrêt")
    manifest["table_id"] = value["TableId"]
    save(manifest)
    proof("table-created.txt", f"{now()} DescribeTable rc=0 : {TABLE}, ACTIVE, id String, On-demand, Standard, sans index, Stream ni réplication.\nMarqueur d'appartenance vérifié.\n")
    print("Table ACTIVE enregistrée avec son identifiant unique.")


def seed():
    source_required()
    manifest = state()
    guard(manifest)
    require(manifest.get("table_id"), "Enregistrer la table d'abord")
    table(manifest)
    values = admin("dynamodb", "scan", "--table-name", TABLE, "--consistent-read").get("Items", [])
    require(all(v in (item("001"), item("002")) for v in values), "Données inattendues : aucune écriture")
    for key in ("001", "002"):
        if item(key) not in values:
            admin("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item(key)),
                  "--condition-expression", "attribute_not_exists(id)")
    verify_items()
    proof("items.txt", f"{now()} Scan et GetItem admin rc=0 : exactement les items fictifs 001 et 002 ; cinq attributs String chacun, valeurs conformes.\n")
    print("Deux items fictifs vérifiés par Scan et GetItem administrateur.")


def create_reader():
    source_required()
    manifest = state()
    guard(manifest)
    table(manifest)
    require(not manifest.get("user_id"), "Utilisateur déjà enregistré")
    absent("iam", "get-user", "NoSuchEntity", "--user-name", READER)
    value = admin("iam", "create-user", "--user-name", READER, "--tags",
                  f"Key=TP4LabId,Value={manifest['lab_id']}")["User"]
    manifest["user_id"] = value["UserId"]
    save(manifest)
    keys = reader(manifest, require_key=False)
    require(not keys, "Clé inattendue après création : inspecter avant configuration")
    proof("reader-created.txt", f"{now()} CreateUser rc=0 : {READER}.\nGetUser : UserId et tag d'appartenance conformes au manifest.\nListGroupsForUser, ListAttachedUserPolicies, ListUserPolicies : listes vides ; aucune permissions boundary.\nAucun accès console créé ; état GetLoginProfile : {'PARTIAL (SCP)' if manifest.get('audit_limitations', {}).get('get-login-profile') else 'absence observée'}.\nListAccessKeys : liste vide ; aucune clé créée par l'agent.\nProfil lecteur à configurer manuellement avant tout test DynamoDB.\n")
    print("Utilisateur créé sans permission ni accès console. MANUAL READER KEY REQUIRED : voir README.")


def apply_policy(phase):
    source_required()
    manifest = state()
    guard(manifest)
    table(manifest)
    previous = "initial" if phase == "attributes" else "attributes"
    require(manifest["phase"] == previous, "Transition inattendue")
    require(all_passed(previous), "La suite précédente doit avoir été entièrement observée et validée")
    reader(manifest, None if previous == "initial" else previous)
    bind(manifest)
    path = PRIVATE / f"policies/fgac-{phase}.json"
    # Même nom inline : remplacement, jamais deux Allow cumulés.
    admin("iam", "put-user-policy", "--user-name", READER, "--policy-name", POLICY,
          "--policy-document", "file://" + str(path))
    manifest["phase"] = phase
    manifest["policy_applied_at"] = now()
    save(manifest)
    reader(manifest, phase)
    proof(f"policy-{phase}.txt", f"{now()} PutUserPolicy rc=0 ; TP2AFGAC remplacée.\nGetUserPolicy conforme ; aucun groupe, managed policy, autre policy inline ou policy de ressource.\nAucun accès console créé par nos opérations ; vérification GetLoginProfile : {'PARTIAL (SCP)' if manifest.get('audit_limitations', {}).get('get-login-profile') else 'absence observée'}.\nARN exact vérifié, masqué dans le dépôt.\n")
    print("Policy relue et vérifiée. Attendre la propagation IAM (par exemple 30 secondes), puis lancer les tests ; aucun PASS anticipé.")


def verify_table():
    manifest = state()
    guard(manifest)
    table(manifest)
    verify_items()
    print("DescribeTable + GetItem 001/002 + Scan admin : conformité observée.")


def cleanup_check():
    manifest = state()
    guard(manifest)
    table(manifest)
    verify_items()
    reader(manifest, manifest["phase"] if manifest["phase"] != "initial" else None)
    require(manifest["phase"] == "leadingkeys" and all(all_passed(p) for p in ("initial", "attributes", "leadingkeys")), "Tests incomplets : nettoyage final non prêt")
    print("READY_FOR_CLEANUP — ressources identifiées ; aucune suppression. Attendre l'instruction explicite CLEANUP.")


def cleanup(authorization):
    require(authorization == "CLEANUP", "Autorisation explicite CLEANUP requise ; aucune suppression")
    manifest = state()
    guard(manifest)
    require(manifest.get("table_id") and manifest.get("user_id"), "Appartenance non enregistrée")
    require(all(all_passed(p) for p in ("initial", "attributes", "leadingkeys")), "Suites incomplètes : examiner avant nettoyage")
    # Vérifier les deux ressources avant la première suppression. Reprise possible après interruption.
    user_result = aws("tp2a-admin", "iam", "get-user", "--user-name", READER)
    user_exists = user_result.returncode == 0
    if user_exists:
        names = admin("iam", "list-user-policies", "--user-name", READER)["PolicyNames"]
        require(names in ([], [POLICY]), "Policy inconnue : arrêt")
        keys = reader(manifest, "leadingkeys" if names else None, require_key=False)
    else:
        require(error_code(user_result) == "NoSuchEntity", "Absence utilisateur non démontrée")
        keys = []
    table_result = aws("tp2a-admin", "dynamodb", "describe-table", "--table-name", TABLE)
    table_exists = table_result.returncode == 0
    if table_exists:
        table(manifest)
    else:
        require(error_code(table_result) == "ResourceNotFoundException", "Absence table non démontrée")
    if user_exists:
        for entry in keys:
            # L'identifiant n'est transmis qu'au processus AWS, jamais aux journaux.
            admin("iam", "update-access-key", "--user-name", READER, "--access-key-id", entry["AccessKeyId"], "--status", "Inactive")
            admin("iam", "delete-access-key", "--user-name", READER, "--access-key-id", entry["AccessKeyId"])
        require(not admin("iam", "list-access-keys", "--user-name", READER)["AccessKeyMetadata"], "Clé encore présente")
        if names:
            admin("iam", "delete-user-policy", "--user-name", READER, "--policy-name", POLICY)
        admin("iam", "delete-user", "--user-name", READER)
    if table_exists:
        admin("dynamodb", "delete-table", "--table-name", TABLE)
        # Attente courte par interrogation, aucun journal de données/identifiants.
        for attempt in range(24):
            result = aws("tp2a-admin", "dynamodb", "describe-table", "--table-name", TABLE)
            if result.returncode != 0 and error_code(result) == "ResourceNotFoundException":
                break
            require(result.returncode == 0, "Erreur AWS durant la vérification de suppression")
            time.sleep(5)
        else:
            raise Stop("Table encore visible ; nettoyage PARTIAL, conserver .secrets")
    absent("dynamodb", "describe-table", "ResourceNotFoundException", "--table-name", TABLE)
    absent("iam", "get-user", "NoSuchEntity", "--user-name", READER)
    # La session de ce seul profil est terminée ; aucun logout --all.
    result = subprocess.run(["aws", "logout", "--profile", "tp2a-admin"], env=isolated(), text=True, capture_output=True)
    require(result.returncode == 0, "Ressources absentes ; logout a échoué, conserver .secrets")
    require(PRIVATE == Path("/home/gatta/Downloads/TP4/.secrets") and not PRIVATE.is_symlink(), "Chemin de secrets non conforme")
    shutil.rmtree(PRIVATE)
    proof("cleanup.txt", f"{now()} CLEANUP PASS\nAccess Key désactivée puis supprimée ; policy TP2AFGAC et utilisateur supprimés.\nTable : ResourceNotFoundException observée. Utilisateur : NoSuchEntity observée.\nSession tp2a-admin terminée ; seul .secrets du TP4 supprimé. Builder ID et MFA conservés.\n")
    print("CLEANUP PASS — absences observées ; session terminée ; secrets locaux supprimés.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-env", "preflight", "register-table", "seed", "create-reader", "verify-table", "apply-attributes", "apply-leadingkeys", "test-initial", "test-attributes", "test-leadingkeys", "matrix", "cleanup-check", "cleanup"])
    parser.add_argument("authorization", nargs="?")
    args = parser.parse_args()
    try:
        if args.command.startswith("test-"):
            run_tests(args.command.removeprefix("test-"))
        elif args.command.startswith("apply-"):
            apply_policy(args.command.removeprefix("apply-"))
        elif args.command == "cleanup":
            cleanup(args.authorization)
        else:
            {"check-env": check_env, "preflight": preflight, "register-table": register_table,
             "seed": seed, "create-reader": create_reader, "verify-table": verify_table,
             "matrix": matrix, "cleanup-check": cleanup_check}[args.command]()
    except (Stop, ValueError, OSError, KeyError, TypeError) as exc:
        print("ARRÊT : " + redact(str(exc)), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
