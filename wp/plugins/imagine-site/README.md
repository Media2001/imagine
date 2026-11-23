# Imagine — site (B-00, modèle provisoire)

**Ce modèle de démonstration n’est pas le modèle éditorial définitif.** Il sera remplacé après l’audit de l’existant. Aucun ACF, thème ou constructeur de pages n’est embarqué ici.

- Types publics : `imagine_numero`, `imagine_evenement`, `imagine_partenaire` ; taxonomie `imagine_thematique` sur les articles natifs `post`.
- Rattachement d’un article : métadonnée entière `imagine_numero_id` ; indicateur `imagine_reserve`. Déclarations en code, exposées par le REST natif ; écriture réservée aux personnes pouvant éditer les articles.
- Calendrier fictif stocké dans `imagine_demo_calendrier`, visible avec `[imagine_demo_calendrier]`.
- Bibliothèques `Imagine\Pilotage` et `Imagine\Connecteur` chargées par un autoloader PSR-4 simple, depuis leurs `src/` frères copiés sans modification. Ce sont des bibliothèques, **pas des plugins activables** : aucune fausse déclaration d’activation. Aucun moteur métier ni connecteur réseau n'était appelé par B-00.
- Depuis C-08, `Acces\Moteur` et le vérificateur `Robots` sont réellement appelés par `Paywall`. Les bibliothèques closes ne sont ni modifiées ni activées comme extensions.
- Les mots de passe natifs B-00 restent stockés comme repli si C-08 est désactivé. Avec C-08 actif, **ce mot de passe n'est jamais un droit de lecture**. La décision Memberships/Subscriptions autorise l'abonné ou renvoie le seul extrait public.

## Installation et réglages

Depuis PowerShell, à la racine du dépôt : `python wp/outils/demo/construire.py`. Le constructeur ne vise que `imagine-test-demo`, installe d’abord sa garde MU hors ligne, copie ce plugin et les bibliothèques, l’active et crée les fixtures. Il garde le thème par défaut tant que le thème `imagine` n’existe pas.

Les mots de passe générés restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans le dépôt. Aucune licence commerciale, compte WooCommerce.com ou passerelle de paiement n’est configuré. L’exception Novamira relève exclusivement de la création normale autorisée de l’outil.

## Tests B-00

```powershell
python -m unittest discover -s wp/tests/demo -p "test_b00*.py" -v
python wp/outils/demo/construire.py --preuve reconstruction
python wp/tests/demo/b00-verifier.py
```

`b00-recette.php` est inclus par WP-CLI (pas évalué par `eval-file`, incompatible avec `strict_types`) : types, 15 dates, 5 numéros, 20 articles, 10 médias, thématiques, comptes fictifs, bibliothèques et versions réelles, email/HTTP/paiements fermés. `b00-snapshot.php` inventorie indépendamment les objets tagués et leurs empreintes ; la reconstruction vérifie mêmes IDs, slugs, URL, textes et médias sans doublon. La recette HTTP B-00 décrivait le verrou natif provisoire; ses attentes « mot de passe => complet » sont délibérément remplacées par C-08.

## C-08 — paywall serveur

`Paywall.php` assemble numéro/date éditoriale, identité WordPress, adhésions Memberships, lien natif `_subscription_id` et état/dates CRUD Subscriptions. Il appelle les bibliothèques pures C-06/C-03, sans les modifier. Il ne lit aucun corps dans le moteur de décision.

Réglages (administration C-10 à venir) :

- `imagine_acces_plans` : tableau `ID du plan Memberships => abonnement|offert|groupe`, vide par défaut (aucun accès abonné). Les états et dates natifs restent obligatoires. Les rôles natifs `administrator` et `editor` correspondent à l'équipe C-06.
- `imagine_acces_extrait_caracteres` : 320 par défaut, borné à 40–1000. C'est un plafond sur **l'extrait éditorial explicitement public**, jamais sur `post_content`. Sans extrait, phrase neutre. Le mot de passe natif peut encore donner son message de protection dans certaines fonctions d'extrait WordPress, sans exposer le corps.
- La grâce n'est pas un synonyme de `on-hold`. Elle exige les deux métadonnées UTC `_imagine_acces_grace_debut` / `_imagine_acces_grace_fin` de l'objet Subscriptions, une adhésion active/paused, un propriétaire cohérent et des dates valides; la fin effective est le minimum des bornes natives. Aucun délai n'est inventé. Les fixtures posent une large fenêtre **entièrement fictive** pour la démonstration; le cycle réel des impayés est hors lot.

Les réponses dynamiques sont conservativement privées/no-store (pas de cache d'hébergement testé). Les objets de requête refusés sont clonés et expurgés, jamais réécrits dans le cache objet. Gardes supplémentaires : contenu, REST rendu/brut, extraits, flux, oEmbed, métadonnées de partage sans articleBody. XML-RPC est désactivé sur ce squelette. Le DNS Robots est délibérément indisponible hors ligne : UA et IP de proxy ne donnent jamais un droit. Un vrai robot Internet n'est pas validé par ce lot.

```powershell
python wp/outils/demo/c08.py --seed
python wp/tests/demo/c08-faults.py
python wp/tests/demo/c08-verifier.py
python wp/tests/demo/c08-regression.py
python -m unittest discover -s wp/tests/demo -p "test_*.py" -v
```

Cible fixe `imagine-test-demo`, aucune création/reconstruction B-00. `c08.py` sans `--seed` réinstalle seulement les fichiers C-08 et exécute la recette PHP. `--seed` réutilise les mêmes IDs pour 3 comptes fictifs, 1 plan, 2 adhésions, 2 abonnements manuels sans passerelle et 2 articles réservés supplémentaires. Les identifiants restent dans `C:\Users\Ced\.imagine-demo\c08-identifiants.json`. `construire.py --theme-only` reste inchangé.

Preuves, limites et mode d'emploi : `production/C-08/`. Les articles B-00 restent intacts mais le numéro T1 affiche aussi les deux fixtures C-08. Les anciens tests B-00/B-01 à cardinalité globale « quatre articles » et à autorisation par mot de passe ne constituent plus la recette du site augmenté; C-08 vérifie séparément le snapshot B-00 exact, toutes ses URL, le HTML et les droits natifs. Aucun PDF n'est sécurisé par C-08; ni découverte complète, ni achat d'un numéro, ni mode lecture spécifique ne sont revendiqués.

