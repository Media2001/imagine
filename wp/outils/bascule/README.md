# Bascule

Ces scripts transforment l’existant sur la copie vérifiée, puis sur une copie fraîche lors de la mise en ligne décidée par Ced. Ne jamais remonter une base de staging. Ne placer ici ni neutralisation, ni anonymisation, ni installation de Novamira.

Exécuter `bash lancer` dans le contexte isolé choisi par l’opérateur ; le lanceur ne cherche pas de site et n’ouvre aucune connexion. Il valide les noms et permissions avant de commencer, puis exécute les fichiers exécutables `010-nom`, `020-nom`, etc. dans l’ordre numérique. Chaque numéro est unique. Chaque script futur doit être idempotent et testé séparément. À la première erreur, le lanceur s’arrête et renvoie le code du script. Aucun saut automatique au redémarrage : on reprend depuis le début. Le journal de progression (nom, résultat, code ; aucune sortie métier) va sur stderr, à conserver par l’appelant hors racine web. Aucun script numéroté à ce stade.
