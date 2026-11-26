<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Demande seule : note Woo privée + événement C10 déterministe, dans la même transaction. */
final class Retractation
{
    public const OPTION = 'imagine_retractation_reglages';
    public const MANUELLE = '_imagine_retractation_debut';
    public const META = 'imagine_retractation';
    public const JOURNAL = 'imagine_reglages_journal_retractation_';

    public static function configuration(): array
    {
        return get_option(self::OPTION, ['jours' => 14, 'origine' => 'paiement']);
    }

    public static function commande(int $target, int $user): mixed
    {
        $order = wc_get_order($target);
        if (!$order || $user < 1 || $order->get_customer_id() !== $user) {
            return null;
        }
        if ($order->get_type() === 'shop_subscription') {
            $order = wc_get_order((int)$order->get_parent_id());
            if (!$order || (int)$order->get_customer_id() !== $user) {
                return null;
            }
        }
        return $order->get_type() === 'shop_order' ? $order : null;
    }

    public static function debut(mixed $order): ?int
    {
        $manual = self::dateManuelle((string)$order->get_meta(self::MANUELLE));
        return RetractationRegles::debut(self::configuration(), $order->get_date_paid()?->getTimestamp(), $manual);
    }

    public static function dateManuelle(string $value): ?int
    {
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value, new \DateTimeZone('UTC'));
        return $date && $date->format('Y-m-d') === $value ? $date->getTimestamp() : null;
    }

    public static function ouverte(mixed $order): bool
    {
        return RetractationRegles::ouverte(
            self::configuration(),
            $order->get_date_paid()?->getTimestamp(),
            self::dateManuelle((string)$order->get_meta(self::MANUELLE)),
            time()
        );
    }

    public static function lire(int $order): ?array
    {
        $event = get_option(self::JOURNAL . $order, null);
        if ($event === null) {
            return null;
        }
        if (!is_array($event) || !is_array($event['apres'] ?? null)) {
            throw new \RuntimeException('Trace de rétractation illisible.');
        }
        $record = $event['apres'];
        $record['raison'] = '';
        $record['compte'] = (int)($event['qui_id'] ?? 0);
        if (!empty($record['note'])) {
            $meta = get_comment_meta((int)$record['note'], self::META, true);
            if (is_array($meta)) {
                $record = $meta;
            }
        }
        return $record;
    }

    public static function demander(int $target, int $user, string $confirmation, string $reason): array|\WP_Error
    {
        $order = self::commande($target, $user);
        if (!$order || $confirmation !== 'confirmer') {
            return new \WP_Error('imagine_retractation_refus', __('Confirmation ou titulaire invalide.', 'imagine-site'));
        }
        global $wpdb;
        $id = (int)$order->get_id();
        $key = self::JOURNAL . $id;
        $lock = 'imagine_retractation_' . $id;
        if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            return new \WP_Error('imagine_retractation_occupee', __('Demande en cours : réessayez.', 'imagine-site'));
        }
        $note = 0;
        $transaction = false;
        try {
            self::invalider($key);
            $existing = self::lire($id);
            if ($existing !== null) {
                return $existing;
            }
            // Recontrôle sous verrou, y compris pour un POST direct à l'étape 2.
            $order = self::commande($target, $user);
            if (!$order || !self::ouverte($order)) {
                return new \WP_Error('imagine_retractation_delai', __('Demande refusée : délai dépassé ou date absente.', 'imagine-site'));
            }
            if ($wpdb->query('START TRANSACTION') === false) {
                throw new \RuntimeException('Transaction indisponible.');
            }
            $transaction = true;
            $record = ['commande' => $id, 'compte' => $user, 'date' => gmdate('Y-m-d\TH:i:s\Z', time()),
                'raison' => sanitize_textarea_field($reason)];
            $note = (int)$order->add_order_note(
                sprintf(__('Demande de rétractation reçue le %s. Aucun effet automatique.', 'imagine-site'), $record['date']),
                false
            );
            $record['note'] = $note;
            if (!$note || !add_comment_meta($note, self::META, wp_slash($record), true)
                || get_comment_meta($note, self::META, true) !== $record) {
                throw new \RuntimeException('Note non persistée.');
            }
            $event = ['quand_utc' => $record['date'], 'qui_id' => $user, 'qui_login' => wp_get_current_user()->user_login,
                'option' => 'imagine_retractation', 'avant' => null,
                'apres' => ['commande' => $id, 'date' => $record['date'], 'note' => $note]];
            if (!add_option($key, $event, '', false) || get_option($key) !== $event) {
                throw new \RuntimeException('Journal non persisté.');
            }
            if ($wpdb->query('COMMIT') === false) {
                throw new \RuntimeException('Validation indisponible.');
            }
            $transaction = false;
            return $record;
        } catch (\Throwable) {
            if ($transaction) {
                $wpdb->query('ROLLBACK');
            }
            self::invalider($key);
            if ($note) {
                clean_comment_cache($note);
                wp_cache_delete($note, 'comment_meta');
            }
            return new \WP_Error('imagine_retractation_stockage', __('Enregistrement impossible : aucune confirmation, réessayez.', 'imagine-site'));
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    public static function register(): void
    {
        add_action('woocommerce_account_dashboard', static function (): void {
            if (isset($_GET['imagine_retractation']) && is_scalar($_GET['imagine_retractation'])) {
                echo self::panneau((int)$_GET['imagine_retractation'], wp_unslash($_POST));
            }
        }, 5);
        add_action('woocommerce_view_order', [self::class, 'entree']);
        add_action('woocommerce_subscription_details_after_subscription_table', static function ($subscription): void {
            self::entree((int)$subscription->get_id());
        });
        add_filter('woocommerce_my_account_my_orders_actions', static function (array $actions, $order): array {
            $owned = self::commande((int)$order->get_id(), get_current_user_id());
            if ($owned && self::ouverte($owned)) {
                $actions['imagine_retractation'] = ['url' => self::url((int)$order->get_id()), 'name' => __('Me rétracter', 'imagine-site')];
            }
            return $actions;
        }, 30, 2);
        add_action('admin_menu', static function (): void {
            add_submenu_page('imagine', __('Demandes de rétractation', 'imagine-site'), __('Rétractations', 'imagine-site'),
                'manage_options', 'imagine-retractations', [self::class, 'administration']);
        });
    }

    public static function url(int $target): string
    {
        return add_query_arg('imagine_retractation', $target, wc_get_page_permalink('myaccount'));
    }

    public static function entree(int $target): void
    {
        $order = self::commande($target, get_current_user_id());
        if (!$order) {
            return;
        }
        try {
            $receipt = self::lire((int)$order->get_id());
            if ($receipt !== null) {
                echo self::accuse($receipt);
            } elseif (self::ouverte($order)) {
                echo '<p><a class="button" href="' . esc_url(self::url($target)) . '">' . esc_html__('Me rétracter', 'imagine-site') . '</a></p>';
            }
        } catch (\Throwable) {
            echo '<p>' . esc_html__('Demandes temporairement indisponibles.', 'imagine-site') . '</p>';
        }
    }

    public static function accuse(array $record): string
    {
        return '<section class="imagine-retractation-accuse"><h2>' . esc_html__('Accusé de réception', 'imagine-site')
            . '</h2><p>' . esc_html(sprintf(__('Demande reçue le %s pour la commande n°%d.', 'imagine-site'), $record['date'], $record['commande']))
            . '</p><p>' . esc_html__('La demande est enregistrée. Aucun remboursement, aucune annulation et aucun accès fermé automatiquement.', 'imagine-site')
            . '</p></section>';
    }

    public static function panneau(int $target, array $post): string
    {
        $order = self::commande($target, get_current_user_id());
        $refus = '<p role="alert">' . esc_html__('Demande refusée : titulaire, confirmation ou délai invalide.', 'imagine-site') . '</p>';
        if (!$order) {
            return $refus;
        }
        try {
            $receipt = self::lire((int)$order->get_id());
            if ($receipt !== null) {
                return self::accuse($receipt);
            }
        } catch (\Throwable) {
            return $refus;
        }
        if (!self::ouverte($order)) {
            return $refus;
        }
        foreach (['etape', '_c25', 'raison', 'confirmation'] as $key) {
            if (isset($post[$key]) && !is_string($post[$key])) {
                return $refus;
            }
        }
        $step = $post['etape'] ?? '';
        $reason = sanitize_textarea_field($post['raison'] ?? '');
        if (strlen($reason) > 8000) {
            return $refus;
        }
        $action = 'imagine_c25_' . $target;
        $confirmAction = $action . '_confirmer_' . hash('sha256', $reason);
        if ($post !== [] && !in_array($step, ['preparer', 'confirmer'], true)) {
            return $refus;
        }
        if ($step !== '' && !wp_verify_nonce($post['_c25'] ?? '', $step === 'preparer' ? $action : $confirmAction)) {
            return $refus;
        }
        if ($step === 'confirmer') {
            $result = self::demander($target, get_current_user_id(), $post['confirmation'] ?? '', $reason);
            return is_wp_error($result) ? $refus : self::accuse($result);
        }
        $start = self::debut($order);
        $end = $start + self::configuration()['jours'] * 86400;
        $html = '<section id="imagine-retractation"><h2>' . esc_html__('Me rétracter', 'imagine-site') . '</h2><p>'
            . esc_html(sprintf(__('Commande n°%d — début du délai : %s UTC ; fin : %s UTC.', 'imagine-site'), $order->get_id(), gmdate('Y-m-d H:i:s', $start), gmdate('Y-m-d H:i:s', $end)))
            . '</p><p>' . esc_html__('Cette démarche enregistre seulement une demande. Aucune conséquence financière ni sur vos accès.', 'imagine-site') . '</p>';
        $html .= '<form method="post" action="' . esc_url(self::url($target)) . '">';
        if ($step === 'preparer') {
            $html .= '<h3>' . esc_html__('Étape 2 sur 2 — confirmation', 'imagine-site') . '</h3><p>' . esc_html($reason)
                . '</p><input type="hidden" name="raison" value="' . esc_attr($reason) . '">'
                . '<input type="hidden" name="etape" value="confirmer">'
                . '<input type="hidden" name="_c25" value="' . esc_attr(wp_create_nonce($confirmAction)) . '">'
                . '<button type="submit" name="confirmation" value="confirmer">' . esc_html__('Confirmer ma demande de rétractation', 'imagine-site') . '</button>';
        } else {
            $html .= '<h3>' . esc_html__('Étape 1 sur 2 — votre demande', 'imagine-site') . '</h3>'
                . '<input type="hidden" name="etape" value="preparer">'
                . '<input type="hidden" name="_c25" value="' . esc_attr(wp_create_nonce($action)) . '">'
                . '<p><label for="imagine-c25-raison">' . esc_html__('Motif (facultatif)', 'imagine-site')
                . '</label><textarea id="imagine-c25-raison" name="raison" maxlength="2000"></textarea></p>'
                . '<button type="submit">' . esc_html__('Continuer', 'imagine-site') . '</button>';
        }
        return $html . ' <a href="' . esc_url($order->get_view_order_url()) . '">' . esc_html__('Abandonner', 'imagine-site') . '</a></form></section>';
    }

    public static function administration(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'), '', ['response' => 403]);
        }
        echo '<div class="wrap"><h1>' . esc_html__('Demandes de rétractation — aucune action automatique', 'imagine-site') . '</h1>';
        $rows = RetractationConfidentialite::lignes();
        if (is_wp_error($rows)) {
            echo '<p role="alert">' . esc_html__('Lecture impossible : réessayez.', 'imagine-site') . '</p></div>';
            return;
        }
        echo '<table class="widefat"><thead><tr><th>' . esc_html__('Date UTC', 'imagine-site') . '</th><th>'
            . esc_html__('Commande', 'imagine-site') . '</th><th>' . esc_html__('Motif facultatif', 'imagine-site') . '</th></tr></thead><tbody>';
        foreach ($rows as $row) {
            $order = wc_get_order((int)$row['commande']);
            $url = $order ? $order->get_edit_order_url() : '';
            echo '<tr><td>' . esc_html($row['date']) . '</td><td><a href="' . esc_url($url) . '">#'
                . (int)$row['commande'] . '</a></td><td>' . esc_html($row['raison']) . '</td></tr>';
        }
        echo '</tbody></table></div>';
    }

    private static function invalider(string $key): void
    {
        wp_cache_delete($key, 'options');
        wp_cache_delete('alloptions', 'options');
        wp_cache_delete('notoptions', 'options');
    }
}
