# Matrice des tests

Résultats AWS et contrôles CLI/locaux explicitement identifiés. Les lignes D, I, A et B décrivent l'état avant nettoyage ; les lignes C relatent le nettoyage autorisé. `NOT TESTED` signifie aucune observation. Les tests unitaires ne valident pas IAM.

| Étape | Identité | Action | Clé | Projection | Attendu | Observé | Statut | Preuve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | tp2a-admin | DescribeTable + options | — | métadonnées | ACTIVE, schéma et options conformes | rc=0, ACTIVE, id String, On-demand, Standard | PASS | [Preuve](../preuves/01-table-created.png) |
| D02 | tp2a-admin | GetItem consistent-read | 001 | complète | item fictif exact, cinq String | rc=0, valeurs exactes vérifiées | PASS | [Preuve](../preuves/02-items.png) |
| D03 | tp2a-admin | GetItem consistent-read | 002 | complète | item fictif exact, cinq String | rc=0, valeurs exactes vérifiées | PASS | [Preuve](../preuves/02-items.png) |
| D04 | tp2a-admin | GetUser + listes IAM initiales | — | métadonnées | lecteur sans groupe, policy ni clé initiale | rc=0, UserId conforme et listes vides à la création | PASS | [Preuve](../preuves/reader-created.txt) |
| D05 | tp2a-admin | GetLoginProfile | — | métadonnées | NoSuchEntity pour confirmer absence de login | rc=254, AccessDenied explicite par SCP | PARTIAL | [Preuve](../preuves/audit-login-profile.txt) |
| D06 | tp2a-reader | GetCallerIdentity | — | métadonnées | identité exacte du reader, même compte | rc=0, ARN exact et compte conformes | PASS | [Preuve](../preuves/reader-identity.txt) |
| D07 | tp2a-admin | Audit final policy, groupes et clé | — | métadonnées | seule TP2AFGAC LeadingKeys et une clé active | rc=0, inline exacte ; aucun groupe/managed policy ; une clé active | PASS | [Preuve](../preuves/pre-cleanup-check.txt) |
| I01 (initial) | tp2a-reader | get-item | 001 | allowed | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/I01.txt) |
| A01 (attributes) | tp2a-reader | get-item | 001 | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/A01.txt) |
| A02 (attributes) | tp2a-reader | get-item | 001 | ssn | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A02.txt) |
| A03 (attributes) | tp2a-reader | get-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A03.txt) |
| A04 (attributes) | tp2a-reader | query | 001 | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/A04.txt) |
| A05 (attributes) | tp2a-reader | scan | — | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/A05.txt) |
| A06 (attributes) | tp2a-reader | scan | — | ALL_ATTRIBUTES | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A06.txt) |
| A07 (attributes) | tp2a-reader | put-item | 999 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A07.txt) |
| A08 (attributes) | tp2a-reader | get-item | 002 | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/A08.txt) |
| A09 (attributes) | tp2a-reader | get-item | 001 | internal_note | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A09.txt) |
| A10 (attributes) | tp2a-reader | update-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A10.txt) |
| A11 (attributes) | tp2a-reader | delete-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/A11.txt) |
| B01 (leadingkeys) | tp2a-reader | get-item | 001 | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/B01.txt) |
| B02 (leadingkeys) | tp2a-reader | get-item | 002 | allowed | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B02.txt) |
| B03 (leadingkeys) | tp2a-reader | get-item | 001 | ssn | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B03.txt) |
| B04 (leadingkeys) | tp2a-reader | get-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B04.txt) |
| B05 (leadingkeys) | tp2a-reader | query | 001 | allowed | SUCCESS | rc=0, SUCCESS | PASS | [Journal](../preuves/B05.txt) |
| B06 (leadingkeys) | tp2a-reader | query | 002 | allowed | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B06.txt) |
| B07 (leadingkeys) | tp2a-reader | scan | — | allowed | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B07.txt) |
| B08 (leadingkeys) | tp2a-reader | put-item | 999 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B08.txt) |
| B09 (leadingkeys) | tp2a-reader | get-item | 001 | internal_note | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B09.txt) |
| B10 (leadingkeys) | tp2a-reader | update-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B10.txt) |
| B11 (leadingkeys) | tp2a-reader | delete-item | 001 | absente | AccessDenied | rc=254, AccessDeniedException | EXPECTED DENY | [Journal](../preuves/B11.txt) |
| C00 | tp2a-admin | Inventaire et conservation | — | — | compte/noms/identifiants exacts, preuves sauvegardées | rc=0 ; lectures, listes, appartenance et sauvegarde vérifiées | PASS | [Journal](../preuves/cleanup.txt) |
| C01 | tp2a-admin | UpdateAccessKey + ListAccessKeys | — | — | unique clé Inactive | rc=0 ; unique clé Inactive observée | PASS | [Journal](../preuves/cleanup.txt) |
| C02 | tp2a-admin | DeleteAccessKey + ListAccessKeys | — | — | liste vide | rc=0 ; zéro clé observée | PASS | [Journal](../preuves/cleanup.txt) |
| C03 | tp2a-admin | DeleteUserPolicy + GetUserPolicy | — | — | TP2AFGAC absente | suppression rc=0 ; GetUserPolicy rc=254 NoSuchEntity | PASS | [Journal](../preuves/cleanup.txt) |
| C04 | tp2a-admin | Permissions restantes et UserId | — | — | aucune policy/groupe, utilisateur exact | rc=0 ; listes vides et UserId conforme | PASS | [Journal](../preuves/cleanup.txt) |
| C05 | tp2a-admin | DeleteUser | — | — | suppression du seul lecteur | rc=0 | PASS | [Journal](../preuves/cleanup.txt) |
| C06 | tp2a-admin | GetUser | — | — | NoSuchEntity | rc=254 ; NoSuchEntity observé | PASS | [Journal](../preuves/cleanup.txt) |
| C07 | tp2a-admin | ListUsers | — | — | nom exact absent | rc=0 ; tp2a-dynamo-reader absent | PASS | [Journal](../preuves/cleanup.txt) |
| C08 | tp2a-admin | DeleteTable | — | — | suppression du seul ARN du laboratoire | rc=0 ; suppression demandée | PASS | [Journal](../preuves/cleanup.txt) |
| C09 | tp2a-admin | DescribeTable | — | — | ResourceNotFoundException | rc=254 ; ResourceNotFoundException observée | PASS | [Journal](../preuves/cleanup.txt) |
| C10 | tp2a-admin | ListTables | — | — | nom exact absent | rc=0 ; NovaUsersTP2A absente en eu-north-1 | PASS | [Journal](../preuves/cleanup.txt) |
| C11 | CLI local | aws logout tp2a-admin | — | — | session CLI terminée et cache vide | rc=0 ; cache login vide | PASS | [Journal](../preuves/cleanup.txt) |
| C12 | Fichiers locaux | Suppression .secrets TP4 | — | — | seul dossier privé du TP absent | absence vérifiée ; ~/.aws non visé, Builder ID et MFA préservés | PASS | [Journal](../preuves/cleanup.txt) |

A01–A07 et B01–B08 reprennent les scénarios de votre demande. A08–A11 et B09–B11 sont des contrôles complémentaires (002, internal_note, UpdateItem, DeleteItem). Les écritures Update/Delete portent une condition fausse pour éviter une altération si les droits sont trop larges ; une erreur ConditionalCheckFailedException est FAIL.

Les retours réels et l'heure UTC sont conservés dans les journaux expurgés. Attendre la propagation IAM, puis relancer une suite si nécessaire : aucun échec n'est converti automatiquement en succès.
