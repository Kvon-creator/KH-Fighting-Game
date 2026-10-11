"""Read-only sprite and motion QA. No raster editing or image-generation calls."""
from pathlib import Path
import argparse
import hashlib
import json
import math
from collections import deque
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r"D:\KH Fighting Game".lower(), ROOT
READY = ROOT / "design/sprites/smooth/sora/replacement_work/ready"

def components(alpha):
    mask = alpha > 100
    try:
        from scipy.ndimage import label, find_objects
        labeled, count = label(mask, structure=np.ones((3, 3)))
        objects = find_objects(labeled)
        counts = np.bincount(labeled.ravel())
        return sorted((int(counts[i]), (s[1].start, s[0].start, s[1].stop, s[0].stop))
                      for i, s in enumerate(objects, 1) if counts[i] > 8)
    except ImportError:
        seen = np.zeros(mask.shape, dtype=bool)
        result = []
        for y, x in np.argwhere(mask):
            if seen[y, x]:
                continue
            queue = deque([(int(x), int(y))]); seen[y, x] = True
            size = 0; x0 = x1 = int(x); y0 = y1 = int(y)
            while queue:
                xx, yy = queue.pop(); size += 1
                x0 = min(x0, xx); x1 = max(x1, xx)
                y0 = min(y0, yy); y1 = max(y1, yy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = xx + dx, yy + dy
                        if 0 <= nx < 512 and 0 <= ny < 512 and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; queue.append((nx, ny))
            if size > 8:
                result.append((size, (x0, y0, x1 + 1, y1 + 1)))
        return sorted(result)

def inspect(folder):
    directory = READY / folder
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8-sig"))
    rows = []; maximum_error = 0
    for frame in manifest["frames"]:
        path = directory / frame["file"]
        image = Image.open(path)
        assert image.size == (512, 512) and image.mode == "RGBA"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == frame["sha256"]
        alpha = image.getchannel("A")
        assert alpha.getextrema() == (0, 255)
        bounds = alpha.getbbox()
        assert bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 512 and bounds[3] < 512, bounds
        joints = frame["joints"]
        far_thigh = manifest.get("projectedFarThigh", 86)
        near_thigh = manifest.get("projectedNearThigh", 86)
        shin = manifest.get("projectedShin", 54)
        far_shin = manifest.get("projectedFarShin", shin)
        near_shin = manifest.get("projectedNearShin", shin)
        for a, b, length in [(0, 1, far_thigh), (1, 2, far_shin), (3, 4, near_thigh), (4, 5, near_shin)]:
            maximum_error = max(maximum_error, abs(math.dist(joints[a], joints[b]) - length))
        if "freeShoulder" in frame:
            for a, b, length in [(frame["freeShoulder"], frame["freeElbow"], frame["freeUpperLength"]),
                                 (frame["freeElbow"], frame["freeWrist"], frame["freeForearmLength"])]:
                maximum_error = max(maximum_error, abs(math.dist(a, b) - length))
        all_components = components(np.asarray(alpha))
        assert not all_components[:-1], (frame["index"], all_components[:-1])
        if manifest["animation"] == "run_stop" or frame["index"] in (0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13):
            assert bounds[3] == 470, (frame["index"], bounds)
        elif frame["index"] in (6, 14):
            if "qualityBenchmark" in manifest:
                assert bounds[3] < 470, (frame["index"], bounds)
            else:
                assert bounds[3] == 456, (frame["index"], bounds)
        else:
            assert bounds[3] == 468, (frame["index"], bounds)
        rows.append(dict(index=frame["index"], phase=frame["phase"], bounds=bounds,
                         lowerEdgeClearance=470 - bounds[3],
                         detachedComponents=all_components[:-1]))
        game = Image.open(directory / "frames_128" / frame["file"])
        assert game.mode == "RGBA" and game.size == (128, 128)
    assert maximum_error < .002
    assert len(set(frame["sha256"] for frame in manifest["frames"])) == 16
    suffix = "Loop" if manifest["loop"] else "Once"
    for size in (512, 128):
        gif_path = directory / f"Preview_{size}_{suffix}.gif"
        gif = Image.open(gif_path)
        assert gif.n_frames == 16
        assert (b"NETSCAPE2.0" in gif_path.read_bytes()) == manifest["loop"]
        delays = []
        for i in range(gif.n_frames):
            gif.seek(i); delays.append(gif.info["duration"])
        assert delays == [f["durationMs"] for f in manifest["frames"]]
    if "qualityBenchmark" in manifest:
        benchmark = READY / manifest["qualityBenchmark"]
        assert hashlib.sha256(benchmark.read_bytes()).hexdigest() == manifest["qualityBenchmarkSha256"]
        assert Image.open(benchmark).n_frames == 13
        for reference, sha256 in zip(manifest["sourcePaths"], manifest["sourceHashes"]):
            assert hashlib.sha256(Path(reference).read_bytes()).hexdigest() == sha256
    return dict(animation=manifest["animation"], frameCount=16,
                maximumJointLengthRoundingError=maximum_error,
                allImagesDecode=True, transparent512And128=True,
                frames=rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", default="flat_cycle_v5")
    parser.add_argument("--stop", default="flat_stop_v5")
    args = parser.parse_args()
    loop = inspect("run_loop/" + args.loop)
    stop = inspect("run_stop/" + args.stop)
    assert (READY / "run_loop" / args.loop / "sora_run_loop_00.png").read_bytes() == (READY / "run_stop" / args.stop / "sora_run_stop_00.png").read_bytes()
    source = READY / "run_start/direct_imagegen_trial/whole_figure_review_v3/frame_11.png"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == "cb54c1d39b5ea7a83a1bd053bd876a49391993d0ea2bec8a1d36472f1c6e737c"
    original = READY / "run_start/direct_imagegen_trial/attempt_03/sora_run_start_original.png"
    assert hashlib.sha256(original.read_bytes()).hexdigest() == "6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e"
    idle = READY / "standing_idle/sora_stand_idle_00.png"
    assert hashlib.sha256(idle.read_bytes()).hexdigest() == "baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7"
    report = dict(sourceAndSelectedSheetPreserved=True, stopEntryByteIdentical=True,
                  loop=loop, stop=stop,
                  scope="Offline decode, registration and construction QA; not a claim of final natural motion or Godot testing.")
    print(json.dumps(report, indent=2))
