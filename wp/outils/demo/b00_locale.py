"""Paquet officiel fr_FR, téléchargé par l'outil hôte, jamais via le site hors ligne."""
import hashlib
import io
import json
from pathlib import PurePosixPath
from urllib.request import urlopen
import zipfile


def install(builder):
    version = builder.wp('core', 'version')['stdout'].strip()
    url = 'https://downloads.wordpress.org/translation/core/' + version + '/fr_FR.zip'
    with urlopen(url, timeout=120) as response:
        package = response.read()
    files = {}
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        for name in archive.namelist():
            path = PurePosixPath(name)
            if len(path.parts) != 1 or 'fr_FR' not in name or path.suffix not in ('.po', '.mo', '.json', '.php'):
                raise ValueError('Paquet de langue inattendu : aucune extraction libre')
            data = archive.read(name)
            files[name] = hashlib.sha256(data).hexdigest()
            builder.upload('languages/' + name, data)
    code = '$names=json_decode(' + json.dumps(json.dumps(list(files))) + ',true);$out=[];foreach($names as $n){$p=WP_LANG_DIR . "/" . $n;if(str_ends_with($n,".php")){token_get_all(file_get_contents($p),TOKEN_PARSE);}$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    actual = json.loads(builder.wp('eval', code)['stdout'])
    if actual != files:
        raise RuntimeError('Paquet fr_FR téléversé divergent')
    builder.wp('option', 'update', 'WPLANG', 'fr_FR')
    if builder.wp('eval', 'echo get_locale();')['stdout'].strip() != 'fr_FR':
        raise RuntimeError('Locale fr_FR non relue')
    return {'source': url, 'sha256': hashlib.sha256(package).hexdigest(), 'files_sha256': actual, 'locale': 'fr_FR'}
