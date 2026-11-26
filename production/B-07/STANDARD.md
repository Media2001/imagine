# Standard gratuit — décision B-07 (10 lignes)

1. Le cahier impose Event Tickets Plus pour la billetterie ; sa licence n'est pas confirmée et son installation reste interdite dans ce lot.
2. Son éditeur fournit Event Tickets gratuit : RSVP et billets gratuits, ajoutables aux articles, pages et types personnalisés (source officielle 0, fonctionnalités et FAQ).
3. Event Tickets gratuit fonctionne sans The Events Calendar : le modèle provisoire `imagine_evenement` B-00 n'exige donc pas de migration pour un RSVP (source 0, FAQ).
4. L'agenda, les vues mois/liste/jour, la fiche, les lieux et les organisateurs sont fournis par The Events Calendar gratuit, extension distincte (source officielle 1, fonctionnalités).
5. The Events Calendar gratuit annonce le JSON-LD ; Event Tickets seul n'est pas un agenda complet (source 1, fonctionnalités).
6. Les champs personnalisés d'inscription sont annoncés parmi les fonctions de Plus : la case explicite « être recontacté » n'est pas le formulaire standard gratuit documenté (source 0, description et FAQ).
7. Event Tickets gratuit envoie normalement un email de confirmation et comprend des fonctions de billets, stock et rapports : ce n'est pas le parcours B-07, sans billet, quota, export d'inscrits ni email (source 0, fonctionnalités et FAQ).
8. Décision technique à défaut : ne pas installer ces deux extensions pour en neutraliser/recoder le parcours ; conserver B-00 et son thème, avec un raccord WordPress minimal et des callbacks RGPD additifs.
9. Aucun paquet tiers, licence, compte marchand, carte, billet, SDK ni framework de réservation n'est installé ; ce choix reste réversible au branchement de la billetterie autorisée.
10. Sources : readmes officiels de l'éditeur dans le SVN WordPress, réponses réellement téléchargées et empreintes dans `sources-standard.json`, textes GPL `source-standard-0.txt` et `source-standard-1.txt` ; pages commerciales bloquées HTTP 403, non utilisées.

## Sources exactes (rejouables sans le site)

- Source 0 : `https://plugins.svn.wordpress.org/event-tickets/trunk/readme.txt` — passages Description, Features, FAQ (lignes 16–63 et 162–176 du témoin local).
- Source 1 : `https://plugins.svn.wordpress.org/the-events-calendar/trunk/readme.txt` — Description et Features (lignes 16–66 du témoin local).

Ce sont des sources de capacité, pas une preuve d'installation ou d'exécution du standard. Le balisage livré est celui du raccord natif : uniquement nom, début, lieu, description et URL réellement affichés ; aucune promesse de résultat enrichi ni plan SEO complet.
