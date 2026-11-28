<?php

declare(strict_types=1);

require '/opt/t01/imagine-site/vendor/autoload.php';
spl_autoload_register(static function(string $class):void{
    $prefix='Imagine\\Site\\';
    if(str_starts_with($class,$prefix)){
        $path='/repo/wp/plugins/imagine-site/'.str_replace('\\','/',substr($class,strlen($prefix))).'.php';
        if(is_file($path)){require_once $path;}
    }
},true,true);
