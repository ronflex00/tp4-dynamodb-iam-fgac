# TP4 EXECUTION REPORT

État au 26 novembre 2026. Les observations CLI proviennent du profil isolé tp2a-admin, dont le compte et le principal sont conformes au manifest et distincts de root. La région est eu-north-1.

| Contrôle | État observé |
| --- | --- |
| Table DynamoDB | Déclarée ACTIVE en console par l'utilisateur ; deux DescribeTable : ResourceNotFoundException, rc=254 ; ListTables : zéro table, rc=0 |
| Items 001/002 | Non créés ; insertion suspendue tant que la table n'est pas retrouvée |
| Utilisateur IAM | Absent au préflight : NoSuchEntity ; aucune création lancée |
| Profil reader | Non configuré |
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
| Captures | Aucune capture ; journaux CLI réels et expurgés disponibles |
| Documentation | PDF lu, provenance et conformité documentées ; README, huit réponses et compte-rendu actualisés |
| Tests locaux | Quinze tests hors ligne réussis ; modèles JSON et JSON privés avec ARN exact validés |
| Git | Modifications conservées dans le dépôt local ; aucune publication |
| Audit secrets | Fichiers privés exclus ; compte masqué dans les journaux ; audit local avant commit |
| Ressources AWS restantes | Aucune table visible dans le compte/région du profil ; table déclarée en console à localiser ; aucune suppression effectuée |

**FINAL STATUS : PARTIAL**

## Cause à résoudre avant reprise

L'état console déclaré et l'observation CLI ne correspondent pas. Les hypothèses sont un autre compte/projet dans la console, une autre région, un nom différent ou une création qui reste à terminer. Aucune de ces hypothèses n'est affirmée comme cause établie. `ResourceNotFoundException` n'est ni un AccessDenied IAM attendu ni une preuve d'accès FGAC.

L'utilisateur doit comparer les contextes sans communiquer le numéro de compte ici. Pour vérifier localement le compte du profil, dans son terminal personnel uniquement :

```fish
source scripts/use-lab-env.fish
aws sts get-caller-identity --profile tp2a-admin --query Account --output text
```

Comparer ce résultat avec l'ID affiché dans la console AWS, puis confirmer seulement « même compte » ou « compte différent », la région et le nom de table. Ne pas envoyer la sortie STS ou une capture du bandeau de compte. L'option --query utilisée ici sélectionne un champ d'identité pour une comparaison locale ; elle n'est jamais utilisée comme protection de données DynamoDB.

Après rapprochement : revérifier la table réelle et ses paramètres, enregistrer TableId/appartenance, insérer les deux items autorisés sans écrasement, vérifier leurs valeurs, puis créer le reader sans permission. L'unique clé technique restera une intervention humaine. Les policies et tous les tests sont ensuite prêts à être exécutés.

Voir [preuve du diagnostic](../preuves/table-recheck.txt), [préflight](../preuves/preflight.txt), [matrice](tests.md) et [conformité au PDF](sources/README.md). Aucun nettoyage n'est autorisé.
