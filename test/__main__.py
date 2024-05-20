from .. import assembler
import shutil
import pathlib
import subprocess
import inspect
import sys

if __name__ == "__main__":
    n2tas = shutil.which("Assembler.sh")
    if n2tas is None:
        print("Assembler.sh must be included in PATH"
              "(part of the Nand2Tetris suite.)")
        sys.exit(1)

    test_dir = pathlib.Path(inspect.getfile(inspect.currentframe())).parent
    asm_files = test_dir.joinpath("asm").glob("*.asm")
    for f in asm_files:
        subprocess.run([n2tas, f], stdout=subprocess.DEVNULL)
        with f.open() as infile, f.with_suffix(".phack").open("w") as outfile:
            outfile.writelines(assembler.assemble(infile.readlines()))

        hack_files = [f.with_suffix(".hack"), f.with_suffix(".phack")]
        if subprocess.run(["diff", *hack_files]).returncode:
            print("Assembly output differs on file", f)
            sys.exit(1)
