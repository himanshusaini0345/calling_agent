import torch
from transformers import pipeline
from datasets import load_dataset

device = "cuda:0" if torch.cuda.is_available() else "cpu"

asr_pipe = pipeline(
    "automatic-speech-recognition",
    model="collabora/whisper-tiny-hindi",
    chunk_length_s=30,
    device=device
)

ds = load_dataset("mozilla-foundation/common_voice_13_0", "hi", split="validation")
sample = ds[0]["audio"]
prediction = asr_pipe(sample.copy(), return_timestamps=True)
