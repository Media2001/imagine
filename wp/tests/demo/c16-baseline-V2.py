"""Replay original C16 HTTP acceptance without overwriting historical receipts."""
from pathlib import Path
import importlib.util
import sys
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('c16_original_acceptance',Path(__file__).with_name('c16-http.py'))
recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)
original_save=recipe.c16.save
recipe.c16.save=lambda name,value:original_save(name if name.endswith('-V2') else name+'-V2',value)
if __name__=='__main__':sys.exit(recipe.run('http-base-V2'))
