# Matrice des tests

Résultats AWS uniquement. `NOT TESTED` signifie aucune observation. Les tests locaux ne valident pas IAM.

| Étape | Identité | Action | Clé | Projection | Attendu | Observé | Statut | Preuve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I01 (initial) | tp2a-reader | get-item | 001 | allowed | AccessDenied | Non exécuté | NOT TESTED | — |
| A01 (attributes) | tp2a-reader | get-item | 001 | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| A02 (attributes) | tp2a-reader | get-item | 001 | ssn | AccessDenied | Non exécuté | NOT TESTED | — |
| A03 (attributes) | tp2a-reader | get-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| A04 (attributes) | tp2a-reader | query | 001 | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| A05 (attributes) | tp2a-reader | scan | — | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| A06 (attributes) | tp2a-reader | scan | — | ALL_ATTRIBUTES | AccessDenied | Non exécuté | NOT TESTED | — |
| A07 (attributes) | tp2a-reader | put-item | 999 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| A08 (attributes) | tp2a-reader | get-item | 002 | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| A09 (attributes) | tp2a-reader | get-item | 001 | internal_note | AccessDenied | Non exécuté | NOT TESTED | — |
| A10 (attributes) | tp2a-reader | update-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| A11 (attributes) | tp2a-reader | delete-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| B01 (leadingkeys) | tp2a-reader | get-item | 001 | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| B02 (leadingkeys) | tp2a-reader | get-item | 002 | allowed | AccessDenied | Non exécuté | NOT TESTED | — |
| B03 (leadingkeys) | tp2a-reader | get-item | 001 | ssn | AccessDenied | Non exécuté | NOT TESTED | — |
| B04 (leadingkeys) | tp2a-reader | get-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| B05 (leadingkeys) | tp2a-reader | query | 001 | allowed | SUCCESS | Non exécuté | NOT TESTED | — |
| B06 (leadingkeys) | tp2a-reader | query | 002 | allowed | AccessDenied | Non exécuté | NOT TESTED | — |
| B07 (leadingkeys) | tp2a-reader | scan | — | allowed | AccessDenied | Non exécuté | NOT TESTED | — |
| B08 (leadingkeys) | tp2a-reader | put-item | 999 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| B09 (leadingkeys) | tp2a-reader | get-item | 001 | internal_note | AccessDenied | Non exécuté | NOT TESTED | — |
| B10 (leadingkeys) | tp2a-reader | update-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |
| B11 (leadingkeys) | tp2a-reader | delete-item | 001 | absente | AccessDenied | Non exécuté | NOT TESTED | — |

A01–A07 et B01–B08 reprennent les scénarios de votre demande. A08–A11 et B09–B11 sont des contrôles complémentaires (002, internal_note, UpdateItem, DeleteItem). Les écritures Update/Delete portent une condition fausse pour éviter une altération si les droits sont trop larges ; une erreur ConditionalCheckFailedException est FAIL.

Les retours réels et l'heure UTC sont conservés dans les journaux expurgés. Attendre la propagation IAM, puis relancer une suite si nécessaire : aucun échec n'est converti automatiquement en succès.
