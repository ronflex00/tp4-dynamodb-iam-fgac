# Sources et traçabilité

## Sujet officiel manquant

Emplacement attendu : `docs/sources/TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf`.

Nombre de pages annoncé : 10. **Le PDF n'est pas présent lors de la préparation du 26 novembre 2026.** Il faut le copier ici. Aucun contenu ou exigence du professeur n'a été reconstitué à sa place.

Après réception : lire intégralement le document avec un lecteur PDF ou `pdftotext -layout`, comparer les noms, les scénarios, les huit questions et la première policy avec les préparatifs. Signaler et corriger tout écart avant création. L'extraction de texte numérique ne demande pas de service OCR ni d'envoi vers AWS.

Consigner ensuite ici : date de lecture, nombre de pages, empreinte SHA256 et écarts éventuels. La lecture et ce rapprochement restent **À FAIRE**. Une fois réellement effectués, enregistrer l'empreinte privée pour débloquer les scripts :

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path
pdf = Path('docs/sources/TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf')
Path('.secrets/source-reviewed.sha256').write_text(hashlib.sha256(pdf.read_bytes()).hexdigest() + '\n')
PY
```

Ce marqueur est une attestation opérateur de lecture, pas une preuve automatique de conformité pédagogique.

## Consignes reçues

Le texte fourni dans la conversation demande l'ensemble de l'arborescence, les deux policies, les tests, la gouvernance, l'isolement des secrets et l'arrêt avant nettoyage. Ces éléments sont préparés. Le texte annonce que la première policy vient du PDF : cela reste à comparer. La seconde policy `LeadingKeys`, l'exclusion de Scan, les contrôles supplémentaires et les marqueurs d'appartenance constituent la solution technique complémentaire.

## Documentation primaire consultée le 26 novembre 2026

- [DynamoDB : conditions FGAC, Attributes et LeadingKeys](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html).
- [IAM : opérateurs de condition et contrôle Null](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html).
- [AWS CLI : connexion temporaire, cache isolé et logout](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
- [IAM : logique d'évaluation des policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html).
- [IAM : rôles et identifiants temporaires](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

Les sources AWS justifient la technique et ne remplacent pas le sujet du professeur.
