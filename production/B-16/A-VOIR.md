# B-16 — à ouvrir sur la démo fictive uniquement

Base : `http://192.168.129.32:8085`.

- `/demo-2026-t1-reserve-1/` : anonyme = titre, résumé éditorial, thématique, numéro et extrait/paywall ; A-PAPIER = texte complet, sans appel final ; P-NUMERO = texte complet puis appel final vers la même destination que « S'abonner » du menu.
- `/demo-2026-t1-ouvert/` : libre pour tous ; depuis l'instruction 1 de la fusion, aucun appel final pour le seul motif C08 `contenu_ouvert` : ce motif ne permet pas d'inférer l'origine du droit, et une seconde projection des droits est interdite.
- `/c08-article-reserve-automatique/` : résumé vide = aucun résumé ajouté, pas de signature par défaut.
- Éditeur d'article : extrait natif = résumé public, étiquettes = mots-clés ; boîte « Signature publique » = nom signé sans lien ni adresse. Vide, aucun paragraphe. Les essais temporaires signature/mots-clés et numéro manquant sont restaurés ; aucune signature inventée ne reste sur la démo.
- Mode lecture : l'en-tête entier et l'appel final disparaissent via le marqueur B03 existant. Corps C08 et médias B11 conservés.

Capture de la vraie réponse anonyme, pendant les champs fictifs temporaires : `browser-final5-V2.png`. Vérifier le visuel avec les maquettes quand elles arriveront ; aucun design livré ici.

Commandes :
```
python -B production/B-16/verifier.py
python -B production/B-16/verifier.py --live
python -B production/B-13/qualifier.py B-16
```

Capture courante : `browser-corrections-final-V2.png`. Réception courante `reception-corrections-V2.json`. R1 : méthode `abonne()` supprimée, seuls les motifs C08 achat/découverte complets donnent l'appel ; les autres, dont abonnement/offert/groupe/grâce/équipe, ne le donnent pas. R2 : HTML complet de l'en-tête **et du footer d'appel**, attributs/href/commentaires inclus ; mutation posée dans un attribut du vrai bloc **avant extraction**, puis enlevée. R3 : références officielles WordPress ajoutées au README, sans navigation externe. Rejeu **1217 tests / 36738 assertions PASS**, outils23/852 sans échec, paquets13 sans échec.

Preuves corrigées : 15 contrôles natifs dont vrai profil A-PAPIER temporairement `complimentary`, puis `pending-cancel` avant/à/après la borne, et 77 contrôles sur 9 réponses. État métier, profils et Action Scheduler relus identiques. Les caches de rapports WCS planifiés à shutdown sortaient du rollback : première dérive constatée, restaurée exactement par IDs, puis seul callback différé de caches de rapports neutralisé dans le processus de recette, jamais dans le code livré ; `recovery-actions-final-V2.json` et dernière preuve native le distinguent. Cinq tests PHPUnit B16 utilisent aussi le vrai C08 sur entrées natives du banc C20, inchangé. Complément B11 initial23PASS conservé, single.php n'a pas rechangé pendant cette correction.

Les reçus initiaux et A-VOIR antérieur restent historiques. Aucune clôture visuelle ni GO sur le réel.
