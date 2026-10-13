"""Read-only check run with the portable runtime after authorized installation."""
import json
import torch

available = torch.cuda.is_available()
result = {"torch": torch.__version__, "cuda_runtime": torch.version.cuda,
          "cuda_available": available, "device": None, "vram_bytes": None}
if available:
    device = torch.cuda.get_device_properties(0)
    result.update(device=device.name, vram_bytes=device.total_memory)
print(json.dumps(result))
