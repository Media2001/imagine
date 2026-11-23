# B-01 — À voir dans le navigateur

Site unique : **imagine-test-demo**, démonstration entièrement fictive. Thème Imagine actif.
Toutes les pages portent « squelette, sans habillage ». Noir sur blanc, une colonne ; les couvertures colorées sont les images factices déjà fournies par B-00, pas une direction graphique.

| Gabarit | Adresse à ouvrir | Ce qui doit apparaître |
|---|---|---|
| Accueil | http://192.168.129.32:8085/ | Le numéro fictif 4, le plus récent selon sa date de sortie, cinq derniers articles, liens kiosque, thématiques, agenda ; emplacement du futur lien d’abonnement. |
| Kiosque | http://192.168.129.32:8085/numeros/ | Les cinq numéros, dans l’ordre T4, hors-série, T3, T2, T1 ; couverture et date. |
| Numéro | http://192.168.129.32:8085/numeros/demo-2026-t4/ | Couverture, présentation, quatre articles du numéro au sommaire, lien vers son PDF factice. |
| Article ouvert | http://192.168.129.32:8085/demo-2026-t1-ouvert/ | Titre, chapô, signature fictive, numéro d’appartenance, thématique et texte complet jusqu’à la scène fictive 5. |
| Thématique | http://192.168.129.32:8085/thematiques/demo-thematique-3/ | Les cinq articles de « Futurs fictifs », tous numéros confondus, sans corps d’article. |
| Agenda — liste | http://192.168.129.32:8085/evenements/ | Les deux événements inventés, ordonnés par date croissante. |
| Événement — fiche | http://192.168.129.32:8085/evenements/demo-events-2/ | Titre, date fictive du 11 décembre 2026, texte, retour à l’agenda. |
| Partenaires — liste | http://192.168.129.32:8085/partenaires/ | Les deux partenaires fictifs et leurs liens. |
| Partenaire — fiche | http://192.168.129.32:8085/partenaires/demo-partners-2/ | Titre, texte fictif, retour à la liste. |
| Page simple | http://192.168.129.32:8085/calendrier-fictif/ | Le calendrier de parution factice 2026–2028, avec son tableau. |
| Recherche | http://192.168.129.32:8085/?s=fictif | Formulaire natif, résultats sous forme de titres/liens/extraits, pagination native. |
| 404 | http://192.168.129.32:8085/b01-page-inexistante-xyz/ | « Page introuvable », recherche et retour à l’accueil ; statut HTTP **404**, pas un faux succès 200. |
| En-tête et pied communs | http://192.168.129.32:8085/ | Navigation, accès au compte via la connexion WordPress native, lien « S’abonner », lien d’évitement et mention du squelette en pied. |

## Contrôles supplémentaires

- Article réservé : http://192.168.129.32:8085/demo-2026-t1-reserve-1/ — verrou natif provisoire B-00 conservé ; le texte réservé ne doit pas être dans la réponse anonyme. Ce n’est pas encore le paywall C-08.
- Recherche vide : http://192.168.129.32:8085/?s=b01-aucun-resultat-xyz — état vide explicite.
- Repli `index.php` : http://192.168.129.32:8085/?post_type=post — liste minimale de contenus.

« S’abonner » mène à l’emplacement identifié sur l’accueil : aucun tunnel ni achat n’a été inventé. L’espace compte est hors périmètre ; ne pas confondre son lien d’entrée avec un espace déjà réalisé.

## Preuves

- `verification.json` : **41 pages HTML**, **7 ressources**, **500 assertions réussies / 0 échec** ; les 45 contrôles runtime sont inclus dans ces 500, pas à additionner.
- `http/` : corps réels de toutes les réponses HTML ; statuts, types MIME, URL et empreintes dans `verification.json`.
- `installation.json` : activation par le script B-00, relecture du thème actif et des empreintes de ses 19 fichiers.
- `browser.json`, `captures/` : **19 captures réelles** (15 bureau, 4 mobile), dont les 12 gabarits de page et deux états supplémentaires ; aucune largeur débordante mesurée.
- `browser-interactions.json` : quatre contrôles navigateur réussis ; lien d’évitement au clavier, focus du contenu, article ouvert complet et recherche native.
- Les journaux rouge/vert, le défaut HTML trouvé sur le formulaire protégé puis sa correction sont conservés dans `tests/`.

La validation est structurelle : parseur HTML5 local html5lib 1.1 et contrôles sémantiques explicites. Ce n’est ni une certification W3C exhaustive, ni un audit WCAG complet, ni une validation graphique du futur site.
