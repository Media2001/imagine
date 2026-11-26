"""Quatre questions manifestement inventées, aucune réponse de lecteur préremplie."""
import sys
sys.dont_write_bytecode = True
import c24

ROWS = [
    {'id':'situation-fictive','titre':'Situation entièrement fictive','multiple':False,'choix':[{'id':'reveur-fictif','titre':'Rêveur de nuages fictif'},{'id':'explorateur-fictif','titre':'Explorateur de lunes fictif'}]},
    {'id':'interets-fictifs','titre':'Centres d’intérêt entièrement fictifs','multiple':True,'choix':[{'id':'jardins-lunaires-fictifs','titre':'Jardins lunaires fictifs'},{'id':'cerfs-volants-fictifs','titre':'Cerfs-volants sous-marins fictifs'}]},
    {'id':'age-fictif','titre':'Tranche d’âge entièrement fictive','multiple':False,'choix':[{'id':'age-cent-lunes-fictif','titre':'De 100 à 199 lunes fictives'},{'id':'age-deux-cents-lunes-fictif','titre':'200 lunes fictives et plus'}]},
    {'id':'localite-fictive','titre':'Localité entièrement fictive','multiple':False,'choix':[{'id':'village-nuages-fictif','titre':'Village des nuages fictif'},{'id':'ile-lucioles-fictive','titre':'Île des lucioles fictive'}]},
]

def run(label):
    c24.guard();before=c24.state()
    old=c24.wp('echo wp_json_encode(get_option("imagine_personnalisation_questions",null));')
    assert old is None or old==ROWS,'Questions étrangères'
    value=c24.wp('$rows='+c24.php_json(ROWS)+';$clean=Imagine\\Site\\PersonnalisationReglages::nettoyer($rows);if($rows!==$clean)throw new RuntimeException("Questions refusées");update_option(Imagine\\Site\\Personnalisation::CATALOGUE,$rows,false);echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());')
    assert value==ROWS
    assert c24.wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());')==ROWS
    assert before==c24.state()
    c24.save(label,{'questions':value,'profiles_preserved':True})

if __name__=='__main__':run(sys.argv[1])
