# A-19 — Cohérence des abonnements et adhésions

## Le standard, en dix lignes

1. Memberships peut accorder un accès autonome ou le lier à un abonnement Subscriptions.
2. La durée du plan décide si l’accès suit l’abonnement ou continue selon sa propre durée.
3. Pour une durée liée, l’abonnement actif rend normalement l’adhésion active, ou en essai durant l’essai.
4. Un abonnement suspendu met normalement cette adhésion en pause.
5. L’annulation en fin de période maintient l’accès jusqu’au terme, avant la fermeture définitive.
6. Une durée illimitée ou indépendante peut conserver l’accès après les paiements ; ce n’est pas forcément un défaut.
7. Le lien explicite enregistré par l’intégration est `_subscription_id` sur l’adhésion ; son lecteur natif n’invente aucun lien.
8. Un opérateur peut lier manuellement les objets, y compris ceux de deux titulaires différents.
9. `get_related_orders('all','any')` lit les commandes liées, parent, renouvellement, réabonnement et changement compris.
10. `is_manual()` tient aussi compte du staging et des passerelles disponibles ; ce diagnostic lit le drapeau manuel **enregistré**.

Documentation officielle consultée : `https://woocommerce.com/document/woocommerce-memberships-subscriptions-integration/`. Code installé inspecté en conteneur jetable : intégration Memberships (`get_subscription_id`, `get_subscription`, `update_related_membership_status`) et `WC_Subscription` (`is_manual`, `get_related_orders`, `get_payment_method_meta`). Provenance et SHA256 dans `production/A-19/sources-officielles.json`. Pas de modification du standard, pas de réglage de droits ni paiement.

## Commande opérateur, uniquement après autorisation sur copie vérifiée

```text
python3 wp/outils/bascule/a19/confine.py --wp-path=/copie-verifiee --audit=/rapports/audit-date/audit.json --output=/rapports/coherence-date --as-of=2026-11-26T00:00:00Z
```

`--as-of` facultatif : instant UTC courant par défaut, figé une seule fois ; une date impossible est refusée sans la recopier. Sortie neuve, sœur du rapport A02, hors site et dépôt. Landlock ABI3+, conteneur Linux déconnecté, SQL READ ONLY et protections A11 inchangés. Le PHP direct est refusé. `coherence.json` et `coherence.md` : 0700/0600. Refus par code seul sauf six noms techniques fermés de drop-ins. L’opérateur peut lister lui-même les liens par `find /copie-verifiee -type l`, sans intégrer ses résultats aux rapports.

## Comment chaque compte est formé

- **Tableau croisé** : une adhésion portant un lien positif vers un abonnement du magasin natif compte une fois, par plan et couple d’états. Deux adhésions liées au même abonnement font deux liens, pas deux abonnements.
- **Abonnements sans adhésion** : aucun lien explicite depuis une adhésion non supprimée, par état. Aucun rapprochement par email, compte ou produit.
- **Adhésions sans abonnement** : lien absent, nul ou non numérique, par plan/état. **Adhésions au lien manquant** : lien positif mais abonnement absent de la collection native, séparément. Les objets supprimés/corbeille ne sont pas rétablis.
- **Plusieurs actifs** : strict état `active`, comptes invités exclus. Pour les adhésions, comptes distincts au sein du même plan ; un total de comptes distincts et un détail par plan évitent de confondre personnes et enregistrements en trop.
- **Automatiques sans moyen enregistré** : strict état actif et drapeau manuel enregistré à faux ; absence de passerelle ou absence d’une valeur déclarée par son schéma natif. Les identifiants techniques de passerelle sont conservés, jamais son titre. Un jeton Woo explicitement lié au bon abonnement, titulaire et passerelle constitue une référence enregistrée.
- Le schéma standard `woocommerce_subscription_payment_meta` permet aussi de lire la **présence** des références propres à une passerelle, sans les sortir. Si une passerelle n’expose ni schéma ni jeton natif, son cas est **inconnu**, compté à part dans `automatic_payment_reference_unknown` : jamais classé « absent » par supposition. Une référence présente n’est pas une preuve de validité ou de débit ; aucun service bancaire n’est interrogé.
- **Prochain paiement passé** : strict état actif, date UTC positive strictement antérieure à l’instant de référence. Absence de date ou égalité à cet instant non comptées.
- **Aucune commande payée** : aucune commande explicitement liée n’a ni date native de paiement ni état natif payé. Parent, renouvellement, réabonnement et changement sont inclus ; l’historique daté n’est pas assimilé à une seule commande courante.
- **Manuels** : tous états de la collection native, par passerelle déclarée, d’après `get_requires_manual_renewal('edit')`, pas la bascule effective du staging.

Toutes ces phrases figurent aussi sous `counts.definitions` dans le rapport. Aucun cas n’est qualifié d’« erreur » ; accès offerts, liens manuels et paiements hors ligne peuvent être voulus. Plan = ID uniquement ; aucun ID de compte, abonnement, commande, aucun nom, email, référence ou montant n’est rendu. États reconnus sur liste fermée, états inconnus sous `autre` ; syntaxe technique des passerelles contrôlée. PHP pur `Analysis.php` agrège, `Inventory.php` ne fait que la projection native. Rien n’est corrigé, lié, annulé ou synchronisé.

## Rejeu fictif

```text
python -B wp/tests/a19/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-rejeu-NOUVEAU
python -B wp/tests/a19/verify.py production/A-19/preuves/final
```

Banc sans argument de site : vrais WordPress/Woo/Subscriptions/Memberships, classique et HPOS, couple cohérent, absence de lien, lien pendant, doublons de compte et d’adhésion, référence présente/absente/inconnue, commande parent et renouvellement réellement payés, échéance passée relue par getter natif. Canaris, refus symboliques/configuration/drop-ins, date impossible, gardes SQL/mail/HTTP/cron/fichiers et empreintes toutes tables/fichiers. Python Windows UTF8 et cp1252 ; PHP seulement en conteneurs jetables dont la suppression est vérifiée. Aucun réel, archive Imagine, compte externe, staging, droit d’accès ou déploiement.
