# A-33 — Historique du blocage initial

Les constats ci-dessous sont les refus authentiques du premier candidat, pas l'état de livraison courant. Le parent a ensuite appliqué la fusion A-32 et requalifié sa photographie, puis rescellé et lu A-32 PASS. Le premier candidat A-33 jamais qualifié a été sorti sans perte vers le scratch a32-a33-final-2226 pour reprendre l'installation documentée de LIVRAISON.md, sans modifier aucun lecteur. La réception finale post-enregistrement, dont dépend PRET, reste extérieure au paquet dans files/rapports/.

L'outil A-33 et sa matrice propre sont terminés : 30 tests Python dans chacune des deux consoles Windows, 23 contrôles PHP purs et 52 contrôles natifs par console, PSR-12 sans erreur ni avertissement. Windows mesuré : Python **3.11.15**, UTF-8 / cp1252, TMPDIR absent. Bases et fichiers du semis identiques avant/après ; les sept canaux et les deux types inconnus distincts sont couverts. L'image a été repréparée après le dernier changement de tests.

Le portail général final a réellement été exécuté successivement dans les deux consoles. Dans chacune : **1 204 tests, 36 671 assertions, zéro échec/erreur/ignoré ; 23 outils, 852 contrôles, zéro échec**. Mais sa ligne indépendante reste rouge :

```text
PAQUETS : 12 vérifiés, 1 échecs ; hors rejeu : aucun ; A-32 A32_PARTIAL_EVIDENCE
```

`wp/tests/a32/run.py:sources()` photographie récursivement `wp/outils/bascule/`, en excluant seulement a29/a30/a31 et certains README. L'ajout demandé d'A-33 introduit donc **huit nouveaux fichiers** dans sa photographie. Comparaison exacte avec `production/A-32/preuves/final/sources.json` : huit ajouts, aucun ancien fichier changé, aucun supprimé (`a32-impact.json`). C'est une invalidation par ajout de lot, pas une modification d'A-32 ou du gardien. Le lecteur A-32 sans argument reproduit lui-même le refus ; A-31 reste vert.

Aucun lecteur ni empreinte d'A-32 n'a été changé ; aucun paquet n'a été exclu. Les **92 fichiers protégés** de l'import, des lecteurs réutilisés et du lanceur sont inchangés (`protection.json`). PRET A-33 n'est pas créé. Le paquet courant préserve la matrice propre verte ET les vrais portails rouges ; son vérificateur reste volontairement rouge `A33_GATES_INVALID`. Une sortie Composer/PowerShell 0 n'est pas promue en portail accepté.

Après création de la déclaration A-33, un rejeu général indépendant a confirmé la découverte et l'exécution du nouveau lecteur dans le vrai bac T-03 : **13 paquets vérifiés, deux refus attendus (A-32 `A32_PARTIAL_EVIDENCE`, A-33 `A33_GATES_INVALID`), aucune exclusion**. Les 1 204 tests et 852 contrôles restent verts. Ce reçu de lecture après sceau est conservé hors du paquet : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a33-20261127-2055/post-registration/reception.json`. Les onze sondes du lecteur en miroir scratch ont également passé leurs attendus de blocage/refus ; ce n'est pas un PASS du paquet. L'inverse positif du mutant de portail global n'est pas revendiqué sur cette base déjà rouge.

## Autorisation technique nécessaire au parent

Faire requalifier A-32 par son propriétaire sur les sources finales incluant A-33, sans assouplir son lecteur, sans changer les empreintes à la main et sans exclure A-32. Ensuite seulement : replays A-33 et A-32 tous inclus, re-sceau par les contrôles propres, PRET. La finalisation de T-03 reste au parent et n'a pas été commencée ici.

Un premier essai général a aussi observé un échec tiers `ContactBrevoC29Test::testMatricePureIndependante` / `refus_hors_catalogue` ; il est conservé hors dépôt dans le scratch `pre-gates`. Il n'a été ni réparé ni effacé par A-33. Les deux portails finaux ne reproduisent plus cet échec ; ils ne sont bloqués que par A-32.

## Lecture parent exacte, depuis la racine du dépôt

```text
python -B production/A-33/verify.py
python -B production/A-32/verify.py
python -B production/A-31/verify.py
```

Attendus actuels : A-33 = sortie 1 / `A33_GATES_INVALID`, A-32 = sortie 1 / `A32_PARTIAL_EVIDENCE`, A-31 = sortie 0 / `A31_PACKAGE_PASS`. Aucun argument, aucune mutation.

Limites du banc : un magasin classique ; extensions commerciales inactives pendant le collecteur ; variante import matérialisée par son empreinte native et non par un nouvel import gelé. Les originaux sont pesés, pas les miniatures, fichiers non inscrits ou dossiers privés extérieurs. Aucun poids des dossiers exclus n'est reconstitué ; aucun usage réel autorisé.
