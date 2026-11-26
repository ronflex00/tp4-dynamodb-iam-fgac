# TP4 — Limiter les données DynamoDB avec IAM FGAC

Nova Services · Gouvernance des identités et des habilitations · Formateur : Mohammad Jabbari · Exécution : 26 novembre 2026, Europe/Paris.

**COMPLETE — nettoyage autorisé, exécuté et vérifié.** Les 23 scénarios DynamoDB antérieurs au nettoyage ont été exécutés : six PASS et dix-sept EXPECTED DENY, sans FAIL ni test reader requis non exécuté. Douze captures initiales et les journaux expurgés ont été préservés ; une treizième capture montre le journal de nettoyage. La clé, la policy, l’utilisateur et la table TP4 sont supprimés. Aucun push effectué. GetLoginProfile demeure un contrôle administrateur PARTIAL à cause d'une SCP ; cette limite n'est pas assimilée à un succès FGAC.

## 1. Contexte

Le support Nova Services doit consulter un annuaire en protégeant les informations internes. Le PDF officiel de dix pages a été lu intégralement et rapproché des préparatifs : noms, items, première policy et huit questions. [Provenance et conformité](docs/sources/README.md). Aucune ressource TP3 n'a été modifiée.

Le PDF prescrit la création en console. La table a été créée par l'utilisateur dans cette console ; celui-ci a ensuite expressément autorisé l'insertion des items et les opérations IAM automatiques par CLI. Ces variantes sont documentées. La clé reader a été créée et configurée manuellement, sans transmission de secret dans la conversation.

## 2. Objectif FGAC

Étape A : lecture des seuls id, username et email sur 001 et 002. Étape B : mêmes attributs sur le seul dossier 001. Les résultats réels établissent le refus de ssn, internal_note, des lectures sans projection et des écritures. La restriction finale retire aussi Scan et refuse GetItem/Query sur 002.

## 3. Architecture

L'utilisateur technique tp2a-dynamo-reader reçoit une seule inline policy TP2AFGAC sur l'ARN exact de NovaUsersTP2A. L'état final ajoute LeadingKeys 001 aux conditions sur les attributs. [Diagramme et décisions](docs/architecture.md). Aucun groupe, managed policy, autre inline policy ou resource policy de table n'élargit les droits observés.

## 4. Environnement AWS

Arch Linux, Fish ; AWS CLI 2.37.9, Python 3.14.10, Git 2.56.1. Workspace : /home/gatta/Downloads/TP4. Les chemins de profils et cache sont isolés dans .secrets/. AWS_PAGER est vide, conformément à la syntaxe de cette variable.

Paramètres déclarés par l'utilisateur : projet Blank Canvas, AWS Free plan, région eu-north-1, MFA Builder ID TOTP actif, compte du cours conservé. STS vérifie le compte et les identités, pas le plan, les crédits, le MFA IAM ou la correspondance historique avec TP3. Aucun changement de plan effectué.

La connexion admin est temporaire par aws login ; aucune clé admin créée. L'environnement a été sourcé dans Fish pour la reprise. GetCallerIdentity admin et reader réussissent (rc=0), avec compte/principal admin conformes au manifest et ARN reader exactement égal à celui de tp2a-dynamo-reader. [Preuve expurgée](preuves/reader-identity.txt). Aucune identité root utilisée.

## 5. Table DynamoDB

NovaUsersTP2A est ACTIVE : id String, aucune sort key, Standard, On-demand. Aucun index, Stream, réplication, PITR, sauvegarde supplémentaire ou resource policy. La date de création est postérieure au préflight d'absence ; le tag d'appartenance a été ajouté seulement à cette table, et son TableId conservé. [Appartenance](preuves/table-ownership.txt), [capture ACTIVE](preuves/01-table-created.png).

Le premier diagnostic d'absence était réel : l'utilisateur a ensuite précisé que la table n'avait jamais été créée à ce moment. Il l'a réellement créée avant la reprise réussie. Ce diagnostic historique est conservé, sans le présenter comme un refus IAM.

Les items fictifs ont été insérés par PutItem conditionnel sans écrasement, puis vérifiés par Scan administrateur et deux GetItem consistent-read :

| id String | username | email | ssn | internal_note |
| --- | --- | --- | --- | --- |
| 001 | alice | alice@example.com | FICTIF-001 | Demonstration interne |
| 002 | bob | bob@example.com | FICTIF-002 | Demonstration interne |

Tous les attributs sont String et les zéros initiaux sont conservés. Exactement deux items, valeurs conformes ; l'item 999 est absent. [Journal administrateur](preuves/items.txt), [capture des deux lectures](preuves/02-items.png).

## 6. Identité IAM

CreateUser a créé tp2a-dynamo-reader sans groupe, permission ou mot de passe. UserId et tag sont conformes au manifest. Les listes initiales de groupes et policies étaient vides ; zéro clé était présent avant l'intervention de l'utilisateur. [Preuve de création](preuves/reader-created.txt).

Après configuration manuelle : une seule clé active et une identité STS exacte sont vérifiées. Aucune nouvelle clé créée par l'agent. Aucun login console créé par nos opérations. GetLoginProfile est refusé au rôle admin par un Deny explicite dans une SCP (rc=254) : son contrôle d'absence reste PARTIAL. [Preuve](preuves/audit-login-profile.txt). Aucune SCP ni permission n'a été modifiée pour contourner cette limite.

## 7. Refus initial

I01 : GetItem 001 avec projection id, username, email, avant toute inline policy. Résultat réel : AccessDeniedException, rc=254, EXPECTED DENY. [Journal](preuves/I01.txt), [capture](preuves/03-reader-no-permission.png). La réussite STS prouve l'authentification mais n'accorde aucun droit DynamoDB.

## 8. Policy Attributes

Le [modèle Attributes](policies/fgac-attributes.json) reproduit les pages 5–6 du PDF : GetItem, Query, Scan ; liste d'attributs id, username, email ; Select SPECIFIC_ATTRIBUTES lorsque présent et Null sur Attributes. Le Sid est ReadPublicAttributes.

L'ARN exact, obtenu du compte STS et de la région vérifiés, est conservé dans le JSON privé .secrets/policies/. Le modèle versionné anonymise le numéro de compte. PutUserPolicy puis GetUserPolicy ont confirmé le document exact sous TP2AFGAC ; la propagation a été attendue avant tests. [Preuve d'application](preuves/policy-attributes.txt).

## 9. Projection autorisée

A01 (001) et A08 (002) : PASS, rc=0, avec exactement id, username, email et leurs valeurs fictives attendues. Les champs sensibles sont absents des réponses. [Capture A01](preuves/04-projection-allowed.png). Les tests comparent les données retournées ; aucun filtre CLI --query n'est utilisé pour protéger les données.

## 10. Attribut sensible interdit

A02/B03 demandent id et ssn ; A09/B09 demandent id et internal_note. Quatre requêtes entièrement refusées par AccessDeniedException, rc=254, EXPECTED DENY. [Capture ssn](preuves/05-ssn-denied.png). Le test explicite internal_note est un complément au protocole détaillé du PDF, cohérent avec son objectif de confidentialité.

## 11. Lecture sans projection refusée

A03/B04 omettent ProjectionExpression. Les deux lectures sont refusées par AccessDeniedException, rc=254, EXPECTED DENY. [Capture A03](preuves/06-no-projection-denied.png). Les erreurs techniques, credentials expirés ou paramètres invalides n'auraient pas été comptés comme refus IAM attendu.

## 12. Query / Scan

A04 : Query 001 PASS, rc=0, un seul item avec les trois attributs approuvés. A05 : Scan projeté PASS, rc=0, exactement deux items. A06 : Scan ALL_ATTRIBUTES EXPECTED DENY, rc=254. [Capture Query](preuves/07-query-allowed.png), [capture Scan à deux items](preuves/08-scan-two-items.png).

Après restriction : B05 Query 001 PASS ; B06 Query 002 et B07 Scan projeté EXPECTED DENY, rc=254. [Capture Scan final](preuves/12-scan-denied.png).

## 13. Refus d'écriture

A07/B08 PutItem 999 : AccessDeniedException, rc=254, EXPECTED DENY. Aucun item 999 créé ; aucune remédiation de suppression nécessaire. [Capture PutItem](preuves/09-write-denied.png).

A10/B10 UpdateItem et A11/B11 DeleteItem : même refus réel. Ces commandes portaient une condition fausse pour préserver les fixtures en cas de permission excessive. Elles ont été refusées par IAM ; ConditionalCheckFailedException n'aurait pas été validé. Les deux items ont été revérifiés intacts après les suites.

## 14. Policy LeadingKeys

Le [modèle LeadingKeys](policies/fgac-leadingkeys.json) conserve les attributs approuvés et Select, ajoute ForAllValues:StringEquals sur LeadingKeys 001 et Null sur Attributes/LeadingKeys. GetItem et Query sont les seules actions autorisées ; aucun Scan ni écriture.

Le PDF exige la restriction 001 et deux livrables JSON, sans donner le second document détaillé. Cette construction complémentaire suit la [documentation AWS FGAC](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html). Le même nom inline TP2AFGAC a été remplacé, puis relu ; aucun Allow plus large conservé. [Preuve de transition](preuves/policy-leadingkeys.txt).

## 15. Restriction au dossier 001

Après propagation, B01 GetItem 001 et B05 Query 001 : PASS, rc=0, données exactes et projetées. B02 GetItem 002 et B06 Query 002 : EXPECTED DENY, rc=254. [001 autorisé](preuves/10-leadingkeys-001.png), [002 refusé](preuves/11-leadingkeys-002-denied.png).

Les attributs sensibles et lectures sans projection restent refusés ; B07 Scan est refusé. La policy finale relue correspond au JSON LeadingKeys privé sur l'ARN exact. Aucun groupe, managed policy, autre inline ou resource policy n'ajoute d'accès.

## 16. Matrice

[Les 23 scénarios et les contrôles administrateur](docs/tests.md) indiquent identité, action, clé, projection, attendu, observé, statut et preuve. Résultat reader : six PASS et dix-sept EXPECTED DENY, aucun FAIL/PARTIAL/NOT TESTED parmi les scénarios requis. Les succès sont rc=0 avec contenu exact ; les refus sont AccessDeniedException, rc=254, sur l'opération testée.

D05 GetLoginProfile reste séparément PARTIAL, documenté comme restriction de lecture administrateur. Les dix-huit tests unitaires locaux ne sont pas présentés comme des tests AWS. Douze captures réelles sont revues ; les réponses originales expurgées et leur date restent disponibles.

## 17. Analyse gouvernance

| Élément | Valeur / état |
| --- | --- |
| Demandeur métier nominatif | À VALIDER |
| Propriétaire des données | À VALIDER |
| Justification proposée | Assistance : identifier le dossier et contacter l'usager fictif |
| Attributs proposés à l'approbation | id, username, email ; approbation formelle À VALIDER |
| Attributs exclus | ssn, internal_note |
| Périmètre technique final | Dossier 001 ; approbation métier À VALIDER |
| Date de revue des habilitations | À VALIDER |
| Date d'exécution technique | 26 novembre 2026 ; ne vaut pas date de revue métier |
| Moindre privilège observé | Lecture projetée sur 001, aucun Scan final, aucune écriture |
| Identité de production proposée | Rôle et credentials temporaires ; décision À VALIDER |

Aucune personne responsable, validation formelle ou date de revue inventée. [Réponses aux huit questions du PDF](docs/questions.md).

## 18. Nettoyage

**TERMINÉ ET VÉRIFIÉ.** Après l’autorisation explicite CLEANUP, l’inventaire d’appartenance a été contrôlé et les opérations C00–C12 ont toutes abouti. La clé a été observée Inactive puis supprimée ; la policy inline est absente ; `GetUser`/`ListUsers` confirment l’absence du lecteur ; `DescribeTable`/`ListTables` confirment l’absence de la table. `aws logout` a rc=0 et le cache de session est vide. Seul le dossier `.secrets/` TP4 a été supprimé. Voir le [journal](preuves/cleanup.txt), la [capture réelle](preuves/13-cleanup.png), le [protocole exécuté](docs/cleanup.md) et le [rapport final](docs/rapport-final.md). Builder ID, MFA, `~/.aws` et ressources extérieures préservés. GetLoginProfile reste PARTIAL à cause du Deny SCP.

## 19. Conclusion

Les résultats réels établissent la restriction des attributs, puis de la partition 001. Les 23 tests reader sont conformes et documentés ; 12 captures initiales ont été préservées, avec une 13e capture du nettoyage. La limite d’audit GetLoginProfile refusé par SCP est documentée sans contournement. Statut final : **COMPLETE**, nettoyage vérifié ; aucun push GitHub. Les résultats FGAC décrivent l’état avant suppression.

Validation locale finale : 20 tests unitaires réussis ; liens Markdown, JSON, Bash/Fish, exclusions Git, preuves et scan statique des secrets vérifiés. La comparaison exacte des credentials aux fichiers suivables a réussi en mémoire avant la suppression du dossier privé, sans afficher de valeur. [Journal de validation](preuves/local-validation.txt). Commit local des modifications validées, sans push.
