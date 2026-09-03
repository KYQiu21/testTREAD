import argparse
import csv
from pathlib import Path

from .embedding import ProtT5Embedder, resolve_device
from .inference import MODEL_SPECS, load_tread_model, predict_embedding, segment_prediction
from .io import read_fasta


def _write_segments(path, rows):
    fieldnames = [
        "sequence_id",
        "sequence_length",
        "repeat_index",
        "start",
        "end",
        "length",
        "mean_repeat_score",
        "repeat_class",
        "class_score",
    ]
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _write_residue_scores(path, record_id, prediction, type_names, mode="a"):
    path = Path(path)
    exists = path.exists() and mode == "a"
    fieldnames = ["sequence_id", "position", "repeat_probability"] + [
        name.replace(" ", "_").replace("-", "_") + "_probability"
        for name in type_names
    ]

    with path.open(mode, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        if not exists or mode == "w":
            writer.writeheader()

        for i, repeat_prob in enumerate(prediction.repeat_probability, start=1):
            row = {
                "sequence_id": record_id,
                "position": i,
                "repeat_probability": float(repeat_prob),
            }
            if prediction.type_probabilities is not None:
                for name, probs in zip(type_names, prediction.type_probabilities):
                    key = name.replace(" ", "_").replace("-", "_") + "_probability"
                    row[key] = float(probs[i - 1])
            writer.writerow(row)


def run_predict(args):
    records = read_fasta(args.fasta)
    device = resolve_device(args.device)

    print(f"TREAD: {len(records)} sequence(s) loaded from {args.fasta}")
    print(f"TREAD model: {args.model}")
    print(f"Compute device: {device}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    segments_path = outdir / "segments.tsv"
    residue_path = outdir / "residue_scores.tsv"
    if residue_path.exists():
        residue_path.unlink()

    print("Loading ProtT5 (first run may download model files)...")
    embedder = ProtT5Embedder(device=device)
    print("Loading TREAD weights...")
    model = load_tread_model(args.model, device)

    all_segments = []
    type_names = MODEL_SPECS[args.model]["type_names"]

    for n, record in enumerate(records, start=1):
        print(f"[{n}/{len(records)}] {record.identifier} ({len(record.sequence)} aa)")
        embedding = embedder.embed(
            record.sequence,
            chunk_length=args.embedding_chunk_length,
            overlap=args.embedding_overlap,
        )
        prediction = predict_embedding(model, embedding)
        segments = segment_prediction(
            prediction,
            args.model,
            threshold=args.threshold,
            min_length=args.min_length,
        )

        for row in segments:
            row["sequence_id"] = record.identifier
            row["sequence_length"] = len(record.sequence)
            if row["class_score"] is None:
                row["class_score"] = ""
            all_segments.append(row)

        if not args.no_residue_scores:
            _write_residue_scores(residue_path, record.identifier, prediction, type_names)

        print(f"  predicted repeat segments: {len(segments)}")

    _write_segments(segments_path, all_segments)
    print(f"\nDone. Segment annotations: {segments_path}")
    if not args.no_residue_scores:
        print(f"Residue-wise scores: {residue_path}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tread",
        description="TREAD: residue-level protein repeat annotation from FASTA sequences",
    )
    parser.add_argument("--version", action="version", version="TREAD 0.1.0")

    subparsers = parser.add_subparsers(dest="command", required=True)
    predict = subparsers.add_parser(
        "predict",
        help="predict repeat regions from one or more protein sequences",
    )
    predict.add_argument("fasta", help="input protein FASTA file")
    predict.add_argument("-o", "--outdir", default="tread_results", help="output directory")
    predict.add_argument(
        "--model",
        choices=sorted(MODEL_SPECS),
        default="repeatsdb",
        help="trained TREAD model to use (default: repeatsdb)",
    )
    predict.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="compute device; auto uses CUDA when available (default: auto)",
    )
    predict.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="residue probability threshold for segment extraction (default: 0.5)",
    )
    predict.add_argument(
        "--min-length",
        type=int,
        default=15,
        help="minimum predicted repeat-segment length (default: 15)",
    )
    predict.add_argument(
        "--embedding-chunk-length",
        type=int,
        default=1000,
        help="maximum ProtT5 chunk length for long proteins (default: 1000)",
    )
    predict.add_argument(
        "--embedding-overlap",
        type=int,
        default=100,
        help="overlap between ProtT5 chunks for long proteins (default: 100)",
    )
    predict.add_argument(
        "--no-residue-scores",
        action="store_true",
        help="write only segment annotations, not the residue-wise score table",
    )
    predict.set_defaults(func=run_predict)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
