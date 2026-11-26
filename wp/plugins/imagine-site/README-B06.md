# B-06 — Espace coopérateurs

`CooperateursRegles` est pur ; `Cooperateurs` raccorde l’attribut `imagine_cooperateur` (booléen, source `administration`, date UTC) à la fiche utilisateur native et au dashboard Woo. Seul le rôle exact `administrator`, avec droit natif d’éditer le compte et nonce lié au titulaire, pose/retire le statut. Aucun rôle ni capacité ajoutés. Un verrou par titulaire, une relecture et un événement au journal C10/C17 accompagnent chaque vrai changement ; l’échec du journal restaure le statut. Le point `imagine_cooperateur_modifie` n’a aucun écouteur CoopHub.

La racine `imagine_cooperateurs_page`, les marqueurs `imagine_espace_cooperateurs` et leurs descendants sont protégés avant les sorties publiques : objets clonés, contenu/extraits, REST, recherche/flux et sitemap. Seuls les coopérateurs connectés et le rôle administrateur lisent l’espace ; une capacité large isolée ne suffit pas. Les capacités natives de lecture/édition d’une page protégée sont aussi refusées aux non-coopérateurs. Le cache objet brut reste interne : pas de sortie de `post_content` brut ni SQL public contournant les hooks. Aucun filtre de droit d’article, plan Memberships, produit ou consentement n’est modifié.

Les callbacks privacy natifs distincts `imagine-cooperateurs` exportent l’attribut et l’historique propre au titulaire, par pages de 50, sans identité de tiers ; l’effacement retire l’attribut et anonymise sa cible dans le journal, sans effacer l’opérateur ni les événements des autres comptes. C21 reste inchangé et traite toujours les données propres à l’opérateur. Aucune durée de conservation modifiée.

Démonstration uniquement :

```powershell
python -B wp/outils/demo/b06.py baseline LABEL-V2
python -B wp/outils/demo/b06.py deploy LABEL-V2
python -B wp/outils/demo/b06.py seed LABEL-V2
python -B wp/outils/demo/b06-recette.py LABEL-V2
```

Le déploiement exige le reçu initial `baseline-V2.json` et contrôle le bootstrap partagé par ajout minimal, sans réinstallation globale. Le seed reprend les cinq pages vides et refuse une page étrangère. La recette rejoue règles pures hors réseau, vrais callbacks natifs transactionnels, mutations et parcours HTTP GET/POST. Les tests B06 restent sous `wp/tests/demo/`, **hors de la découverte PHPUnit T01** : la commande B06 complémentaire est obligatoire. Les suffixes de reçus sont uniques et terminés par `-V2` ; un reçu existant n’est jamais écrasé.

Les sessions temporaires ne sont ni écrites en preuve ni affichées. Tous les profils/options/actions reviennent à leur état relu, sauf **P-COOP** qui conserve expressément son attribut posé par l’écran natif. Le texte témoin est retiré de la sous-page en fin de recette. Les événements d’audit B06 réels restent append-only, les fixtures natives de test sont rollbackées.

Reçus, sources officielles et parcours : `production/B-06/`. PRET technique n’est ni clôture Claude, ni validation visuelle Ced, ni accord sur le réel.
