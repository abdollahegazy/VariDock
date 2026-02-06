from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

from docking.pipeline.types import PDB, NAMDSimulationDir
from docking.pipeline.stage import Stage
from docking.execution.utils import run_with_interrupt

@dataclass(frozen=True)
class VMDEquilPrepConfig:
    toppar_dir: Path
    # contains eq.namd, eq2.namd, run.namd templates
    template_dir: Path  
    output_dir: Path
    # add more as needed



class VMDEquilPrep(Stage[PDB, NAMDSimulationDir]):
    name = "vmd_equil_prep"
    input_type = PDB
    output_type = NAMDSimulationDir

    def __init__(self, config: VMDEquilPrepConfig):
        self.config = config

    def run(self, input: PDB) -> NAMDSimulationDir:
        # 1. psfgen - build PSF/PDB
        # 2. solvate - add water box
        # 3. autoionize - add ions
        # 4. write system files (psf, pdb, xsc)
        # 5. create restraint files from pLDDT
        # 6. copy NAMD config templates

        tcl_header = """
        package require psfgen
        package require solvate
        package require autoionize
        package require pbctools
        """

        tcl_solvate_and_ionize = f"""
        resetpsf
        topology {self.config.toppar_dir}/top_all36_prot.rtf
        pdbalias residue HIS HSE
        pdbalias atom ILE CD1 CD
        segment P {{pdb {input.path}}}
        coordpdb {input.path} P
        guesscoord
        writepsf {self.config.output_dir}/{input.path.stem}.psf
        writepdb {self.config.output_dir}/{input.path.stem}.pdb


        solvate {self.config.output_dir}/{input.path.stem}.psf {self.config.output_dir}/{input.path.stem}.pdb -o {self.config.output_dir}/solvated -t 10
        autoionize -psf {self.config.output_dir}/solvated.psf -pdb {self.config.output_dir}/solvated.pdb -sc 0.15 -o {self.config.output_dir}/ionized
        """

        tcl_write_system = f"""
        mol new {input.path}
        set prot_ca [atomselect top "protein and name CA"]

        set molid [mol new {self.config.output_dir}/ionized.psf]
        mol addfile {self.config.output_dir}/ionized.pdb $molid

        animate write pdb {self.config.output_dir}/system.pdb
        animate write psf {self.config.output_dir}/system.psf
        pbc writexst {self.config.output_dir}/system.xsc
        """
        

        tcl_beta_columns = f"""
        set betas [$prot_ca get beta]
        set resids [$prot_ca get resid]
        for {{set i 0}} {{$i < [llength $betas]}} {{incr i}} {{
            set prot2 [atomselect top "protein and resid [lindex $resids $i]"]
            $prot2 set beta [lindex $betas $i]
            $prot2 delete
        }}
        $prot_ca delete

        set all [atomselect top "all"]
        set sel [atomselect top "protein and name N C O CA CB"]
        set sel2 [atomselect top "protein and beta > 0.7 and name N C O CA CB"]

        $all set beta 0
        $sel set beta 1
        animate write pdb {self.config.output_dir}/restrain.pdb
        
        $all set beta 0
        $sel2 set beta 1
        animate write pdb {self.config.output_dir}/restrain2.pdb

        $sel2 delete
        $sel delete
        $all delete

        foreach m [molinfo list] {{ mol delete $m}}

        exit
        """

        tcl_script = tcl_header + tcl_solvate_and_ionize + tcl_write_system + tcl_beta_columns

        script_path = self.config.output_dir / "prep.tcl"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(tcl_script)

        # run_with_interrupt(["vmd", "-dispdev", "none", "-eofexit", "-e", str(script_path)])
        with open(self.config.output_dir / "vmd_prep.log", "w") as f:
            run_with_interrupt(
                ["vmd", "-dispdev", "text", "-eofexit", "-e", str(script_path)],
                stdout=f,
                stderr=subprocess.STDOUT
            )
        shutil.copytree(self.config.toppar_dir, self.config.output_dir / "toppar", dirs_exist_ok=True)
        shutil.copy(self.config.template_dir / "eq.namd", self.config.output_dir)
        shutil.copy(self.config.template_dir / "eq2.namd", self.config.output_dir)
        shutil.copy(self.config.template_dir / "run.namd", self.config.output_dir)

        for sh_file in ["eq.sh", "eq2.sh", "run.sh"]:
            src = self.config.template_dir / sh_file
            dst = self.config.output_dir / sh_file
            content = src.read_text()
            content = content.replace("DUMMY_NAME", input.path.stem)
            dst.write_text(content)
            

        intermediate_files = [
            f"{input.path.stem}.psf",
            f"{input.path.stem}.pdb",
            "solvated.psf",
            "solvated.pdb",
            "solvated.log",
            "ionized.psf",
            "ionized.pdb",
            "ionized.log",
            "prep.tcl",
        ]
        for f in intermediate_files:
            path = self.config.output_dir / f
            if path.exists():
                path.unlink()
        return NAMDSimulationDir(path=self.config.output_dir)