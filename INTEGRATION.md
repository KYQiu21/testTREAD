# Integration into the current TREAD repository

1. Keep the existing `tread/model.py` and `tread/utils.py` unchanged for the first accessibility revision.
2. Add `tread/io.py`, `tread/embedding.py`, `tread/inference.py`, and `tread/cli.py` from this patch.
3. Replace the empty `tread/__init__.py` with the version in this patch.
4. Move the existing trained weights into the Python package so normal `pip install .` includes them:

```bash
git mv trained_model tread/trained_model
```

5. Add `pyproject.toml` at repository root.
6. Replace the current README with a polished version based on `README_DRAFT.md`.
7. Install in a clean environment and test:

```bash
pip install .
tread --help
tread predict example.fasta
```

## Important validation before declaring this finished

- Confirm that `linear-edge_model_repeatsdb.pt` is a state_dict compatible with `DMDModel(multi=True, num_types=6)`.
- Confirm that `linear-edge_model_propeller_blade.pt` is compatible with `DMDModel(multi=False)`.
- Confirm the exact six repeat-type order used when the RepeatsDB model was trained. The current patch uses the manuscript order; the checkpoint/output order must match training exactly.
- Compare CLI predictions against the current Colab/HF output for several short sequences, especially reviewer example Q60773.
- Validate long-sequence ProtT5 chunking against full-sequence embeddings/predictions before making a strong claim that it is equivalent.
- Test both CUDA and CPU installation paths in fresh environments.
