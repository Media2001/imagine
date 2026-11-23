<?php

declare(strict_types=1);

namespace Imagine\Theme;
?>
<form role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
    <p><label for="imagine-search"><?php esc_html_e('Rechercher dans les contenus', 'imagine'); ?></label></p>
    <p><input type="search" id="imagine-search" name="s" value="<?php echo esc_attr(get_search_query(false)); ?>">
        <button type="submit"><?php esc_html_e('Rechercher', 'imagine'); ?></button></p>
</form>
