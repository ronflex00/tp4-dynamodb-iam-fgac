# TP4 EXECUTION REPORT

État au 26 novembre 2026. Les observations CLI proviennent du profil isolé tp2a-admin, dont le compte et le principal sont conformes au manifest et distincts de root. La région est eu-north-1.

| Contrôle | État observé |
| --- | --- |
| Table DynamoDB | ACTIVE, DescribeTable rc=0 ; id String, Standard, On-demand, options conformes et appartenance enregistrée |
| Items 001/002 | Créés par CLI autorisée, sans écrasement ; Scan admin et GetItem 001/002 confirment exactement les valeurs fictives |
| Utilisateur IAM | tp2a-dynamo-reader créé ; aucun groupe, policy inline/managed, permissions boundary ou clé au contrôle initial |
| Profil reader | Région eu-north-1 et sortie JSON préparées ; saisie manuelle de la clé et confirmation attendues |
| Refus initial | NOT TESTED |
| Projection autorisée | NOT TESTED |
| Attribut sensible refusé | NOT TESTED |
| Lecture complète refusée | NOT TESTED |
| Query | NOT TESTED |
| Scan initial | NOT TESTED |
| PutItem refusé | NOT TESTED |
| LeadingKeys 001 | NOT TESTED |
| Accès 002 refusé | NOT TESTED |
| Scan final refusé | NOT TESTED |
| Captures | 01-table-created.png et 02-items.png : captures réelles de réponses AWS dans des terminaux dédiés, revues visuellement |
| Documentation | PDF lu, provenance et conformité documentées ; README, huit réponses et compte-rendu actualisés |
| Tests locaux | Dix-huit tests hors ligne réussis ; modèles JSON et JSON privés avec ARN exact validés |
| Git | Modifications conservées dans le dépôt local ; aucune publication |
| Audit secrets | Fichiers privés exclus ; compte masqué dans les journaux ; audit local avant commit |
| Ressources AWS restantes | Table NovaUsersTP2A, items 001/002 et utilisateur tp2a-dynamo-reader conservés ; aucune policy FGAC posée ni suppression exécutée |

**FINAL STATUS : PARTIAL**

## Limite d'audit observée

GetLoginProfile, exécuté avec tp2a-admin, répond AccessDenied (rc=254) avec un **Deny explicite dans une SCP** sur iam:GetLoginProfile. Aucun login console n'a été créé par nos commandes ; son absence n'a pas pu être confirmée par cette API. Le contrôle D05 reste PARTIAL. Aucune SCP, permission ou offre AWS n'a été modifiée. Ce résultat ne valide ni le refus initial DynamoDB ni les droits FGAC du reader. Les autres lectures IAM ont réussi et constaté les listes vides.

## Intervention humaine actuelle

Créer l'unique clé technique dans IAM et la saisir uniquement dans le terminal personnel, selon [la procédure](configuration-reader.md). Aucun secret ni sortie STS n'est demandé dans la conversation. Confirmer seulement « profil reader configuré ». L'agent vérifiera alors l'identité et lancera le refus initial avant toute policy, puis les suites Attributes et LeadingKeys en remplaçant la même inline policy.

Le blocage précédent est résolu : l'utilisateur a indiqué que la table n'avait pas encore été créée lors du [diagnostic historique](../preuves/table-recheck.txt), puis l'a réellement créée. Elle est maintenant retrouvée ACTIVE dans le compte et la région du manifest.

Preuves : [table](../preuves/01-table-created.png), [items](../preuves/02-items.png), [création lecteur](../preuves/reader-created.txt), [audit IAM](../preuves/reader-audit.txt), [limite SCP](../preuves/audit-login-profile.txt). Voir aussi [matrice](tests.md) et [conformité au PDF](sources/README.md). Aucun nettoyage n'est autorisé.
