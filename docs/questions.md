# Réponses aux huit questions fournies

Les huit questions ont été rapprochées de la page 10 du PDF officiel, lu le 26 novembre 2026. Elles correspondent aux formulations de votre demande. Les 23 scénarios reader consignés dans [la matrice](tests.md) illustrent les mécanismes FGAC décrits ; la proposition d'identité temporaire de production reste une recommandation.

## 1. Pourquoi FGAC ne masque pas une lecture complète ?

IAM autorise ou refuse la requête. Il ne reçoit pas une lecture complète pour en effacer ensuite les champs sensibles. Le client doit demander une projection autorisée ; la lecture sans projection doit être refusée. Dans ce laboratoire, le contrôle `Null` évite qu'une absence d'attributs satisfasse la condition de liste. Voir les [conditions FGAC DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html).

## 2. Différence entre attribut et permission IAM

Un attribut est un champ de données, par exemple `email`. Une permission décrit qui peut faire une action sur une ressource et sous quelles conditions. Une permission `GetItem` limitée à certains attributs ne crée pas une permission séparée appelée `email`. Demander `ssn` doit faire échouer toute la requête.

## 3. Pourquoi inclure la clé primaire ?

`id` identifie le dossier ; Query utilise cet attribut dans sa condition de clé. Il doit donc figurer dans la liste approuvée des attributs accédés. Dans la table sans sort key ni index du TP, cette clé est `id` de type String. Une liste `username,email` seule ne décrit pas tous les attributs utilisés par les requêtes du scénario.

## 4. Pourquoi --query ne protège pas les données ?

`--query` est un filtre JMESPath exécuté par la CLI sur la réponse reçue. Par exemple, sélectionner `Item.email` à l'affichage ne supprime pas les autres attributs du flux réseau déjà reçu. `--projection-expression` fait partie de la requête DynamoDB et peut être contrôlé par IAM. Les tests n'utilisent pas `--query` pour leur protection.

## 5. Pourquoi tester l'absence de projection ?

C'est une tentative directe d'obtenir la totalité de l'item. Si elle réussit, la seule réussite du test avec projection ne démontre aucune confidentialité des autres champs. Le test vérifie donc le refus de la requête entière et son code réel ; une erreur de credentials n'est pas une preuve de refus IAM.

## 6. Pourquoi retirer Scan pour limiter à 001 ?

Scan parcourt la table sans cibler une valeur de partition. Il n'apporte pas le contexte LeadingKeys nécessaire. La deuxième policy retire donc Scan et exige une clé présente égale à 001 pour les actions conservées. Un FilterExpression `id=001` sur Scan serait un filtrage de données, pas une frontière d'autorisation. Voir la [documentation FGAC](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html).

## 7. Pourquoi un autre Allow élargit l'accès ?

Dans les cas où ils sont applicables, les Allow se cumulent ; un Allow plus large peut autoriser une requête qui ne satisfait pas le premier. Par exemple, conserver la policy A permettrait encore de lire 002 malgré l'ajout de la policy B. On remplace donc la même inline policy, puis on inspecte groupes, managed policies et resource policy. Un Deny explicite, les SCP et les boundaries peuvent encore restreindre les droits. Voir la [logique d'évaluation IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html).

## 8. Comment remplacer la clé technique par une identité temporaire en production ?

Confier les permissions à un rôle IAM : rôle d'exécution pour un service AWS, fédération/Identity Center pour un humain, fédération OIDC pour une charge compatible. Le SDK obtient et renouvelle des credentials temporaires STS sans clé IAM persistante dans l'application. Le rôle conserve les conditions sur les données ; sa trust policy borne qui peut l'assumer. En contexte multi-client, un identifiant validé ou un principal tag peut définir la partition accessible, après vérification de sa provenance. Voir les [rôles IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).
