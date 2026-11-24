# Lot C-11 — Le PDF du numéro, protégé

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-08, C-06 (clos).
**Cahier des charges** : §3.9, §4.4. **Cas d'acceptance** : ceux de R-25 à R-31 qui portent sur le PDF.

## Pourquoi

Le paywall protège l'article, pas encore le PDF. Sur le site de démonstration, le PDF factice d'un numéro s'ouvre par son adresse directe, pour n'importe qui. C'est la fuite classique d'un magazine payant.

## Ce qu'on veut

- Le PDF d'un numéro n'a **plus d'adresse publique**. Il est servi par une adresse du site qui passe par la décision d'accès (type « PDF du numéro », déjà prévu par C-06) : droit → le fichier ; pas de droit → page du numéro avec le bloc adéquat, jamais le fichier.
- Le fichier lui-même n'est pas atteignable en contournant WordPress (adresse directe dans les médias, liste de dossier, pièce jointe, API REST des médias, recherche, plan de site).
- Les réglages d'accès qui concernent le PDF (robots vérifiés, PDF antérieurs à l'abonnement) sont lus depuis l'écran de C-10.
- Acheteur d'un numéro : droit au PDF de ce numéro seulement. Si ce droit n'est pas encore branchable, dis-le et laisse fermé.
- En-têtes : pas de mise en cache partagée d'un PDF servi à un abonné.
- Fermé par défaut à la moindre erreur.

La solution doit rester simple et portable : pas de dépendance à une configuration de serveur qu'on ne maîtrisera pas chez l'hébergeur final. Si une règle de serveur est nécessaire pour fermer l'accès direct, propose-la à part et prouve que, sans elle, rien ne fuit quand même (fichier rangé hors de la racine publique, ou nom non devinable **et** jamais exposé : explique ton choix en cinq lignes).

## Preuve

Test d'étanchéité rejouable : en anonyme, aucune des voies ci-dessus ne renvoie les octets du PDF (empreinte du fichier témoin absente de toute réponse) ; en abonné actif, le fichier est servi.

## Livrables

Code, test, `production/C-11/A-VOIR.md` (l'adresse à ouvrir en anonyme puis en abonné), `PRET`.
