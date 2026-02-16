!pip install gliner torch transformers
from gliner import GLiNER
from pathlib import Path

# Куда положить (папка detectors/models/ в вашем проекте)
out_dir = Path("src/private_layer/detectors/models/private-layer-v1")
out_dir.mkdir(parents=True, exist_ok=True)

model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")
model.save_pretrained(str(out_dir))
print("Saved to", out_dir)