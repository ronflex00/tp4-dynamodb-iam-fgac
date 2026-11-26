# Nettoyage final — terminé et vérifié

L’instruction explicite `CLEANUP` a été reçue. Le nettoyage a été exécuté le 26 novembre 2026 dans `eu-north-1`, après contrôle STS, inventaire des noms, TableId/UserId, tag d’appartenance et conservation des preuves. Aucun écart d’inventaire n’a été observé.

## Résultats réellement observés

Le journal [preuves/cleanup.txt](../preuves/cleanup.txt), les [résultats structurés](../preuves/results-cleanup.json) et la [capture réelle](../preuves/13-cleanup.png) documentent les 13 étapes C00–C12. Chaque vérification de suppression a été distinguée d’un refus IAM :

- C00 : identité, région, appartenance, inventaire et sauvegarde des preuves vérifiés.
- C01–C02 : l’unique clé a été désactivée (état Inactive observé), supprimée, puis la liste était vide.
- C03–C04 : inline `TP2AFGAC` supprimée ; `GetUserPolicy` a répondu `NoSuchEntity`; les listes de permissions/groupes étaient vides et le UserId conforme.
- C05–C07 : utilisateur supprimé ; `GetUser` a répondu `NoSuchEntity` et `ListUsers` confirmait son absence.
- C08–C10 : seule `NovaUsersTP2A` supprimée ; `DescribeTable` a répondu `ResourceNotFoundException` et `ListTables` confirmait son absence en `eu-north-1`.
- C11 : `aws logout --profile tp2a-admin` rc=0 et cache de login vide.
- C12 : seul le `.secrets/` du projet TP4 a été supprimé et son absence vérifiée. `~/.aws`, le compte AWS, le Builder ID et MFA n’ont pas été ciblés.

## Portée et limite d’audit

Aucune ressource hors TP4, aucun rôle `/managed/`, aucune SCP, aucun compte ou MFA n’a été modifié. L’audit préalable de `GetLoginProfile` reste **PARTIAL** : une SCP a renvoyé un Deny explicite. `AccessDenied` n’a jamais été traité comme preuve de suppression ; les absences ont été confirmées par les réponses `NoSuchEntity`/`ResourceNotFoundException` et les opérations de liste.

Les 12 captures initiales, les 23 journaux de tests, les JSON de résultats et les empreintes ont été conservés avant suppression. L’archive expurgée est dans `downloads/` (ignorée par Git) ; le manifeste des empreintes versionné est [preuves/preservation-before-cleanup.json](../preuves/preservation-before-cleanup.json).

**Statut nettoyage : PASS.** Voir le [rapport final](rapport-final.md).
