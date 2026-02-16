"""Reads FASTA files and extracts the sequence information. The main function, `_read_single_fasta`, takes a file path as input, reads the contents of the FASTA file, and returns the concatenated sequence as a string. It handles cases where the FASTA file may contain multiple lines for the sequence and ensures that only valid sequence lines are included in the final output. If no sequence is found in the provided FASTA file, it raises a ValueError to alert the user."""
# varidock/io/fasta.py
from pathlib import Path

def _read_single_fasta(path: Path) -> str:
    """Read a single-sequence FASTA file and return the sequence as a string. The function ignores header lines (starting with '>') and concatenates all sequence lines into a single string. If the FASTA file does not contain any valid sequence lines, it raises a ValueError.
    
    :param path: Path to the FASTA file.
    :type path: Path
    :return: The concatenated sequence string.
    :rtype: str
    """
    text = path.read_text().splitlines()
    seq_lines = [ln.strip() for ln in text if ln.strip() and not ln.startswith(">")]
    if not seq_lines:
        raise ValueError(f"No sequence found in FASTA: {path}")
    return "".join(seq_lines)
