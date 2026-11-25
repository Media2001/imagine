"""C15 guarded read-only native inspection; no secrets."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c15
c15.profils.guard('imagine-test-demo')
print(c15.wp(r'''$f=get_option('imagine_c09_fixture');$s=wcs_get_subscription($f['subscriptions']['A-PAPIER']);$p=new ReflectionClass($s);$methods=[];foreach(['payment_failed','payment_complete','get_dates','get_date_types','get_related_orders'] as $m){if($p->hasMethod($m)){$r=$p->getMethod($m);$lines=file($r->getFileName());$methods[$m]=implode('',array_slice($lines,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));}}$o=wc_get_order($f['orders']['A-VIR']);$r=new ReflectionMethod($o,'payment_complete');$lines=file($r->getFileName());$methods['order_payment_complete']=implode('',array_slice($lines,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));echo wp_json_encode(['ids'=>$f,'methods'=>$methods,'paper'=>[$s->get_status(),$s->get_data(),$s->get_requires_manual_renewal(),$s->get_payment_method()]]);'''))
