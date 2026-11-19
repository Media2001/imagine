# Lot C-03 — Vérification des robots d'indexation

**Chantier** : C · code sur mesure. **Nature** : PHP pur et tests, sans WordPress.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Robots/` et `tests/Robots/`.
**Livrables** : code, tests, `production/C-03/notes.md`, puis `production/C-03/PRET`.
**Cas d'acceptance concernés** : R-27, et en partie R-26 et R-28.

## Pourquoi

Le texte complet d'un article réservé n'est servi qu'à l'abonné connecté et aux robots d'indexation **vérifiés** (§3.9, §4.4). « Un agent utilisateur seul ne suffit pas » : n'importe qui peut se faire passer pour un robot. Une erreur dans un sens ouvre tout le contenu payant ; dans l'autre, elle fait disparaître le site des moteurs.

Ce lot ne fait que répondre à une question : *cette requête vient-elle d'un robot vérifié ?* Le branchement sur le paywall viendra dans un lot ultérieur.

## À implémenter

1. **Une fonction de décision** : entrée = agent utilisateur et adresse IP ; sortie = robot vérifié (lequel), ou non vérifié avec le motif.
2. **Deux méthodes de vérification**, par robot, configurables :
   - résolution inverse de l'adresse IP, contrôle que le nom obtenu appartient à un domaine autorisé du robot, puis **résolution directe de ce nom**, qui doit redonner la même adresse IP ;
   - appartenance à des plages d'adresses publiées par l'exploitant du robot (IPv4 et IPv6).
3. **Une liste de robots configurable** (pas de liste figée dans le code de décision). Livre une configuration de départ pour Google et Bing (§4.4), en citant pour chaque domaine et chaque source de plages la page de documentation officielle de l'exploitant.
4. **La résolution DNS derrière une interface**, injectée. Le moteur ne fait lui-même aucun appel réseau : les tests utilisent une fausse résolution.
5. **Un cache des décisions** par adresse IP, derrière une interface, avec deux durées distinctes (réponse positive, réponse négative).
6. **Le comportement en cas de panne** : résolution impossible ou trop lente → **non vérifié**. Le doute profite au paywall, jamais au visiteur.

## Points de vigilance à couvrir par des tests

- Bon agent utilisateur, adresse quelconque → non vérifié.
- Résolution inverse qui renvoie un nom du bon domaine, mais résolution directe qui ne redonne pas l'adresse → non vérifié (résolution inverse falsifiée).
- Nom qui *contient* le domaine sans s'y terminer (`googlebot.com.exemple.net`) → non vérifié.
- Adresse IPv6.
- Adresse du visiteur derrière un répartiteur : le moteur reçoit l'adresse en argument et ne lit aucun en-tête lui-même. Explique dans `notes.md` pourquoi l'en-tête `X-Forwarded-For` ne doit être cru que s'il vient d'un répartiteur connu, et ce qu'il faudra régler chez l'hébergeur.
- Agent utilisateur d'un robot absent de la liste → non vérifié, sans résolution.
- Délai de résolution dépassé → non vérifié, et la décision négative est mise en cache moins longtemps.

## Ce que tu ne décides pas

- La liste définitive des robots admis (au-delà de Google et Bing) : question pour le référenceur. Liste dans `notes.md` ceux qui publient une méthode de vérification, sans les activer.
- Les durées de cache : propose des valeurs, isolées dans la configuration.

## Exigences

Celles du lot C-01 ; espace de noms `Imagine\Pilotage\Robots`.
