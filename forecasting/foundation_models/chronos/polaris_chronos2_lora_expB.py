from pathlib import Path

import pandas as pd
import torch

from chronos import Chronos2Pipeline
from chronos.chronos2.preprocess import from_data_frame


DATA_PATH = "/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"

OUTPUT_DIR = Path(
    "/home/punith-bs/01polaris/chronos/polaris_lora_expB_500"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PREDICTION_LENGTH = 24
CONTEXT_LENGTH = 24

TARGET = "SW_IN"
COVARIATES = ["TA", "RH", "TS_-0.01m", "PRECIP"]

TRAIN_END = pd.Timestamp("2024-07-31 23:00:00")
VAL_START = pd.Timestamp("2024-08-01 00:00:00")
VAL_END = pd.Timestamp("2024-08-31 23:00:00")


print("=" * 80)
print("POLARIS — Chronos-2 LoRA EXPERIMENT B — 500 STEPS")
print("=" * 80)

print(f"\nPyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

df = pd.read_csv(DATA_PATH)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

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

print(f"\nFull dataset: {df.shape}")
print(f"Start: {df['TIMESTAMP'].min()}")
print(f"End:   {df['TIMESTAMP'].max()}")

# ------------------------------------------------------------
# Chronological split
# ------------------------------------------------------------

train_df = df[
    df["TIMESTAMP"] <= TRAIN_END
].copy()

val_df = df[
    (df["TIMESTAMP"] >= VAL_START)
    & (df["TIMESTAMP"] <= VAL_END)
].copy()

print("\nExperiment B split:")
print(
    f"Training:    {len(train_df)} rows "
    f"| {train_df['TIMESTAMP'].min()} -> {train_df['TIMESTAMP'].max()}"
)
print(
    f"Validation:  {len(val_df)} rows "
    f"| {val_df['TIMESTAMP'].min()} -> {val_df['TIMESTAMP'].max()}"
)

print(
    "\nHeld-out TEST will be:"
    "\n  2024-09-01 -> 2024-12-31"
)

# ------------------------------------------------------------
# Prepare Chronos inputs
# ------------------------------------------------------------

def prepare(frame):
    x = frame[
        ["TIMESTAMP", TARGET] + COVARIATES
    ].copy()

    x = x.rename(
        columns={"TIMESTAMP": "timestamp"}
    )

    x["item_id"] = "Nuolja"

    x = x[
        ["item_id", "timestamp", TARGET] + COVARIATES
    ]

    return from_data_frame(
        x,
        target_columns=[TARGET],
        prediction_length=PREDICTION_LENGTH,
        id_column="item_id",
        timestamp_column="timestamp",
    )


print("\nPreparing Chronos inputs...")

train_inputs = prepare(train_df)
val_inputs = prepare(val_df)

print(f"Training PreparedInputs: {len(train_inputs)}")
print(f"Validation PreparedInputs: {len(val_inputs)}")

print("\nTraining PreparedInput:")
print(f"  type: {type(train_inputs[0])}")
print(f"  keys: {list(train_inputs[0].keys())}")

print("\nValidation PreparedInput:")
print(f"  type: {type(val_inputs[0])}")
print(f"  keys: {list(val_inputs[0].keys())}")

# ------------------------------------------------------------
# Load Chronos-2
# ------------------------------------------------------------

print("\nLoading Chronos-2...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2"
)

print("Chronos-2 loaded.")

# ------------------------------------------------------------
# LoRA configuration
# ------------------------------------------------------------

from peft import LoraConfig

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0,
    target_modules=[
        "self_attention.q",
        "self_attention.v",
        "self_attention.k",
        "self_attention.o",
        "output_patch_embedding.output_layer",
    ],
)

# ------------------------------------------------------------
# Train
# ------------------------------------------------------------

print("\nStarting Experiment B — 500-step LoRA...")
print("Learning rate: 1e-5")
print("Batch size: 1")
print("Context length: 24")
print("Prediction length: 24")
print(f"Output: {OUTPUT_DIR}")

pipeline.fit(
    inputs=train_inputs,
    validation_inputs=val_inputs,
    prediction_length=PREDICTION_LENGTH,
    finetune_mode="lora",
    lora_config=lora_config,
    context_length=CONTEXT_LENGTH,
    learning_rate=1e-5,
    num_steps=500,
    batch_size=1,
    min_past=24,
    output_dir=str(OUTPUT_DIR),
    finetuned_ckpt_name="finetuned-ckpt",
    disable_data_parallel=True,
)

checkpoint = OUTPUT_DIR / "finetuned-ckpt"

print("\n" + "=" * 80)
print("EXPERIMENT B COMPLETE")
print("=" * 80)

print(f"Checkpoint exists: {checkpoint.exists()}")
print(f"Checkpoint path: {checkpoint}")

if checkpoint.exists():
    print("\nCheckpoint contents:")
    for p in sorted(checkpoint.iterdir()):
        print(f"  {p.name}")

print("\nSUCCESS — Experiment B training completed.")
