# Banc C05 dédié

Toutes les écritures de ce banc sont dans ses répertoires C05 et dans un nouveau conteneur possédé. Il ne charge ni les scripts d’import A01 ni les tests de découverte du dépôt. Python hôte sert seulement au transport Docker et à la lecture des reçus ; **tous les PHP, tests et WordPress tournent dans le conteneur**.

Image réutilisée, sans pull : `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2` (banc A01 compatible existant). Bibliothèque de paquets : `/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip` sous WSL Ubuntu, lecture seule ; SHA-256 `ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083`. Ce paquet n’est jamais exporté dans le dépôt. Aucun téléchargement ou licence activée.

`run.py prepare` crée un conteneur `imagine-c05-<aléatoire>` avec le label `org.imagine.c05-runner=true`, réseau `none`, sans montages ni ports, sans privilèges, capacités supprimées. L’image doit déjà être disponible. Le transport réutilise `wsl.exe -d Ubuntu -- docker`, aucune installation hôte.

`unit` copie exclusivement les PHP C01 en lecture seule, les PHP C05 et les fichiers dédiés du banc, vérifie leurs empreintes puis lance `tests/Echeancier/run.php`. C’est une suite d’assertions PHP autonome, **pas PHPUnit**. La sortie structurée et les journaux sont conservés, y compris les RED historiques. La syntaxe de chaque PHP copié est vérifiée ; aucun PHPCS/Composer nouvellement installé ni contrôle PSR-12 automatisé n’est revendiqué.

`e2e` réinitialise uniquement `/scratch` et `/report` **dans ce conteneur possédé**, crée ses bases inventées classique et HPOS et active le vrai Subscriptions. MariaDB écoute uniquement sur socket Unix. Aucun serveur HTTP/FPM. Aucune archive de site ni export SQL. Emails et HTTP bloqués ; pas de passerelle de paiement. Chaque date future est vérifiée dans `next_payment` et dans une action native, puis **cette seule action** est exécutée explicitement en accéléré. Les horloges système/PHP ne sont pas modifiées ; les confirmations Woo ont l’heure réelle du banc.

Le raccord est appliqué explicitement entre validations, pas par un branchement automatique de production. Les commandes sont réelles en base ; les validations sont des transitions Woo locales fictives, pas des opérations bancaires. Option A du 22/11 : quatre positions par bloc de quatre numéros ; les 28 fenêtres fictives à cinq dates sont désormais acceptées. Quatre scénarios par stockage : 20 février et 9/10/11 avril 2027, donc veille/jour/lendemain de clôture.

`admin-scenario.php` active l’adaptation dédiée sans toucher au bootstrap partagé : formulaire WP réel (champs, nonce, refus anonyme), enregistrement Settings API sans REST, douze combinaisons persistées/relues par stockage et effets sur moteur/projections. Pas de sauvegarde par requête HTTP ni d’inspection visuelle revendiquée. Marge vide ou option absente : planification refusée, aucun défaut.

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

Éviter de réemployer un nom de reçu à conserver. `verify.py` sans paramètres vérifie `reprise-final-unit` / `reprise-final-e2e` : empreintes actuelles, compteurs dérivés, quatre rangs par bloc, cinq dates acceptées, réglages et C01 inchangé, absence exacte de tous les conteneurs C05 connus. Il écrit `production/C-05/preuves/verification.json`, avec l’état de PRET et ses empreintes s’il est présent. Ce n’est ni une clôture par les relecteurs, ni un GO réel.

`official-review.py` relit huit pages officielles publiques (six Woo préexistantes, deux Settings API WP) et produit `production/C-05/sources/review-2026-11-22.json`, avec courts extraits horodatés et empreintes. Il n’est jamais appelé par le banc offline. `sources.py` et les reçus du 21/11 restent historiques. La collecte HTTP hôte est indépendante de la fixture, sans réseau dès sa création.
