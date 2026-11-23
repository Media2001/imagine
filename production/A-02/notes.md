# A-02 — livraison du script d'audit

**Statut : prêt à relire sur preuves synthétiques. Aucun audit d'Imagine effectué.** Le marqueur PRET concerne uniquement l'outil et son banc, pas le staging d'Imagine ni une autorisation d'y accéder.

## Résultat vérifié

Paquet final : `production/A-02/preuves/211ac0849094/`.

- **122 assertions réussies, 0 échouée** : 15 unitaires, 100 d'intégration/qualification et 7 du runner. Ce sont des assertions autonomes nommées, pas un décompte PHPUnit.
- Vérification indépendante relue : `production/A-02/verification-finale.json` ; cohérence Markdown/JSON, sept sections, cinq priorités, dérive de contenu et d'inventaire des sources, empreintes et absence Docker vérifiées.
- WordPress **7.0.9**, WooCommerce **11.1.1**, Subscriptions **9.4.1**, Memberships **1.30.3**, PHP CLI **8.2.36**, MariaDB **10.11.19**. Le banc public compatible est un artefact déjà disponible, sans dépendance à un script A-01 en qualification. La version 6.9.1 d'Imagine n'a pas été modifiée, ni testée par cet audit.
- Deux sites intégralement fictifs, **classique et HPOS**, chacun avec trois abonnements, trois adhésions, deux règles de restriction (contenu et taxonomie, dont sept jours de différé), produit récurrent et commandes de deux années. Les vraies extensions commerciales sont activées hors réseau, sans licence ni compte.
- **55 tables dans chaque base**, schémas et toutes les lignes pris en compte. L'empreinte logique avant/après est strictement identique ; les fichiers du site le sont aussi. Variante séparée sans cache ni journal : autres paires d'empreintes identiques.
- Conteneur `imagine-a02-audit-211ac0849094` supprimé et absence relue. Aucun volume, montage, port, service Web ou TCP ; réseau `none`, capacités supprimées, MariaDB par socket uniquement.

Empreintes logiques finales (même valeur avant et après) :

```text
classic 68a81651d856eb2b2a4a41bd6c1cbce4e3d78025ad6cd689098ba40a1df79496
hpos    9016a49d6041ad521a488c2993cab68dd76b0a36d82b3b2e4ee92745e499227d
```

SHA-256 du script `wp/outils/bascule/audit` :
`68aadda51ca1ed07310d4852dd8a5a7f1696442e78f883d0a8eecc4fd6798e07`.

## Couverture du brief

| Rubrique | Observation produite |
|---|---|
| Versions | WordPress/PHP CLI/base, toutes les extensions et thèmes, état actif/inactif/MU, minima en-têtes/constantes, dernière version connue dans le cache seulement. |
| Commerce | Stockage faisant autorité, passerelles statiquement présentes, abonnements état × périodicité, adhésions plan × état, commandes par année UTC, produit récurrent et réglages non sensibles. |
| Memberships | Plans et objets par ID, types/taxonomies ciblés, règles enregistrées, immédiat/différé et durée. Aucun titre ni utilisateur exporté. |
| Contenu | Types/taxonomies présents et socle WordPress vide connu, comptes, articles annuels, 50 clés de métadonnées fréquentes sans valeurs, constructeurs connus actifs. |
| Base | Taille données/index estimée, lignes SELECT exactes par table, attribution prudente WordPress/Woo/WCS/AS, candidates non attribuées, 20 options autoload lourdes (nom/taille). |
| Planification | Action Scheduler par hook/état ; WP-Cron par hook/récurrence avec compte et prochaine date ; aucun argument ni tâche exécutée. |
| Risques | Comparaison installé/cache, maintenance > deux ans si date locale connue, versions des surcharges Woo par rapport aux templates installés, noms de fonctions/méthodes dépréciées sans lignes brutes. |

Chaque rapport finit par cinq priorités d'environ une demi-page. Les exemples `classic/audit.md` et `hpos/audit.md` sont des **résultats réellement générés**, non des modèles remplis à la main.

## Pourquoi ce petit collecteur spécifique

Le standard a été examiné : les en-têtes et métadonnées de plugins sont déjà documentés par `get_plugins()` ; WordPress stocke les résultats de mises à jour dans `update_plugins` ; Woo documente le magasin faisant autorité et ses templates ; Memberships fournit ses règles et délais nativement. Références publiques lues et vérifiées HTTP 200 dans `sources-officielles.json` :

- `https://developer.wordpress.org/reference/functions/get_plugins/`
- `https://developer.wordpress.org/reference/functions/wp_update_plugins/`
- `https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/`
- `https://woocommerce.com/document/woocommerce-memberships-restrict-content/`
- `https://developer.woocommerce.com/docs/theming/theme-development/fixing-outdated-woocommerce-templates`

Ces mécanismes sont réutilisés comme formats, sans réimplémenter les droits ni les paiements. Le sur-mesure se limite à la projection documentaire et aux agrégats. Charger WordPress ou ses extensions pendant l'audit pourrait exécuter migrations, caches, tâches ou hooks : l'outil ne les charge donc jamais. La configuration est tokenisée, non évaluée ; les données sérialisées sont décodées sans classes ni magie. Les requêtes passent par une transaction READ ONLY ; les identifiants SQL sont validés et les valeurs paramétrées.

## Rejeu indépendant

Depuis `C:\Users\Ced\imagine` :

```text
python wp/tests/a02-audit/run.py
python wp/tests/a02-audit/verify.py production/A-02/preuves/IDENTIFIANT_AFFICHE
```

Contrôler seulement la livraison figée, sans nouvelle création :

```text
python wp/tests/a02-audit/verify.py production/A-02/preuves/211ac0849094
```

Le vérificateur est en lecture seule et vérifie aussi que Docker répond avant de conclure à l'absence du conteneur exact. `wp/tests/a02-audit/README.md` détaille le lancement opérateur et les prérequis. Le runner ne prend aucun site/archive comme argument et ne télécharge rien.

Les paquets RED et intermédiaires restent conservés, notamment entrée absente, configuration manquante/conditionnelle, faux identifiants de passerelles, durée du différé, symlink parent et attribution des tables WCS. **Ils ne sont pas la preuve finale**. Une vérification d'un ancien paquet refuse à juste titre les nouveaux fichiers ou les hashes différents.

## Limites et contrôles supplémentaires

Les limites sont également dans chaque rapport et le README : pas de réseau de mise à jour ; cache/date absents = inconnus, pas « à jour » ; PHP observé = CLI ; passerelles présentes statiquement ≠ passerelles enregistrées/activées ; détection des constructeurs non exhaustive ; types dynamiques vides non inférés ; règles sauvegardées ≠ validation des droits effectifs ; tables non attribuées ≠ orphelines certaines ; tailles physiques estimées ; configuration/site simple standard requis ; journal conventionnel limité aux derniers 4 Mio. Aucune suppression ni arbitrage de droit/paiement/comptabilité.

Contrôle additionnel **PHPCS PSR-12** : **0 erreur, 99 avertissements**, code retour **1**, conservé honnêtement dans `style/` (96 lignes longues, 3 avertissements symbole/point d'entrée pour les scripts monofichiers et tests). Ce contrôle ne modifie rien et n'est pas présenté comme une commande verte ; ses avertissements de présentation ne sont pas des échecs des 122 assertions fonctionnelles. Le PHAR public a été exécuté uniquement dans son propre conteneur offline, supprimé ensuite. Aucun PHP installé/lancé sur Windows. Le scratch a été explicitement utilisé ; un fichier temporaire de cet outillage initialement placé par TMPDIR dans Temp a été déplacé immédiatement, et son absence à cet emplacement a été vérifiée.

Aucun Git, verrou parent, fichier de pilotage, autre lot, site réel ou archive Imagine modifié. Aucun GO réel demandé ou sous-entendu.
