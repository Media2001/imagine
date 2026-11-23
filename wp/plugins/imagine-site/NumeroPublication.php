<?php
/** B01: a published/scheduled issue must have a real editorial release date. */
declare(strict_types=1);
namespace Imagine\Site;

final class NumeroPublication
{
    public static function valid(mixed $value): bool
    {
        if (!is_string($value) || !preg_match('/^\d{4}-\d{2}-\d{2}$/D', $value)) {
            return false;
        }
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value);
        return $date !== false && $date->format('Y-m-d') === $value;
    }

    public static function register(): void
    {
        add_action('init', static function (): void {
            register_post_meta('imagine_numero', 'imagine_sortie', [
                'type' => 'string', 'single' => true, 'show_in_rest' => true,
                'auth_callback' => static fn (): bool => current_user_can('edit_posts'),
            ]);
        }, 20);
        add_filter('wp_insert_post_data', [self::class, 'prepare'], 10, 2);
        add_filter('rest_pre_insert_imagine_numero', [self::class, 'rest'], 10, 2);
        add_filter('update_post_metadata', [self::class, 'update'], 10, 4);
        add_filter('delete_post_metadata', [self::class, 'delete'], 10, 5);
    }

    public static function prepare(array $data, array $postarr): array
    {
        if ($data['post_type'] !== 'imagine_numero' || !in_array($data['post_status'], ['publish', 'future'], true)) {
            return $data;
        }
        $date = $postarr['meta_input']['imagine_sortie'] ?? get_post_meta((int) ($postarr['ID'] ?? 0), 'imagine_sortie', true);
        if (!self::valid($date)) {
            // WP's insertion filter cannot return WP_Error. Fail closed to draft;
            // REST below supplies the explicit actionable error before insertion.
            $data['post_status'] = 'draft';
        }
        return $data;
    }

    public static function rest(mixed $prepared, \WP_REST_Request $request): mixed
    {
        if (is_wp_error($prepared)) {
            return $prepared;
        }
        $id = (int) ($prepared->ID ?? $request['id'] ?? 0);
        $status = $prepared->post_status ?? get_post_status($id);
        $meta = (array) $request->get_param('meta');
        $date = $meta['imagine_sortie'] ?? get_post_meta($id, 'imagine_sortie', true);
        if (in_array($status, ['publish', 'future'], true) && !self::valid($date)) {
            return new \WP_Error('imagine_sortie_required', __('Une date de sortie valide (AAAA-MM-JJ) est obligatoire pour publier un numéro.', 'imagine-site'), ['status' => 400]);
        }
        // Core writes REST metadata after the post: forward this pending value
        // to the native insertion guard, without writing any other field here.
        if (array_key_exists('imagine_sortie', $meta)) {
            $prepared->meta_input['imagine_sortie'] = $meta['imagine_sortie'];
        }
        return $prepared;
    }

    private static function published(int $id): bool
    {
        return get_post_type($id) === 'imagine_numero' && in_array(get_post_status($id), ['publish', 'future'], true);
    }

    public static function update(mixed $check, int $id, string $key, mixed $value): mixed
    {
        return $key === 'imagine_sortie' && self::published($id) && !self::valid($value) ? false : $check;
    }

    public static function delete(mixed $check, int $id, string $key, mixed $value, bool $all): mixed
    {
        return $key === 'imagine_sortie' && ($all || self::published($id)) ? false : $check;
    }
}
