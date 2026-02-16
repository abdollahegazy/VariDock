"""Tests for AF3MSAMerger."""

import json
import pytest
from pathlib import Path

from varidock.types import AF3MSAOutput,  Ligand
from varidock.stages.alphafold3.merger import AF3MSAMerger, AF3MSAMergerConfig


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Output directory for merged JSONs."""
    return tmp_path / "complexes"


@pytest.fixture
def merger(tmp_output: Path) -> AF3MSAMerger:
    """Merger with default config."""
    return AF3MSAMerger(AF3MSAMergerConfig(output_dir=tmp_output, seed=42))


def _make_monomer_json(
    tmp_path: Path, protein_id: str, chain_id: str, sequence: str
) -> AF3MSAOutput:
    """Helper: write a fake AF3 monomer data JSON and return an AF3MSAOutput."""
    data = {
        "sequences": [
            {
                "protein": {
                    "id": [chain_id],
                    "sequence": sequence,
                    "unpairedMsa": f"unpaired_msa_for_{protein_id}",
                    "pairedMsa": f"paired_msa_for_{protein_id}",
                    "templates": [{"template_id": f"tmpl_{protein_id}"}],
                    "modifications": [],
                }
            }
        ]
    }
    json_path = tmp_path / protein_id / f"{protein_id}_data.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data))

    return AF3MSAOutput(
        data_json_path=json_path,
        protein_id=protein_id,
        chain_id=chain_id,
    )


# --- Basic functionality ---


class TestMergerDimer:
    """Test merging two monomer MSAs into a dimer."""

    def test_dimer_no_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")
        msa_b = _make_monomer_json(tmp_path, "AT3G23050", "C", "ARNDQ")

        result = merger.run(msa_outputs=[msa_a, msa_b])

        assert result.json_path.exists()
        assert result.name == "at3g62980_at3g23050"

        payload = json.loads(result.json_path.read_text())
        assert len(payload["sequences"]) == 2
        assert payload["sequences"][0]["protein"]["id"] == ["F"]
        assert payload["sequences"][1]["protein"]["id"] == ["C"]
        assert payload["sequences"][0]["protein"]["sequence"] == "MKVLF"
        assert payload["sequences"][1]["protein"]["sequence"] == "ARNDQ"
        assert payload["modelSeeds"] == [42]
        assert payload["dialect"] == "alphafold3"
        assert payload["version"] == 1

    def test_dimer_with_ccd_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")
        msa_b = _make_monomer_json(tmp_path, "AT3G23050", "C", "ARNDQ")
        ligand = Ligand(name="auxin", ccd="IAC", af3_sequence_id="L")

        result = merger.run(msa_outputs=[msa_a, msa_b], ligands=[ligand])

        payload = json.loads(result.json_path.read_text())
        assert len(payload["sequences"]) == 3
        assert payload["sequences"][2]["ligand"]["id"] == ["L"]
        assert payload["sequences"][2]["ligand"]["ccdCodes"] == ["IAC"]
        assert result.name == "at3g62980_at3g23050_auxin"

    def test_dimer_with_smiles_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")
        msa_b = _make_monomer_json(tmp_path, "AT3G23050", "C", "ARNDQ")
        ligand = Ligand(name="custom", smiles="CC(=O)O", af3_sequence_id="X")

        result = merger.run(msa_outputs=[msa_a, msa_b], ligands=[ligand])

        payload = json.loads(result.json_path.read_text())
        assert payload["sequences"][2]["ligand"]["smiles"] == "CC(=O)O"
        assert "ccdCodes" not in payload["sequences"][2]["ligand"]


# --- MSA field propagation ---


class TestMSAFieldPropagation:
    """Verify that MSA and template fields are correctly copied."""

    def test_unpaired_msa_copied(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")

        result = merger.run(msa_outputs=[msa_a])
        payload = json.loads(result.json_path.read_text())

        assert (
            payload["sequences"][0]["protein"]["unpairedMsa"]
            == "unpaired_msa_for_PROT_A"
        )

    def test_paired_msa_copied(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")

        result = merger.run(msa_outputs=[msa_a])
        payload = json.loads(result.json_path.read_text())

        assert (
            payload["sequences"][0]["protein"]["pairedMsa"] == "paired_msa_for_PROT_A"
        )

    def test_templates_copied(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")

        result = merger.run(msa_outputs=[msa_a])
        payload = json.loads(result.json_path.read_text())

        assert payload["sequences"][0]["protein"]["templates"] == [
            {"template_id": "tmpl_PROT_A"}
        ]

    def test_modifications_copied(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")

        result = merger.run(msa_outputs=[msa_a])
        payload = json.loads(result.json_path.read_text())

        assert payload["sequences"][0]["protein"]["modifications"] == []

    def test_missing_msa_fields_become_none(self, tmp_path: Path, merger: AF3MSAMerger):
        """If monomer JSON has no MSA fields, they should be None in output."""
        data = {
            "sequences": [
                {
                    "protein": {
                        "id": ["A"],
                        "sequence": "MKVLF",
                    }
                }
            ]
        }
        json_path = tmp_path / "bare" / "bare_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(data))

        msa = AF3MSAOutput(data_json_path=json_path, protein_id="bare", chain_id="A")
        result = merger.run(msa_outputs=[msa])
        payload = json.loads(result.json_path.read_text())

        assert payload["sequences"][0]["protein"]["unpairedMsa"] is None
        assert payload["sequences"][0]["protein"]["pairedMsa"] is None
        assert payload["sequences"][0]["protein"]["templates"] is None


# --- N-mer support ---


class TestNMerSupport:
    """Test support for arbitrary chain counts."""

    def test_monomer(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = _make_monomer_json(tmp_path, "SINGLE", "A", "MKVLF")
        result = merger.run(msa_outputs=[msa])

        payload = json.loads(result.json_path.read_text())
        assert len(payload["sequences"]) == 1

    def test_trimer(self, tmp_path: Path, merger: AF3MSAMerger):
        msas = [
            _make_monomer_json(tmp_path, f"PROT_{c}", c, "MKVLF")
            for c in ["A", "B", "C"]
        ]
        result = merger.run(msa_outputs=msas)

        payload = json.loads(result.json_path.read_text())
        assert len(payload["sequences"]) == 3
        assert result.name == "prot_a_prot_b_prot_c"

    def test_trimer_with_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msas = [
            _make_monomer_json(tmp_path, f"PROT_{c}", c, "MKVLF")
            for c in ["A", "B", "C"]
        ]
        ligand = Ligand(name="mol", ccd="MOL", af3_sequence_id="L")
        result = merger.run(msa_outputs=msas, ligands=[ligand])

        payload = json.loads(result.json_path.read_text())
        assert len(payload["sequences"]) == 4


# --- Multiple ligands ---


class TestMultipleLigands:
    """Test support for multiple ligands."""

    def test_two_ligands(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")
        ligands = [
            Ligand(name="lig1", ccd="L1C", af3_sequence_id="L"),
            Ligand(name="lig2", ccd="L2C", af3_sequence_id="M"),
        ]

        result = merger.run(msa_outputs=[msa], ligands=ligands)
        payload = json.loads(result.json_path.read_text())

        assert len(payload["sequences"]) == 3
        assert payload["sequences"][1]["ligand"]["ccdCodes"] == ["L1C"]
        assert payload["sequences"][2]["ligand"]["ccdCodes"] == ["L2C"]
        assert result.name == "prot_a_lig1_lig2"


# --- Naming ---


class TestNaming:
    """Test auto-generated and explicit naming."""

    def test_auto_name_no_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msa_a = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")
        msa_b = _make_monomer_json(tmp_path, "AT3G23050", "C", "ARNDQ")

        result = merger.run(msa_outputs=[msa_a, msa_b])
        assert result.name == "at3g62980_at3g23050"

    def test_auto_name_with_ligand(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")
        ligand = Ligand(name="auxin", ccd="IAC", af3_sequence_id="L")

        result = merger.run(msa_outputs=[msa], ligands=[ligand])
        assert result.name == "at3g62980_auxin"

    def test_explicit_name(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")

        result = merger.run(msa_outputs=[msa], name="my_custom_job")
        assert result.name == "my_custom_job"

    def test_output_path_matches_name(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = _make_monomer_json(tmp_path, "AT3G62980", "F", "MKVLF")

        result = merger.run(msa_outputs=[msa], name="test_job")
        assert result.json_path.parent.name == "test_job"
        assert result.json_path.name == "test_job.json"


# --- Error handling ---


class TestErrorHandling:
    """Test validation and error cases."""

    def test_empty_msa_outputs_raises(self, merger: AF3MSAMerger):
        with pytest.raises(ValueError, match="At least one MSA output"):
            merger.run(msa_outputs=[])

    def test_missing_data_json_raises(self, tmp_path: Path, merger: AF3MSAMerger):
        msa = AF3MSAOutput(
            data_json_path=tmp_path / "nonexistent" / "data.json",
            protein_id="MISSING",
            chain_id="A",
        )
        with pytest.raises(FileNotFoundError):
            merger.run(msa_outputs=[msa])

    def test_no_protein_entry_raises(self, tmp_path: Path, merger: AF3MSAMerger):
        """JSON with no protein sequence entry should raise."""
        data = {"sequences": [{"ligand": {"id": ["L"], "ccdCodes": ["IAC"]}}]}
        json_path = tmp_path / "bad" / "bad_data.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(data))

        msa = AF3MSAOutput(data_json_path=json_path, protein_id="bad", chain_id="A")
        with pytest.raises(ValueError, match="No protein entry"):
            merger.run(msa_outputs=[msa])

    def test_ligand_with_both_smiles_and_ccd_raises(
        self, tmp_path: Path, merger: AF3MSAMerger
    ):
        msa = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")
        ligand = Ligand(name="bad", smiles="CC", ccd="BAD", af3_sequence_id="L")

        with pytest.raises(ValueError, match="cannot have both"):
            merger.run(msa_outputs=[msa], ligands=[ligand])

    def test_ligand_without_sequence_id_raises(
        self, tmp_path: Path, merger: AF3MSAMerger
    ):
        msa = _make_monomer_json(tmp_path, "PROT_A", "A", "MKVLF")
        ligand = Ligand(name="bad", ccd="BAD", af3_sequence_id=None)

        with pytest.raises(ValueError, match="must have an AF3 sequence ID"):
            merger.run(msa_outputs=[msa], ligands=[ligand])
