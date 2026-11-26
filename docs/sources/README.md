# Sources et traçabilité

## Sujet officiel lu

Le document [TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf](<TP4 - Limiter les données DynamoDB avec IAM FGAC.pdf>) a été copié depuis le fichier fourni dans `/home/gatta/Téléchargements/`, puis lu intégralement le **26 novembre 2026**. `pdfinfo` confirme **10 pages**. `pdftotext -layout` a permis la lecture du texte, des items et du JSON, sans OCR ni envoi à un service externe.

Empreinte SHA256 : `a1d59c555cdb8b04ef6f228a91cd2bd57523b5968efcaa78be5b46e76a56e53c`.

La même empreinte est conservée dans `.secrets/source-reviewed.sha256`. Ce marqueur atteste la lecture opérateur et identifie le document ; il ne remplace ni les tests AWS ni une validation métier.

## Conformité et origine des exigences

| Élément | Source PDF | Vérification / décision |
| --- | --- | --- |
| Free plan, crédits, région, MFA, aucune clé admin | Pages 2–3 | Paramètres déclarés par l'utilisateur ; identité non-root et région revérifiées en CLI. Crédits et console Settings non relus par l'agent. |
| Création table et items en console, vérification CLI | Pages 1, 3–4 | Table réellement créée en console puis vérifiée ACTIVE. L'utilisateur a autorisé l'insertion automatique des items par CLI ; cette variante a été exécutée et vérifiée. |
| Noms, clé id String, Standard, On-demand, aucun ajout | Pages 3–4 | Identiques aux préparatifs ; absence des ressources observée avant toute création. |
| Deux items et leurs cinq attributs String | Page 4 | Valeurs exactes confirmées ; id 001/002 reste une chaîne. |
| Reader sans accès console ni permissions ; une clé CLI | Pages 4–5 | CreateUser exécuté sans groupe, policy, mot de passe ni clé. Listes IAM initiales vides observées ; GetLoginProfile est refusé par SCP : contrôle d'absence de login PARTIAL. Clé exclusivement humaine. |
| Première inline policy TP2AFGAC | Pages 5–6 | Actions, ARN, Attributes, Select et Null conformes ; Sid aligné sur ReadPublicAttributes. |
| Projection valide, ssn interdit, absence de projection | Pages 6–7 | Scénarios A01–A03 conformes ; seuls les résultats AWS alimenteront la matrice. |
| Query, Scan projeté, Scan ALL_ATTRIBUTES, PutItem 999 | Page 8 | Scénarios A04–A07 conformes ; username du test 999 aligné sur test-refus. Condition anti-écrasement complémentaire. |
| Deux versions JSON et restriction au dossier 001 | Pages 1, 9–10 | Le PDF demande la restriction et deux JSON, mais ne fournit pas le second JSON ni le protocole détaillé de transition. |
| Huit questions | Page 10 | Correspondent aux huit réponses préparées. |
| Nettoyage console puis confirmation CLI | Page 9 | Documenté ; pas d'exécution sans instruction CLEANUP de l'utilisateur. |

Les modèles versionnés anonymisent le numéro de compte. `preflight` a produit les JSON privés avec l'ARN exact ; leur validation locale a réussi. Les alias d'attributs des scripts désignent les mêmes noms réels que dans le PDF.

## Compléments techniques et instructions de l'utilisateur

- **Demande utilisateur :** conserver ce dossier TP4 et les scripts Fish/Bash, produire des preuves expurgées et des commits locaux, arrêter avant le nettoyage jusqu'à réception de `CLEANUP`. Le dossier d'exemple `tp2a-fgac` du PDF n'est pas créé.
- **Autorisation reçue après création console :** effectuer automatiquement les opérations possibles avec tp2a-admin, notamment insérer les deux items. `seed` et `create-reader` sont des variantes CLI de la méthode console du professeur, autorisées par cette demande. La méthode réellement utilisée sera consignée dans le compte-rendu.
- **Construction complémentaire :** deuxième policy avec LeadingKeys 001, Null sur Attributes et LeadingKeys, GetItem/Query uniquement, remplacement de la même inline policy. L'objectif est explicite dans le PDF ; cette implémentation détaillée s'appuie sur AWS.
- **Contrôles complémentaires :** refus internal_note, UpdateItem et DeleteItem, lecture 002 à l'étape A, audit des permissions parallèles, tag TP4LabId et identifiants uniques de ressources. Ils ne sont pas présentés comme imposés par le professeur.
- **Nettoyage :** le script CLI reste une variante automatisée de la procédure console du PDF. Aucune exécution n'est actuellement autorisée.
- **Limite AWS observée :** la SCP refuse explicitement GetLoginProfile au rôle administrateur. Ce contrôle reste PARTIAL et n'est pas transformé en preuve d'absence, ni en refus DynamoDB attendu. Les trois nouveaux tests locaux vérifient la distinction entre ce cas précis, un refus générique et un login profile présent. Aucune restriction AWS n'est modifiée.

## Documentation primaire consultée le 26 novembre 2026

- [DynamoDB : conditions FGAC, Attributes et LeadingKeys](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html).
- [IAM : opérateurs de condition et contrôle Null](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html).
- [AWS CLI : connexion temporaire, cache isolé et logout](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
- [IAM : logique d'évaluation des policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html).
- [IAM : rôles et identifiants temporaires](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

Les sources AWS justifient la technique et ne remplacent pas le sujet du professeur.
