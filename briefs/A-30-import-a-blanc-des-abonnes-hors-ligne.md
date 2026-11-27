# Lot A-30 — L'import à blanc des abonnés hors ligne

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-13 (contrôle du fichier), A-22 (gardien des sorties). **Cahier des charges** : §4.3 (« Abonnés hors ligne », « Abonnés sans email », « Activation des comptes »), §2.3, §3.13 (« Encodage sans email »). Relis-les.

## Pourquoi

Environ 1 500 abonnés par domiciliation ou par virement seront importés depuis un export de la base Access. A-13 dit si le fichier est propre. L'étape suivante, l'import (A-06), attend le fichier d'Imagine et une décision de Ced. Entre les deux, il manque une réponse que l'administration voudra avant tout import : **que ferait l'import, ligne par ligne, sur ce site-là ?** Combien de comptes créés, combien de lignes qui tombent sur un compte existant, combien sans adresse électronique, combien dont le type d'abonnement n'a pas de correspondance.

**Ce lot n'importe rien.** Il ne crée aucun compte, aucun abonnement, n'écrit rien dans le site. Tu ne verras jamais le vrai fichier.

## Ce qu'on veut

**Le standard d'abord.** Dis en cinq lignes ce que l'import natif de WooCommerce et celui de Subscriptions savent faire d'un fichier d'abonnés, et pourquoi il faut ou non autre chose pour un passage à blanc.

Un outil en lecture seule, `wp/outils/bascule/a30/`, lancé par le gardien commun, qui prend le fichier contrôlé par A-13, sa correspondance des colonnes, et une **table de correspondance des types** (quel « type d'abonnement » d'Access devient quel produit du site) :

- la table des types est un fichier de configuration, livré en exemple, entièrement fictif. Un type absent de la table est compté « à décider », jamais deviné ;
- pour chaque ligne, une issue d'une liste fermée : compte à créer ; compte existant à la même adresse (un seul compte par adresse, §3.7) ; ligne sans adresse électronique (comptée à part, elle suivra la règle du §3.13 : aucune adresse inventée ici) ; type à décider ; ligne refusée par A-13 ;
- un fichier qu'A-13 refuse (IBAN, encodage douteux) est refusé ici de la même façon, par le même code, sans le rejouer autrement ;
- sorties : des **nombres** par issue, par produit et par mode de paiement, groupes de moins de cinq fondus comme dans A-20 ; et, à côté du fichier, jamais dans le dépôt, la liste des numéros de ligne par issue. Aucune donnée de ligne n'est recopiée ;
- sur une copie neutralisée, les adresses sont anonymisées : le rapprochement avec les comptes existants vaut « inconnu après neutralisation », jamais zéro. Dis-le dans le mode d'emploi.

Aucune règle métier nouvelle : l'outil ne décide pas si un abonné échu est importé, ni de la date de sa prochaine échéance, ni de ce que devient un doublon. Ce qui demanderait une règle est une option de la configuration, désactivée par défaut, et tu le signales.

## Preuve

Sur le banc fictif, classique et HPOS, avec les fichiers d'essai d'A-13 complétés : chaque issue est reconnue sur les bonnes lignes ; un type hors table donne « à décider » ; le fichier à IBAN est refusé sans qu'aucune valeur ne sorte ; empreintes de la base et des fichiers identiques avant et après ; les cinq canaris ; la commande du mode d'emploi lancée telle qu'elle est écrite. **Un seul paquet de preuves**, vérificateur sans argument. Suite Python rejouable sous Windows (cp1252).

## Livrables

L'outil, ses tests, la table des types d'exemple, deux lignes dans le mode d'emploi de l'audit, `production/A-30/PRET`. Rapport court, avec les règles que tu as dû laisser en option.
