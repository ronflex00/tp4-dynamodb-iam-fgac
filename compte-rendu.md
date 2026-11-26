# TP4 — Limiter les données DynamoDB avec IAM FGAC

Module : Gouvernance des identités et des habilitations. Entreprise du cas : Nova Services. Formateur indiqué : Mohammad Jabbari. Préparation : 26 novembre 2026, Europe/Paris.

**État : PARTIAL.** La préparation locale et les vérifications de connexion ont été effectuées. Aucun test de droit DynamoDB ni aucune capture de ces tests n'a été réalisé. Les exigences explicites du professeur ne peuvent pas être attestées : le PDF de dix pages manque. Les sections ci-dessous présentent le protocole demandé et les observations disponibles.

## 1. Contexte

Le support doit consulter des données utiles à l'assistance tout en excluant les attributs confidentiels. Le TP3 est annoncé terminé et nettoyé par l'utilisateur ; aucune ressource TP3 n'a été modifiée. La demande fournie définit les préparatifs. Le sujet officiel attendu est documenté dans [les sources](docs/sources/README.md).

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

Observation préalable : DescribeTable a renvoyé ResourceNotFoundException, rc=254 ; la table était absente lors de la vérification en lecture seule. Cette vérification sera renouvelée avant création. Aucune table créée. Voir [preuve de pré-vérification](preuves/preflight-readonly.txt).

## 6. Identité IAM

Nom visé : tp2a-dynamo-reader, aucun groupe, login console ou permission initiale. Une seule clé de laboratoire à créer manuellement puis configurer dans un terminal personnel ; aucun secret ne sera transmis à Codex. Observation préalable : GetUser a renvoyé NoSuchEntity, rc=254. Utilisateur non créé. Les tags, TableId et UserId sont des garde-fous techniques complémentaires pour limiter les opérations au TP4.

## 7. Refus initial

Protocole I01 : GetItem 001 avec projection approuvée, profil reader sans permission. Attendu : AccessDenied. Observé : NOT TESTED, car utilisateur et clé n'existent pas encore. Un GetCallerIdentity réussi ne permet pas de conclure sur les permissions DynamoDB.

## 8. Policy Attributes

[Modèle JSON](policies/fgac-attributes.json) préparé selon votre texte, à comparer au PDF. GetItem, Query, Scan, liste d'attributs `id`, `username`, `email`, Select spécifique lorsque présent et contrôle Null. L'ARN exact sera obtenu du compte vérifié et conservé dans le JSON privé `.secrets/policies/`. Le modèle versionné n'est pas déployable. Installation non effectuée.

## 9. Projection autorisée

A01 et A08 doivent retourner respectivement les trois attributs approuvés de 001 et 002, avec les valeurs fictives exactes. Le script contrôle la réponse, pas seulement rc=0. Observé : NOT TESTED. Les scripts passent ProjectionExpression à DynamoDB ; aucun filtre CLI --query n'est utilisé pour protéger les données.

## 10. Attribut sensible interdit

A02/B03 demandent id et ssn ; A09/B09 demandent id et internal_note. Le refus attendu porte sur toute la requête. Observé : NOT TESTED. Les tests complémentaires internal_note sont issus de votre objectif et ne sont pas attribués au professeur sans lecture du PDF.

## 11. Lecture sans projection refusée

A03/B04 omettent ProjectionExpression. L'objectif est un véritable AccessDenied, pas une sortie CLI masquée. Observé : NOT TESTED. Les erreurs de connexion, jeton expiré ou validation de paramètres produisent FAIL et jamais EXPECTED DENY.

## 12. Query / Scan

A04 : Query 001 projeté, succès attendu. A05 : Scan projeté, exactement deux items attendus. A06 : Scan ALL_ATTRIBUTES, refus attendu. B05 : Query 001 autorisé ; B06 : Query 002 refusé ; B07 : Scan projeté refusé. Tous : NOT TESTED.

## 13. Refus d'écriture

A07/B08 tentent PutItem 999, sans écraser un item existant grâce à une condition. En cas de succès inattendu : FAIL, vérification admin de l'item fictif précis, suppression ciblée du seul 999, vérification de son absence puis arrêt. Le script n'efface aucune table dans cette remédiation.

UpdateItem et DeleteItem sont aussi testés avec une condition fausse sur l'item existant pour éviter de l'altérer si une permission excessive existe. ConditionalCheckFailedException reste FAIL : seule une erreur AccessDenied de l'opération correspondante établit le refus attendu. Observé : NOT TESTED pour toutes les écritures.

## 14. Policy LeadingKeys

[Modèle complémentaire](policies/fgac-leadingkeys.json) : GetItem/Query seulement, attributs approuvés, LeadingKeys exactement `001`, contrôle de présence pour les deux clés de condition. Scan retiré. Solution fondée sur la [documentation AWS FGAC](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html) ; exigences exactes du PDF non vérifiées. Aucune policy attachée.

## 15. Restriction au dossier 001

La policy B remplace la policy inline A sous le même nom TP2AFGAC. L'audit exige l'absence d'autres inline/managed policies, groupes, login console et resource policy de table. Les tests B01/B05 doivent réussir ; B02/B06 doivent refuser 002. Attendre la propagation IAM avant les retests. Observé : NOT TESTED.

## 16. Matrice

[Matrice complète](docs/tests.md) avec attendu, observé, statut et preuve. Les suites la régénèrent à partir des appels effectivement exécutés. Tous les scénarios reader sont NOT TESTED. PASS et EXPECTED DENY ne seront utilisés qu'après observation conforme. Les résultats des tests unitaires locaux ne remplissent pas cette matrice.

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

**NON LANCÉ — autorisation CLEANUP non reçue.** Le [protocole](docs/cleanup.md) est préparé. Le compte, Builder ID, MFA et ressources extérieures seront préservés. Aucune ressource TP4 n'a été créée à ce stade ; leur absence préalable n'est pas une preuve de nettoyage final.

## 19. Conclusion

Préparation locale effectuée, connexion temporaire et identité non-root vérifiées, table et utilisateur absents lors du contrôle préalable. Le PDF est indispensable pour poursuivre la réalisation conforme au sujet. La création en console et la clé reader sont des étapes humaines prévues. Aucun test FGAC n'est déclaré réussi, aucune capture fictive créée, aucun nettoyage exécuté. Statut du TP : **PARTIAL**.

Validation locale observée : deux modèles JSON conformes au validateur structurel, quinze tests unitaires réussis, syntaxe Bash/Fish et environnements sourcés vérifiés, Markdown analysé et liens locaux contrôlés, audit des fichiers suivables sans secret détecté. Les fichiers de profil ont les permissions 600, les répertoires privés 700. Voir le [journal de validation locale](preuves/local-validation.txt). Les commits sont locaux, sans publication.
