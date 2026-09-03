from pathlib import Path

from tread.io import read_fasta


def test_read_fasta(tmp_path: Path):
    fasta = tmp_path / "x.fa"
    fasta.write_text(">a description\nACDEFG\n>b\nHIKLMN*\n")
    records = read_fasta(fasta)
    assert [r.identifier for r in records] == ["a", "b"]
    assert records[0].sequence == "ACDEFG"
    assert records[1].sequence == "HIKLMN"
