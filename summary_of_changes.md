# Executive Summary of Changes

This document summarizes all changes made during the observability, stability, and memory-robustness improvements to the OCR API application, from the initial state to the current codebase.

## High-level outcomes
- Added robust logging and observability (console + rotating files, periodic container/process stats).
- Introduced safe cleanup hooks and thread caps to reduce CPU memory pressure and noisy parallelism.
- Instrumented memory snapshots across OCR/YOLO/captioning pipeline to pinpoint spikes.
- Made the system configurable via environment (.env) with sensible defaults and sample env guidance.
- Implemented adaptive memory guard (optional) to avoid OOM by gracefully degrading only when needed.
- Provided monitor verbosity and global silencer toggles to control logs volume.

---

## Changes by area

### 1) Logging & Observability
- Added `observability/logging_setup.py`
  - Configures root logging to console and rotating file (`logs/app.log`, 10 MB x 10 backups).
  - Harmonized log format across modules.
- Added `observability/resource_monitor.py`
  - Background thread logs every 2s to `logs/container_stats.log`: CPU, load average, system memory, disk, optional network IO, process RSS/VMS, process CPU%, optional cgroup memory limit, and optional GPU stats (via NVML).
  - New env toggles:
    - `MONITOR_ENABLED=true|false` – disable/enable the monitor globally.
    - `MONITOR_SHOW_GPU=true|false` – show/hide GPU stats line.
    - `MONITOR_SHOW_NET=true|false` – show/hide network counters line.
- Integrated monitor lifecycle into `gradio_demo_final.py` (start on boot if enabled; stop on shutdown).

### 2) Memory Guard & Thread Caps
- Added `observability/memory_guard.py`
  - `limit_threads()` sets conservative defaults for CPU-bound libs:
    - `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, `NUMEXPR_NUM_THREADS` = 1.
    - Caps OpenCV threads (if available) and Torch CPU intra-op threads.
  - `cleanup_caches(note)` runs Python GC and clears CUDA allocator cache when available.
- Added adaptive memory guard in `util/utils.py`:
  - Environment-configurable thresholds:
    - `MEM_GUARD_ENABLED=true|false`
    - `MEM_GUARD_SYS_AVAIL_MIN_MB` (default 800)
    - `MEM_GUARD_PROC_RSS_MAX_MB` (default 30000)
  - When memory is low, switches OCR engine from PaddleOCR to EasyOCR for the current request, and reduces caption batch size dynamically.

### 3) OCR/Caption Pipeline Instrumentation & Safety
- `util/utils.py`
  - Added memory snapshot logs (`mem_snapshot`) at key points:
    - Before/after OCR
    - Before/after YOLO
    - Before/after tokenizer/processor
    - After generation (captioning)
    - After annotation
  - Captioning batching made more memory-safe:
    - Build crops per batch (instead of all upfront) to reduce peak RSS.
    - Batch size driven by `ICON_CAPTION_BATCH_SIZE` (default 16) and further reduced dynamically if memory is low.
  - PaddleOCR defaults lowered for safety (still configurable):
    - `PADDLE_MAX_BATCH_SIZE` default 128 (was 1024 originally)
    - `PADDLE_REC_BATCH_NUM` default 128 (was 1024 originally)
  - OCR downscaling logic (temporary):
    - Originally introduced to reduce OOM risk
    - Removed at the user’s request to preserve full-resolution OCR
- `gradio_demo_final.py`
  - Added per-request timing and optional GPU memory snapshot logging.
  - Ensured `cleanup_caches(note="post_request")` runs after each request.

### 4) Environment-based configuration
- Introduced `.env` support via `python-dotenv`:
  - `gradio_demo_final.py` loads `.env` early
  - `util/utils.py` also loads `.env` for direct utility execution
- `requirements.txt` additions:
  - `psutil` (system/process stats)
  - `pynvml` (GPU stats; optional if available)
  - `python-dotenv` (env file support)
- Added `sample.env` with commented entries to guide `.env` configuration:
  - Caption & OCR:
    - `ICON_CAPTION_BATCH_SIZE`
    - `PADDLE_MAX_BATCH_SIZE`
    - `PADDLE_REC_BATCH_NUM`
  - Memory guard:
    - `MEM_GUARD_ENABLED`
    - `MEM_GUARD_SYS_AVAIL_MIN_MB`
    - `MEM_GUARD_PROC_RSS_MAX_MB`
  - Resource monitor:
    - `MONITOR_ENABLED`
    - `MONITOR_SHOW_GPU`
    - `MONITOR_SHOW_NET`

### 5) API application integration
- `gradio_demo_final.py`
  - Logging initialization moved before heavy operations.
  - Thread caps applied at startup (via `limit_threads()`).
  - Resource monitor started/stopped around application lifecycle.
  - Enhanced `/ocr` handler with duration and optional GPU memory logs.
  - Robust error handling and post-request cleanup.

---

## Original vs current behaviors (key deltas)

- Logging
  - Original: console only
  - Current: console + rotating file logs (`logs/app.log`), monitor writes `logs/container_stats.log`.

- OCR engine selection
  - Original: strictly per request `use_paddleocr`
  - Current: respects request, but memory guard can auto-switch to EasyOCR for that request if memory is low (configurable or disableable).

- OCR image scaling
  - Original: none
  - Interim: added downscaling to avoid OOM (removed at user request)
  - Current: full-resolution OCR; no downscaling applied.

- Caption batching
  - Original: effective default ~128 (heavy peak memory)
  - Current: default via env `ICON_CAPTION_BATCH_SIZE` (16), plus dynamic reduction under memory pressure; crops generated per batch to reduce peak.

- PaddleOCR defaults
  - Original: `max_batch_size=1024`, `rec_batch_num=1024`
  - Current defaults: 128/128 (overridable in `.env`)

- Threading
  - Original: library defaults (potentially high)
  - Current: capped to 1 for OMP/OpenBLAS/MKL/VECLIB/NumExpr, OpenCV threads, and Torch CPU threads.

- Cleanup
  - Original: none
  - Current: cache cleanup after OCR, after each caption batch, and after each request.

- Monitor controls
  - Original: N/A
  - Current: `MONITOR_ENABLED` to disable monitor entirely; `MONITOR_SHOW_GPU` and `MONITOR_SHOW_NET` to control verbosity.

---

## New and updated files

- Added
  - `observability/logging_setup.py`
  - `observability/resource_monitor.py`
  - `observability/memory_guard.py`
  - `sample.env` (guide for `.env` configuration)

- Updated
  - `gradio_demo_final.py` (logging, monitor, thread caps, cleanup, timing)
  - `util/utils.py` (memory snapshots, safer batching, adaptive guard, OCR engine fallback)
  - `requirements.txt` (added `psutil`, `pynvml`, `python-dotenv`)

---

## Environment variables (current set)

- Core pipeline
  - `ICON_CAPTION_BATCH_SIZE` – caption batch size (default 16)
  - `PADDLE_MAX_BATCH_SIZE` – PaddleOCR max batch size (default 128)
  - `PADDLE_REC_BATCH_NUM` – PaddleOCR recognition batch size (default 128)

- Memory guard
  - `MEM_GUARD_ENABLED` – enable/disable guard (default true)
  - `MEM_GUARD_SYS_AVAIL_MIN_MB` – minimum system MB to consider memory healthy (default 800)
  - `MEM_GUARD_PROC_RSS_MAX_MB` – per-process RSS MB ceiling before guard triggers (default 30000)

- Resource monitor
  - `MONITOR_ENABLED` – start/stop the monitor (default true)
  - `MONITOR_SHOW_GPU` – include/exclude GPU stats line (default true)
  - `MONITOR_SHOW_NET` – include/exclude network counters (default true)

- Per-request parameters (via form fields)
  - `box_threshold`, `iou_threshold`, `use_paddleocr`, `imgsz`

---

## Operational notes

- Why cleanup may not reduce RSS immediately:
  - Python GC and CUDA allocator cache clearing do not force native libraries to return memory to the OS; RSS may remain high until those buffers are truly freed or the process is recycled.
  - The implemented cleanups prevent further growth in a request but cannot undo a peak allocation that is still in use.

- How to avoid OOM without quality loss:
  - Prefer PaddleOCR, but reduce its batches (`PADDLE_MAX_BATCH_SIZE`, `PADDLE_REC_BATCH_NUM`).
  - Avoid parallel `/ocr` calls under tight memory.
  - Consider per-request worker processes for OCR and recycle periodically for hard RSS drops.

---

## Quick start

1) Create a `.env` based on `sample.env` and tune values.
2) Install dependencies (`requirements.txt`).
3) Run the app; logs will be written to `logs/app.log` and (if enabled) `logs/container_stats.log`.
4) Adjust thresholds and monitor toggles if you want fewer logs or more aggressive protection.

---

## Future options (optional)
- Per-request OCR worker subprocess with periodic recycle to guarantee RSS drops.
- Structured JSON logging for easier parsing/analysis.
- Prometheus endpoint for metrics consumption instead of log file scraping.
