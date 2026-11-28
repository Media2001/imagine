import sys
sys.dont_write_bytecode=True
import b16 as o
print(o.wp('global $wp_filter;$out=[];foreach(($wp_filter["shutdown"]->callbacks??[]) as $p=>$list){foreach($list as $row){$f=$row["function"];$out[]=["priority"=>$p,"function"=>is_array($f)?[is_object($f[0])?get_class($f[0]):$f[0],$f[1]]:(is_string($f)?$f:"Closure")];}}echo wp_json_encode($out);'))
