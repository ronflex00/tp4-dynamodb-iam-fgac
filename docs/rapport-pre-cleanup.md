# TP4 PRE-CLEANUP REPORT

État au 26 novembre 2026. Le TP est en préparation ; ce rapport ne déclenche aucun nettoyage.

| Contrôle demandé | Observation réelle |
| --- | --- |
| AWS account verified | Oui : STS rc=0, identité autre que root ; compte masqué |
| Region | eu-north-1 ; confirmée et configurée |
| Table active | Non : ResourceNotFoundException, rc=254 ; aucune création |
| Items | Non créés ; deux items fictifs préparés |
| Reader | Absent : NoSuchEntity, rc=254 |
| Initial deny | NOT TESTED |
| Attributes policy | Modèle local validé ; ARN à lier ; non appliquée |
| LeadingKeys policy | Modèle local validé ; ARN à lier ; non appliquée |
| GetItem 001 | NOT TESTED |
| GetItem 002 | NOT TESTED |
| Sensitive attributes denied | NOT TESTED |
| Scan initial | NOT TESTED |
| Scan final denied | NOT TESTED |
| PutItem denied | NOT TESTED |
| Captures | Aucune ; seuls des journaux expurgés réels sont disponibles |
| Documentation | Préparée ; conformité au PDF À VÉRIFIER |
| Secrets | Isolés et exclus de Git ; permissions 700/600 vérifiées |
| Git | Dépôt local ; commits préparatoires ; aucune publication |

Preuves : [identité](../preuves/environment.txt), [absence préalable des ressources](../preuves/preflight-readonly.txt), [validation locale](../preuves/local-validation.txt). Les validations locales ne comptent pas comme tests AWS.

**FINAL STATUS : PARTIAL**

Prochaine étape humaine : copier `TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf` dans `docs/sources/` pour permettre sa lecture. Les opérations de création ne commenceront qu'après ce rapprochement. La création de table en console et la création/configuration manuelle de la clé reader restent ensuite nécessaires.

**Aucune autorisation CLEANUP reçue. Aucun nettoyage lancé.** Attendre l'instruction explicite après la réalisation et les tests du laboratoire.
