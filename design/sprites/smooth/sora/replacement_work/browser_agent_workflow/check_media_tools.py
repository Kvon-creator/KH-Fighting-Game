"""Inspect already installed media capabilities; install nothing."""
import importlib.util
import json

available = {name: importlib.util.find_spec(name) is not None
             for name in ("cv2", "av", "imageio", "imageio_ffmpeg")}
if available["imageio_ffmpeg"]:
    import imageio_ffmpeg
    available["bundledFFmpeg"] = imageio_ffmpeg.get_ffmpeg_exe()
print(json.dumps(available))
