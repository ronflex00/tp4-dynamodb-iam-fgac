# Matrice des tests

Résultats AWS uniquement. `NOT TESTED` signifie aucune observation. Les tests locaux ne valident pas IAM.

| Étape | Identité | Action | Clé | Projection | Attendu | Observé | Statut | Preuve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | tp2a-admin | DescribeTable + options | — | métadonnées | ACTIVE, schéma et options conformes | rc=0, ACTIVE, id String, On-demand, Standard | PASS | [Preuve](../preuves/01-table-created.png) |
| D02 | tp2a-admin | GetItem consistent-read | 001 | complète | item fictif exact, cinq String | rc=0, valeurs exactes vérifiées | PASS | [Preuve](../preuves/02-items.png) |
| D03 | tp2a-admin | GetItem consistent-read | 002 | complète | item fictif exact, cinq String | rc=0, valeurs exactes vérifiées | PASS | [Preuve](../preuves/02-items.png) |
| D04 | tp2a-admin | GetUser + listes IAM initiales | — | métadonnées | lecteur sans groupe, policy ni clé initiale | rc=0, UserId conforme et listes vides à la création | PASS | [Preuve](../preuves/reader-created.txt) |
| D05 | tp2a-admin | GetLoginProfile | — | métadonnées | NoSuchEntity pour confirmer absence de login | rc=254, AccessDenied explicite par SCP | PARTIAL | [Preuve](../preuves/audit-login-profile.txt) |
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
