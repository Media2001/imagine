import sys
sys.dont_write_bytecode=True
import c31 as o
import b13
o.guard()
code='''$domains=['jetable-fictif.example.org','temporaire-fictif.example.org','usage-unique-fictif.example.org'];$old=get_option(Imagine\\Site\\DomainesRefuses::OPTION,null);if($old===null){update_option(Imagine\\Site\\DomainesRefuses::OPTION,$domains,false);}elseif($old!==$domains){throw new RuntimeException('Liste existante divergente');}echo wp_json_encode(Imagine\\Site\\DomainesRefuses::configuration());'''
a=o.wp(code);b=o.wp(code);assert a==b
b13.save(o,sys.argv[1],{'domains':a,'idempotent':True})
print(a)
