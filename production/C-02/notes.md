# C-02 — notes de livraison et limites

Statut : bibliothèque PHP pure prête à relire, pas de GO, pas de déploiement.
Références locales : `briefs/C-02-numero-entreprise.md`, cahier des charges
§3.4 (`docs/cahier-des-charges-v3.1.txt`, lignes 444–449),
`docs/decisions.md` point 8 et `docs/recette/cas.md` R-06.

## Ce qui est livré

- `NumeroEntreprise::depuisSaisie(string)` normalise et contrôle en une opération.
  Résultat immuable, constructeur privé ; `normalise` contient dix chiffres
  seulement si tous les contrôles passent. En cas de refus, `normalise` et
  `affichage()` sont null : ne pas envoyer une saisie partiellement nettoyée en
  comptabilité. La saisie d’origine n’est ni conservée ni journalisée.
- `estValide()` signifie **cohérence mathématique locale**, jamais existence,
  statut actif, inscription TVA, identité ni aptitude à la facturation électronique.
- `Motif` distingue vide, longueur, caractères interdits, premier chiffre et clé.
  Les messages client sont en français ; `message($traduire)` passe le texte par
  la fonction injectée. Aucun chargement WordPress. Le futur adaptateur fournit
  le catalogue de traduction et l’échappement de sortie ; il ne faut pas afficher
  les codes de motifs ni une exception technique au client.
- `RechercheDenomination` est une interface PHP, **pas un écran de recherche**.
  L’implémentation livrée `RechercheDenominationIndisponible` ne lit aucune donnée,
  n’appelle aucun réseau et retourne un `ResultatRecherche` indisponible avec
  `denomination === null`. Son message est « La recherche de dénomination n’est
  pas disponible. ». Cela ne signifie jamais « entreprise inexistante ».
  Le résultat immuable peut aussi porter un nom fourni par un futur adaptateur,
  exercé seulement par un double de test explicitement fictif.
- Pas de dépendance de production ajoutée ; `composer.json` et `composer.lock`
  inchangés. Tests PHPUnit et PSR-12 par les commandes existantes. Seuls un
  appendice du README d’extension et la suite Entreprise du XML partagé sont ajoutés.

## Interprétations explicites

J’ai compris « saisi librement » comme tolérance aux séparateurs, pas comme
suppression aveugle de tous les caractères non numériques :

1. Seuls les chiffres ASCII `0`–`9`, les points, les tirets ASCII et les espaces
   Unicode de catégorie `Zs` sont admis. Les espaces ordinaires, insécables et
   fines insécables sont testés. Tabulations, retours ligne, caractères invisibles
   hors `Zs`, signe `+`, barres obliques, chiffres Unicode et UTF-8 mal formé sont refusés.
2. `BE` facultatif, contigu, au début après les espaces de bord, sans sensibilité
   à la casse ; ni `B E`, ni préfixe répété ou étranger. Les séparateurs numériques
   peuvent être mélangés et ne doivent pas déjà former des groupes exacts.
3. Après retrait des séparateurs : neuf chiffres deviennent dix avec **un seul**
   zéro initial ; aucune complétion d’une autre longueur. La clé reste obligatoire.
4. Priorité des motifs : caractères interdits (avant toute suppression), absence de
   chiffres, longueur, premier chiffre, clé. Un préfixe/separateur sans chiffre est vide.
5. La règle du brief accepte un premier chiffre 0 ou 1 et une clé 01 à 97 incluse.
   Une base nulle avec sa clé calculée est mathématiquement cohérente ; aucune
   règle supplémentaire d’attribution réelle n’est inventée. Ne pas utiliser ce
   contrôle comme preuve de TVA ni de validité juridique.
6. La recherche est indépendante du contrôle : seul l’appelant décide de l’invoquer
   après `estValide()`. Le stub répond toujours indisponible, même si l’appelant
   lui passe un résultat invalide. Aucune ouverture de droits ni décision comptable.

## Sources officielles possibles — état documentaire, pas étude en ligne

**Aucune recherche Web, consultation d’entreprise ou requête BCE/VIES n’a été faite.**
Les pièces locales nomment le registre belge et le service européen, mais ne
contiennent pas leurs conditions d’accès. Les adresses ci-dessous sont des
**pistes documentaires indicatives non consultées et non vérifiées dans ce lot**,
à vérifier lors d’un lot d’étude autorisé. Ni leur disponibilité actuelle ni
leurs conditions ne sont garanties. Elles ne sont pas des URL appelées par le code.

| Piste officielle à examiner | Adresse documentaire / entrée indicative | Ce qui est établi localement | Accès et limites à confirmer avant tout choix |
|---|---|---|---|
| Banque-Carrefour des Entreprises (BCE), SPF Économie | https://economie.fgov.be/fr/themes/entreprises/banque-carrefour-des | Le brief désigne le registre belge comme source possible ; aucune condition de service attestée. | Choisir l’offre adaptée (consultation, service automatisé, données réutilisables), droits d’automatisation/réutilisation, licence, inscription, authentification, coût éventuel, quotas, fraîcheur et champs exposés. Aucun accès gratuit/libre/API ou droit de scraping supposé. |
| BCE Public Search — repère de consultation, pas transport retenu | https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html?lang=fr | Aucun contenu ou résultat BCE n’est enregistré dans le dépôt pour ce lot. | Confirmer la documentation, les conditions et l’autorisation d’un usage automatisé ; une interface de consultation n’est pas à elle seule une API autorisée. Ne pas la scraper. |
| VIES — service européen de validation TVA | https://ec.europa.eu/taxation_customs/vies/ ; aide indicative https://ec.europa.eu/taxation_customs/vies/#/faq ; contrat technique indicatif https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl | Le brief le cite comme piste pour la TVA, pas comme preuve de disponibilité de toute dénomination. | Confirmer protocole disponible, conditions d’usage, authentification éventuelle, quotas/concurrence, couverture belge, présence et sens des champs nom/adresse, pannes et signification des résultats. Ne pas supposer qu’un identifiant BCE est validable TVA ou qu’un résultat TVA remplace le registre général. |

**Limite structurelle du lot** : contrôle numérique, existence enregistrée et statut
TVA sont trois notions différentes. Pour tout futur service, séparer nom trouvé,
absence de résultat, numéro non reconnu et indisponibilité technique ; prévoir
un délai dur, une politique de reprise/cache, une provenance et une confirmation
client. Le contrat local actuel ne modélise que trouvé / non disponible : l’état
« introuvable » devra être défini avec le fournisseur retenu, pas fabriqué ici.
Aucune affirmation sur un coût, quota, SLA, inscription ou droit d’accès n’est
validée par les preuves de recette PHP.

## Standard d’abord

Le lot autonome est explicitement demandé en PHP pur et ne branche aucun module
WooCommerce. Les sources locales n’établissent pas qu’une extension retenue fournit
exactement cette normalisation et ces motifs. Aucune nouvelle étude en ligne n’a
été autorisée ici : pas d’affirmation de couverture native, de licence ou de
manque d’une extension. Avant l’intégration, reprendre le standard retenu dans
A-00 et vérifier son éventuel champ professionnel, sans réécrire le tunnel.

## Numéros étrangers — hors lot

Ils sont refusés ici, sans conversion ni retrait de leur pays. Pour les accepter :
champ pays explicite, normalisateurs/contrôles propres à chaque juridiction,
conservation du pays et des zéros, contrat de recherche adapté, messages client,
fixtures par pays, politique d’absence/panne et validation avec Step des champs
transmis. Ne pas appliquer la clé belge à un autre pays ni transformer un numéro
étranger en numéro belge par suppression de lettres.

## À arbitrer par Ced

- **Décision 8 reste ouverte** : faut-il rechercher et faire confirmer une dénomination
  en ligne, ou conserver seulement ce contrôle local ? Aucun service activé.
- Si recherche retenue : autoriser d’abord une étude des conditions BCE/VIES et du
  fournisseur, puis choisir une offre et une politique explicite en cas de panne
  (bloquante ou non). Aucune règle de commande/comptabilité n’est décidée ici.
- R-06 n’est pas une recette de bout en bout accomplie : le branchement du champ,
  l’affichage, la confirmation et la transmission WooCommerce → Odoo restent ultérieurs.
  Le catalogue des recettes n’est ni modifié ni automatisé.

## Corrections et décisions écrites — 21 novembre 2026

Instruction 3 : assertion littérale indépendante `0123.456.749` ajoutée pour une base calculée, sans reprendre la formule substr du code. Instruction 2 documentaire BCE/VIES explicitement reportée par Ced (docs/arbitrages-2026-11-21.md, C-02/1) ; aucune recherche ni appel à un service. `PremierChiffre` accepté tel quel (C-02/2). Contrôle local seul conservé (C-02/3) ; recherche réelle toujours non autorisée. Instruction 5 cosmétique facultative différée pour préserver les sources C-02 déjà composées et vérifiées par C-04, aucun défaut fonctionnel.

Standard d'abord : comparaison au livrable A-00 local (couverture-extensions.md, tableau et besoins 1/4/9/11/19 ; registre de sources local), pas une nouvelle preuve éditeur :
- WooCommerce/Subscriptions : commandes, facturation et renouvellements documentés en A-00 ; normalisation belge libre + neuf chiffres + clé modulo97 + motifs français C-02 : doute, aucune preuve locale précise.
- Memberships/Teams : droits d'adhésion/comptes/places documentés ; même normalisation et contrôle belge : doute, aucune preuve locale.
- Stripe/PayPal : moyens et mandats de paiement documentés ; ne prouvent pas un contrôle belge de numéro d'entreprise : doute.
- Rank Math/Event Tickets : schémas/billetterie documentés, ne prouvent pas cette API belge : doute.
Le besoin autonome de PHP pur est explicitement commandé par le brief ; ce doute justifie ce périmètre isolé, pas une réécriture du tunnel ni l'affirmation d'une incapacité native. Au branchement, confronter le champ professionnel réellement installé et ses hooks au contrat C-02, réutiliser la couverture éventuelle plutôt que la doubler. Aucun achat ou service retenu.

## Résultat frais du 21 novembre 2026

Suite complète en conteneur jetable : 175 tests / 19 912 assertions, zéro échec ; dont Entreprise 41 tests / 19 561 assertions. PHPUnit, PHPCS, syntaxe, Composer strict, concordance de manifeste et nettoyage PASS. Preuves tests-21nov/. Aucun test réel ou dérivé, aucune installation hôte, site ou service externe.

## Preuves et isolation

Voir `tests/rapport.md`, les journaux RED/GREEN, `final.{json,log,xml}`,
`c04-regression.{json,log,xml}`, `exemple.json`, `cleanup.json`,
`fichiers-livres.json` et `artifact-verification.json`.
Le banc propre C-02 importe le lanceur C-01 sans le modifier ni créer de bytecode
chez ses voisins. Il utilise une image synthétique déjà présente, sans montage,
port, base, site ou service WordPress démarré. La préparation télécharge seulement
Composer et les dépendances publiques de développement dans le conteneur jetable ;
le réseau est déconnecté avant toute exécution métier. Rien n’est installé sur
l’hôte, aucune requête applicative ni consultation d’entreprise n’a lieu.

Le contexte cite `C:/Users/Ced/imagine` : c’est là que le brief et les livrables
existent. Le répertoire d’exécution fourni `C:/- Claude Project -/imagine` ne
contient pas ces briefs ; il n’a pas été utilisé comme dépôt ni modifié. Aucun
accès à une sauvegarde d’origine, site réel, secret, compte, Git ou déploiement.
