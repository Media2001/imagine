"""Reuse A04 public preparation, redirected strictly to A08-owned files."""
import importlib.util
import pathlib
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a04_public',ROOT.parent/'a04/prepare_public.py')
prepare=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)
prepare.OUT=ROOT.parents[2]/'production/A-08/dependances'
prepare.SOURCES={name:metadata for name,metadata in prepare.SOURCES.items() if name in ['wordpress-7.0.zip','woocommerce-11.0.1.zip']}
if __name__=='__main__':sys.exit(prepare.main())
