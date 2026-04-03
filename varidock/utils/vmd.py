# fix this idk what the workaround is bc i dont wanna need vmd py blehhhh
# import sys

# sys.path.append("/home/abdolla/anaconda3/lib/python3.12/site-packages")
# sys.path.append("/tank/abdolla/plafp/analysis")

# vmd -dispdev text -python -e "$1" "${@:2}"
from typing import Any

from pathlib import Path
import subprocess


# def _run_vmd(script: str, *args) -> Any:

#     cmd = """vmd -dispdev text -python -e""" # "$1" "${@:2}"""
#     script_path = Path(__file__).parent / "_vmd_scripts" / script
#     result = subprocess.run(
#         [cmd, str(script_path), *[str(a) for a in args]],
#         capture_output=True,
#         text=True
#     )
#     if result.returncode != 0:
#         raise RuntimeError(f"VMD error: {result.stderr}")
#     return result.stdout.strip()

def rmsd_align(
    moving_pdb: Path, reference_pdb: Path, moving_sel: str, reference_sel: str
) -> None:
    """
    Aligns the entire moving pdb to the reference pdb based on the specified atom selections, using RMSD minimization.

    Parameters:
    - moving_pdb (Path): Path to the PDB file of the structure to be aligned (the "moving" structure).
    - reference_pdb (Path): Path to the PDB file of the reference structure to which the moving structure will be aligned.
    - moving_sel (str): VMD atom selection string specifying the subset of atoms in the moving structure to use for alignment (e.g., "name CA" to select alpha carbons).
    - reference_sel (str): VMD atom selection string specifying the subset of atoms in the reference structure to use for alignment (e.g., "name CA" to select alpha carbons).
    """
    try:
        from vmd import molecule, atomsel, measure  # type: ignore
    except ImportError:
        raise ImportError(
            "This function requires vmd-python. Run with vmd's Python interpreter."
        )

    moving_id = molecule.load("pdb", str(moving_pdb))
    reference_id = molecule.load("pdb", str(reference_pdb))

    ref = atomsel(reference_sel, molid=reference_id)
    mov = atomsel(moving_sel, molid=moving_id)

    all_moving = atomsel("all", molid=moving_id)
    all_moving.move(measure.fit(mov, ref))
