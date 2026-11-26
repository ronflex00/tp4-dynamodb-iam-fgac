# Clé technique — intervention humaine

## État vérifié avant création de clé

L'utilisateur `tp2a-dynamo-reader` existe dans le compte du manifest. Son UserId et son tag d'appartenance ont été vérifiés. Aucun groupe, aucune policy inline, aucune managed policy, aucune permissions boundary et aucune clé n'étaient présents lors de l'audit préalable. La région et la sortie JSON du profil isolé `tp2a-reader` sont préparées. Le profil n'accorde aucun droit par lui-même.

Le rôle administrateur rencontre un **Deny explicite dans une SCP** sur `iam:GetLoginProfile` (rc=254). Aucun mot de passe ni accès console n'a été créé par nos commandes CreateUser. L'absence de login profile n'a toutefois pas pu être confirmée par cette API : audit **PARTIAL**, conservé dans [la preuve](../preuves/audit-login-profile.txt). Aucune permission n'a été ajoutée pour contourner cette restriction. Ce résultat concerne une lecture de métadonnées administrateur ; il ne valide aucun refus DynamoDB du reader.

## Création de la clé dans votre console

IAM → Users → `tp2a-dynamo-reader` → Security credentials → Access keys → Create access key → cas d'usage CLI. Lire les alternatives, puis créer **une seule** clé de laboratoire. Si une clé est déjà présente, ne pas en créer une seconde : faire vérifier l'état par l'agent. Si AWS refuse l'opération, communiquer seulement l'erreur expurgée ; ne pas changer le plan ni les permissions.

Ne pas faire de capture de l'écran de clé ni exporter les secrets dans les livrables. Saisir les valeurs uniquement dans votre terminal personnel, hors des outils Codex :

```fish
cd /home/gatta/Downloads/TP4
source scripts/use-lab-env.fish
aws configure --profile tp2a-reader
chmod 600 .secrets/config .secrets/credentials
```

Au prompt : saisir l'Access Key ID et la Secret Access Key, région `eu-north-1`, sortie `json`. Les secrets ne doivent pas être collés dans la conversation, une commande ou un fichier versionné. Ne pas utiliser `aws configure` pour créer une clé administrateur.

Confirmer simplement **« profil reader configuré »**. Il n'est pas nécessaire d'envoyer une sortie STS ou un numéro de compte. L'agent vérifiera ensuite l'identité exacte du reader, l'unique clé active et le véritable refus GetItem avant de poser toute policy FGAC.

## Reprise automatique après confirmation

1. `python3 scripts/lab.py test-initial` : STS reader exact, compte conforme, un véritable AccessDenied de GetItem projeté. Une erreur NoCredentials ou ExpiredToken reste un problème d'authentification.
2. `python3 scripts/lab.py apply-attributes`, propagation IAM, puis `bash scripts/test-attributes.sh`.
3. `python3 scripts/lab.py apply-leadingkeys` remplace la même inline policy ; propagation, puis `bash scripts/test-leadingkeys.sh`.
4. Matrice, captures réelles, compte-rendu et validations seront complétés à partir des résultats observés. Arrêt avant tout nettoyage.

Le contrôle GetLoginProfile conserve explicitement sa limite PARTIAL lorsque la même SCP le refuse ; les tests DynamoDB sont évalués indépendamment à partir de leurs réponses réelles. Tout autre problème d'audit continue d'arrêter l'exécution.
