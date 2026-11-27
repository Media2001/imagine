# Lot B-11 — Vidéos, podcasts et sommaire audio

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-04 (page numéro), C-06 et C-11 (décision d'accès, fichier servi hors racine publique). **Cahier des charges** : §3.14 (« Vidéos externes intégrées par numéro et sur les pages article ; liens vers les podcasts »), §3.3 (« sommaire audio » de la page numéro), §3.1 (zone 2), §4.4 (cookies). Relis-les.

## Pourquoi

La rédaction accompagne des numéros et des articles d'une vidéo hébergée ailleurs, d'un podcast, et d'un sommaire lu à voix haute. Une vidéo intégrée charge un lecteur chez un tiers, qui dépose des cookies : elle ne peut pas s'afficher d'office. Le sommaire audio, lui, est un fichier d'Imagine réservé aux ayants droit, comme le PDF.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que WordPress fait seul d'une adresse de vidéo collée dans un contenu (oEmbed, et l'appel sortant que le serveur fait alors), et le lecteur audio natif du navigateur.

- **Vidéo externe**, sur un numéro et sur un article : un champ « adresse de la vidéo ». L'hôte doit figurer dans une liste fermée en réglage ; sur la démonstration, un seul hôte manifestement fictif. **Par défaut, la page affiche un lien** (« Voir la vidéo », qui ouvre le service) : ni cadre intégré, ni script, ni vignette venue du tiers, et **aucun appel sortant du serveur**, oEmbed compris.
- Un réglage fermé « intégrer le lecteur après consentement », éteint. L'outil de consentement n'est pas choisi : allumé sur la démonstration, il affiche un emplacement vide et n'appelle rien. Dis en trois lignes ce qu'il faudra le jour venu.
- **Podcast** : un champ « lien vers le podcast », rendu comme un lien, rien d'autre.
- **Sommaire audio** du numéro : un fichier audio rangé et servi **exactement comme le PDF de C-11** (hors racine publique, droit contrôlé à chaque demande par la décision d'accès de C-06), joué par le lecteur audio natif du navigateur. Fichier d'essai : quelques secondes de silence, fabriquées.

Règles :

- la vidéo ou le podcast d'un article réservé suit le texte : qui ne reçoit que l'extrait ne reçoit ni le lien ni l'adresse ;
- le sommaire audio est réservé à ceux qui ont droit au numéro (abonné actif, acheteur du numéro) : c'est le défaut prudent, la question est rangée pour Imagine. Aucune règle d'accès nouvelle : celles de C-06, telles quelles ;
- aucun style inventé : le squelette de B-01.

## Preuve

Proportionnée. Un numéro et un article d'essai avec vidéo, podcast et sommaire audio ; zéro requête sortante observée, à l'affichage comme à l'enregistrement, réglage éteint puis allumé ; un hôte hors liste est refusé à la saisie ; un anonyme n'obtient ni le fichier audio ni son adresse, et ne voit ni lien ni adresse de vidéo sur l'article réservé (un contrôle qui trouve d'abord le lien avec le bon profil, puis son absence ; une mutation témoin). Données d'essai laissées en place, déclarées fictives dans `A-VOIR.md`.

## Livrables

Le code, ses tests, la section du README de l'extension, `production/B-11/A-VOIR.md`, `PRET`. Rapport court.
