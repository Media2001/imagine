# Relecture indépendante Codex — B-14

Date : 27 novembre 2026. Références : brief B-14, doctrine, grille de relecture, décisions, cahier des charges §3.2, §3.3 et chapitre 5. Examen du code, des tests et des preuves de `production/B-14`, capture comprise. Aucun accès à un site, une base ou un compte ; aucune lecture de la relecture Claude ; seul ce rapport est écrit.

## 1. Conformité

La composition suit l'ordre demandé : numéro, conversion, reportage libre conditionnel, newsletter, thématiques, trois événements au plus, Soutenir, coopérative, partenaire. Les sections sont rendues côté serveur, titrées et sans style ajouté. Le résumé provient du numéro ; aucun extrait d'article n'est rendu par le composant. La suppression des Derniers articles est documentée. Couverture eager/high, illustration du reportage lazy/low, partenaire B-05 et étiquette Partenariat conservés. README, capture et PRET présents. L'illustration synthétique ajoutée au reportage de démonstration est explicitement signalée.

**B14-01 — important — `wp/plugins/imagine-site/Accueil.php:49` : ancienne ancre d'abonnement perdue.** Le générateur de sections ne conserve que l'ancre des thématiques ; aucune section du nouvel accueil ne porte `id="imagine-abonnement"`. Or les trois gabarits `paywall-abonnement.php`, `paywall-connexion.php` et `paywall-decouverte_epuisee.php` utilisent encore `/#imagine-abonnement` à leur ligne 8 ; le menu de secours utilise aussi cette destination. Un lecteur refusé par le paywall qui clique sur l'abonnement arrive donc sur l'accueil sans atteindre le bloc de conversion. **Correction proposée :** conserver l'identifiant historique sur la section de conversion, sans créer une deuxième section, et vérifier qu'un lien du paywall atteint cette cible unique contenant « S'abonner ».

## 2. Exactitude métier

Cas déroulés à la lecture du code, distincts d'une exécution WordPress :

- **Numéro courant en vente, reportage libre présent.** `numero()` appelle la requête B-04 : publications triées par date éditoriale décroissante puis ID décroissant. Le produit C-14 publié, achetable et en stock fournit le lien d'achat. Le premier article libre dans l'ordre `menu_order`, puis ID, fournit titre, image et lien. La sélection correspond actuellement à celle du gabarit B-04.
- **Produit dépublié, aucun reportage libre.** Le sélecteur de produit ne renvoie plus d'URL ; le bouton d'achat disparaît. Les décisions d'accès sans code `libre` ne sélectionnent aucun reportage ; la section entière disparaît et la newsletter suit la conversion. Aucun corps d'article n'est rendu.
- **Limites de dates et d'effectifs.** À dates de numéro égales, le départage par ID reste celui de B-04. Pour l'agenda, un événement à l'instant de début est déjà classé passé par B-07 ; les événements futurs sont triés par début puis ID, puis limités à trois. Le changement d'année n'introduit pas de règle propre à B-14. Sans numéro publié, le message prévu s'affiche et aucun lien de découverte, d'achat ou reportage n'est produit.

## 3. Tests

Exécutions effectuées sans écriture de preuves supplémentaires :

| Commande | Résultat de cette relecture |
|---|---|
| `python -B production/B-14/verifier.py` | PASS : intégrité des sources et preuves ; 17 contrôles natifs, 45 navigateur, deux profils et un test PHPUnit attestés dans les archives. |
| `python -B production/B-13/qualifier.py B-14` | PASS : neuf contre-exemples du vérificateur, mutations uniquement en mémoire. |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` | Échec d'environnement avant exécution : Docker inaccessible via WSL, `Wsl/Service/E_ACCESSDENIED`. Zéro test exécuté. |

Les 1 206 tests / 36 680 assertions et les 23 outils / 852 contrôles sont les résultats archivés par la production, vérifiés par le premier script, **pas un nouveau rejeu réussi**. Les écarts de paquets A-32 et A-33 sont déclarés et distincts du lot. Les recettes natives, navigateur et `--live` n'ont pas été lancées : elles accèdent au site, ce qu'interdit `relecteurs/AGENTS.md`. Aucune préparation d'image ni installation effectuée.

Les preuves couvrent les deux profils demandés, l'ordre, les attributs des images, les contenus interdits, l'achat avant/après dépublication, l'absence de reportage, Partenariat et les témoins C-26. Elles ne couvrent pas B14-01.

**B14-02 — mineur — `wp/tests/demo/b14-runtime.php:20` : le contrôle « reportage_designe_b04 » ne vérifie pas l'identité du reportage B-04.** Il vérifie seulement que le résultat d'`Accueil::libre()` est libre. Si deux articles sont libres et que B-14 choisit le second, ce contrôle reste vert. Le navigateur ne compare pas non plus l'identifiant du reportage affiché avec celui de la page numéro. **Correction proposée :** prévoir deux articles libres avec des ordres distincts, puis comparer l'identifiant rendu sur l'accueil à celui désigné par B-04 ; couvrir aussi le départage par ID à ordre égal.

## 4. Sécurité et données

Aucune fuite de texte réservé identifiée dans le composant examiné : uniquement titre, miniature et lien pour le reportage, résumé explicite du numéro. Échappements adaptés aux textes, attributs et URL. Le composant n'ajoute ni formulaire, ni écriture, ni endpoint nécessitant nonce ou autorisation. Les preuves utilisent des données fictives et attestent l'absence des témoins C-26 ainsi que zéro tentative HTTP/mail pendant les rendus observés. Cette attestation n'a pas été reproduite en direct durant la relecture.

## 5. Doctrine

Le « standard d'abord » est documenté en cinq lignes avec références WordPress. La composition utilise les images natives et les composants existants, sans nouveau réglage du numéro ni calcul de prix ou de droits. Namespace, typage strict, traductions et échappements sont présents. Aucun besoin d'arbitrage métier ou visuel pour corriger les deux points relevés. La validation visuelle reste extérieure à ce verdict.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles sont présentes dans le README et le relevé de sources ; aucun site documentaire n'a été consulté durant cette relecture.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut de ce niveau identifié.
- **Important : B14-01**, rétablir la destination des liens d'abonnement existants vers l'accueil.
- **Mineur : B14-02**, vérifier l'identité du reportage sélectionné, au-delà de son seul statut libre.

Limite de validation : le rejeu PHP indépendant reste à obtenir dans un environnement où WSL/Docker est accessible ; son échec ici ne démontre pas un échec du code.
