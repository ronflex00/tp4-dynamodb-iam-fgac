# Nettoyage final — autorisation en attente

**Aucune suppression n'est autorisée à ce stade.** Attendre le message explicite `CLEANUP` de l'utilisateur après le rapport pré-nettoyage.

## Préparation sans suppression

```bash
bash scripts/cleanup-check.sh
```

Ce contrôle exige le manifest privé, le même compte, le même principal admin, la même région, les marqueurs du laboratoire, les TableId/UserId attendus, la table ACTIVE, les deux items conformes, la policy B et toutes les suites observées. Il n'exécute aucune suppression et ne vaut pas autorisation.

L'audit GetLoginProfile conserve sa limite PARTIAL lorsqu'une SCP refuse explicitement cette lecture ; ce refus ne vaut pas preuve d'absence d'un accès console. Cette limite doit figurer dans le rapport, même si les tests DynamoDB ont ensuite tous été observés conformes.

## Exécution après autorisation uniquement

```bash
bash scripts/cleanup.sh CLEANUP
```

Le mot fourni en argument sert de garde-fou ; l'opérateur doit aussi avoir reçu l'instruction explicite dans la conversation. Le script ne peut pas vérifier seul le consentement humain.

1. Contrôler l'identité et les deux ressources exactes avant la première suppression ; refuser un autre compte, principal, tag ou identifiant unique.
2. Désactiver puis supprimer l'unique Access Key de `tp2a-dynamo-reader` ; ne jamais afficher son identifiant ou secret. Vérifier la liste vide.
3. Supprimer uniquement l'inline policy `TP2AFGAC`, puis cet utilisateur. Toute policy, groupe ou ressource inattendue bloque le script.
4. Supprimer uniquement `NovaUsersTP2A`. Attendre puis observer `ResourceNotFoundException` ; vérifier aussi `NoSuchEntity` pour l'utilisateur. Un AccessDenied ne prouve aucune absence.
5. Terminer le seul profil admin par `aws logout --profile tp2a-admin`, conformément à la [documentation CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
6. Supprimer uniquement `/home/gatta/Downloads/TP4/.secrets`, après ces observations. Préserver Builder ID, MFA et preuves non sensibles. Ne pas toucher à `~/.aws` ni aux dossiers TP3.
7. Relire `preuves/cleanup.txt`, faire une vraie capture `13-cleanup.png`, mettre à jour le compte-rendu et le rapport final, exécuter l'audit des secrets puis créer un commit local.

Si le nettoyage est interrompu, conserver le manifest et les profils ; ne pas annoncer CLEANUP PASS. Le script peut reprendre si une ressource est déjà absente ou une clé a déjà été supprimée, sans étendre la portée. Une session expirée doit être réauthentifiée avant la reprise. Ne jamais supprimer le manifest pour contourner un contrôle d'appartenance.

Statut observé : **NOT TESTED — nettoyage non lancé et aucune autorisation CLEANUP reçue.**
