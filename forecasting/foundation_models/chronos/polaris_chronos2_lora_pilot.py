import os
import shutil
from pathlib import Path

import pandas as pd
import torch

from chronos import Chronos2Pipeline
from chronos.chronos2.preprocess import from_data_frame


DATA_PATH = "/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"

OUTPUT_DIR = Path("/home/punith-bs/01polaris/chronos/polaris_lora_pilot")

PREDICTION_LENGTH = 24
CONTEXT_LENGTH = 24

TRAIN_END = "2024-09-30 23:00:00"
VAL_START = "2024-10-01 00:00:00"
VAL_END = "2024-10-31 23:00:00"


print("=" * 80)
print("POLARIS — Chronos-2 LoRA PILOT")
print("=" * 80)

# ------------------------------------------------------------------
# 1. Environment
# ------------------------------------------------------------------

print("\nPyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# ------------------------------------------------------------------
# 2. Load dataset
# ------------------------------------------------------------------

df = pd.read_csv(DATA_PATH, parse_dates=["TIMESTAMP"])

required = [
    "TIMESTAMP",
    "TA",
    "RH",
    "SW_IN",
    "TS_-0.01m",
    "PRECIP",
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df[required].copy()

if df.isna().any().any():
    raise ValueError("Dataset contains NaNs.")

df = df.rename(columns={"TIMESTAMP": "timestamp"})
df["item_id"] = "Nuolja"

df = df[
    [
        "item_id",
        "timestamp",
        "SW_IN",
        "TA",
        "RH",
        "TS_-0.01m",
        "PRECIP",
    ]
].sort_values(["item_id", "timestamp"]).reset_index(drop=True)

print("\nFull dataset:", df.shape)
print("Start:", df["timestamp"].min())
print("End:", df["timestamp"].max())

# ------------------------------------------------------------------
# 3. Chronological train / validation split
# ------------------------------------------------------------------

train_df = df[df["timestamp"] <= TRAIN_END].copy()

val_df = df[
    (df["timestamp"] >= VAL_START)
    & (df["timestamp"] <= VAL_END)
].copy()

print("\nTraining:")
print("  Rows:", len(train_df))
print("  Start:", train_df["timestamp"].min())
print("  End:", train_df["timestamp"].max())

print("\nValidation:")
print("  Rows:", len(val_df))
print("  Start:", val_df["timestamp"].min())
print("  End:", val_df["timestamp"].max())

if len(train_df) < CONTEXT_LENGTH + PREDICTION_LENGTH:
    raise ValueError("Training set is too short.")

if len(val_df) < CONTEXT_LENGTH + PREDICTION_LENGTH:
    raise ValueError("Validation set is too short.")

# ------------------------------------------------------------------
# 4. Convert to official Chronos PreparedInput format
# ------------------------------------------------------------------

print("\nPreparing Chronos inputs...")

train_inputs = from_data_frame(
    train_df,
    target_columns=["SW_IN"],
    prediction_length=PREDICTION_LENGTH,
    id_column="item_id",
    timestamp_column="timestamp",
)

val_inputs = from_data_frame(
    val_df,
    target_columns=["SW_IN"],
    prediction_length=PREDICTION_LENGTH,
    id_column="item_id",
    timestamp_column="timestamp",
)

print("Training PreparedInputs:", len(train_inputs))
print("Validation PreparedInputs:", len(val_inputs))

train_input = train_inputs[0]
val_input = val_inputs[0]

print("\nTraining PreparedInput:")
print("  context shape:", train_input["context"].shape)
print("  n_targets:", train_input["n_targets"])
print("  n_covariates:", train_input["n_covariates"])
print("  n_future_covariates:", train_input["n_future_covariates"])

print("\nValidation PreparedInput:")
print("  context shape:", val_input["context"].shape)
print("  n_targets:", val_input["n_targets"])
print("  n_covariates:", val_input["n_covariates"])
print("  n_future_covariates:", val_input["n_future_covariates"])

# ------------------------------------------------------------------
# 5. Load pretrained Chronos-2
# ------------------------------------------------------------------

print("\nLoading Chronos-2...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2"
)

print("Chronos-2 loaded.")

# ------------------------------------------------------------------
# 6. LoRA pilot
# ------------------------------------------------------------------

if OUTPUT_DIR.exists():
    print("\nRemoving previous pilot output...")
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

lora_config = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.0,
    "target_modules": [
        "self_attention.q",
        "self_attention.v",
        "self_attention.k",
        "self_attention.o",
        "output_patch_embedding.output_layer",
    ],
}

print("\nStarting 10-step LoRA pilot...")
print("Learning rate: 1e-5")
print("Batch size: 1")
print("Context length: 24")
print("Prediction length: 24")
print("Output:", OUTPUT_DIR)

finetuned_pipeline = pipeline.fit(
    inputs=train_inputs,
    validation_inputs=val_inputs,
    prediction_length=PREDICTION_LENGTH,
    finetune_mode="lora",
    lora_config=lora_config,
    context_length=CONTEXT_LENGTH,
    learning_rate=1e-5,
    num_steps=10,
    batch_size=1,
    min_past=CONTEXT_LENGTH,
    output_dir=OUTPUT_DIR,
    finetuned_ckpt_name="finetuned-ckpt",
    remove_printer_callback=False,
    disable_data_parallel=True,
)

print("\n" + "=" * 80)
print("PILOT COMPLETE")
print("=" * 80)

checkpoint = OUTPUT_DIR / "finetuned-ckpt"

print("Checkpoint exists:", checkpoint.exists())
print("Checkpoint path:", checkpoint)

if checkpoint.exists():
    print("\nCheckpoint contents:")
    for p in sorted(checkpoint.iterdir()):
        print(" ", p.name)

# ------------------------------------------------------------------
# 7. Quick inference test on held-out validation context
# ------------------------------------------------------------------

print("\nRunning post-training inference test...")

val_context = val_input["context"][:, -CONTEXT_LENGTH:]

pred = finetuned_pipeline.predict(
    inputs=[val_context],
    prediction_length=PREDICTION_LENGTH,
    context_length=CONTEXT_LENGTH,
)

print("Prediction type:", type(pred))
print("Prediction shape:", pred[0].shape)

median_idx = list(finetuned_pipeline.quantiles).index(0.5)

median = pred[0][0, median_idx].detach().cpu().numpy()

print("Median forecast shape:", median.shape)
print("Forecast first 10 values:")
print(median[:10])
print("Forecast min:", float(median.min()))
print("Forecast max:", float(median.max()))

print("\nSUCCESS — LoRA pilot completed.")
