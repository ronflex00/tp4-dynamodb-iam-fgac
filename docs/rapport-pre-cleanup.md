# TP4 PRE-CLEANUP REPORT

État au 26 novembre 2026. Le TP est en préparation ; ce rapport ne déclenche aucun nettoyage.

| Contrôle demandé | Observation réelle |
| --- | --- |
| AWS account verified | Oui : STS rc=0, identité autre que root ; compte masqué |
| Region | eu-north-1 ; confirmée et configurée |
| Table active | Annoncée ACTIVE par l'utilisateur ; non retrouvée en CLI : ResourceNotFoundException, rc=254 ; ListTables vide, rc=0 |
| Items | Non créés ; deux items fictifs préparés |
| Reader | Absent : NoSuchEntity, rc=254 |
| Initial deny | NOT TESTED |
| Attributes policy | Conforme au PDF ; JSON privé avec ARN exact validé ; non appliquée |
| LeadingKeys policy | Construction complémentaire validée avec ARN exact ; non appliquée |
| GetItem 001 | NOT TESTED |
| GetItem 002 | NOT TESTED |
| Sensitive attributes denied | NOT TESTED |
| Scan initial | NOT TESTED |
| Scan final denied | NOT TESTED |
| PutItem denied | NOT TESTED |
| Captures | Aucune ; seuls des journaux expurgés réels sont disponibles |
| Documentation | PDF de dix pages lu ; rapprochement et écarts documentés |
| Secrets | Isolés et exclus de Git ; permissions 700/600 vérifiées |
| Git | Dépôt local ; commits préparatoires ; aucune publication |

Preuves : [identité](../preuves/environment.txt), [préflight après lecture](../preuves/preflight.txt), [écart console/CLI](../preuves/table-recheck.txt), [validation locale](../preuves/local-validation.txt). Les validations locales ne comptent pas comme tests AWS.

**FINAL STATUS : PARTIAL**

Prochaine étape humaine : rapprocher le compte, la région et le nom de table affichés en console avec le profil tp2a-admin, sans communiquer d'identifiant de compte ni de secret. La table annoncée créée n'est pas retrouvée dans le périmètre vérifié. Ne pas la recréer et ne pas élargir les permissions pour obtenir artificiellement un résultat.

**Aucune autorisation CLEANUP reçue. Aucun nettoyage lancé.** Attendre l'instruction explicite après la réalisation et les tests du laboratoire.
