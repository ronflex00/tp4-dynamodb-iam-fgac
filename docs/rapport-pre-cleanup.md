# TP4 PRE-CLEANUP REPORT

État au 26 novembre 2026, région eu-north-1. **READY_FOR_CLEANUP** : les 23 scénarios DynamoDB ont été exécutés et sont conformes, avec 6 PASS (rc=0) et 17 EXPECTED DENY (AccessDeniedException, rc=254). Aucun test reader requis n'est non exécuté ou FAIL. Aucune suppression n'a été lancée.

## Vérifications finales

| Contrôle | Résultat observé |
| --- | --- |
| Identités | STS admin hors root, reader exactement tp2a-dynamo-reader ; même compte que le manifest |
| Table | NovaUsersTP2A ACTIVE, id String, Standard, On-demand ; appartenance et TableId conformes |
| Données | Exactement 001 et 002, cinq attributs String fictifs chacun ; valeurs administrateur vérifiées |
| Permissions finales | Seule inline TP2AFGAC = LeadingKeys ; aucun groupe, managed policy, autre inline ou resource policy de table |
| Clé reader | Une seule clé active, créée/configurée manuellement ; aucune nouvelle clé créée par l'agent |
| Transition | Policy Attributes remplacée sous le même nom ; propagation IAM attendue avant chaque suite |
| Contrôle sans suppression | cleanup-check rc=0 : READY_FOR_CLEANUP ; aucune mutation de nettoyage |

## Tous les tests reader

Les projections `allowed` désignent id, username, email. Une projection ssn ou internal_note inclut aussi id. SUCCESS est validé sur les valeurs exactes retournées, pas seulement sur le code de sortie. Les données complètes sont vérifiées uniquement avec l'administrateur.

| Étape | Action | Clé | Projection | Résultat réel | Statut | Preuve |
| --- | --- | --- | --- | --- | --- | --- |
| I01 (initial) | get-item | 001 | allowed | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/I01.txt) |
| A01 (attributes) | get-item | 001 | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/A01.txt) |
| A02 (attributes) | get-item | 001 | ssn | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A02.txt) |
| A03 (attributes) | get-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A03.txt) |
| A04 (attributes) | query | 001 | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/A04.txt) |
| A05 (attributes) | scan | — | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/A05.txt) |
| A06 (attributes) | scan | — | ALL_ATTRIBUTES | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A06.txt) |
| A07 (attributes) | put-item | 999 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A07.txt) |
| A08 (attributes) | get-item | 002 | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/A08.txt) |
| A09 (attributes) | get-item | 001 | internal_note | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A09.txt) |
| A10 (attributes) | update-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A10.txt) |
| A11 (attributes) | delete-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A11.txt) |
| B01 (leadingkeys) | get-item | 001 | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/B01.txt) |
| B02 (leadingkeys) | get-item | 002 | allowed | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B02.txt) |
| B03 (leadingkeys) | get-item | 001 | ssn | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B03.txt) |
| B04 (leadingkeys) | get-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B04.txt) |
| B05 (leadingkeys) | query | 001 | allowed | rc=0, SUCCESS | PASS | [Journal](../preuves/B05.txt) |
| B06 (leadingkeys) | query | 002 | allowed | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B06.txt) |
| B07 (leadingkeys) | scan | — | allowed | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B07.txt) |
| B08 (leadingkeys) | put-item | 999 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B08.txt) |
| B09 (leadingkeys) | get-item | 001 | internal_note | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B09.txt) |
| B10 (leadingkeys) | update-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B10.txt) |
| B11 (leadingkeys) | delete-item | 001 | absente | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B11.txt) |

## Anomalies et limites

- **GetLoginProfile : PARTIAL.** Le rôle admin rencontre un Deny explicite par SCP, rc=254. Aucun login console créé par nos opérations, mais absence non confirmée par cette API. Aucune restriction, offre ou permission n'a été modifiée pour contourner le refus. Ce contrôle administrateur est distinct des 23 tests DynamoDB conformes.
- Le premier diagnostic ResourceNotFoundException était réel : l'utilisateur a ensuite confirmé que la table n'avait pas encore été créée. Après sa création, la table correcte a été retrouvée et enregistrée. Cet incident historique est résolu.
- Aucune réussite PutItem inattendue, aucune remédiation de l'item 999 et aucune anomalie FGAC observées. Les tests Update/Delete comportaient une condition fausse ; ils ont néanmoins été refusés par AccessDenied, sans modification des items.
- Demandeur métier, propriétaire des données, approbation formelle et date de revue restent À VALIDER. Le présent statut concerne la préparation technique du nettoyage.

## Preuves, validation et Git

Douze captures réelles, numérotées 01 à 12, sont disponibles dans [preuves/](../preuves/README.md), ainsi que les 23 journaux reader, leurs JSON et les audits. La capture 13-cleanup.png est absente puisque le nettoyage n'est ni autorisé ni exécuté. Les captures CLI affichent des réponses réelles ou les journaux datés de ces réponses ; elles ont été revues et ne montrent aucun credential ni identifiant de compte.

La [matrice](tests.md) inclut aussi les contrôles administrateur, avec D05 explicitement PARTIAL. Voir [identité reader](../preuves/reader-identity.txt), [policy Attributes](../preuves/policy-attributes.txt), [policy LeadingKeys](../preuves/policy-leadingkeys.txt), [contrôle pré-nettoyage](../preuves/pre-cleanup-check.txt) et [validation locale](../preuves/local-validation.txt).

Dix-huit tests locaux réussis ; modèles et policies privées avec ARN exact validés. Markdown, liens, Bash/Fish, exclusions Git et absence de secrets sont contrôlés avant commit. Le dépôt reste local, sans push. Les valeurs réelles du fichier credentials sont comparées en mémoire aux fichiers suivables sans affichage ; les secrets/caches restent dans .secrets/ ignoré.

## Ressources encore actives

- Table NovaUsersTP2A, avec les seuls items fictifs 001 et 002.
- Utilisateur tp2a-dynamo-reader, unique clé active et seule inline TP2AFGAC LeadingKeys.
- Profils isolés tp2a-admin et tp2a-reader, cache et manifest locaux conservés ; session admin temporaire non terminée par l'agent.

Compte AWS, Builder ID, MFA et ressources des autres TP préservés. Aucune clé désactivée, aucune policy supprimée, aucune table supprimée et aucun logout exécuté.

**FINAL STATUS : READY_FOR_CLEANUP**

Attendre l'instruction explicite **CLEANUP**. Le [script de vérification](../scripts/cleanup-check.sh) ne supprime rien ; le nettoyage définitif reste non autorisé.
