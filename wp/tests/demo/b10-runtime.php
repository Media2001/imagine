<?php

declare(strict_types=1);

use Imagine\Site\PointsVente;

if (!defined('WP_CLI') || !WP_CLI || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || wp_get_environment_type() !== 'local') {
    throw new RuntimeException('Cible refusée');
}
$checks = [];
$expect = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$mapping = ['nom' => 'enseigne', 'adresse' => 'rue', 'localite' => 'ville', 'postal' => 'cp'];
$expect('unicode_natif_nfc_nfd_ligatures', Imagine\Site\PointsVenteRegles::cle('Ḉœur-Æther-Fictif') === 'coeur-aether-fictif'
    && Imagine\Site\PointsVenteRegles::cle("C\u{0327}\u{0301}œur-Æther-Fictif") === 'coeur-aether-fictif');
$csv = "enseigne;rue;ville;cp;personne\nCommerce fictif \\ A;1 rue inventée;Étoile-Fictive;00001;SECRET\n";
$first = PointsVente::importer($csv, $mapping, ';');
$ids = get_option(PointsVente::ACTIFS);
$expect('chargement', $first === ['pris' => 1, 'refus' => []] && count($ids) === 1);
$expect('antislash_natif', PointsVente::lignes()[0]['nom'] === 'Commerce fictif \\ A');
$again = PointsVente::importer($csv, $mapping, ';');
$expect('rechargement_ids_stables', $again === $first && get_option(PointsVente::ACTIFS) === $ids);
$expect('colonnes_personnelles_non_mappees_absentes', !str_contains(wp_json_encode(PointsVente::lignes()), 'SECRET'));
$old = $ids[0];
$new = PointsVente::importer(str_replace('Commerce fictif \\ A', 'Autre fictif', $csv) . "malformé;deux\n", $mapping, ';');
$expect('remplacement_et_refus_numero_motif', $new === ['pris' => 1, 'refus' => [['ligne' => 3, 'motif' => 'nombre_colonnes']]]
    && get_post($old) === null && PointsVente::lignes()[0]['nom'] === 'Autre fictif');
$before = get_option(PointsVente::ACTIFS);
$allRefused = PointsVente::importer("enseigne;rue;ville;cp;personne\nSECRET;incomplet\n", $mapping, ';');
$expect('tous_refuses_numeros_sans_remplacement', $allRefused === ['pris' => 0, 'refus' => [['ligne' => 2, 'motif' => 'nombre_colonnes']]] && get_option(PointsVente::ACTIFS) === $before);
try {
    PointsVente::importer("mauvais;entête\nrefus;fictif\n", $mapping, ';');
    $expect('entete_refusee', false);
} catch (InvalidArgumentException $e) {
    $expect('entete_refusee', get_option(PointsVente::ACTIFS) === $before);
}
$explicit = $mapping + ['personne' => 'personne'];
PointsVente::importer($csv, $explicit, ';');
$expect('mapping_personne_explicite', PointsVente::lignes()[0]['personne'] === 'SECRET');
update_option(PointsVente::CONFIG, ['mapping' => $mapping, 'separateur' => ';', 'carte' => '0'], false);
$expect('retrait_mapping_personne_cache_immediatement', !str_contains(PointsVente::afficher(''), 'SECRET'));
update_option(PointsVente::CONFIG, ['mapping' => $explicit, 'separateur' => ';', 'carte' => '0'], false);
$expect('affichage_personne_explicite', str_contains(PointsVente::afficher(''), 'SECRET'));
delete_option(PointsVente::CONFIG);
$expect('reglage_deux_valeurs_ferme', PointsVente::carte('0') === '0' && PointsVente::carte('1') === '1'
    && PointsVente::carte('autre') === '0' && PointsVente::carte(null) === '0');
$type = get_post_type_object(PointsVente::TYPE);
$expect('type_prive_sans_REST_recherche', $type && !$type->public && !$type->show_in_rest && $type->exclude_from_search);
echo wp_json_encode(['checks' => $checks, 'normalizer_available' => class_exists('Normalizer')]);
