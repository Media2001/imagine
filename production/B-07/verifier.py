"""Entrée canonique B07 ; l'ancien vérificateur est conservé sous nom historique."""
import runpy
from pathlib import Path

def verify():
    return runpy.run_path(str(Path(__file__).with_name('verifier-correction2141.py')))['verify']()

if __name__=='__main__':raise SystemExit(verify())
