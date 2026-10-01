import sys

from .bot import run

run(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
