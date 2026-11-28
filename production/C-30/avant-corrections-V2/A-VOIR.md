# C-30 — Bienvenue, aucun avantage financier

Démo uniquement : `http://192.168.129.32:8085/bienvenue/`.

- Sans code, avec `?code=NON_LISTE_INTERDIT` ou un code fictif : même page « Bienvenue », texte d'Imagine laissé vide, lien « S’abonner ». Aucun code ni libellé interne dans la page.
- Codes démonstration : `fictif-affiche`, `fictif-magazine`, `fictif-evenement`. Un code connu est gardé par la session Woo ; le dernier code connu gagne avant la commande, un inconnu n'écrase rien.
- Cookie opaque natif `wp_woocommerce_session_*`, HTTPOnly, pas de nouveau cookie propre au code : durée native de la version installée, 2 jours invité / 7 jours connecté, renouvelée par Woo à son seuil natif (sources officielles installées et empreintes dans `standard2-V2.json`). Pas de traceur ni de script ajouté par ce lot.
- Administration : `Réglages → Codes suivis` (liste fermée, journalisée) ; `Imagine → Codes suivis` (période UTC, nombres de commandes payées et nombres C27 présentés séparément, sans identité).
- Export et effacement natifs : callbacks « Codes suivis », candidat de checkout inclus. Effacement ne change ni la commande, ni son total, ni ses droits.

**Interprétation technique explicite** : au checkout classique seulement, `_imagine_code_suivi_candidat` conserve une sélection provisoire pour permettre le paiement asynchrone sans session. Seule `_imagine_code_suivi` après état payé et date native compte ; transfert unique verrouillé, candidat supprimé, sceau technique préservé après effacement. Aucun code C16, aucun prix ni coupon. Aucun tunnel réel ni checkout Blocks prétendu livré. L'avantage de bienvenue reste à décider par Imagine, dans un lot séparé.

Preuves : `native-final2-V2.json` (23 contrôles, vraies commandes natives fictives rollbackées), `browser-final2-V2.json` (99 contrôles, 10 réponses), `browser-final2-V2-sessions.json` (table de sessions restituée exactement), image/rejeu T01, mutation réelle du validateur inconnue dans PHPUnit. Source C27 du compte inchangée, libellé avec antislash relu jusque dans l'export.

Capture : `browser-final2-V2.png`. Les commandes/identités/réglages testés ont retrouvé leur état initial ; seule la page et les trois codes de démonstration explicitement demandés restent.

```
python -B production/C-30/verifier.py
python -B production/C-30/verifier.py --live
python -B production/B-13/qualifier.py C-30
```
