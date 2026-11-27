# A-28 — réception et limites

## Périmètre

La liste fermée et ses sources officielles figurent en dix points dans `standard.md`, avec les reçus de récupération dans `official-sources.json`. Elle couvre six tables de données Fluent Forms et deux types de contenu Flamingo, avec leurs révisions et métadonnées. Le formulaire Contact Form 7 (`wpcf7_contact_form`), ses réglages, le magazine et les types hors liste ne sont pas supprimés. Ni extension nouvelle, ni heuristique générique sur « form » ou « message », ni lecture de l'archive d'Imagine.

La politique obligatoire est un seul JSON versionné, transmis dans le vrai payload de l'import pour les lecteurs Python et PHP. Une table connue ne se conserve ni par `garder` ni par `anonymiser` : seul `vider` est admis. Le refus Python donne `sql_preflight / FORM_MESSAGES_DECISION_REFUSED / table` ; le refus PHP réel donne `native_neutraliser`, le même code et un suffixe technique fermé, sortie 78. Il n'ajoute pas la dernière table arbitraire visitée par PDO. Le reste du diagnostic A-01 garde son ancien contrat.

Le compteur `form_message_residues` compte les posts/révisions encore présents, chaque ligne des tables de la liste **et les lignes de postmeta rattachées à un identifiant connu avant purge, même si son parent a disparu**. Avant toute exécution PHP, le worker lit uniquement les identifiants des deux types fermés et leurs révisions transitives ; il les conserve dans son contexte privé `/scratch/a01-context.json`, hors du site restauré (mode 0600), sans les publier au rapport. Le vérificateur d'une nouvelle phase reçoit cette même provenance, validée comme liste d'entiers positifs. Un Engine conservé en mémoire garde aussi sa photographie initiale. Un résidu positif produit `FORM_MESSAGES_REMAIN`, sortie 1, sans amorcer WordPress ; les données sont relues après la sonde. Aucun postmeta orphelin d'origine inconnue n'est attribué ou supprimé globalement. Les comparaisons SQL des types sont binaires, comme la liste PHP stricte : le témoin hors liste `Flamingo_Inbound`, ses révisions et ses métadonnées restent dans l'empreinte protégée, sans être confondus par la collation avec `flamingo_inbound`.

Pour obtenir un PSR-12 strict sans exclusion, les quatre déclarations existantes ont été séparées dans `store.php`, `form-decision-refused.php`, `engine.php`, `guard.php` ; `lib.php` conserve son interface d'inclusion. Le vrai payload A-01 transporte explicitement ces quatre fichiers. La mise en forme et les constantes découpées ont une preuve native d'équivalence des jetons, puis les imports et le différentiel hors formulaires sont rejoués. L'exception reçoit la liste déjà chargée ; `garder`/`anonymiser` sont refusés aussi si la table connue est absente. Les deux suffixes sans citation exacte restent en **doute explicite** dans `standard.md`, sans élargissement de politique.

## Preuve avant correction

`preuves/final/before/native.json` est la vraie exécution ancienne, sur six imports complets classique/HPOS d'archives fabriquées dans le runner : **108 contrôles verts**, qui attestent le défaut, pas sa correction. Par défaut les six tables connues et la table inconnue sont vides, mais les deux types Flamingo et quatre métadonnées canaris restent. Avec `garder` sur la table connue, son canari reste ; avec `garder` sur la table inconnue, celui de cette table reste. Le type fictif inconnu reste dans tous les passages. Les empreintes de l'ancien import et son runner supprimé sont conservés ; ses deux sources PHP authentiques sont dans `reference/` pour le test différentiel, pas dans le runtime livré.

Un `garder` est une décision **de table** dans A-01 ; il n'existe pas de décision par type de contenu. Aucun faux réglage par type n'a été inventé pour ce banc.

## Preuves corrigées et commandes de relecture

Le paquet courant est uniquement `preuves/final`. Son vérificateur en lecture seule ne prend aucun argument :

```powershell
C:/Python314/python.exe -B production/A-28/verify.py
```

Les matrices et portes exécutées sont décrites dans `RESULTATS.md`. Rejeu explicite du banc sur une sortie neuve, hors des preuves reçues : `python -B wp/tests/a28/matrix.py --output "$SORTIE_NEUVE"`. Il effectue de vrais imports complets dans les deux environnements Windows ; PHP n'est jamais lancé sur Windows. La copie vers `/subject` utilise le payload A-01 réel, pas une liste de dépendances parallèle cachée. Le parseur historique et les suites sont transportés à leur chemin canonique, et la suite diagnostique PDO a une vraie base fictive à contrainte unique.

Les témoins retirent réellement le blocage dans la copie **du conteneur**, puis restaurent exactement `engine.php`. Le nouveau vecteur omet **seulement la purge postmeta** pendant les deux transformations du vrai import : les deux parents et leurs révisions ont disparu, quatre lignes `_a28_message` canaris subsistent, la provenance privée compte quatre identifiants connus. Le vérificateur CLI refuse (1), le seul contrôle retiré accepte (0), le contrôle restauré refuse (1), en classique et HPOS et sous les deux encodages. Les canaris ne sont pas publiés. Les anciens témoins sur tables/posts restent exécutés ; les refus `garder` du CLI PHP comparent les empreintes SQL/fichiers. Le différentiel hors formulaires compare les tables, le rapport (hors compteur zéro) et les anciens diagnostics dans deux processus PHP séparés.

L'ancien paquet complet a été copié intact hors dépôt avant retrait de PRET, sous `scratch/a28-correction-20261127-0258/old-production`. Les RED I1 et décision sur table absente, ainsi que le premier développement natif (ses tests passent mais l'empaqueteur avait changé pendant son exécution), restent hors dépôt ; leurs vrais statuts ne sont pas renommés. `red-green.json` conserve les handles. Seul le nouveau paquet final constitue la qualification actuelle. La baseline d'avant A-28 reste une preuve historique identifiée, requise par le brief.

## Hors liste : question fermée

**Faut-il supprimer également les types de contenu hors liste : oui ou non ?** A-28 n'en décide rien : le comportement A-01 est conservé. Le canari du type fictif `fiction_magazine`, ses révisions et ses métadonnées restent exactement identiques après import. Une table inconnue reste vide par défaut et peut encore être conservée par la décision existante `garder` lorsqu'A-01 l'admet. Ce lot ne prouve donc pas une anonymisation universelle de tous les messages possibles, des pièces jointes, des taxonomies libres ou d'autres extensions. Leur qualification reste nécessaire ; ne pas transformer ce PRET en GO sur le réel.

## Limites et voisins

Banc WordPress/WooCommerce réel de l'image locale A-01, avec tables Fluent et contenus Flamingo **entièrement fictifs** ; aucun site partagé, compte réel, service commercial ou nouvelle compatibilité de version n'est qualifié. Pas de publication web/Novamira. Les réglages/rendus de formulaires, champs, SEO, commandes et fichiers retenus sont comparés dans chaque import réussi ; les commandes de Ced sont comparées byte pour byte, avec seulement les trois lignes autorisées ajoutées au README de l'import.

Les paquets d'A-21 à A-27 sont invalidés par le nouvel import ; leurs rejeux et scellements appartiennent au parent, **aucun n'est lancé ni rescellé ici**. A-29 reste réservé au parent. `dependency-invalidations.json` porte les empreintes de l'import gelé et l'heure ; `REJEUX-PARENT.md` rappelle la transmission. Le contrôle de périmètre porte uniquement sur les racines de l'import et les lignes README d'A-28 : aucune totalité d'inventaire de voie 2/A26/A27/T03/A30 n'est épinglée. Les versions des fichiers communs observées avant chaque porte globale sont enregistrées, sans attendre leur stabilité. Aucun gardien commun, autre lot ou voie 2 n'est modifié ; le verrou commun est rafraîchi et conservé.
