<?php

declare(strict_types=1);

// Mutation runtime temporaire : la déclaration privée du seul type B09 est inversée.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Mutation hors cible refusée');
}
add_filter('register_post_type_args', static function (array $args, string $type): array {
    if ($type === 'imagine_contact') {
        $args['public'] = true;
        $args['publicly_queryable'] = true;
        $args['exclude_from_search'] = false;
        $args['show_in_rest'] = true;
        $args['rest_base'] = 'imagine_contact';
    }
    return $args;
}, 1000, 2);
