# TP4 — Limiter les données DynamoDB avec IAM FGAC

Nova Services · Gouvernance des identités et des habilitations · Formateur indiqué : Mohammad Jabbari.

**État : PARTIAL — préparation locale réalisée, PDF absent, tests DynamoDB non exécutés.** La connexion `tp2a-admin` et la vérification STS ont réussi le 26 novembre 2026. Aucun résultat IAM DynamoDB n'est anticipé. Aucune ressource AWS n'a été créée par cette préparation. Aucun nettoyage n'a été lancé.

## Source et périmètre

La demande fournie sert aux préparatifs. Le sujet officiel reste à copier dans [docs/sources/](docs/sources/README.md) sous le nom `TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf` (10 pages). Les exigences du professeur sont **non vérifiées** tant que ce PDF n'a pas été lu. La première policy est le modèle demandé dans votre texte, à comparer au PDF. La seconde est une solution technique complémentaire documentée avec les sources AWS.

Les JSON versionnés contiennent `REGION` et `ACCOUNT_ID` : **modèles non déployables**. `preflight` fabrique les deux JSON avec l'ARN exact vérifié, uniquement dans `.secrets/policies/`, pour ne pas publier l'identifiant de compte. Une validation locale ne constitue pas un test AWS.

## Environnement isolé

Fish (Arch Linux), depuis le dossier TP4 :

```fish
source scripts/use-lab-env.fish
aws --version
python3 --version
git --version
bash scripts/check-env.sh
```

Bash :

```bash
source scripts/use-lab-env.sh
bash scripts/check-env.sh
```

`AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE` et `AWS_LOGIN_CACHE_DIRECTORY` désignent exclusivement `.secrets/`. `AWS_PAGER` est vide : AWS attend une commande dans cette variable, pas un répertoire. Les identifiants d'environnement et endpoints personnalisés sont retirés pour éviter d'utiliser une autre identité. Les scripts d'orchestration rétablissent eux-mêmes cet isolement. Ne jamais activer `set -x` ou `aws --debug`.

Paramètres confirmés par l'utilisateur le 26 novembre 2026 à partir du TP3 : Blank Canvas, AWS Free plan, eu-north-1 (Stockholm), MFA Builder ID TOTP actif, même compte annoncé que TP3. Le plan, le MFA et la correspondance historique avec TP3 n'ont pas été vérifiés par STS. Le MFA Builder ID ne prouve pas à lui seul le MFA d'un principal IAM AWS.

Le profil admin utilise `aws login` avec des identifiants temporaires, aucune clé admin permanente. Région et sortie JSON ont été configurées dans le seul fichier isolé. Après expiration, Codex peut relancer `aws login --profile tp2a-admin` dans cet environnement et attendre l'intervention navigateur ; ne pas partager l'URL d'autorisation ni son code. STS refuse root dans les scripts.

## Déroulement après réception du sujet

1. Lire les dix pages, rapprocher les exigences, compléter [la provenance](docs/sources/README.md) et consigner l'empreinte du PDF comme indiqué dans ce document. Aucun script ne considère la simple présence du PDF comme une lecture.
2. Exécuter `python3 scripts/lab.py preflight`. Cette commande vérifie l'identité, la région, l'absence exacte de la table et de l'utilisateur. Si une ressource existe ou qu'une API est refusée : arrêt et inspection, aucun écrasement. Le manifest privé conserve compte, principal, ARN et marqueur d'appartenance. La vérification en lecture seule déjà faite doit être renouvelée à cette étape.
3. Créer la table **dans la console AWS** : DynamoDB → Tables → Create table. Nom `NovaUsersTP2A`, partition `id` String, aucune sort key, Standard, On-demand, aucun index, Stream, réplication ou sauvegarde supplémentaire. Ajouter le tag `TP4LabId` avec la valeur affichée par `preflight`. Attendre `ACTIVE`. Le tag est un garde-fou technique complémentaire à votre demande.
4. Exécuter `python3 scripts/lab.py register-table`, puis `python3 scripts/lab.py seed` et `bash scripts/verify-table.sh`. Le script vérifie aussi l'absence de policy de ressource, conserve le TableId, insère seulement les deux items fictifs manquants et ne remplace jamais un item existant. Inspecter en console l'absence de sauvegarde supplémentaire.
5. Exécuter `python3 scripts/lab.py create-reader`. L'utilisateur exact `tp2a-dynamo-reader` reçoit un marqueur d'appartenance, aucune permission, aucun groupe, aucune clé et aucun login console.
6. **Étape humaine :** IAM → Users → tp2a-dynamo-reader → Security credentials → Access keys → Create access key → CLI. Créer une seule clé. Dans votre terminal personnel, hors de Codex, après avoir sourcé le script Fish, saisir `aws configure --profile tp2a-reader` ; région `eu-north-1`, sortie `json`. Saisir directement les secrets au prompt. Ne jamais les coller dans la conversation, une commande, une capture ou Git. Appliquer `chmod 600 .secrets/config .secrets/credentials`. STS sera contrôlé par la suite initiale, sans exposer son ARN complet.
7. Exécuter `python3 scripts/lab.py test-initial` : seul un véritable AccessDenied du GetItem projeté est accepté. STS n'atteste pas les droits DynamoDB.
8. Exécuter `python3 scripts/lab.py apply-attributes`. La seule inline policy `TP2AFGAC` est installée. Attendre la propagation IAM (par exemple 30 secondes), puis `bash scripts/test-attributes.sh`. Tout échec arrête la suite et reste FAIL. Une relance remplace la dernière matrice de cette phase ; conserver ailleurs une copie expurgée si l'historique de propagation est utile.
9. Après validation complète de l'étape A, exécuter `python3 scripts/lab.py apply-leadingkeys`. **Le même nom inline est remplacé**, les deux permissions ne sont jamais cumulées. Attendre la propagation, puis `bash scripts/test-leadingkeys.sh`.
10. Lire [la matrice](docs/tests.md), effectuer les vraies captures non sensibles et produire le rapport pré-nettoyage. `bash scripts/cleanup-check.sh` vérifie les préconditions sans supprimer. **S'arrêter et attendre l'instruction explicite `CLEANUP`.**

Les appels AWS sont faits par `subprocess` sans shell ni boto3. L'audit inspecte groupes, managed policies, policies inline, login console, permission boundary et policy de ressource de la table. Les restrictions d'organisation restent hors du périmètre vérifiable par ce seul audit ; les tests réels font foi. Aucune élévation automatique des droits n'est prévue si l'identité actuelle manque de permissions.

## Données fictives

| id (String) | username | email | ssn | internal_note |
| --- | --- | --- | --- | --- |
| 001 | alice | alice@example.com | FICTIF-001 | Demonstration interne |
| 002 | bob | bob@example.com | FICTIF-002 | Demonstration interne |

Tous les attributs sont String. Les zéros initiaux sont conservés. Le support lit `id`, `username`, `email` sur les deux items en A, puis seulement sur `001` en B. `ssn`, `internal_note`, lecture sans projection et écritures doivent être refusés.

## Vérification locale

```bash
python3 scripts/validate-policies.py --templates
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/validate-project.py
git diff --check
git status --short
```

Après `preflight`, `python3 scripts/validate-policies.py` valide les deux policies privées avec l'ARN réel. Pour le JSON et le Markdown, le vérificateur local contrôle la structure, les liens locaux et les clôtures de blocs ; il ne remplace pas une revue de fond. Les tests unitaires utilisent des réponses synthétiques et ne produisent aucune preuve AWS.

Le contrôle Markdown utilise `markdown-it-py`, déjà disponible dans cet environnement. Les scripts AWS et la validation des policies utilisent uniquement la bibliothèque standard Python et AWS CLI. Les commits préparatoires portent l'auteur technique local `Codex <codex@local.invalid>` ; aucune identité personnelle n'est configurée globalement.

Les logs expurgés dans [preuves/](preuves/README.md) sont versionnables. Les JSON de résultats, la matrice et les captures doivent être relus avant un commit. Les captures PNG restent absentes tant qu'aucune vraie capture n'a été prise. Git est local uniquement ; aucune publication autorisée.

Voir [compte-rendu](compte-rendu.md), [architecture](docs/architecture.md), [questions](docs/questions.md) et [nettoyage](docs/cleanup.md).
