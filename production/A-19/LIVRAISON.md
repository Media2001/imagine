# A-19 — Livraison du 26 novembre 2026

**Prêt à relire, non clos.** Outil de lecture seule sur les liens explicites Memberships/Subscriptions : tableau croisé par plan/états ; abonnements sans adhésion ; adhésions sans lien et au lien pendant séparées ; comptes à plusieurs actifs ; références de paiement absentes ou inconnues séparées ; dates de prochain paiement passées ; absence de commande liée payée ; modes manuels par passerelle. Chaque nombre porte sa définition. Aucun rapprochement par personne/email, aucun correctif, aucun droit d’accès décidé.

## Exécution prouvée

Paquet unique `preuves/final`, dernier contexte cp1252 à la racine et contexte UTF8 dans `utf8/`. Deux matrices réelles sous **Python 3.14.7 Windows**, locale cp1252 ; stdout/stderr cp1252 avec `PYTHONUTF8=0`, puis UTF8 avec mode 1 mesurés. Chaque contexte : **9 assertions PHP pures, 98 assertions natives classic/HPOS, 7 gardes runner et 3 tests Python**, zéro échec. Enfants Python à encodage explicite. PSR12 strict zéro erreur/avertissement. Préparation image après ajout des tests, retour 0. Commandes complètes et retours : `preuves/final/windows-matrix.json`.

```text
python -B wp/tests/a19/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-rejeu-NOUVEAU
python -B wp/tests/a19/verify.py production/A-19/preuves/final
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Banc réel : WordPress 7.0.9, WooCommerce 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3, les deux stockages faisant autorité. Liens relus par les objets natifs ; parent et renouvellement réellement payés ; échéance passée relue après activation (le standard la recalculait lorsqu’elle était posée avant). Couple cohérent, actif non lié, adhésion autonome, lien vers un abonnement supprimé et doublon hérité explicitement construit. Référence native présente, manquante et adaptateur absent : ce dernier reste inconnu, jamais absent par supposition.

Empreintes logiques de toutes les tables, Action Scheduler et fichiers identiques avant/après ; vraies tentatives SQL/mail/HTTP/cron/fichiers bloquées. Confineur obligatoire, sortie disjointe, six drop-ins fermés, liens symboliques fichier/dossier, configurations arbitraires et date impossible. Canaris absents de stdout/stderr et de tous fichiers produits, aucun ID de compte/abonnement/commande rendu. Les codes d’erreur sont sur **liste littérale fermée** : une exception d’extension au nom ressemblant à un code est ramenée au refus générique ; test natif RED avant correctif puis vert en deux consoles. Runtime commun et A17 non modifiés. Suppression des seuls conteneurs possédés vérifiée.

## Standard et décisions prises à défaut

Dix lignes du mode d’emploi décrivent l’intégration officielle et le code installé ; provenance dans `sources-officielles.json`. `Analysis.php` est pur PHP ; projection native isolée dans `Inventory.php`. Le mode est le drapeau enregistré, pas `is_manual()` qui force le manuel sur staging ou passerelle indisponible. L’historique payé inclut toute commande liée via l’API native, date de paiement conservée ou statut payé. Le lien explicite n’est pas réinterprété selon le titulaire : le standard permet des liens manuels entre titulaires différents. Les comptes « actifs » sont de strict état actif, sans inventer une règle d’accès. Deux lignes propres seulement font contrat sur le README audit partagé, aucune empreinte globale ; manifestes bornés au lot.

## Limites

Une référence présente ne prouve ni sa validité ni un débit futur. Sans schéma natif de passerelle ni jeton Woo lié, le diagnostic est inconnu et compté séparément. Objets de la collection native non supprimés seulement ; plan sans lien ou offre manuelle ne sont jamais qualifiés d’erreurs. Essais intermédiaires, premiers paquets et RED hors dépôt ; seul dernier paquet vert livré. Aucun réel, archive Imagine, compte externe, secret, staging, Git ou déploiement ; PHP seulement dans conteneurs jetables. Pas de suite PHPUnit globale revendiquée : suites dédiées et vraie reconstruction d’image prouvées. Claude seul clôt.
