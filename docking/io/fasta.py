from pathlib import Path

def _read_single_fasta(path: Path) -> str:
    text = path.read_text().splitlines()
    seq_lines = [ln.strip() for ln in text if ln.strip() and not ln.startswith(">")]
    if not seq_lines:
        raise ValueError(f"No sequence found in FASTA: {path}")
    return "".join(seq_lines)
