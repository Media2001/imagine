# Lot A-05 — Le script de nettoyage

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-04 (tu construis dessus sans attendre sa clôture, ses corrections passent avant).

## Pourquoi

Le diagnostic de l'archive montre un site qui a dix ans de restes : des tables d'une extension désinstallée (`ahm_*`), des statistiques Matomo depuis 2015, un journal des emails envoyés, des extensions d'import et d'export qui ne serviront plus (`docs/ecarts.md`, 24 et 25/11). Le jour de la bascule, ce ménage sera refait sur la copie fraîche : c'est donc un script de bascule, comme A-04.

**Ce lot ne décide pas ce qu'on retire.** Ce qui part du site réel se décidera après l'audit du staging d'Imagine, par Ced. Ce lot fournit l'outil qui exécute un plan, et rien d'autre.

## Ce qu'on veut

`wp/outils/bascule/nettoyer`, qui applique à un site un **plan de nettoyage** (fichier versionné du dépôt, noms seulement, aucune valeur) :

1. **Extensions** : pour chacune, `garder`, `desactiver` ou `retirer`. Retirer = désactiver, puis supprimer les fichiers. La routine de désinstallation de l'extension (qui peut effacer ses données) ne tourne que si le plan le demande explicitement pour cette extension.
2. **Tables** : par nom exact ou par famille (préfixe), `garder` ou `supprimer`.
3. **Options et tâches planifiées orphelines** : par préfixe ou par crochet, `garder` ou `supprimer`.
4. **Dossiers de `uploads`** : par chemin exact, `garder` ou `supprimer`.

Règles de sûreté :

- **Tout ce que le plan ne nomme pas reste en place.** Pas de famille « retirée d'office ».
- Refus, avec le nom en cause : une extension dont une extension gardée dépend ; WooCommerce, Subscriptions, Memberships et la passerelle de paiement ; le thème actif ; une table du cœur ou d'une extension gardée ; un chemin hors de `uploads` ou qui en sort une fois résolu.
- Mêmes préalables qu'A-04 (sauvegarde récente hors du site, maintenance, statut du site) : réutilise ses garde-fous, ne les réécris pas.
- **Mode à blanc** : la liste de ce qui serait fait, avec les tailles (lignes, octets, fichiers), sans rien toucher. C'est ce que Ced lira avant de décider.
- Reprenable, journalisé comme A-04, et **relancé sur un site déjà nettoyé, il ne fait rien**.

Livre aussi `plan-imagine.exemple.json` : les extensions, familles de tables et dossiers connus par le diagnostic (noms dans `docs/ecarts.md`), **tous à `garder`**. C'est un formulaire à remplir par Ced, pas une proposition de ta part.

## Preuve

Sur le banc fictif d'A-04, classique et HPOS, auquel tu ajoutes : une extension inactive qui a laissé des tables, une famille de tables datées, une extension active à retirer, des options et une tâche orphelines, un dossier dans `uploads`.

- à blanc : rien ne change (empreinte de la base et des fichiers avant et après) ;
- réel : ce que le plan nomme a disparu, tout le reste est intact ;
- non-régression A-03 avant et après : dis ce que la comparaison montre. Si le retrait d'une extension sort en « anormal », ne requalifie rien et ne modifie pas A-03 : décris-le, et prouve par inventaire avant et après ;
- chaque refus de la liste ci-dessus ;
- un arrêt provoqué puis une reprise ; un second passage sans effet.

Preuves proportionnées. Tu n'ouvres pas l'archive d'Imagine et tu ne remplis pas le plan d'Imagine.

## Livrables

Le script, ses tests, le mode d'emploi, le plan d'exemple, `production/A-05/PRET`. Rapport court.
