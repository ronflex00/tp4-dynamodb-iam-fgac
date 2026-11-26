#!/usr/bin/env python3
"""Expurge des textes AWS ; ne remplace pas la revue visuelle des captures."""
import re
import sys


def redact(text):
    # Les réponses brutes d'identité restent privées ; aucune clé n'est journalisée.
    text = re.sub(r"\b\d{12}\b", "[COMPTE_MASQUÉ]", text)
    text = re.sub(r"\b(?:AKIA|ASIA|AIDA|AROA)[A-Z0-9]{16}\b", "[IDENTIFIANT_MASQUÉ]", text)
    text = re.sub(r'(?i)("?(?:SecretAccessKey|SessionToken|AccessKeyId|Authorization|Cookie|aws_secret_access_key|aws_session_token|aws_access_key_id)"?\s*[:=]\s*)("[^"\n]*"|[^\s,]+)', r'\1"[SECRET_MASQUÉ]"', text)
    text = re.sub(r'https?://[^\s"<>]+\?[^\s"<>]+', '[URL_AVEC_PARAMÈTRES_MASQUÉE]', text)
    text = re.sub(r'(arn:aws:sts::\[COMPTE_MASQUÉ\]:assumed-role/[^/\s]+/)[^\s"<>]+', r'\1[SESSION_MASQUÉE]', text)
    text = re.sub(r'arn:aws:organizations::\[COMPTE_MASQUÉ\]:policy/[^\s"<>]+', '[SCP_MASQUÉE]', text)
    text = re.sub(r'(?i)(authorization id:\s*)[a-z0-9-]+', r'\1[IDENTIFIANT_DIAGNOSTIC_MASQUÉ]', text)
    return text


if __name__ == "__main__":
    sys.stdout.write(redact(sys.stdin.read()))
