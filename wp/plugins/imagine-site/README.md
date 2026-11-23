# Imagine — site (B-00, modèle provisoire)

**Ce modèle de démonstration n’est pas le modèle éditorial définitif.** Il sera remplacé après l’audit de l’existant. Aucun ACF, thème ou constructeur de pages n’est embarqué ici.

- Types publics : `imagine_numero`, `imagine_evenement`, `imagine_partenaire` ; taxonomie `imagine_thematique` sur les articles natifs `post`.
- Rattachement d’un article : métadonnée entière `imagine_numero_id` ; indicateur `imagine_reserve`. Déclarations en code, exposées par le REST natif ; écriture réservée aux personnes pouvant éditer les articles.
- Calendrier fictif stocké dans `imagine_demo_calendrier`, visible avec `[imagine_demo_calendrier]`.
- Bibliothèques `Imagine\Pilotage` et `Imagine\Connecteur` chargées par un autoloader PSR-4 simple, depuis leurs `src/` frères copiés sans modification. Ce sont des bibliothèques, **pas des plugins activables** : aucune fausse déclaration d’activation. Aucun moteur métier ni connecteur réseau n’est appelé par ce lot.
- Les articles réservés utilisent **provisoirement la protection native par mot de passe de WordPress** ; l’extrait public est ajouté au formulaire. Le texte complet reste dans `post_content`, absent des réponses anonymes. Ce n’est pas le paywall du lot C-08 et ce n’est pas une validation des droits d’abonnement.

## Installation et réglages

Depuis PowerShell, à la racine du dépôt : `python wp/outils/demo/construire.py`. Le constructeur ne vise que `imagine-test-demo`, installe d’abord sa garde MU hors ligne, copie ce plugin et les bibliothèques, l’active et crée les fixtures. Il garde le thème par défaut tant que le thème `imagine` n’existe pas.

Les mots de passe générés restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans le dépôt. Aucune licence commerciale, compte WooCommerce.com ou passerelle de paiement n’est configuré. L’exception Novamira relève exclusivement de la création normale autorisée de l’outil.

## Tests B-00

```powershell
python -m unittest discover -s wp/tests/demo -p "test_b00*.py" -v
python wp/outils/demo/construire.py --preuve reconstruction
python wp/tests/demo/b00-verifier.py
```

`b00-recette.php` est inclus par WP-CLI (pas évalué par `eval-file`, incompatible avec `strict_types`) : types, 15 dates, 5 numéros, 20 articles, 10 médias, thématiques, comptes fictifs, bibliothèques et versions réelles, email/HTTP/paiements fermés. `b00-snapshot.php` inventorie indépendamment les objets tagués et leurs empreintes ; la reconstruction vérifie mêmes IDs, slugs, URL, textes et médias sans doublon. La recette HTTP vérifie aussi les liens, la connexion de l’administrateur fictif et la protection native provisoire.
