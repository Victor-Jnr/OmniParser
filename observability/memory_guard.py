import os
import gc
import logging
from typing import Optional

try:
	import psutil
except Exception:
	psutil = None

try:
	import torch
except Exception:
	torch = None

try:
	import cv2
except Exception:
	cv2 = None

_logger = logging.getLogger(__name__)


def get_rss_mb() -> float:
	if psutil is None:
		return 0.0
	process = psutil.Process(os.getpid())
	return float(process.memory_info().rss) / 1e6


def cleanup_caches(note: Optional[str] = None) -> None:
	"""Perform a soft cleanup: Python GC + clear CUDA cache (if available)."""
	try:
		gc.collect()
		if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
			try:
				torch.cuda.empty_cache()
			except Exception:
				pass
		new_rss = get_rss_mb()
		if note:
			_logger.info(f"memory_guard: cleanup done ({note}), rss={new_rss:.1f}MB")
		else:
			_logger.info(f"memory_guard: cleanup done, rss={new_rss:.1f}MB")
	except Exception as e:
		_logger.warning(f"memory_guard: cleanup error: {e}")


def limit_threads() -> None:
	"""Reduce thread counts for BLAS/OpenMP-heavy libs and OpenCV."""
	# Env variables (must be set early; calling again is harmless)
	os.environ.setdefault("OMP_NUM_THREADS", "1")
	os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
	os.environ.setdefault("MKL_NUM_THREADS", "1")
	os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
	os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
	# OpenCV thread limiter
	try:
		if cv2 is not None and hasattr(cv2, "setNumThreads"):
			cv2.setNumThreads(1)
	except Exception:
		pass
	# Torch intra-op threads (CPU path)
	try:
		if torch is not None and hasattr(torch, "set_num_threads"):
			torch.set_num_threads(1)
	except Exception:
		pass
	_logger.info("memory_guard: thread limits applied")
