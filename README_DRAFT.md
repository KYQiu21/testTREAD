# TREAD

**TREAD (Transfer learning-based REpeat Annotation using Protein EmbeDdings)** predicts protein repeat regions directly from amino-acid sequences using ProtT5 residue embeddings and trained residue-level TREAD models.

The recommended interface is the local command-line tool. Google Colab and Hugging Face are provided as optional online demos.

## Installation

Python 3.9 or newer is recommended. A CUDA-capable GPU is strongly recommended for ProtT5 embedding generation, although CPU execution is supported and is substantially slower.

```bash
git clone https://github.com/KYQiu21/TREAD.git
cd TREAD
pip install .
```

If your system requires a specific CUDA build of PyTorch, install PyTorch for your CUDA version first and then run `pip install .`.

On the first prediction run, the ProtT5 model `Rostlab/prot_t5_xl_uniref50` is downloaded automatically from Hugging Face and cached locally.

## Quick start

Analyze a FASTA file with the general RepeatsDB-trained TREAD model:

```bash
tread predict protein.fasta
```

Results are written to `tread_results/`:

- `segments.tsv`: predicted repeat regions with 1-based inclusive residue coordinates.
- `residue_scores.tsv`: residue-wise repeat probabilities and, for the RepeatsDB model, probabilities for six repeat-fold classes.

Analyze multiple proteins by placing multiple FASTA records in the same file:

```bash
tread predict proteins.fasta -o my_results
```

Use the beta-propeller blade model:

```bash
tread predict protein.fasta --model propeller-blade
```

View all options:

```bash
tread predict --help
```

## Long proteins

TREAD does not impose the 600/1200-residue limits of the online demo. For long proteins, ProtT5 embeddings are generated from overlapping sequence chunks and merged before TREAD inference. The default chunk length is 1000 residues with 100-residue overlap and can be changed with:

```bash
tread predict protein.fasta --embedding-chunk-length 1000 --embedding-overlap 100
```

Because chunking changes the ProtT5 context near chunk boundaries, long-sequence chunking should be validated against full-sequence embedding on proteins that fit in memory before publication/release.

## Models

`repeatsdb` (default) provides a general repeat/non-repeat score together with predictions for six repeat-fold classes:

- all-alpha solenoid
- all-beta solenoid
- beta-alpha solenoid
- TIM barrel
- beta-barrel
- beta-propeller

`propeller-blade` is the beta-propeller blade-specific model used for the propeller analysis.

## Online demos

- Google Colab: https://colab.research.google.com/drive/1gbtb5BtevWE9vChJrYgiNW2mQSW_kN8j
- Hugging Face Space: https://huggingface.co/spaces/kevinky/TREAD

The online interfaces are intended as convenient demonstrations. The command-line installation is recommended for reproducible analyses and larger jobs.
