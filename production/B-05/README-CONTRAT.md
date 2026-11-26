
## B-05 — partenaires

`Partenaires` enregistre `imagine_partenaire_du_mois` dans le formulaire Settings API **C10 existant**, via les hooks administratifs, sans modifier la bibliothèque close. Un seul identifiant de partenaire publié, choix manuel ; absent, zéro, invalide ou dépublié : pas de bloc. Les valeurs invalides soumises conservent le choix valide courant. Nonce, contrôle `manage_options` et sauvegarde restent ceux de `options.php`. Pas de rotation, nouveau rôle, service ni règle d'acceptation.

Le thème conserve le gabarit individuel B01 et son filtre natif `WP_HTML_Tag_Processor` : `sponsored` ajouté aux liens HTTP(S) sortants du corps partenaire, avec conservation des autres relations. Les fiches internes restent ordinaires ; aucun lien d'article n'est touché. Bloc, cartes de liste et fiche portent la classe structurelle `imagine-partnership` et le texte **Partenariat** ; aucun CSS ajouté. Le designer doit encore dessiner leur distinction.

Le CPT est exclu de la recherche ; les requêtes publiques de recherche/flux sont également fermées lorsqu'un visiteur force explicitement son type. Les requêtes éditoriales du thème restent sur `post`. Rejeu ciblé : `python -B wp/tests/demo/b05-verifier.py` ; installation autorisée sur la seule démo : `python -B wp/outils/demo/b05.py deploy LABEL`. Tests natifs/Chromium et deux captures, sources officielles et limites : `production/B-05/`. Les reçus antérieurs et les sections partagées sont préservés par contrat, pas par un hash global de README.
