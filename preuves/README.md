# Preuves réelles et expurgées

Les `.txt` produits ici contiennent des résultats réellement observés par AWS CLI et expurgés. Les suites ajoutent `I01.txt`, `A01.txt`… et `B01.txt`… seulement après un appel réel, ainsi que leurs JSON de résultats. Les contrôles locaux sont identifiés séparément ; ils ne prouvent aucun droit AWS.

Les captures 01 à 12 **proviennent de vrais écrans**. Les deux premières montrent de nouvelles réponses AWS dans des fenêtres foot dédiées. Les captures reader affichent les journaux expurgés et datés des appels réellement exécutés ; leur statut et leur code de sortie sont visibles. Toutes ont été revues avant copie dans preuves/. Les numéros de compte sont masqués ; seuls les items fictifs du TP apparaissent. Voir [captures administrateur](captures-admin.txt) et [captures reader](captures-reader.txt). Aucun écran de clé n'est capturé.

| Fichier demandé | Contenu à capturer | État |
| --- | --- | --- |
| 01-table-created.png | Table ACTIVE et schéma | CAPTURE RÉELLE REVUE |
| 02-items.png | Deux items fictifs | CAPTURE RÉELLE REVUE |
| 03-reader-no-permission.png | Refus initial réel | CAPTURE RÉELLE REVUE |
| 04-projection-allowed.png | A01 | CAPTURE RÉELLE REVUE |
| 05-ssn-denied.png | A02 | CAPTURE RÉELLE REVUE |
| 06-no-projection-denied.png | A03 | CAPTURE RÉELLE REVUE |
| 07-query-allowed.png | A04 | CAPTURE RÉELLE REVUE |
| 08-scan-two-items.png | A05 et ses deux items | CAPTURE RÉELLE REVUE |
| 09-write-denied.png | A07 | CAPTURE RÉELLE REVUE |
| 10-leadingkeys-001.png | B01 | CAPTURE RÉELLE REVUE |
| 11-leadingkeys-002-denied.png | B02 | CAPTURE RÉELLE REVUE |
| 12-scan-denied.png | B07 | CAPTURE RÉELLE REVUE |
| 13-cleanup.png | Absences après nettoyage autorisé | NON AUTORISÉ |

Afficher de préférence le journal déjà expurgé dans un terminal neutre avant une vraie capture. Masquer le numéro de compte et le bandeau d'identité dans la console. Ne jamais photographier les écrans de création de clé, un QR MFA, les cookies, les codes de connexion ou le contenu de `.secrets/`. Relire visuellement chaque image avant Git.

`scripts/redact.py` expurge des textes via stdin/stdout. Ne pas lui transmettre de credentials : ce n'est pas une garantie de détection de tous les secrets possibles. Il n'expurge pas les images ; une capture sensible doit être refaite ou expurgée localement puis revue.
