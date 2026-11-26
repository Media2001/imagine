<?php

declare(strict_types=1);

use Imagine\Site\PersonnalisationRegles as R;

$root = '/repo/wp/plugins/imagine-site/';
$checks = [];
$checks['regles_presentes'] = is_file($root . 'PersonnalisationRegles.php');
if ($checks['regles_presentes']) {
    require $root . 'PersonnalisationRegles.php';
    $q = [['id' => 'situation-fictive', 'titre' => 'Situation fictive', 'multiple' => false,
        'choix' => [['id' => 'explorateur-fictif', 'titre' => 'Explorateur fictif'], ['id' => 'reveur-fictif', 'titre' => 'Rêveur fictif']]]];
    $checks['catalogue_ferme_valide'] = R::catalogue($q) === $q;
    foreach (['question_duplicate', 'choice_duplicate', 'html', 'libre', 'type', 'id'] as $case) {
        $bad = $q;
        if ($case === 'question_duplicate') { $bad[] = $q[0]; }
        if ($case === 'choice_duplicate') { $bad[0]['choix'][] = $q[0]['choix'][0]; }
        if ($case === 'html') { $bad[0]['titre'] = '<b>Texte</b>'; }
        if ($case === 'libre') { $bad[0]['libre'] = true; }
        if ($case === 'type') { $bad[0]['multiple'] = 'oui'; }
        if ($case === 'id') { $bad[0]['id'] = 'réparé'; }
        try { R::catalogue($bad); $checks['refus_'.$case] = false; }
        catch (InvalidArgumentException) { $checks['refus_'.$case] = true; }
    }
    $utf = $q; $utf[0]['titre'] = str_repeat('é', 150);
    $checks['utf8_caracteres'] = R::catalogue($utf) === $utf;
}
if ($checks['regles_presentes']) {
    $checks['transition_presente'] = method_exists(R::class, 'repondre');
    if ($checks['transition_presente']) {
        $now = '2026-11-26T17:00:00Z'; $later = '2026-11-26T17:01:00Z';
        $on = R::repondre($q, [], ['situation-fictive'=>['reveur-fictif']], $now);
        $checks['etiquette_datee'] = $on === ['situation-fictive'=>['choix'=>['reveur-fictif'],'date_utc'=>$now]];
        $checks['inchangement_garde_date'] = R::repondre($q, $on, ['situation-fictive'=>['reveur-fictif']], $later) === $on;
        $checks['effacer_reponses'] = R::repondre($q, $on, [], $later) === [];
        $checks['retire_non_reattribue'] = R::repondre([], $on, [], $later) === $on;
        foreach ([['situation-fictive'=>['inconnu']], ['autre'=>[]], ['situation-fictive'=>['reveur-fictif','explorateur-fictif']], ['situation-fictive'=>'libre']] as $i=>$bad) {
            try { R::repondre($q, $on, $bad, $later); $checks['choix_refuse_'.$i] = false; }
            catch (InvalidArgumentException) { $checks['choix_refuse_'.$i] = true; }
        }
        $checks['effacer_tout_historique'] = R::repondre([], $on, [], $later, true) === [];
        foreach ([false,true] as $consent) { foreach ([false,true] as $newsletter) { foreach ([false,true] as $email) {
            $checks['conjonction_'.(int)$consent.(int)$newsletter.(int)$email] = R::transmissible(['accord'=>$consent,'date_utc'=>$now], $newsletter, $email) === ($consent && $newsletter && $email);
        } } }
        $checks['consentement_manquant_ferme'] = !R::transmissible([], true, true);
        $checks['consentement_malforme_ferme'] = !R::transmissible(['accord'=>true,'date_utc'=>'hier'], true, true);
    }
}
$bad = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>$bad], JSON_UNESCAPED_UNICODE);
exit($bad ? 1 : 0);
