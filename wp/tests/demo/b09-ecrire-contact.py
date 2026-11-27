"""B09 réemploie strictement le contrat corrigé, sans modifier les sources B08."""
from pathlib import Path
root = Path(__file__).resolve().parents[2]
p = root/'plugins/imagine-site'
for name in ['Sujet.php','SujetConfidentialite.php']:
    raw=(p/name).read_text(encoding='utf-8')
    raw=raw.replace('Sujet','Contact').replace('sujet','contact').replace('b08','b09').replace('B08','B09')
    raw=raw.replace('ContactRegles', 'SujetRegles')
    raw=raw.replace('Propositions de contacts','Messages de contact').replace('Proposition de contact','Message de contact')
    raw=raw.replace('Proposition enregistrée localement','Message enregistré localement')
    raw=raw.replace('proposition','demande de contact').replace('Proposition refusée','Demande refusée')
    raw=raw.replace("'texte' => 'Contact'", "'texte' => 'Message'")
    raw=raw.replace("__('Contact', 'imagine-site')", "__('Message', 'imagine-site')")
    raw=raw.replace('Proposer un contact','Enregistrer le message')
    raw=raw.replace('Cooperative::OPTION', "'imagine_b09_pages'")
    # Ne pas utiliser une clé de requête avec espaces après transformation rédactionnelle.
    raw=raw.replace("['demande de contact']", "['contact']").replace("add_query_arg('demande de contact'", "add_query_arg('contact'")
    out=p/name.replace('Sujet','Contact')
    assert not out.exists()
    out.write_text(raw,encoding='utf-8')
test=p/'tests/ContactAdapterTest.php'
raw=test.read_text(encoding='utf-8').replace("['Contact']", "['Message']")
test.write_text(raw,encoding='utf-8')
