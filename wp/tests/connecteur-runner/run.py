"""Reuse the C-01 isolated bench without modifying its sources or evidence."""
import importlib.util
import sys

sys.dont_write_bytecode = True
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c01_bench', ROOT / 'wp/tests/numeros-runner/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
bench.PLUGIN = ROOT / 'wp/plugins/imagine-connecteur'
bench.OUT = ROOT / 'production/C-04/tests'
bench.STATE = bench.OUT / 'runner-state.json'
bench.LABEL = 'org.imagine.c04-runner'

if __name__ == '__main__':
    bench.main()
