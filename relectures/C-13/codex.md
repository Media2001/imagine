# Relecture indépendante Codex — C-13

Date : 25 novembre 2026. Périmètre : brief C-13, production/C-13, raccords et tests concernés dans wp/, doctrine, décisions et cahier des charges §3.13, avec §3.5 pour les droits aux numéros. Rapport Claude non consulté. Aucun site, compte ou base consulté ; seul ce rapport est écrit.

## 1. Conformité

Le code fournit le menu WordPress, la sélection du numéro, les compteurs Belgique/étranger, les exclusions, le CSV au format C10 et le journal. Les limites de la recette sont annoncées explicitement. Le redépôt de PRET est demandé par les arbitrages du 25 novembre : sa présence ne constitue pas en soi une anomalie.

**C13-01 — Bloquant — Bénéficiaires offerts et groupés absents du raccord.** Fichier : `wp/plugins/imagine-site/EnvoiNatif.php:160`. Chaque souscription produit un seul destinataire, identifié par son client et son adresse de livraison ; aucune attribution de bénéficiaire n'est lue, et l'origine est systématiquement `abonnement`. Pour un abonnement groupé doté de plusieurs places attribuées, le raccord ne peut donc pas produire les adresses de ces bénéficiaires. Le §3.13 les exige explicitement ; l'absence de fixtures natives ne suffit pas à expliquer cette limitation du code. **Correction proposée :** lire les relations natives de bénéficiaires, fournir leurs identités/adresses et la bonne origine à C07, historiser les attributions, et tester un cadeau ainsi qu'un groupe avec places attribuées et libres. Fermer explicitement l'export d'un abonnement dont les bénéficiaires requis ne sont pas résolus.

**C13-02 — Important — La recette positive demandée sur C09 n'est pas acquise.** Fichier : `production/C-13/resultats.json:61`. `A_SANSMAIL_inclus` vaut `false` ; le reçu indique aussi zéro destinataire C09. Les deux témoins C13 en grâce démontrent une chaîne technique, mais pas la liste attendue pour les profils C09, notamment l'abonné sans email. L'exclusion d'un paiement non validé est prudente et ne doit pas être supprimée pour faire réussir un test. **Correction proposée :** préparer des données postales fictives explicitement traçables et cohérentes avec les profils requis, sans transformer un statut administratif actif en paiement ; vérifier les identités exactes attendues et obtenir une recette complète, en conservant des contre-exemples non payés.

## 2. Exactitude métier

**C13-03 — Important — Les renouvellements restent attachés au premier bloc de quatre numéros.** Fichier : `wp/plugins/imagine-site/EnvoiNatif.php:154`. Chaque observation appelle `ouvrir($start)` depuis la date de début de la souscription, puis recalcule ses quatre premiers numéros. Aucun bloc renouvelé ni événement de renouvellement n'est transmis au moteur C01. Une souscription qui conserve son début initial après renouvellement reste donc exclue des numéros de sa deuxième année avec `numero_non_du`, même active et payée. **Correction proposée :** raccorder les blocs et renouvellements effectivement enregistrés à C01, puis fournir à C07 les droits historiques correspondants ; ne pas déplacer artificiellement la date initiale. Ajouter le cas de renouvellement du §3.5.

**C13-04 — Important — Le gel des listes dépend encore du calendrier courant.** Fichier : `wp/plugins/imagine-site/EnvoiNatif.php:115`. Le calcul historique recharge le calendrier courant et recalcule les droits et la borne de sélection des relevés. Les relevés ne conservent ni version du calendrier ni bloc de numéros attribué. Par exemple, une suspension observée après la clôture initiale est ignorée au premier export ; si cette clôture est ensuite repoussée au-delà de la suspension dans l'option du calendrier, le même numéro exclut désormais l'abonné. Le constructeur de calendrier utilisé ici ne fait pas appliquer la garde de modification des clôtures de C01. **Correction proposée :** conserver les références historiques nécessaires et faire respecter l'immuabilité des clôtures passées sur la voie persistante ; tester qu'un changement de calendrier après clôture ne modifie ni destinataires ni adresses de la liste clôturée.

Cas déroulés à la main, par lecture du raccord et des bibliothèques, sans les présenter comme des tests PHP exécutés :

- **§3.5, commande le 8 octobre 2026 après clôture du n°170.** Avec le calendrier correspondant, une observation antérieure à la prochaine clôture, un paiement validé, une adresse complète et aucun terme atteint, `ouvrir` retient les quatre numéros suivants : 171–174, soit les quatre trimestres 2027 de la démo, et le hors-série 2027. C07 inclut la ligne. Aucun champ email n'est nécessaire : ce cas est cohérent.
- **§3.5, renouvellement en octobre 2027.** Le résultat attendu est 175–178 et le hors-série 2028. Si la souscription renouvelée garde son début au 8 octobre 2026, le raccord calcule encore 171–174 et le hors-série 2027. Les numéros 2028 sont exclus : C13-03.
- **§3.13, suspension après clôture.** À calendrier inchangé, les observations à partir de la clôture sont ignorées et la ligne antérieure reste inchangée. Le test livré couvre cette situation. La modification ultérieure du calendrier ne bénéficie pas de cette protection : C13-04.

Limites examinées : création ou observation exactement à la clôture exclue (`>=`), paiement exactement à la clôture non validé (`<`), fin exactement à la clôture exclue par C07 ; passage 2026/2027 cohérent pour le premier bloc. Un calendrier vide refuse la sélection ; un calendrier partiel peut produire un bloc incomplet selon C01, sans avertissement spécifique dans cet écran. Un relevé identique n'est pas réécrit ; deux exports sont deux événements distincts, ce qui convient au journal demandé.

## 3. Tests

Commande locale effectivement exécutée depuis la racine, sans cache Python ni installation :

```powershell
python -B -c "import sys,unittest,pathlib;sys.path[:0]=[str(p) for p in pathlib.Path('production/B-01/validation').glob('*.whl')];s=unittest.defaultTestLoader.discover('wp/tests/demo',pattern='test_*.py');r=unittest.TextTestRunner(verbosity=1).run(s);print('UNITAIRES',r.testsRun,'SUCCES',r.wasSuccessful());sys.exit(not r.wasSuccessful())"
```

Résultat : **33 tests, OK, code de sortie 0**. Cette suite de non-régression annoncée par le lot porte sur les tests Python locaux des lots précédents ; elle ne valide pas le raccord PHP C13.

Les recettes C13 PHP/HTTP et la commande `--require-complete` n'ont **pas été rejouées**. `c13.py` consulte le site dès sa garde, téléverse la recette même sans `--deploy`, exécute des mutations natives et écrit `production/C-13/resultats.json`. Cela contrevient aux droits du relecteur : « accéder à un site, à une base ou à un compte » est interdit, comme toute autre écriture. PHP n'est pas disponible dans le PATH local. Les 47 assertions vertes et le code strict 2 sont donc des résultats historiques déclarés par la production, pas des résultats reproduits dans cette relecture.

**C13-05 — Important — Absence de banc local autonome pour les règles du raccord.** Fichier : `wp/tests/demo/c13-runtime.php:34`. Même les scénarios synthétiques de gel commencent par lire un relevé de la base et dépendent de la fixture C13. Il n'existe pas de suite locale C13 permettant de vérifier ces règles sans site ; les tests livrés ne couvrent ni bloc renouvelé ni calendrier modifié après clôture. **Correction proposée :** rendre ces scénarios autonomes avec horloge, calendrier et observations fictifs injectés ; couvrir les cas C13-01 à C13-04, l'égalité à la clôture, le calendrier incomplet et le rejeu. Conserver séparément la recette native d'intégration.

Les assertions HTTP lues couvrent les rôles, l'anonyme, POST, le nonce lié au numéro, les en-têtes privés, les formules et le journal. La panne d'écriture du journal est exercée dans la recette PHP. En revanche, `repartition_exacte` vérifie une identité arithmétique construite par le raccord ; la vérification suivante BE=1/étranger=1 apporte un oracle indépendant, limité aux deux témoins C13.

## 4. Sécurité et données

Sur les chemins inspectés : capacité vérifiée dans la page et le contrôleur, nonce lié au numéro, POST obligatoire, numéro borné par une expression régulière, sorties HTML échappées, requêtes préparées pour les préfixes d'options. Le CSV est généré en mémoire ; C10 fournit les colonnes et C07/C04 protègent les cellules commençant par une formule, y compris après des caractères de contrôle ou espaces ASCII. Les anomalies bloquent l'export ; une écriture du journal non confirmée le bloque également.

Aucun secret ni donnée réelle identifié dans les fichiers concernés lus. Les données des fixtures sont explicitement fictives, avec adresses `@example.org`. Les fichiers privés d'identifiants n'ont pas été ouverts. Aucun changement de sortie du paywall propre à ce lot identifié. Ces constats sont statiques : aucune validation HTTP indépendante n'est revendiquée.

## 5. Doctrine

Réutilisation effective de WordPress pour l'administration, des objets WooCommerce pour les lectures, de C01/C07 pour les numéros et la sélection, de C10 pour le format et de C04 pour la protection CSV. Les fichiers PHP déclarent les types stricts et l'espace de noms Imagine ; les options et hooks sont préfixés ; un README documente le raccord et ses limites.

La méthode `calculer` dépend encore de WordPress pour son calendrier et contient des décisions temporelles d'adaptation : C13-05 propose de rendre cette partie testable hors WordPress. Les commentaires renvoient surtout aux lots C01/C07 ; les corrections devront rattacher explicitement les règles de droits et de gel aux §3.5 et §3.13. Les références officielles sont présentes dans la production mais n'ont pas été consultées en ligne pendant cette relecture. L'écart « documentation consultée après le premier tracer » est déclaré par la production.

### Décisions techniques, défaut proposé

Le complément de fixtures demandé dans `production/C-13/A-VOIR.md:24` relève de la **technique**, tant qu'il porte exclusivement sur des données fictives et respecte les règles existantes. **Défaut prudent proposé :** faire réaliser par le producteur une préparation isolée et rejouable des données nécessaires, explicitement marquée comme fictive ; garder l'export fermé pour les profils dont les droits ne sont pas démontrés. Ce choix de test n'exige pas un arbitrage de Ced et ne remplace pas les corrections du raccord. Aucun paiement réel, aucun assouplissement des critères métier et aucune modification de site ne sont autorisés par ce rapport.

### Pour Imagine

Aucune nouvelle règle métier à arbitrer pour corriger les points relevés : les bénéficiaires, les renouvellements et le gel sont déjà spécifiés. Aucun défaut technique ne doit être transformé en réglage métier permettant de contourner ces obligations.

La validation visuelle de l'écran reste à Ced ; aucune capture ou visite du site n'a été effectuée ici.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.**

- **Bloquant :** C13-01 — bénéficiaires offerts/groupés non raccordés.
- **Important :** C13-02 — acceptation C09 incomplète ; C13-03 — renouvellements absents ; C13-04 — gel dépendant du calendrier courant ; C13-05 — tests du raccord non autonomes et cas structurants manquants.
- **Mineur :** aucun point distinct retenu.

Ce verdict n'est ni un GO, ni une clôture, ni une validation visuelle.
