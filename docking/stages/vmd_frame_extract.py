from dataclasses import dataclass
from pathlib import Path
import subprocess

from docking.pipeline.types import Trajectory, ConformationSet, PDB
from docking.pipeline.stage import Stage
from docking.execution.utils import run_with_interrupt

@dataclass
class VMDFrameExtractionConfig:
    output_dir: Path
    # add more as needed


class VMDFrameExtraction(Stage[Trajectory, ConformationSet]):
    name = "vmd_frame_extraction"
    input_type = Trajectory
    output_type = ConformationSet

    def __init__(self, config: VMDFrameExtractionConfig):
        self.config = config

    def run(self, input: Trajectory) -> ConformationSet:
        # 1. Load PSF
        # 2. Load each .coor file as a frame
        # 3. Select protein atoms
        # 4. Write each frame as PDB
        # 5. Return ConformationSet with list of PDBs

        
        tcl = f"""
            set molid [mol new "{input.psf}"]
            mol addfile {input.pdb} $molid
            """
        
        for coor in input.coor_files:
            tcl += f'mol addfile "{coor}" $molid\n'
        
        tcl += f"""
        package require topotools
        set prot [atomselect $molid "protein"]
        topo -molid $molid -sel $prot guessatom element mass            

        $prot writepsf {self.config.output_dir}/protein.psf

        set numframes [molinfo top get numframes]
        for {{set i 0}} {{$i < $numframes}} {{incr i}} {{
            $prot frame $i
            $prot writepdb {self.config.output_dir}/protein_conf$i.pdb
        }}
        $prot delete
        mol delete $molid
        exit
        """

        script_path = self.config.output_dir / "frame_extraction.tcl"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(tcl)

        with open(self.config.output_dir / "vmd_frame_extraction.log", "w") as f:
            run_with_interrupt(
                ["vmd", "-dispdev", "none", "-eofexit", "-e", str(script_path)], 
                stdout=f, 
                stderr=subprocess.STDOUT)
            
        pdb_files = sorted(self.config.output_dir.glob("protein_conf*.pdb"))
        return ConformationSet(
            psf=self.config.output_dir / "protein.psf",
            pdbs=[PDB(path=p) for p in pdb_files],
        )
    




