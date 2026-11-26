# TP4 EXECUTION REPORT

Exécution TP4 terminée, nettoyage explicitement autorisé et vérifié. Les résultats FGAC ci-dessous décrivent l'état réellement observé avant nettoyage. Voir le [rapport final](rapport-final.md), le [rapport pré-nettoyage historique](rapport-pre-cleanup.md) et la [matrice détaillée](tests.md).

| Contrôle | Résultat observé avant nettoyage |
| --- | --- |
| Table DynamoDB | NovaUsersTP2A ACTIVE, conforme, eu-north-1 |
| Items 001/002 | Exactement deux items fictifs, cinq String chacun, vérifiés administrateur |
| Utilisateur IAM | tp2a-dynamo-reader ; aucun groupe/managed policy ; une inline TP2AFGAC |
| Profil reader | STS identité exacte ; une clé technique |
| Refus initial | I01 EXPECTED DENY, AccessDeniedException, rc=254 |
| Projection autorisée | A01/A08 et B01 PASS, rc=0 |
| Attribut sensible refusé | ssn et internal_note refusés en A et B, rc=254 |
| Lecture complète refusée | A03/B04 EXPECTED DENY, rc=254 |
| Query | 001 autorisé en A et B ; 002 refusé en B |
| Scan initial | A05 PASS, deux items ; ALL_ATTRIBUTES refusé en A06 |
| PutItem refusé | A07/B08 EXPECTED DENY, rc=254 ; Update/Delete également refusés |
| Scan final | B07 EXPECTED DENY, rc=254 |
| Tests AWS | 23 conformes : 6 PASS, 17 EXPECTED DENY |
| Nettoyage | C00–C12 PASS ; journal et capture conservés |
| Tests locaux | 20 réussis hors ligne ; modèles, liens, syntaxe et contrôles validés |
| Git | Commit local demandé ; aucune publication GitHub |
| Audit secrets | Contrôle en mémoire pré-suppression ; scan statique final réussi ; `.secrets/` absent |
| Ressources TP4 restantes | Aucune ; clé, policy, user et table supprimés et absences vérifiées |

**Limite d'audit :** GetLoginProfile reste PARTIAL, car une SCP a refusé cette lecture au rôle admin. Aucune SCP ni permission n'a été modifiée. Les responsables métier et la date de revue restent À VALIDER.

**FINAL STATUS : COMPLETE.** Compte AWS, Builder ID, MFA, `~/.aws` et ressources des autres TP préservés.
