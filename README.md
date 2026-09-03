# TREAD

TREAD is a supervised protein-repeat annotation framework that predicts residue-wise repeat probabilities from ProtT5 embeddings.

This `testTREAD` repository is a packaging/CLI test version. The original TREAD model architecture and repeat-range utilities are retained in `tread/model.py` and `tread/utils.py`; the new files add FASTA input, automatic ProtT5 embedding generation, checkpoint loading, a command-line interface, and tabular output.

## Repository layout

```text
testTREAD/
├── pyproject.toml
├── README.md
├── LICENSE
├── examples/
├── scripts/
│   └── copy_weights_from_old_repo.py
└── tread/
    ├── __init__.py
    ├── model.py          # original TREAD model implementation
    ├── utils.py          # original TREAD range/profile utilities
    ├── embedding.py      # FASTA sequence -> ProtT5 residue embeddings
    ├── inference.py      # checkpoint loading and TREAD inference
    ├── io.py             # FASTA parser
    ├── cli.py            # `tread predict`
    └── trained_model/
        ├── linear-edge_model_repeatsdb.pt
        └── linear-edge_model_propeller_blade.pt
```

## 1. Add the existing trained weights

The two existing checkpoint files should live **inside the Python package** at `tread/trained_model/`.

If you already have the old `TREAD` repository locally, from the root of `testTREAD` run:

```bash
python scripts/copy_weights_from_old_repo.py /path/to/old/TREAD
```

Equivalent manual command:

```bash
cp /path/to/old/TREAD/trained_model/*.pt tread/trained_model/
```

Check that the layout is:

```text
tread/trained_model/linear-edge_model_repeatsdb.pt
tread/trained_model/linear-edge_model_propeller_blade.pt
```

## 2. Install

A clean virtual environment is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

`-e` installs the repository in editable mode, which is convenient while testing.

Check the CLI:

```bash
tread --help
tread predict --help
```

## 3. Predict repeats from FASTA

```bash
tread predict proteins.fasta
```

By default results are written to `tread_results/`:

```text
tread_results/
├── segments.tsv
└── residue_scores.tsv
```

Use a custom output directory:

```bash
tread predict proteins.fasta -o my_results
```

Select a trained model:

```bash
tread predict proteins.fasta --model repeatsdb
tread predict proteins.fasta --model propeller-blade
```

TREAD automatically uses CUDA when available and otherwise falls back to CPU:

```bash
tread predict proteins.fasta --device auto
```

Explicit device selection is also possible:

```bash
tread predict proteins.fasta --device cuda
tread predict proteins.fasta --device cpu
```

## Outputs

`segments.tsv` contains human-readable repeat annotations with 1-based inclusive coordinates.

`residue_scores.tsv` contains the residue-level repeat probability and, when supported by the selected trained model, repeat-fold probabilities.

## Long proteins

The CLI does not impose the 600/1200-residue web-interface limits. For long sequences, ProtT5 embeddings are generated in overlapping chunks and combined before TREAD inference. This behavior should be validated against full-sequence embeddings before being presented as a formally benchmarked feature.

## Online demos

The existing Google Colab and Hugging Face Space can remain available as convenient demos. The local CLI is intended to become the canonical, reproducible implementation.
