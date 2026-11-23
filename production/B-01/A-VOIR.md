# B-01 — À voir, état intégré actuel

**Site unique fictif : imagine-test-demo.** Thème Imagine actif, WordPress 7.0.9, langue française. Toutes les pages portent « squelette, sans habillage » : noir/blanc, police système, une colonne, pas de direction graphique inventée.

| Gabarit | Adresse | Ce que Ced doit voir |
|---|---|---|
| Accueil | http://192.168.129.32:8085/ | Numéro fictif 4, daté « 15 octobre 2026 », puis exactement les cinq articles IDs **82, 81, 45, 44, 43** dans cet ordre : deux articles C08, reportage libre T4, réservés T4 n°3 et n°2. Aucun Hello world. |
| Kiosque | http://192.168.129.32:8085/numeros/ | Cinq numéros : T4, HS, T3, T2, T1 ; dates françaises et couvertures fictives. |
| Numéro | http://192.168.129.32:8085/numeros/demo-2026-t4/ | Couverture, résumé, quatre articles T4 au sommaire, PDF factice. |
| Numéro augmenté | http://192.168.129.32:8085/numeros/demo-2026-t1/ | Quatre articles B00 et **deux C08**, pas une fausse attente de quatre articles totaux. |
| Article ouvert | http://192.168.129.32:8085/demo-2026-t1-ouvert/ | Titre, chapô, auteur, numéro, thématique et corps jusqu'à « Scène fictive 5. ». |
| Article réservé | http://192.168.129.32:8085/demo-2026-t1-reserve-1/ | Rendu C08 actuel, sans corps réservé dans la réponse anonyme exercée. Le mot de passe natif B00 a déjà été retiré. Ce contrôle n'est pas une certification du paywall. |
| Thématique | http://192.168.129.32:8085/thematiques/demo-thematique-3/ | Articles liés, tous numéros confondus, titres/liens/extraits publics. |
| Agenda | http://192.168.129.32:8085/evenements/ | Deux événements, dates croissantes localisées. |
| Événement | http://192.168.129.32:8085/evenements/demo-events-2/ | « 11 décembre 2026 », titre, texte et retour agenda. |
| Partenaires | http://192.168.129.32:8085/partenaires/ | « Partenariat », déclaration des liens sponsorisés, deux partenaires. `rel="sponsored"` vérifié dans le HTML des cartes. Distinction graphique à fournir par le designer. |
| Partenaire | http://192.168.129.32:8085/partenaires/demo-partners-2/ | Titre, contenu fictif et retour liste. Les liens externes éventuels du contenu sont déclarés sponsored ; aucun partenaire réel contacté. |
| Page simple | http://192.168.129.32:8085/calendrier-fictif/ | Calendrier brut B00 de **15 lignes 2026–2028** ; seuls les cinq numéros 2026 sont matérialisés. |
| Recherche | http://192.168.129.32:8085/?s=fictif | Formulaire natif GET, cartes et pagination. La recherche serveur dans les corps réservés relève du correctif bloquant C08, pas de ce PRET B01. |
| Recherche vide | http://192.168.129.32:8085/?s=b01-aucun-resultat-xyz | « Aucun résultat pour votre recherche. » |
| 404 | http://192.168.129.32:8085/b01-page-inexistante-xyz/ | « Page introuvable », recherche, accueil ; vrai HTTP **404**. |
| Repli index | http://192.168.129.32:8085/?post_type=post | Liste native minimale. |
| En-tête/pied | http://192.168.129.32:8085/ | Sept entrées stables, évitement clavier et mention squelette. Compte = lien de connexion ; abonnement = emplacement explicite, pas un tunnel d'achat. |

## Preuves actuelles

- `b01-final-verification.json` : état final, sources et preuves liées par empreintes ; `PRET` vaut seulement prêt au second tour technique B01.
- `verification.json` / `runtime.json` / `http/` : **554 assertions réussies**, dont **62 runtime incluses**, **43 pages HTML**, **7 ressources**, aucune erreur structurelle.
- `tests/runtime-final.json` : **16 contrôles PHP réussis**, publication sans date refusée, publication datée native/REST autorisée, collision d'URL, localisation et sémantique sponsored.
- `tests/isolated-environment.json` : **6 tests Python réussis**, tous les paquets de validation présents dans un environnement neuf, installé hors ligne depuis les six wheels figés.
- `tests/oracle-cardinality-mutant.json` : l'ancien contrôle limité au nombre est volontairement rejeté par le nouveau test.
- `installation.json` et `plugin-installation.json` : thème déployé par l'option actuelle `--theme-only`, garde date séparé, readback exact.
- `browser.json` / `captures/` : **19 captures actuelles**, 15 bureau et 4 mobile, et **5 contrôles d'interaction** réussis ; pas de débordement mesuré.
- `scope-integrity.json` : C08/C09/C10 protégés et données inchangés ; aucune réinitialisation des profils.

Les anciens `http/`, captures, rapports et PRET de la livraison pré-C08 sont uniquement dans `historique/pre-C08-livraison-initiale/` ; ils ne décrivent plus l'état courant. Les journaux rouges/verts de correction restent des traces de tests, pas un second jeu de preuves actuel.

Pas de certification WCAG/W3C exhaustive, de performance fine ni de validation graphique. Détails, traçabilité au cahier et reports C08 : `notes.md`.
