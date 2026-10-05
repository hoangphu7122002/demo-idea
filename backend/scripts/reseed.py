"""Reset and re-seed the demo DB: `cd backend && uv run python scripts/reseed.py`."""

import time

from app.seeds.reseed import reseed

if __name__ == "__main__":
    t = time.perf_counter()
    counts = reseed()
    print(f"reseeded {counts} in {time.perf_counter() - t:.2f}s")
