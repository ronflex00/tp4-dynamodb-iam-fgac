# TP4 — Limiter les données DynamoDB avec IAM FGAC

Nova Services · Gouvernance des identités et des habilitations · Formateur indiqué : Mohammad Jabbari.

**État : PARTIAL — table ACTIVE, items vérifiés, lecteur créé ; clé technique manuelle en attente.** Le profil administrateur isolé confirme la table en eu-north-1 et les deux items exacts. Le lecteur ne possède aucune policy ni groupe ; zéro clé était présent à sa création. Deux captures réelles sont conservées. Les tests reader attendent ses credentials ; aucun nettoyage ni publication n'a été lancé. L'audit GetLoginProfile est PARTIAL car une SCP refuse cette lecture de métadonnées.

## Source et périmètre

Le [sujet officiel et le rapprochement détaillé](docs/sources/README.md) ont été lus : dix pages, mêmes noms, données, première policy et huit questions. Le Sid initial a été aligné sur ReadPublicAttributes. Le PDF demande la création de la table et des deux items en console ; après avoir annoncé la table créée en console, l'utilisateur a explicitement autorisé l'insertion automatique des items avec tp2a-admin. Cette variante sera distinguée de la méthode du professeur. Le PDF demande deux versions JSON mais fournit seulement la première ; la seconde est une construction technique complémentaire.

Les JSON versionnés contiennent `REGION` et `ACCOUNT_ID` : **modèles non déployables**. Les deux JSON avec l'ARN exact vérifié sont maintenant disponibles uniquement dans `.secrets/policies/`, pour ne pas publier l'identifiant de compte. Leur validation locale a réussi ; elle ne constitue pas un test AWS.

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

## Étape actuelle : clé technique manuelle

Le PDF est lu, le compte et le principal non-root sont conformes au manifest, la région est eu-north-1. La table créée par l'utilisateur est désormais retrouvée et ACTIVE ; son schéma, ses options, son ARN exact et sa date de création sont vérifiés. Le tag TP4LabId a été ajouté à cette seule table, puis le TableId enregistré. **Ne pas relancer preflight ni effacer le manifest.**

Le blocage précédent est résolu : l'utilisateur a confirmé que la table n'avait pas encore été créée lors du premier diagnostic. L'agent a inséré 001 et 002 par CLI, sans écrasement, puis vérifié les cinq attributs String exacts et l'absence d'autres items. `tp2a-dynamo-reader` est créé, sans groupe ni policy. Son profil local a uniquement la région et la sortie JSON configurées ; aucune clé n'a été créée par l'agent.

Suivre [la procédure manuelle de clé et configuration](docs/configuration-reader.md), puis confirmer simplement « profil reader configuré ». L'agent vérifiera STS et le refus implicite avant de poser toute policy. Le Deny SCP sur GetLoginProfile est [consigné séparément](preuves/audit-login-profile.txt) et n'est pas un test de refus DynamoDB.

## Déroulement du laboratoire

1. **Effectué :** dix pages lues, exigences rapprochées et empreinte consignée. Aucun script ne considère la simple présence du PDF comme une lecture.
2. **Effectué :** `python3 scripts/lab.py preflight` a vérifié l'identité, la région et l'absence exacte des ressources. Le manifest privé conserve compte, principal, ARN et marqueur d'appartenance. Toute ressource apparaissant ensuite doit être inspectée et reconnue avant reprise.
3. **Effectué :** table créée dans la console AWS par l'utilisateur, vérifiée ACTIVE par CLI : `NovaUsersTP2A`, partition `id` String, aucune sort key, Standard, On-demand, aucun index, Stream, réplication, PITR ou sauvegarde supplémentaire. Tag complémentaire TP4LabId ajouté et observé ; TableId enregistré.
4. **Effectué :** `register-table` puis `seed`. Les insertions conditionnelles par CLI, autorisées par l'utilisateur, ont créé les deux items exacts. Scan administrateur et GetItem 001/002 ont confirmé leurs données ; deux captures réelles sont disponibles. La table n'a pas de policy de ressource.
5. **Effectué :** `create-reader` a créé `tp2a-dynamo-reader`. Les listes de groupes, policies inline/managed et clés sont vides. Aucun accès console créé par nos opérations. L'API GetLoginProfile est explicitement refusée par une SCP au rôle admin : son contrôle d'absence reste PARTIAL, sans modification des restrictions AWS.
6. **Étape humaine :** IAM → Users → tp2a-dynamo-reader → Security credentials → Access keys → Create access key → CLI. Créer une seule clé. Dans votre terminal personnel, hors de Codex, après avoir sourcé le script Fish, saisir `aws configure --profile tp2a-reader` ; région `eu-north-1`, sortie `json`. Saisir directement les secrets au prompt. Ne jamais les coller dans la conversation, une commande, une capture ou Git. Appliquer `chmod 600 .secrets/config .secrets/credentials`. STS sera contrôlé par la suite initiale, sans exposer son ARN complet.
7. Exécuter `python3 scripts/lab.py test-initial` : seul un véritable AccessDenied du GetItem projeté est accepté. STS n'atteste pas les droits DynamoDB.
8. Exécuter `python3 scripts/lab.py apply-attributes`. La seule inline policy `TP2AFGAC` est installée. Attendre la propagation IAM (par exemple 30 secondes), puis `bash scripts/test-attributes.sh`. Tout échec arrête la suite et reste FAIL. Une relance remplace la dernière matrice de cette phase ; conserver ailleurs une copie expurgée si l'historique de propagation est utile.
9. Après validation complète de l'étape A, exécuter `python3 scripts/lab.py apply-leadingkeys`. **Le même nom inline est remplacé**, les deux permissions ne sont jamais cumulées. Attendre la propagation, puis `bash scripts/test-leadingkeys.sh`.
10. Lire [la matrice](docs/tests.md), effectuer les vraies captures non sensibles et produire le rapport pré-nettoyage. `bash scripts/cleanup-check.sh` vérifie les préconditions sans supprimer. **S'arrêter et attendre l'instruction explicite `CLEANUP`.**

Les appels AWS sont faits par `subprocess` sans shell ni boto3. L'audit inspecte groupes, managed policies, policies inline, permission boundary et policy de ressource. GetLoginProfile fait l'objet d'une tentative réelle ; le refus explicite par SCP est enregistré PARTIAL, sans être assimilé à une absence de login ni à un test reader. Tout autre problème d'audit arrête les scripts. Aucune élévation des droits ni modification de SCP n'est prévue. Les tests réels font foi pour les droits DynamoDB.

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

Les logs expurgés dans [preuves/](preuves/README.md) sont versionnables. Les captures réelles 01-table-created.png et 02-items.png ont été prises dans des fenêtres de terminal dédiées affichant de nouvelles réponses AWS, puis revues visuellement. Les autres captures attendent les tests. `scripts/show-proof.py` prépare ces affichages sans numéro de compte ni ARN. Git est local uniquement ; aucune publication autorisée.

Voir [compte-rendu](compte-rendu.md), [architecture](docs/architecture.md), [questions](docs/questions.md) et [nettoyage](docs/cleanup.md).
