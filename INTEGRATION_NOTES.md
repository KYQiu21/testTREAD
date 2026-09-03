# testTREAD integration notes

## What was retained from the current GitHub repository

- `tread/model.py` — original TREAD model implementation
- `tread/utils.py` — original plotting/range utility implementation
- MIT license
- Existing checkpoint filenames

## What was added

- `tread/embedding.py` — automatic ProtT5 embedding generation
- `tread/inference.py` — packaged checkpoint loading and inference wrapper
- `tread/io.py` — FASTA reader
- `tread/cli.py` — `tread predict ...` command-line entry point
- `pyproject.toml` — dependencies, install metadata, CLI registration, package-data rules
- README and test scaffolding

## Weight placement

Move/copy the original root-level `trained_model/*.pt` files into:

```text
tread/trained_model/
```

This is deliberate. It makes the checkpoint files part of the installed package, so prediction does not depend on the user's current working directory or a separately managed model path.

## Important validation still required

Before this becomes the production TREAD repository, verify:

1. The exact `DMDModel(...)` constructor settings used for each checkpoint.
2. Whether the six repeat-class outputs are in the order currently listed in `tread/inference.py`.
3. ProtT5 preprocessing/output equivalence with the current Colab/HF implementation.
4. New CLI predictions against a known sequence from the existing implementation.
5. Long-sequence chunked embedding equivalence before making a strong long-protein support claim.
