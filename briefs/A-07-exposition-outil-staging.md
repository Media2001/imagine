# Lot A-07 — Contrôle de l'exposition de l'outil de staging

**Chantier** : A. **Nature** : contrôle en lecture seule. Aucune modification, aucune règle créée ou supprimée.
**Livrable** : `production/A-07/exposition.md`, puis `production/A-07/PRET`.
**Délai** : une heure.

## Pourquoi

Ta fiche du 19/11 indique que le tableau de bord de l'outil de staging (port 7000), son accès agent (`/mcp`) et les sites (ports 8081 à 8200) n'ont pas d'authentification, que le tableau de bord écoute sur toutes les interfaces, et que l'API peut générer une connexion administrateur. Sur le réseau local, c'est acceptable. Il faut s'assurer que rien de tout cela n'est joignable depuis Internet. Ced n'utilise aucun tunnel.

## À vérifier, sans rien changer

1. **Ce qui écoute** : ports publiés par Docker et adresses d'écoute (toutes interfaces ou locale), dans WSL et côté Windows.
2. **Le passage de WSL vers le réseau local** : règles de redirection de ports de Windows (`netsh interface portproxy show all`), mode réseau de WSL, et ce qui rend les ports 7000 et 8081 joignables depuis un autre appareil du réseau local.
3. **Le pare-feu Windows** : règles entrantes qui autorisent ces ports, et pour quels profils de réseau (privé, public).
4. **La box** : sans identifiant de la box, tu ne peux pas lire ses redirections. Vérifie ce qui est possible sans se connecter à son administration : présence d'un service UPnP et, s'il répond, la liste des redirections qu'il déclare (lecture seule). N'en crée et n'en supprime aucune.
5. **Les tunnels et accès distants** installés sur la machine (Cloudflare, ngrok, Tailscale, accès à distance) : présents ou non, actifs ou non.
6. **Le test depuis l'extérieur** : ne lance pas de balayage de ports de l'adresse publique. Indique seulement à Ced comment le vérifier lui-même en une minute depuis un téléphone en 4G.

## Format du rapport

Une page. En tête, une réponse en une ligne : « rien n'est joignable depuis Internet d'après ce qui a pu être vérifié », ou la liste de ce qui l'est. Ensuite un tableau : point vérifié, résultat, preuve (la commande lancée), et ce qui n'a **pas** pu être vérifié.

Termine par des recommandations classées, sans en appliquer aucune : par exemple limiter l'écoute du tableau de bord à l'adresse locale, ou ajouter un mot de passe. Ced décide.

Aucun mot de passe, aucune adresse IP publique et aucun identifiant dans le rapport.
