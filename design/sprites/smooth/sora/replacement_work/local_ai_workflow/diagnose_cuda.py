"""Read-only CUDA initialization diagnostic; no image editing or settings changes."""
import json
import traceback
import torch

result = {"torch": torch.__version__, "cuda_runtime": torch.version.cuda,
          "cuda_available": torch.cuda.is_available(),
          "device_count": torch.cuda.device_count(), "initialization_error": None}
try:
    torch.cuda.init()
    result["initialized"] = True
except Exception:
    result["initialized"] = False
    result["initialization_error"] = traceback.format_exc()
print(json.dumps(result))
