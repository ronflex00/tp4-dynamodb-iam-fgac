# TP4 AWS DYNAMODB FGAC — FINAL REPORT

Date : 26 novembre 2026 · Projet : `/home/gatta/Downloads/TP4` · Région : `eu-north-1`.

## Tests AWS

23 scénarios reader observés conformes avant nettoyage : **6 PASS** et **17 EXPECTED DENY** (AccessDeniedException, rc=254). Aucun test requis non exécuté ni FAIL. Les résultats restent disponibles dans `docs/tests.md`, les journaux et JSON conservés. Le contrôle d’audit administratif GetLoginProfile reste **PARTIAL** : refus explicite SCP. Cette limite n’est pas comptée comme test DynamoDB.

## Tests locaux

**20 tests unitaires réussis**. Les validations de projet, modèles de policies, liens Markdown, syntaxes Bash/Fish, images et audit statique des secrets sont consignées dans `preuves/local-validation.txt`. La comparaison des valeurs secrètes aux fichiers suivis a été faite en mémoire avant suppression de `.secrets`; aucune valeur n’a été affichée.

## FGAC

- **Attributes FGAC :** conforme aux résultats réellement observés. Projections `id`, `username`, `email` autorisées ; `ssn`, `internal_note` et absence de projection refusés. GetItem/Query/Scan projeté sur 001/002 et refus de Scan ALL_ATTRIBUTES/PutItem conformes à la première policy.
- **LeadingKeys FGAC :** conforme aux résultats observés. GetItem/Query projetés sur 001 autorisés ; accès à 002, attributs sensibles, projection absente, Scan, PutItem, UpdateItem et DeleteItem refusés.

## Nettoyage autorisé

| Ressource / session | Résultat observé |
| --- | --- |
| Access Key unique de `tp2a-dynamo-reader` | Désactivée, état Inactive observé, puis supprimée ; liste vide |
| Policy inline `TP2AFGAC` | Supprimée ; GetUserPolicy → NoSuchEntity |
| IAM user `tp2a-dynamo-reader` | Supprimé ; GetUser → NoSuchEntity, absent de ListUsers |
| Table `NovaUsersTP2A` | Suppression achevée ; DescribeTable → ResourceNotFoundException, absente de ListTables |
| Session `tp2a-admin` | `aws logout` rc=0 ; cache de login vide |
| Secrets locaux | Seul `/home/gatta/Downloads/TP4/.secrets/` supprimé et absence vérifiée |

Aucune ressource extérieure au TP4 n’a été modifiée. `~/.aws`, le compte AWS, Builder ID et MFA ont été conservés. Aucune SCP ou rôle `/managed/` modifié. Aucune publication GitHub.

## Captures et documentation

13 captures réelles conservées : les 12 preuves initiales et [13-cleanup.png](../preuves/13-cleanup.png). Les preuves d’origine ont été empreintées et archivées avant la première suppression ; voir [manifeste](../preuves/preservation-before-cleanup.json), [journal de nettoyage](../preuves/cleanup.txt) et [index des preuves](../preuves/README.md).

Documentation mise à jour : README, compte-rendu, tests, protocole cleanup, rapport pré-cleanup historique et ce rapport final.

## Git

Commit prévu : `docs: finalize TP4 DynamoDB FGAC and cleanup`. Working tree vérifié après commit. Aucun push.

## Ressources AWS restantes

Aucune ressource créée pour le TP4 ne reste active. Cette affirmation est limitée à l’utilisateur, la policy, la clé et la table inventoriés du laboratoire.

**FINAL STATUS : COMPLETE**
