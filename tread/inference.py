from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from .model import DMDModel
from .utils import get_ranges


REPEAT_TYPES = (
    "all-alpha solenoid",
    "TIM barrel",
    "beta-propeller",
    "beta-barrel",
    "all-beta solenoid",
    "alpha-beta solenoid",
)

MODEL_SPECS = {
    "repeatsdb": {
        "filename": "linear-edge_model_repeatsdb.pt",
        "multi": True,
        "type_names": REPEAT_TYPES,
    },
    "propeller-blade": {
        "filename": "linear-edge_model_propeller_blade.pt",
        "multi": False,
        "type_names": (),
    },
}


@dataclass
class Prediction:
    repeat_probability: np.ndarray
    type_probabilities: list | None


def _bundled_weight_path(filename):
    package_path = Path(__file__).resolve().parent / "trained_model" / filename
    if package_path.exists():
        return package_path

    # Development fallback before the existing repository's trained_model folder
    # has been moved into the package.
    repo_path = Path(__file__).resolve().parent.parent / "trained_model" / filename
    if repo_path.exists():
        return repo_path

    raise FileNotFoundError(
        f"Could not find bundled TREAD weight '{filename}'. Expected it under "
        "tread/trained_model/."
    )


def _extract_state_dict(checkpoint):
    if isinstance(checkpoint, dict):
        for key in ("model_state_dict", "state_dict"):
            if key in checkpoint and isinstance(checkpoint[key], dict):
                checkpoint = checkpoint[key]
                break

    if not isinstance(checkpoint, dict):
        raise TypeError(
            "Unsupported checkpoint format. Expected a PyTorch state_dict or a "
            "dictionary containing 'model_state_dict'/'state_dict'."
        )

    # Accommodate checkpoints saved from DataParallel.
    if checkpoint and all(key.startswith("module.") for key in checkpoint):
        checkpoint = {key[7:]: value for key, value in checkpoint.items()}
    return checkpoint


def load_tread_model(model_name, device):
    if model_name not in MODEL_SPECS:
        raise ValueError(f"Unknown model '{model_name}'")

    spec = MODEL_SPECS[model_name]
    model = DMDModel(
        multi=spec["multi"],
        num_types=len(spec["type_names"]) if spec["multi"] else 6,
        device=device,
    )

    checkpoint = torch.load(_bundled_weight_path(spec["filename"]), map_location=device)
    state_dict = _extract_state_dict(checkpoint)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.device = device
    model.eval()
    return model


def predict_embedding(model, embedding):
    device = next(model.parameters()).device
    embedding = embedding.to(device)

    with torch.inference_mode():
        output = model.predict_single(embedding)

    if model.multi:
        repeat_probability, type_probabilities = output
        return Prediction(repeat_probability, type_probabilities)
    return Prediction(output, None)


def segment_prediction(prediction, model_name, threshold=0.5, min_length=15):
    """Convert residue-wise probabilities into human-readable repeat segments."""
    ranges = get_ranges(
        prediction.repeat_probability,
        cutoff1=threshold,
        min_len=min_length,
        cutoff2=threshold,
        frac2=0.5,
    )

    rows = []
    type_names = MODEL_SPECS[model_name]["type_names"]

    for repeat_index, (start0, end0) in enumerate(ranges, start=1):
        mean_repeat_score = float(np.mean(prediction.repeat_probability[start0:end0]))

        repeat_class = "repeat"
        class_score = None
        if prediction.type_probabilities is not None:
            type_means = [float(np.mean(p[start0:end0])) for p in prediction.type_probabilities]
            best = int(np.argmax(type_means))
            repeat_class = type_names[best]
            class_score = type_means[best]
        elif model_name == "propeller-blade":
            repeat_class = "beta-propeller blade"

        rows.append(
            {
                "repeat_index": repeat_index,
                # Convert Python's [start, end) coordinates to biological
                # 1-based inclusive coordinates.
                "start": start0 + 1,
                "end": end0,
                "length": end0 - start0,
                "mean_repeat_score": mean_repeat_score,
                "repeat_class": repeat_class,
                "class_score": class_score,
            }
        )
    return rows
