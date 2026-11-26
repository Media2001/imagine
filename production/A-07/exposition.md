A-07 — constat du 20 novembre 2026, corrections documentaires du 26 novembre. Aucun accès depuis Internet démontré ; l'absence d'exposition n'est pas établie, notamment en IPv6.

**Surface prioritaire : WSL en mode miroir + règle entrante autorisant le port 7000 sur le profil public.** Si une redirection de box ou une route IPv6 publique laisse passer ce port, le tableau de bord et `/mcp` peuvent devenir joignables. Ce lien de risque n'est pas une preuve d'exposition. Aucun nouveau contrôle réseau n'a été exécuté le 26 novembre ; les observations ci-dessous restent l'instantané déclaré du 20 novembre, non un état courant.

| Point vérifié | Résultat déclaré le 20 novembre | Preuve historique / procédure | Non vérifié |
|---|---|---|---|
| Écoutes | Tableau de bord 7000 publié sur toutes interfaces IPv4/IPv6 ; sites publiés : 8082, 8083, 8084, 8087, 8090, 8091, 8092, 8096, 8097. Pas d'écoute WSL constatée sur 8081 à cet instant. Allocation dynamique dans 8081–8200 : cet instantané n'invalide pas la règle sur toute la plage. | `docker ps --format '{{.Ports}}'` ; `ss -Hlnt` | Traversée effective depuis un autre appareil, états ultérieurs, autres ports. |
| Passage WSL/LAN | WSL miroir ; aucune entrée portproxy ni écoute Windows native retournée sur les ports ciblés. | `wslinfo --networking-mode` ; `netsh interface portproxy show all` ; `Get-NetTCPConnection -State Listen` | Joignabilité LAN et filtrage Hyper-V ; l'écoute WSL ne suffit pas. |
| Pare-feu | Profils observés privés. Règles entrantes actives autorisant 7000 en privé et public, 8081–8200 en privé. | `Get-NetConnectionProfile` ; `Get-NetFirewallProfile` ; association exacte proposée ci-dessous, non rejouée. | Association historique complète non conservée ; portée par interface, règles applicatives/globales et filtrage Hyper-V. Profil public ne signifie pas redirection Internet. |
| Box / UPnP | **Service découvert/répondant : non déterminé. Redirections non déterminées.** La collection a été déclarée vide, sans preuve d'une réponse exploitable de la box ; ce n'est donc pas un zéro réseau établi. | Référence historique conservée : `HNetCfg.NATUPnP.StaticPortMappingCollection` ; commande complète non conservée, pas de nouvelle exécution. | Découverte/accusé de réponse UPnP non établi ; aucune commande de découverte ni sortie brute conservée. Redirections manuelles, DMZ, IPv6 et administration de box non consultées. |
| Cloudflare / cloudflared | Présence : **non vérifié** ; activité : **non vérifié**. | Aucun résultat individuel conservé dans les preuves initiales. | Inventaire initial Windows services/processus/désinstallations non exhaustif ; binaires portables et WSL non établis pour cet outil. Aucun contrôle neuf revendiqué. |
| ngrok | Présence : **non vérifié** ; activité : **non vérifié**. | Aucun résultat individuel conservé dans les preuves initiales. | Même limite Windows/portables ; périmètre WSL non établi pour cet outil. |
| Tailscale / accès distant | Tailscale actif, aucune entrée Funnel activée signalée ; Bureau à distance Windows activé, service en marche. | Windows : `Get-Service`, `Get-Process`, registre Terminal Server/désinstallations ; `tailscale status --json` et `tailscale funnel status --json`, sorties filtrées. | Droits sur le réseau privé distant, autres accès, portables et services WSL ; ces observations ne démontrent pas d'accès Internet au staging. |
| Extérieur | Aucun accès externe ni balayage effectué. | Procédure manuelle de Ced ci-dessous. | Tous les ports non essayés individuellement ; absence générale d'exposition, IPv4 et IPv6. |

**Association pare-feu reproductible, proposée et non exécutée dans ce correctif** (PowerShell ; champs réseau non sensibles uniquement) :

```powershell
Get-NetFirewallRule -PolicyStore ActiveStore -Enabled True -Direction Inbound -Action Allow | ForEach-Object {
    $rule = $_
    $rule | Get-NetFirewallPortFilter | Where-Object {
        $_.Protocol -eq 'TCP' -and $_.LocalPort -match '^(7000|8081|8081-8200)$'
    } | Select-Object @{n='Direction';e={$rule.Direction}}, @{n='Enabled';e={$rule.Enabled}}, @{n='Action';e={$rule.Action}}, Protocol, LocalPort, @{n='Profile';e={$rule.Profile}}
}
```

Ce filtre documente les règles de ports explicitement nommées, pas toutes les autorisations plus larges (`Any`, applications, autres plages) ; leur portée effective reste non vérifiée.

**Test extérieur à faire par Ced, sans balayage ni connexion à un compte :** téléphone en 4G, Wi-Fi/VPN/Tailscale coupés, ouvrir en HTTP l'adresse publique connue de la box suivie de `:7000`, puis **un port de site actuellement publié** relevé dans l'instantané Docker du moment (pas un port choisi à l'aveugle). Une page reconnaissable confirme ce chemin d'exposition ; un délai/échec ne prouve pas une absence générale. Si une IPv6 publique du serveur est disponible, répéter les deux ouvertures avec cette adresse entre crochets. Les autres ports restent non vérifiés tant qu'ils ne sont pas contrôlés un à un. Ne publier aucune adresse et ne saisir aucun identifiant.

**Priorités, non appliquées :** 1. Faire vérifier à Ced redirections/DMZ/filtrage IPv6 et les deux surfaces extérieures. 2. Restreindre l'accès administratif au 7000 et revoir ses autorisations publiques après vérification des usages. 3. Authentifier tableau de bord et `/mcp`, revoir les accès distants. Ce contrôle reste documentaire et en lecture seule ; aucune recommandation ne devient un lot d'action ni un GO.