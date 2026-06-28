import argparse
import importlib.util
import runpy
import sys
from pathlib import Path


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    parser = argparse.ArgumentParser(description="TransVideo app entrypoint")
    parser.add_argument("--gpu-check", action="store_true", help="Kiểm tra GPU/encoder rồi thoát")
    args, passthrough = parser.parse_known_args()

    if args.gpu_check:
        module_path = Path(__file__).parent / "videotrans" / "util" / "gpu_diagnostics.py"
        spec = importlib.util.spec_from_file_location("transvideo_gpu_diagnostics", module_path)
        if spec is None or spec.loader is None:
            print("Không tải được module kiểm tra GPU.")
            return 2
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.diagnose_gpu()
        print(result.summary)
        for line in result.details:
            print(f"- {line}")
        return 0 if result.ok else 2

    sys.argv = ["sp.py"] + passthrough
    runpy.run_path("sp.py", run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
