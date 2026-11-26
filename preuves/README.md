# Preuves réelles et expurgées

Les `.txt` produits ici contiennent des résultats réellement observés par AWS CLI et expurgés. Les suites ajoutent `I01.txt`, `A01.txt`… et `B01.txt`… seulement après un appel réel, ainsi que leurs JSON de résultats. Les contrôles locaux sont identifiés séparément ; ils ne prouvent aucun droit AWS.

Les captures suivantes sont attendues et **ne doivent être créées qu'à partir d'une vraie capture écran**. Aucun PNG n'a été fabriqué ni reconstitué à partir d'un résultat supposé. Aucun outil de capture de navigateur n'est disponible dans cette session ; les journaux sûrs ne sont pas présentés comme des captures.

| Fichier demandé | Contenu à capturer | État |
| --- | --- | --- |
| 01-table-created.png | Table ACTIVE et schéma | À FAIRE |
| 02-items.png | Deux items fictifs | À FAIRE |
| 03-reader-no-permission.png | Refus initial réel | À FAIRE |
| 04-projection-allowed.png | A01 | À FAIRE |
| 05-ssn-denied.png | A02 | À FAIRE |
| 06-no-projection-denied.png | A03 | À FAIRE |
| 07-query-allowed.png | A04 | À FAIRE |
| 08-scan-two-items.png | A05 et ses deux items | À FAIRE |
| 09-write-denied.png | A07 ou B08 | À FAIRE |
| 10-leadingkeys-001.png | B01 | À FAIRE |
| 11-leadingkeys-002-denied.png | B02 | À FAIRE |
| 12-scan-denied.png | B07 | À FAIRE |
| 13-cleanup.png | Absences après nettoyage autorisé | NON AUTORISÉ |

Afficher de préférence le journal déjà expurgé dans un terminal neutre avant une vraie capture. Masquer le numéro de compte et le bandeau d'identité dans la console. Ne jamais photographier les écrans de création de clé, un QR MFA, les cookies, les codes de connexion ou le contenu de `.secrets/`. Relire visuellement chaque image avant Git.

`scripts/redact.py` expurge des textes via stdin/stdout. Ne pas lui transmettre de credentials : ce n'est pas une garantie de détection de tous les secrets possibles. Il n'expurge pas les images ; une capture sensible doit être refaite ou expurgée localement puis revue.
