# B-04 — Première livraison (historique)

**Remplacé pour la relecture courante par `CORRECTIONS.md` et `verification-corrections-finale.json`.** Les comptes, mesures et conclusions ci-dessous décrivent la première livraison, pas les corrections du second passage.

**Fait** : trois gabarits livrés sur imagine-test-demo ; helper commun de présentation C08, achat C14 public fictif et PDF C11 côté serveur.
**Prêt à relire** : B-04 ; `A-VOIR.md`, `verification-finale.json`, captures et besoins designer fournis.
**À valider par Ced** : l’habillage, pas les droits ni un paiement. Aucun GO réel demandé ou présumé.
**Bloqué** : rien pour ce lot fictif. Le précédent arrêt est archivé dans `historique-arret/`.
**Ensuite** : vérification indépendante et rapport/verrou du parent ; aucun Git, file ou rapport global modifié ici.

## Vérifié

**554 contrôles verts, zéro échec**, plus **9 contrôles de préservation verts** : PHP, HTTP, vrai produit Woo, pagination/thématiques, vingt articles, sécurité, navigateur et régressions B03. Détail calculé dans `verification-finale.json`. Seize captures à 375/1280 px ; focus et liens suivis au clavier, zéro exception JS ou débordement constaté. `preparer-image.ps1` relancé sans modification : sortie 0, image T01 vérifiée ; aucun paquet installé.

Les deux mêmes numéros **11 et 39** ont été visités sous anonyme, a-carte et p-numero. Les droits différant réellement, aucune couverture n’a été fabriquée : a-carte lit les articles du 11 mais son PDF antérieur reste fermé ; son PDF du 39 est ouvert. p-numero possède le 11, pas le 39. Aucun corps réservé, URL physique PDF ou indice PDF supplémentaire dans les pages sans droit ; les routes C11 ont été réellement demandées, autorisées/refusées selon le visiteur.

## Décisions prises à défaut

- Prérequis purement techniques autorisés : **nouveau produit propre B04 2475**, simple natif, publié, virtuel, zéro euro, sans stock réel, associé au 11 par C14. Le produit historique **271 reste privé** ; aucune commande, aucun droit, email ou paiement créé. Rejeu : `wp/outils/demo/b04.py product`.
- Le magasin natif est en « coming soon ». Exemption de présentation **GET/HEAD du seul produit marqué B04 sur la cible locale exacte**, via le hook Woo ; aucune option de visibilité changée, aucun checkout/cart exempté. Support Woo natif et suppression de ses wrappers redondants dans le thème : la destination présente le vrai formulaire produit, jamais un lien vers le produit privé.
- Présentation du numéro = extrait public enregistré. Son ancien corps contient un sommaire et un lien PDF ; il n’est pas rendu aveuglément et reste inchangé. Extraits d’articles explicites seulement, jamais générés depuis le corps réservé. Pas de dossier éditorial ou d’audio inventé.
- Pagination WordPress conservée, taille du site 10. Test du même main query natif sur trois pages de taille 2 et liens natifs, sans modifier de réglage. Une sonde sans date a révélé la garde B01 existante (brouillon) : le test a été corrigé, sans la contourner ni changer les sources B01.

## Vingt vrais articles et préservation

`queries-20.json` : vrai numéro temporaire **2500**, articles **2501–2520**, vrais GET HTTP utilisant `wp()` et le chargeur natif de gabarits. Requêtes SQL **page entière / à partir du gabarit** : anonyme **93 / 32**, a-carte **183 / 110**, p-numero **182 / 113**. Ce sont les coûts observés, non une promesse d’optimisation ; l’adaptateur existant relit des droits natifs par article. Aucun cache de droits ou recalcul métier ajouté. Les **21 objets exacts** et le contrôleur HTTP ont ensuite été supprimés et relus absents ; le rejeu des données avait préservé leurs IDs.

Les **146 objets préexistants**, leurs métadonnées/relations, utilisateurs, options et fichiers du plugin partagé sont préservés. Seul objet ajouté durablement : 2475. L’écart usermeta brut vient seulement des deux `wc_last_active` de 9 et 28 : remplacer leurs valeurs en mémoire reproduit exactement le gel ; **aucune restauration de base**. Preuves brutes et réconciliées conservées. Produit et activité native sont des deltas B04 connus, pas une raison de rejouer le contrôle global historique B03.

Cinq fichiers du thème, scripts/tests `b04*` et ce dossier seulement. Bootstrap C15 et sources/fixtures C09/C14 préservés. Timeout du pilote après huit étapes vertes : finalisation contrôlée sans recréer les objets nettoyés. Python QA demandé utilisé, sauf navigateur sur le Playwright 3.11 existant. Commandes, incidents et détails : `COMMANDES.md`.

