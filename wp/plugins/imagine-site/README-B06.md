# B-06 — Espace coopérateurs

`CooperateursRegles` est pur ; `Cooperateurs` raccorde l’attribut `imagine_cooperateur` (booléen strict, source `administration`, date UTC) à la fiche utilisateur native et au dashboard Woo. La pose/retrait exige un rôle configuré, le droit natif `edit_user`, un POST et un nonce lié au titulaire. Aucun rôle ni capacité ajoutés. Un verrou par titulaire, une relecture et un événement au journal C10/C17 accompagnent chaque vrai changement ; l’échec du journal restaure le statut. Le point `imagine_cooperateur_modifie` n’a aucun écouteur CoopHub.

La racine `imagine_cooperateurs_page`, les marqueurs `imagine_espace_cooperateurs` et leurs descendants sont protégés avant les sorties publiques : objets clonés, contenu/extraits, REST unitaire et collection, recherche/flux et sitemap. Seuls les coopérateurs connectés et les rôles configurés pour la lecture lisent l’espace ; une capacité large isolée ne suffit pas. Les capacités natives des pages réservées utilisent le même réglage de lecture. Aucun filtre de droit d’article, plan Memberships, produit ou consentement n’est modifié. Les tests comparent l’article avant/après chaque configuration et chaque rôle ; P-COOP reste à l’extrait.

Les callbacks privacy natifs distincts `imagine-cooperateurs` exportent l’attribut et l’historique propre au titulaire, par pages de 50, sans identité de tiers ; l’effacement retire l’attribut et anonymise sa cible dans le journal, sans effacer l’opérateur ni les événements des autres comptes. C21 reste inchangé et traite toujours les données propres à l’opérateur. Aucune durée de conservation modifiée.

`audits()` distingue journal vide, échec SQL et résultat non-tableau. En panne, l’export retourne un `WP_Error` contrôlé, jamais un faux export complet ; l’effacement rend `items_retained=true`, `done=false`, avec message de reprise. Tests avec événements présents : SELECT initial en panne, reprise d’export, SELECT final en panne après traitement de 50 événements sur 51, événement restant puis reprise complète d’effacement. Source/date ne s’affichent dans la fiche et Mon compte que si `cooperateur === true` ; affichage UTC brut inchangé.

## Deux réglages indépendants

Dans **Imagine → Réglages**, groupe Settings API `imagine_reglages` existant : `imagine_cooperateurs_roles_attribut` autorise la pose/retrait ; `imagine_cooperateurs_roles_lecture` autorise la lecture sans statut. Défaut des deux : **Administrateur seul**. Choix : Administrateur, Éditeur, Gestionnaire de boutique, toute combinaison, ou aucun. Les 8 × 8 configurations sont testées. `manage_options` n’est pas un rôle. Le POST natif `options.php` contrôle capacité et nonce ; le sanitizer exige aussi le rôle Administrateur, refuse rôles inconnus/doublons/types/structures invalides et conserve l’ancienne valeur. Une valeur stockée invalide ferme les dérogations. Changements journalisés, avec restauration si le journal échoue.

Démonstration uniquement :

```powershell
python -B wp/outils/demo/b06.py baseline LABEL-V2
python -B wp/outils/demo/b06.py deploy LABEL-V2
python -B wp/outils/demo/b06.py seed LABEL-V2
python -B wp/outils/demo/b06-recette.py LABEL-V2
python -B wp/outils/demo/b06-finaliser.py
python -B wp/tests/demo/b06-verifier.py fusion-livraison-V2
.\wp\tests\rejouer.ps1
```

Le déploiement exige le reçu initial `baseline-V2.json` et ne remplace que les deux classes B06 : **jamais le bootstrap partagé ni C24**. Le seed reprend les cinq pages vides et refuse une page étrangère. La recette complémentaire rejoue règles pures hors réseau, vrais callbacks natifs transactionnels, erreurs SQL, mutations et HTTP GET/POST ; la collection contient une page publique témoin. `plugins/imagine-site/tests/CooperateursReglesTest.php` est découvert par le `phpunit.xml` déjà présent : `rejouer.ps1` couvre B06 sans site, sans WordPress ni base. Aucun fichier T01 ni bibliothèque close modifié. Les suffixes de reçus sont uniques et terminés par `-V2`. Le finaliseur prépare/vérifie l’image Docker après nouveaux tests, contrôle PSR12 et lance le runner canonique ; ses reçus fixes immuables ne sont pas écrasés. Le rejeu indépendant usuel est `rejouer.ps1`.

Avant mutation, une préimage durable privée est écrite, synchronisée et relue sous le scratch Hermes, hors dépôt. Elle peut contenir des sessions : seuls identifiant opaque et empreinte sont publiés. La recette HTTP restaure depuis cette préimage et compare les lignes utilisateurs/métadonnées exactes, ainsi que pages, options et actions métier. **P-COOP** conserve son attribut vrai ; tous les autres états reviennent à leur préimage. Aucun secret de session n’entre dans un reçu. Texte témoin retiré, vrais événements B06 append-only, fixtures natives rollbackées.

Reçus, sources officielles et parcours : `production/B-06/`. PRET technique n’est ni clôture Claude, ni validation visuelle Ced, ni accord sur le réel.
