# TP4 PRE-CLEANUP REPORT

État au 26 novembre 2026. Le TP est en préparation ; ce rapport ne déclenche aucun nettoyage.

| Contrôle demandé | Observation réelle |
| --- | --- |
| AWS account verified | Oui : STS rc=0, identité autre que root ; compte masqué |
| Region | eu-north-1 ; confirmée et configurée |
| Table active | Oui : DescribeTable rc=0, ACTIVE, schéma/options conformes ; TableId enregistré |
| Items | 001 et 002 exacts, tous les attributs String ; Scan et GetItem admin rc=0 |
| Reader | Créé sans groupe, policy ou clé ; GetLoginProfile PARTIAL à cause d'une SCP |
| Initial deny | NOT TESTED |
| Attributes policy | Conforme au PDF ; JSON privé avec ARN exact validé ; non appliquée |
| LeadingKeys policy | Construction complémentaire validée avec ARN exact ; non appliquée |
| GetItem 001 | NOT TESTED |
| GetItem 002 | NOT TESTED |
| Sensitive attributes denied | NOT TESTED |
| Scan initial | NOT TESTED |
| Scan final denied | NOT TESTED |
| PutItem denied | NOT TESTED |
| Captures | Deux captures réelles et revues : table ACTIVE et items 001/002 |
| Documentation | PDF de dix pages lu ; rapprochement et écarts documentés |
| Secrets | Isolés et exclus de Git ; permissions 700/600 vérifiées |
| Git | Dépôt local ; commits préparatoires ; aucune publication |

Preuves : [table ACTIVE](../preuves/01-table-created.png), [items](../preuves/02-items.png), [lecteur](../preuves/reader-created.txt), [audit SCP partiel](../preuves/audit-login-profile.txt), [validation locale](../preuves/local-validation.txt). Les validations locales ne comptent pas comme tests AWS.

**FINAL STATUS : PARTIAL**

Prochaine étape humaine : créer l'unique clé technique et la saisir dans le terminal personnel pour tp2a-reader. Les détails sont dans [configuration-reader.md](configuration-reader.md). La cause du blocage précédent est résolue : la table n'avait pas encore été créée, puis sa création réelle a été vérifiée par CLI. Ne pas recréer les ressources existantes. Aucun test reader ne commencera avant confirmation de sa configuration.

**Aucune autorisation CLEANUP reçue. Aucun nettoyage lancé.** Attendre l'instruction explicite après la réalisation et les tests du laboratoire.
