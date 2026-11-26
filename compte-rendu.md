# TP4 — Limiter les données DynamoDB avec IAM FGAC

Module : Gouvernance des identités et des habilitations. Entreprise du cas : Nova Services. Formateur indiqué : Mohammad Jabbari. Préparation : 26 novembre 2026, Europe/Paris.

**État : PARTIAL — clé technique manuelle en attente.** Le PDF de dix pages a été lu. La table créée par l'utilisateur est maintenant vérifiée ACTIVE en eu-north-1 ; les deux items fictifs ont été insérés puis contrôlés et le lecteur sans permission a été créé. Deux captures réelles sont conservées. Les tests reader n'ont pas commencé. Le contrôle de métadonnées GetLoginProfile reste PARTIAL à cause d'un Deny explicite dans une SCP, sans contournement de cette restriction.

## 1. Contexte

Le support doit consulter des données utiles à l'assistance tout en excluant les attributs confidentiels. Le TP3 est annoncé terminé et nettoyé par l'utilisateur ; aucune ressource TP3 n'a été modifiée. Le [sujet officiel et sa provenance](docs/sources/README.md) distinguent les exigences du professeur des compléments et autorisations utilisateur.

## 2. Objectif FGAC

Étape A : lecture des seuls `id`, `username`, `email` sur 001 et 002. Étape B : ces mêmes attributs sur le seul dossier 001. Les lectures de `ssn`, `internal_note`, lectures complètes et écritures doivent être refusées. État observé : NOT TESTED pour ces objectifs.

## 3. Architecture

Une identité technique reçoit une seule inline policy, contrôlée à chaque transition ; la table n'accepte aucune permission parallèle. [Diagramme et décisions](docs/architecture.md). Cette architecture est préparée et n'est pas encore déployée.

## 4. Environnement AWS

Arch Linux ; AWS CLI 2.37.9 ; Python 3.14.10 ; Git 2.56.1 ; Fish disponible. Dossier : `/home/gatta/Downloads/TP4`.

Paramètres confirmés par l'utilisateur à partir du TP3 : projet Blank Canvas, AWS Free plan, région eu-north-1, MFA Builder ID TOTP actif, même compte que TP3. Le plan et le MFA n'ont pas été relus dans une console pendant cette session. STS ne permet pas de vérifier ces éléments ni de prouver la correspondance historique avec TP3.

La première tentative STS isolée a réellement échoué avec rc=253 (NoCredentials). `aws login --profile tp2a-admin` a ensuite terminé avec rc=0. La nouvelle vérification STS a réussi et le principal est autre que root. Les profils et caches restent dans `.secrets/`, les identifiants sont expurgés des preuves. Aucune clé admin permanente créée. Voir [preuve de l'environnement](preuves/environment.txt).

## 5. Table DynamoDB

Nom visé : NovaUsersTP2A ; clé `id` String, aucune sort key, Standard, On-demand, aucun index, Stream, réplication ou sauvegarde supplémentaire. Création en console prévue conformément à la demande. Deux items fictifs exacts décrits dans le [README](README.md).

Observation préalable : DescribeTable a renvoyé ResourceNotFoundException, rc=254 ; la table était absente lors de la préparation. Le préflight a renouvelé ce constat après lecture du PDF et conservé l'appartenance dans le manifest privé. Voir [preuve du préflight](preuves/preflight.txt).

Lors de la première reprise, DescribeTable répondait ResourceNotFoundException et ListTables était vide : [diagnostic historique](preuves/table-recheck.txt). L'utilisateur a ensuite identifié la cause : la table n'avait pas encore été créée. Après sa création réelle en console, DescribeTable a répondu rc=0 et ACTIVE. L'ARN correspond au compte du manifest et la date de création est postérieure au constat d'absence. Le tag TP4LabId a été ajouté seulement après ces vérifications ; TableId est enregistré. Standard, On-demand, id String, absence d'index, Stream, réplication, PITR, sauvegarde supplémentaire et resource policy ont été contrôlés. Voir [appartenance](preuves/table-ownership.txt) et [capture ACTIVE](preuves/01-table-created.png).

L'insertion CLI automatique a été expressément autorisée par l'utilisateur, en variante de la création console du PDF. PutItem conditionnel n'a pas écrasé de données. Scan administrateur puis GetItem consistent-read 001/002 confirment exactement deux items et les cinq valeurs String attendues. Voir [journal](preuves/items.txt) et [capture réelle des deux lectures](preuves/02-items.png).

## 6. Identité IAM

`tp2a-dynamo-reader` a été créé par CreateUser après un nouveau constat NoSuchEntity. Son UserId et son tag sont conformes au manifest. Les listes de groupes, policies inline et managed policies sont vides (rc=0), sans permissions boundary. ListAccessKeys retournait zéro clé avant l'intervention humaine. Aucune policy de lecture n'est encore posée. Voir [preuve de création et audit](preuves/reader-created.txt).

Aucun login console ni mot de passe n'a été créé par nos commandes. En revanche, le rôle admin rencontre un **Deny explicite dans une SCP sur iam:GetLoginProfile**, rc=254. L'absence de profil console ne peut donc pas être confirmée par cette API : contrôle PARTIAL, [réponse expurgée](preuves/audit-login-profile.txt). Cette restriction n'a pas été changée et aucun droit supplémentaire n'a été accordé. Elle concerne l'audit administrateur, pas le refus implicite DynamoDB du reader.

Le profil local tp2a-reader est préparé avec région eu-north-1 et sortie JSON ; les fichiers de profil ont les permissions 600. La création de l'unique clé et sa saisie restent exclusivement humaines dans la console puis le terminal personnel. [Procédure prête à exécuter](docs/configuration-reader.md).

## 7. Refus initial

Protocole I01 : GetItem 001 avec projection approuvée, profil reader sans permission. Attendu : AccessDenied. Observé : NOT TESTED, car la configuration de la clé reader n'est pas encore confirmée. L'utilisateur existe désormais sans permission. Un GetCallerIdentity réussi ne permet pas de conclure sur les permissions DynamoDB ; le refus GetLoginProfile de l'administrateur ne valide pas non plus ce scénario.

## 8. Policy Attributes

[Modèle JSON](policies/fgac-attributes.json) comparé aux pages 5–6 du PDF : GetItem, Query, Scan, attributs `id`, `username`, `email`, Select spécifique lorsque présent et contrôle Null conformes. Le Sid a été aligné sur ReadPublicAttributes. Les deux JSON privés `.secrets/policies/` ont été générés avec l'ARN du compte vérifié, puis validés localement. Le modèle versionné reste anonymisé et non déployable. Installation non effectuée.

## 9. Projection autorisée

A01 et A08 doivent retourner respectivement les trois attributs approuvés de 001 et 002, avec les valeurs fictives exactes. Le script contrôle la réponse, pas seulement rc=0. Observé : NOT TESTED. Les scripts passent ProjectionExpression à DynamoDB ; aucun filtre CLI --query n'est utilisé pour protéger les données.

## 10. Attribut sensible interdit

A02/B03 demandent id et ssn ; A09/B09 demandent id et internal_note. Le refus attendu porte sur toute la requête. Observé : NOT TESTED. Le PDF prévoit de protéger les notes internes, mais ne détaille pas ce test supplémentaire ; A09/B09 sont identifiés comme contrôles complémentaires.

## 11. Lecture sans projection refusée

A03/B04 omettent ProjectionExpression. L'objectif est un véritable AccessDenied, pas une sortie CLI masquée. Observé : NOT TESTED. Les erreurs de connexion, jeton expiré ou validation de paramètres produisent FAIL et jamais EXPECTED DENY.

## 12. Query / Scan

A04 : Query 001 projeté, succès attendu. A05 : Scan projeté, exactement deux items attendus. A06 : Scan ALL_ATTRIBUTES, refus attendu. B05 : Query 001 autorisé ; B06 : Query 002 refusé ; B07 : Scan projeté refusé. Tous : NOT TESTED.

## 13. Refus d'écriture

A07/B08 tentent PutItem 999, sans écraser un item existant grâce à une condition. En cas de succès inattendu : FAIL, vérification admin de l'item fictif précis, suppression ciblée du seul 999, vérification de son absence puis arrêt. Le script n'efface aucune table dans cette remédiation.

UpdateItem et DeleteItem sont aussi testés avec une condition fausse sur l'item existant pour éviter de l'altérer si une permission excessive existe. ConditionalCheckFailedException reste FAIL : seule une erreur AccessDenied de l'opération correspondante établit le refus attendu. Observé : NOT TESTED pour toutes les écritures.

## 14. Policy LeadingKeys

[Modèle complémentaire](policies/fgac-leadingkeys.json) : GetItem/Query seulement, attributs approuvés, LeadingKeys exactement `001`, contrôle de présence pour les deux clés de condition. Scan retiré. L'objectif 001 et les deux livrables JSON figurent dans le PDF ; le second JSON n'y est pas fourni. Cette construction détaillée suit la [documentation AWS FGAC](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html). Aucune policy attachée.

## 15. Restriction au dossier 001

La policy B remplacera la policy inline A sous le même nom TP2AFGAC. L'audit vérifie l'absence d'autres inline/managed policies, groupes et resource policy de table. GetLoginProfile conserve un statut PARTIAL documenté si la SCP observée le refuse ; les autres erreurs d'audit arrêtent le script. Les tests B01/B05 doivent réussir ; B02/B06 doivent refuser 002. Attendre la propagation IAM avant les retests. Observé : NOT TESTED.

## 16. Matrice

[Matrice complète](docs/tests.md) avec attendu, observé, statut et preuve. Les contrôles administrateur D01–D04 ont des observations conformes ; D05 GetLoginProfile reste PARTIAL. Tous les scénarios reader sont NOT TESTED. Les suites les rempliront uniquement après les appels réels. Les résultats des tests unitaires locaux ne remplissent pas cette matrice.

## 17. Analyse gouvernance

| Élément | Valeur / état |
| --- | --- |
| Demandeur métier nominatif | À VALIDER |
| Propriétaire des données | À VALIDER |
| Justification proposée | Assistance utilisateur : identifier le dossier et contacter l'usager fictif |
| Attributs proposés à l'approbation | id, username, email ; approbation formelle À VALIDER |
| Attributs exclus | ssn, internal_note |
| Périmètre proposé après restriction | Dossier 001 ; approbation métier À VALIDER |
| Date de revue des habilitations | À VALIDER |
| Date de préparation technique | 26 novembre 2026 ; ne vaut pas date de revue métier |
| Moindre privilège | Lecture seule, attributs limités, partition 001 en B, aucun Scan en B |
| Identité de production proposée | Rôle avec credentials temporaires ; décision À VALIDER |

Aucune validation formelle, personne responsable ou date de revue n'a été inventée. [Réponses aux huit questions](docs/questions.md).

## 18. Nettoyage

**NON LANCÉ — autorisation CLEANUP non reçue.** Le [protocole](docs/cleanup.md) est préparé. La table avec ses deux items et l'utilisateur lecteur sont conservés dans AWS. Le compte, Builder ID, MFA et ressources extérieures sont préservés. Aucun logout ou retrait de secrets n'est exécuté pendant cette attente de configuration.

## 19. Conclusion

Le PDF et les huit questions sont vérifiés. La table ACTIVE, les items 001/002 exacts et le lecteur sans permission sont désormais observés dans AWS. Les policies privées avec ARN exact sont prêtes ; les tests reader attendent l'unique clé manuelle. Deux captures réelles et les journaux sont conservés. La limite SCP sur GetLoginProfile est explicitement PARTIAL et n'a pas été contournée. Aucun test FGAC reader n'est déclaré réussi ; aucun nettoyage ni publication effectué. Statut du TP : **PARTIAL**.

Validation locale : modèles et JSON privés validés ; dix-huit tests unitaires réussis, dont trois contrôles du traitement explicite de l'audit SCP partiel. Syntaxe Bash/Fish, Markdown et secrets sont contrôlés avant commit. Les fichiers de profil ont les permissions 600, les répertoires privés 700. Voir le [journal de validation locale](preuves/local-validation.txt). Les commits restent locaux.
