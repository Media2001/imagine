"""C17 real native HTTP acceptance; target guard in c17_http.run."""
import sys
sys.dont_write_bytecode=True
if __name__=='__main__':
    from c17_http import run
    sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'http-final'))
