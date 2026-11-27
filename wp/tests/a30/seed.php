<?php

declare(strict_types=1);

// Invoked only by the parent inside the disposable A02 fixture before its snapshot.
$product = new WC_Product_Subscription();
$product->set_name('A30_PRODUCT_PRIVATE_CANARY');
$product->set_regular_price('12.00');
$product->set_status('publish');
$product->save();
foreach (range(6, 10) as $number) {
    $email = sprintf('a13-fictif-%02d@example.org', $number);
    $id = wp_insert_user(['user_login' => 'a30-fictif-' . $number, 'user_email' => $email,
        'user_pass' => wp_generate_password(32), 'role' => 'customer',
        'display_name' => 'A30_PERSON_PRIVATE_CANARY']);
    if (is_wp_error($id)) {
        throw new RuntimeException('A30_FIXTURE_SEED_FAILED');
    }
}
echo 'A30_PRODUCT=' . $product->get_id() . "\n";
