# Banc C05 dédié

Toutes les écritures de ce banc sont dans ses répertoires C05 et dans un nouveau conteneur possédé. Il ne charge ni les scripts d’import A01 ni les tests de découverte du dépôt. Python hôte sert seulement au transport Docker et à la lecture des reçus ; **tous les PHP, tests et WordPress tournent dans le conteneur**.

Image réutilisée, sans pull : `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2` (banc A01 compatible existant). Bibliothèque de paquets : `/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip` sous WSL Ubuntu, lecture seule ; SHA-256 `ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083`. Ce paquet n’est jamais exporté dans le dépôt. Aucun téléchargement ou licence activée.

`run.py prepare` crée un conteneur `imagine-c05-<aléatoire>` avec le label `org.imagine.c05-runner=true`, réseau `none`, sans montages ni ports, sans privilèges, capacités supprimées. L’image doit déjà être disponible. Le transport réutilise `wsl.exe -d Ubuntu -- docker`, aucune installation hôte.

`unit` copie exclusivement les PHP C01 en lecture seule, les PHP C05 et les fichiers dédiés du banc, vérifie leurs empreintes puis lance `tests/Echeancier/run.php`. C’est une suite d’assertions PHP autonome, **pas PHPUnit**. La sortie structurée et les journaux sont conservés, y compris les RED historiques. La syntaxe de chaque PHP copié est vérifiée ; aucun PHPCS/Composer nouvellement installé ni contrôle PSR-12 automatisé n’est revendiqué.

`e2e` réinitialise uniquement `/scratch` et `/report` **dans ce conteneur possédé**, crée ses bases inventées classique et HPOS et active le vrai Subscriptions. MariaDB écoute uniquement sur socket Unix. Aucun serveur HTTP/FPM. Aucune archive de site ni export SQL. Emails et HTTP bloqués ; pas de passerelle de paiement. Chaque date future est vérifiée dans `next_payment` et dans une action native, puis **cette seule action** est exécutée explicitement en accéléré. Les horloges système/PHP ne sont pas modifiées ; les confirmations Woo ont l’heure réelle du banc.

Le raccord est appliqué explicitement entre validations, pas par un branchement automatique de production. Les commandes de renouvellement sont réelles en base ; les validations sont des transitions Woo locales fictives, pas des opérations bancaires. Le compteur d’engagement est une proposition, et ses 28 incompatibilités sur le calendrier fictif sont signalées plutôt que masquées.

`close` inspecte le label et l’isolation, supprime seulement le conteneur possédé, puis exige le diagnostic sémantique exact de son absence. Ni prune, ni arrêt d’une ressource sœur, ni écriture dans `.hermes.lock`.

## Rejouer (depuis C:/Users/Ced/imagine)

```bash
python wp/tests/echeancier-runner/run.py prepare && (
  python wp/tests/echeancier-runner/run.py unit --name relecture-unit &&
  python wp/tests/echeancier-runner/run.py e2e --name relecture-e2e
  result=$?
  python wp/tests/echeancier-runner/run.py close
  exit "$result"
)
python wp/tests/echeancier-runner/verify.py --unit relecture-unit --e2e relecture-e2e
```

Éviter de réemployer un nom de reçu que l’on souhaite conserver. `verify.py` sans paramètres vérifie la remise canonique `final-unit-3` / `final-e2e-3`, les empreintes actuelles, les compteurs, les sources C01 inchangées et l’absence de toutes les ressources C05 connues. Il écrit `production/C-05/preuves/verification.json`. Son succès confirme les **preuves techniques**, pas une acceptance métier universelle ; il attend expressément l’absence de `PRET` tant que le contre-exemple subsiste.

`sources.py` relit uniquement six pages officielles publiques et produit un registre de citations local C05 avec courts extraits vérifiés. Il n’est pas exécuté par le banc offline. La collecte HTTP hôte est indépendante de la fixture, qui reste sans réseau dès sa création.
