# TP4 EXECUTION REPORT

Exécution terminée jusqu'à l'arrêt demandé avant nettoyage. Voir le [rapport pré-nettoyage complet](rapport-pre-cleanup.md) et la [matrice détaillée](tests.md).

| Contrôle | Résultat observé |
| --- | --- |
| Table DynamoDB | ACTIVE, conforme, eu-north-1 |
| Items 001/002 | Exactement deux items fictifs, cinq String ; vérifiés administrateur |
| Utilisateur IAM | tp2a-dynamo-reader ; aucune managed policy ni groupe ; seule inline TP2AFGAC |
| Profil reader | STS identité exacte et compte conformes ; une seule clé active |
| Refus initial | I01 EXPECTED DENY, AccessDeniedException, rc=254 |
| Projection autorisée | A01/A08 et B01 PASS, rc=0 |
| Attribut sensible refusé | ssn et internal_note refusés en A et B, rc=254 |
| Lecture complète refusée | A03/B04 EXPECTED DENY, rc=254 |
| Query | 001 autorisé en A et B ; 002 refusé en B |
| Scan initial | A05 PASS, exactement deux items ; ALL_ATTRIBUTES refusé en A06 |
| PutItem refusé | A07/B08 EXPECTED DENY, rc=254 ; Update/Delete également refusés |
| LeadingKeys 001 | B01/B05 PASS ; seuls les trois attributs approuvés |
| Accès 002 refusé | B02/B06 EXPECTED DENY, rc=254 |
| Scan final refusé | B07 EXPECTED DENY, rc=254 |
| Captures | Douze captures réelles revues ; aucun écran de clé ni capture de nettoyage |
| Documentation | Compte-rendu, huit réponses, matrice et provenance finalisés |
| Tests locaux | Dix-huit réussis ; validation JSON/ARN, Markdown et Bash/Fish |
| Git | Commit local des modifications validées ; aucune publication |
| Audit secrets | Fichiers privés exclus ; comparaison locale sans affichage et revue des images |
| Ressources AWS restantes | Table, deux items, lecteur, une clé active et inline LeadingKeys ; sessions et profils locaux conservés |

**Anomalie connue :** GetLoginProfile reste PARTIAL, car une SCP refuse cette lecture au rôle admin. Aucune SCP ni permission n'a été élargie. Les 23 scénarios DynamoDB sont conformes : six PASS et dix-sept EXPECTED DENY. Les responsables métier et la date de revue restent À VALIDER.

**FINAL STATUS : READY_FOR_CLEANUP**

Aucun nettoyage exécuté. Attendre une instruction explicite CLEANUP avant toute suppression. Aucun push GitHub.
