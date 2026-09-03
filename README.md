# TREAD

**TREAD** annotates tandem-repeat regions directly from protein sequences using residue-level ProtT5 embeddings and trained neural-network models.

The command-line interface accepts single- or multi-sequence FASTA files, generates ProtT5 embeddings automatically, runs TREAD inference, and writes repeat segments, residue-wise scores, and profile plots. Users do **not** need to pre-compute embeddings or load model checkpoints manually.

## Installation

TREAD requires **Python 3.10 or newer**. A CUDA-capable GPU is recommended for faster ProtT5 embedding, but CPU execution is supported.

Clone the repository and install it into a clean environment:

```bash
git clone https://github.com/KYQiu21/testTREAD.git
cd testTREAD

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install .
```

The two trained TREAD checkpoints are bundled with the package. On the first prediction run, the ProtT5 encoder (`Rostlab/prot_t5_xl_uniref50`) is downloaded automatically by Hugging Face Transformers and then cached locally.

Check the installation:

```bash
tread --help
tread predict --help
```

## Quick start

Run the general repeat model on the included Q60773 example:

```bash
tread predict examples/Q60773.fasta
```

By default TREAD uses the `repeatsdb` model and writes results to `tread_results/`:

```text
tread_results/
├── segments.tsv
├── residue_scores.tsv
└── plots/
    └── 0001_sp_Q60773_CDN2D_MOUSE_repeat_profile.png
```

Use a custom output directory:

```bash
tread predict examples/Q60773.fasta -o q60773_results
```

## Models

Two trained models are included.

### General repeat annotation

```bash
tread predict proteins.fasta --model repeatsdb
```

This is the default model. It predicts residue-wise repeat probabilities and repeat-fold probabilities.

### Beta-propeller blade annotation

```bash
tread predict proteins.fasta --model propeller-blade
```

This model is specialized for beta-propeller blades.

## Multi-FASTA input

A FASTA file may contain one or many protein sequences:

```bash
tread predict examples/multi.fasta -o multi_results
```

All sequences are processed in one run. Segment and residue-wise annotations are combined into TSV files, while each sequence receives its own profile plot under `multi_results/plots/`.

## Long proteins

TREAD has no 600- or 1200-residue web-interface limit. Long proteins are embedded as overlapping ProtT5 sequence chunks and reconstructed into a full-length residue-embedding matrix before TREAD inference.

For example, the included human ankyrin-2 sequence (ANK2_HUMAN; 3957 residues) can be analyzed directly:

```bash
tread predict examples/Q01484.fasta -o ank2_results
```

The default embedding settings are a 1000-residue chunk length with 100-residue overlap. They can be changed if needed:

```bash
tread predict protein.fasta \
    --embedding-chunk-length 800 \
    --embedding-overlap 100
```

## Output files

### `segments.tsv`

One row per predicted repeat segment. Coordinates are **1-based and inclusive**.

Columns include:

- `sequence_id`
- `sequence_length`
- `repeat_index`
- `start`
- `end`
- `length`
- `mean_repeat_score`
- `repeat_class`
- `class_score`

### `residue_scores.tsv`

One row per residue, containing the residue position and repeat probability. The general `repeatsdb` model also reports repeat-fold probabilities.

Residue-wise output can be disabled when only segment annotations are required:

```bash
tread predict proteins.fasta --no-residue-scores
```

### Profile plots

TREAD generates one PNG repeat-probability profile per input sequence. Predicted repeat segments are shaded and the decision threshold is shown as a dashed line.

Disable plot generation with:

```bash
tread predict proteins.fasta --no-plot
```

## Prediction settings

The default repeat-segment threshold is **0.8**, with a minimum segment length of **15 residues**.

These values can be changed from the command line:

```bash
tread predict proteins.fasta --threshold 0.8 --min-length 15
```

For the complete list of prediction options:

```bash
tread predict --help
```

## CPU and GPU execution

TREAD automatically uses CUDA when available and otherwise runs on CPU:

```bash
tread predict proteins.fasta --device auto
```

A device can also be selected explicitly:

```bash
tread predict proteins.fasta --device cuda
tread predict proteins.fasta --device cpu
```

ProtT5 embedding is the computationally expensive step, so GPU execution is recommended for large datasets and long proteins.

## Repository structure

```text
testTREAD/
├── pyproject.toml
├── README.md
├── LICENSE
├── examples/
│   ├── Q60773.fasta
│   ├── Q01484.fasta
│   ├── O95834.fasta
│   └── multi.fasta
├── tests/
└── tread/
    ├── __init__.py
    ├── cli.py
    ├── embedding.py
    ├── inference.py
    ├── io.py
    ├── model.py
    ├── utils.py
    └── trained_model/
        ├── linear-edge_model_repeatsdb.pt
        └── linear-edge_model_propeller_blade.pt
```

## Development installation

For development, install the package in editable mode with the optional test dependency:

```bash
pip install -e ".[dev]"
pytest
```

## Online demos

The Google Colab notebook and Hugging Face Space remain available as convenient interactive demos. The local command-line implementation is the recommended reproducible interface for analyzing user-provided FASTA files.

- Google Colab: https://colab.research.google.com/drive/1gbtb5BtevWE9vChJrYgiNW2mQSW_kN8j
- Hugging Face Space: https://huggingface.co/spaces/kevinky/TREAD

## License

TREAD is distributed under the MIT License. See `LICENSE` for details.
