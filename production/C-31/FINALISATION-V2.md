# C31 — Finalisation réservée au parent après C32

## État transmis

- Corrections 1–5 appliquées et vérifiées ; code C31 présent sur `imagine-test-demo`, relu par empreintes exactes. Bootstrap partagé inchangé.
- Tests C31 : **9 / 64 assertions PASS**. Paquet imagine-site complet : **267 / 3267 assertions PASS** dans l'image préexistante, sans réseau. Style ciblé PSR-12 : exit 0, zéro erreur (warning-severity 0).
- Native : **46 PASS** ; inscriptions navigateur : **16 PASS** ; Mon compte : **29 PASS**, trois vrais POST ; commande HTTP Store API : **13 PASS**. Scans base : **47 tables / 187 colonnes textuelles**, témoins positifs sessions + commandes HPOS + options/journaux + usermeta. Réglages, utilisateurs, actions et sessions restaurés ; aucun envoi mail.
- `PRET` **absent** et `reception-corrections-V2.json` **absent** volontairement. L'ancien `PRET` est conservé comme `PRET-historique-avant-corrections-V2.txt` ; il n'est pas un marqueur actif. `reception-V2.json` est historique.
- Aucun verrou ni Git touché ; aucun fichier C32 ni runner partagé modifié. Le README partagé n'a pas été modifié.

## Avant le scellé

Le parent intègre **seulement la section C31** du fichier `README-fragment-V2.md` dans `wp/plugins/imagine-site/README.md`, en remplacement de la section C31 existante. Ne pas toucher aux sections voisines. Le contrat capture ensuite cette section, pas le hash du README ou du bootstrap entiers.

La préparation d'image et le rejeu global doivent être exécutés **une seule fois pour C31+C32**, lorsque C32 est terminé. Les commandes suivantes capturent ce passage commun sous C31 ; C32 peut consommer/copier ces mêmes journaux et reçus exacts, sans relancer les opérations.

Depuis `C:/Users/Ced/imagine` :

```text
python -B wp/outils/demo/c31.py image corrections-image-V2
python -B wp/outils/demo/c31.py replay corrections-replay-V2
python -B production/C-31/verifier.py --pre-final --live
python -B production/C-31/finaliser.py
python -B production/C-31/verifier.py --live
python -B production/B-13/qualifier.py C-31
```

`image` appelle exactement `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/preparer-image.ps1` ; `replay` appelle exactement le même lanceur pour `wp/tests/rejouer.ps1`. L'enfant C31 n'a exécuté ni l'un ni l'autre.

Si le parent a déjà exécuté l'unique passage commun avec un autre nom, **ne pas le rejouer** : copier ses sorties réelles sous `corrections-image-V2.json/.log` et `corrections-replay-V2.json/.log`, en conservant commande/exit et en mettant dans chaque JSON le nom exact du journal correspondant. Ne jamais recycler les anciens `image-V2`/`replay-V2` antérieurs aux corrections. En cas de refus ou de mutation après ces preuves, les conserver comme historiques et produire des nouveaux reçus bornés, sans faux PASS.

## Ce que fait le finaliseur

Il relit les preuves locales et leurs sources, les classes distantes, le bloc C31 unique, puis exige l'image préparée et un nouveau `T01_RESULT` vert, outils sans échec et tests du nouvel adaptateur C31 présents. Les seuls paquets rouges étrangers tolérés restent A-32/A-33/A-34, conformément à la file de voie 2. Il scelle **`reception-corrections-V2.json`**, vérifie ce manifeste, puis crée `PRET` et relit le contrat final. Le lecteur historique `verifier.py` reste le point d'entrée des paquets ; il délègue au lecteur de corrections, qui ne valide plus les anciennes preuves seules.

Tant que les nouveaux reçus globaux manquent, utiliser seulement :

```text
python -B production/C-31/verifier.py --pre-final --live
```

Résultat déjà réellement observé : `C31: CORRECTIONS_LOCALES_PASS`, `PRET: false`, attente explicite des deux opérations uniques du parent. Ce vert local n'est pas un PRET et n'est pas présenté comme un rejeu global.

## Incidents résolus et bornes

- Deux rouges natifs ont démontré `billing_email` persisté en session avant le refus, sur checkout classique puis Store API. Les gardes ont été avancées avant ces écritures. Voir `corrections-native-red3-V2.json`, `corrections-store-red1-V2.json`, et les verts finaux.
- Le premier affichage réel Woo Blocks a auto-migré la page Cart et créé une notification Woo. La page a été restaurée depuis sa vraie préimage fictive privée, la seule révision et la seule note créées par la recette retirées, puis les empreintes métier initiales retrouvées : `corrections-cart-restaure-V2.json`. Le runner capture désormais ces préimages avant la navigation et les restaure à chaque passage.
- Le cache natif `_transient_wp_styles_for_blocks` varie selon les pages ; cette seule volatilité de rendu a été ajoutée aux caches B13/B15 déjà permis. Aucune option métier n'est soustraite au contrôle.
- Les navigateurs bloquent les tiers et désactivent JS. Le checkout Blocks est soumis via la vraie Store API avec panier et nonce ; sa capture n'est que le squelette natif, pas un formulaire hydraté. Les formulaires d'inscription et Mon compte sont soumis par clic DOM réel.
- Les deux tentatives de traductions de wp-login sont bloquées et explicitement qualifiées. La notification native lors du changement d'adresse autorisé est également bloquée ; aucun mail ne sort.
