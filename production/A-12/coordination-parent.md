# Coordination A-12 / parent

Le blocage runtime est levé. Dernier rejeu natif : 118 assertions PASS, 7 pures PASS, 7 gates runner PASS ; PHPCS strict sans erreur/avertissement. Sources A-11 et A-02 inchangées. Trente types et dix-huit taxonomies exactement égaux à l'oracle dans chaque mode, `a12_dynamic` inclus et `a12_never` exclu.

**Commande opérateur modifiée** : lancer `python3 wp/outils/bascule/a12/confine.py ...`, pas le PHP brut. Le lanceur applique Landlock au code tiers avant bootstrap et refuse hors conteneur Linux déconnecté. Les deux lignes à intégrer sont à jour dans `integration.md`.

Le parent garde l'ownership de `wp/tests/preparer-image.ps1` et du mode d'emploi commun. Pour déposer PRET sans affirmation invérifiable, le worker doit pouvoir lire le reçu réel de préparation (exit 0, image vérifiée) et l'intégration commune. Merci de déposer leur référence/résultat dans ce dossier A-12 ou de les confirmer par le canal de coordination. Le worker n'exécute aucune préparation partagée ni modification du mode d'emploi commun.
