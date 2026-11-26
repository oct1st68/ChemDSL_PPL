"""ChemDSL command line helper.

    python run.py gen            run ANTLR on grammar/Chem.g4 into CompiledFiles/
    python run.py test           run unittest discovery on tests/
    python run.py serve [port]   start Flask on 127.0.0.1 (default port 8770)
    python run.py repl           terminal REPL using chemdsl/formatter.py
"""
import os
import subprocess
import sys
import unittest

DIR = os.path.dirname(os.path.abspath(__file__))
# Course jar sits one level above this folder; ANTLR_JAR overrides it.
ANTLR_JAR = os.environ.get("ANTLR_JAR", os.path.join(DIR, "..", "antlr4-4.9.2-complete.jar"))
GRAMMAR_DIR = os.path.join(DIR, "grammar")
SRC = "Chem.g4"
CPL_DEST = os.path.join(DIR, "CompiledFiles")
DEFAULT_PORT = 8770


def generate():
    if not os.path.exists(ANTLR_JAR):
        sys.exit(f"ANTLR jar not found at {ANTLR_JAR}. Set ANTLR_JAR.")
    if not os.path.exists(os.path.join(GRAMMAR_DIR, SRC)):
        sys.exit(f"Missing {os.path.join(GRAMMAR_DIR, SRC)}.")
    os.makedirs(CPL_DEST, exist_ok=True)
    print("ANTLR is running...")
    result = subprocess.run(
        ["java", "-jar", ANTLR_JAR, "-o", CPL_DEST, "-visitor", "-no-listener",
         "-Dlanguage=Python3", SRC],
        cwd=GRAMMAR_DIR,
    )
    if result.returncode != 0:
        sys.exit("Generation failed.")
    print("Generated in", CPL_DEST)


def run_tests():
    sys.path.insert(0, DIR)
    suite = unittest.defaultTestLoader.discover(os.path.join(DIR, "tests"), top_level_dir=DIR)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def serve(port):
    sys.path.insert(0, DIR)
    from webapp.app import create_app
    print(f"ChemDSL on http://127.0.0.1:{port}")
    create_app().run(host="127.0.0.1", port=port, debug=False)


def repl():
    sys.path.insert(0, DIR)
    from chemdsl.interpreter import run
    from chemdsl.formatter import format_result
    print("ChemDSL REPL. Ctrl-D to quit.")
    while True:
        try:
            line = input("chem> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip():
            print(format_result(run(line)))


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "gen":
        generate()
    elif cmd == "test":
        run_tests()
    elif cmd == "serve":
        serve(int(argv[2]) if len(argv) > 2 else DEFAULT_PORT)
    elif cmd == "repl":
        repl()
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
