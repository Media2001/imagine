# C-33 — comptes non publics en anonyme

Trois adresses à ouvrir en navigation privée :

1. http://192.168.129.32:8085/?author=2 — page introuvable, **404 sans redirection** et sans adresse publique d’auteur. Les archives par nom sont aussi fermées.
2. http://192.168.129.32:8085/wp-json/wp/v2/users — erreur REST **404**, aucune liste de comptes ; même règle pour un numéro, la casse et l’alias rest_route.
3. http://192.168.129.32:8085/?feed=rss2&withoutcomments=1 — flux d’articles : signature B16 si renseignée, sinon nom du site, jamais le nom du compte de saisie. Atom et oEmbed reçoivent le même traitement, adresse de compte supprimée.

Le sitemap est désactivé au repos (`blog_public=0`). La recette l’a réellement activé pour un témoin puis a restauré l’option exacte : index XML non vide, sans section utilisateurs. L’ancienne adresse directe du fournisseur absent rend ici une page HTML 200 sans compte, pas un sitemap utilisateurs (comportement natif documenté, aucune règle de serveur). Six autres types vus : post, page, product, imagine_numero, imagine_evenement, imagine_partenaire. Aucun type de message de visiteur/contact ni pièce privée dans cet index ; rien d’autre n’a été corrigé.

Preuves courantes : `native-corrections-final-V2.json` (**14 contrôles**), `browser-corrections-final-V2.json` (**89 contrôles, 20 réponses HTTP**, capture Edge inspectée : erreur REST `rest_no_route`, statut 404, aucune identité). Tous les noms et toutes les valeurs des en-têtes, doublons compris, sont examinés en mémoire avant occultation ; seules les trois valeurs location/content-type/link sont archivées, avec la liste de tous les noms reçus. Aucune valeur de cookie ni jeton réel n’est archivée. La preuve n’affirme plus « aucun Set-Cookie » à partir d’en-têtes déjà filtrés. Compte témoin publié contrôlé d’abord. **Six mutations natives sur cinq voies**, plus **cinq mutations de preuve** : identité injectée dans X-C33-Audit-Compte, et retrait de l’auteur de l’article témoin dans les quatre réponses RSS2/Atom, avec signature puis repli au nom du site. Les quatre auteurs XML sont comparés exactement, après décodage, dans le seul item/entry témoin ; URI et url de compte contrôlées séparément. Les retraits d’auteur sont rejetés même si le nom du site reste ailleurs dans le document. Administrateur et éditeur conservent le sélecteur d’auteur REST et l’édition native. Aucun privilège étendu.

```bash
python -B production/C-33/verifier.py --live
python -B wp/tests/demo/c33-control-tests.py
python -B production/C-33/offline.py nouvelle-cible-V2
python -B wp/outils/demo/c33.py native nouvelle-native-V2
python -B wp/outils/demo/c33-browser.py nouveau-browser-V2
```

Compte, article, métadonnées, sessions du seul compte témoin, options et sonde retirés/restaurés puis relus (`restored`, `fixture_removed`, `probe_removed` vrais). Les seules différences d’options sont les quatre transients de rendu B13/B15 déjà bornés dans le banc ; **aucune exception native supplémentaire nécessaire**. Snapshot privé avant mutations, sans secret dans le dépôt. Préparation d’image réellement exécutée (`image-corrections-V2.json`), puis rejeu global obligatoire : **1243 tests / 37036 assertions PASS ; OUTILS 23/852, zéro échec ; PAQUETS 13 vérifiés, zéro échec**, A32 et A33 compris (`replay-corrections-final-V2.json`). Le premier rejeu de correction avait relevé `A-33 VERIFIER_TIMEOUT`, tandis qu’A33 porte un PRET : pas de tolérance ni nouveau délai, reçu conservé (`replay-corrections-V2.json`), rejeu suivant entièrement vert. Les tests légers du vrai adaptateur vérifient les six accroches et leurs priorités/arguments, la 404 d’auteur avant canonical et les gardes de flux/connecté : suite C33 **5 tests / 26 assertions**. Contrôleur pur **7 tests verts** ; l’ancien contrôleur est rejoué rouge sur les faux positifs P1/P2 (`controleurs-red-green-corrections-V2.json`, 17 sous-cas refusés).

Réception fraîche : `reception-corrections-V2.json`. Ancien `reception-V2.json`, reçus natifs/navigateur/rejeux et échecs historiques inchangés ; ancien PRET et versions de recette/vérificateur/A-VOIR conservés sous `historique-avant-corrections-V2/`. Échecs initiaux et comportements natifs anciens décrits dans cet A-VOIR historique, sans réécriture. Les fichiers C31/C32 et le README hors C33 sont comparés aux 215 préimages à la finalisation (`voisins-preservation-corrections-V2.json`) ; aucun sceau voisin repris.

Périmètre : anonymes seulement ; rien changé pour les connectés. Pas de 2FA, limitation de tentatives, hébergement, nom public de compte choisi par un humain, ni réécriture globale des identifiants d’auteur présents sur les objets REST posts. Aucun code clos/B16/C26 modifié, aucun nouveau contenu de visiteur collecté ; pas de donnée ni de site réel.
