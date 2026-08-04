"""Hardware backend selection and reproducibility metadata for optional ML."""

from __future__ import annotations

import os
import platform
import sys
from typing import Any


DEVICE_ENV = "SWEETGOLD_DEVICE"
DEVICE_CHOICES = ("auto", "cpu", "mps", "cuda")


def requested_device() -> str:
    requested = os.environ.get(DEVICE_ENV, "auto").lower()
    if requested not in DEVICE_CHOICES:
        raise ValueError(
            f"unsupported device {requested!r}; choose from {', '.join(DEVICE_CHOICES)}"
        )
    return requested


def resolve_device(torch: Any, requested: str | None = None) -> str:
    """Resolve a requested backend without silently falling back."""
    requested = (requested or requested_device()).lower()
    if requested not in DEVICE_CHOICES:
        raise ValueError(
            f"unsupported device {requested!r}; choose from {', '.join(DEVICE_CHOICES)}"
        )
    if requested == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but is not available")
    return requested


def configure_torch(torch: Any) -> str:
    """Select the process-wide default PyTorch device for existing ML paths."""
    selected = resolve_device(torch)
    torch.set_default_device(selected)
    return selected


def synchronize(torch: Any, device: str) -> None:
    """Wait for asynchronous accelerator work before recording a duration."""
    if device == "cuda":
        torch.cuda.synchronize()
    elif device == "mps":
        torch.mps.synchronize()


def peak_memory_bytes(torch: Any, device: str) -> int | None:
    if device == "cuda":
        return int(torch.cuda.max_memory_allocated())
    return None


def _device_details(torch: Any, selected: str) -> dict[str, Any]:
    if selected == "cuda":
        properties = torch.cuda.get_device_properties(0)
        return {
            "name": properties.name,
            "memory_bytes": properties.total_memory,
            "cuda_version": torch.version.cuda,
            "device_count": torch.cuda.device_count(),
        }
    if selected == "mps":
        get_name = getattr(torch.backends.mps, "get_name", None)
        return {
            "name": get_name() if get_name else "Apple Metal Performance Shaders",
            "built": torch.backends.mps.is_built(),
            "available": torch.backends.mps.is_available(),
        }
    return {"name": platform.processor() or platform.machine() or "CPU"}


def hardware_snapshot(requested: str | None = None) -> dict[str, Any]:
    """Return machine-readable hardware and ML runtime evidence."""
    snapshot: dict[str, Any] = {
        "architecture": platform.machine(),
        "processor": platform.processor() or None,
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "requested_device": requested or requested_device(),
    }
    try:
        import torch
    except ImportError:
        snapshot.update({"pytorch": None, "selected_device": None})
        return snapshot
    selected = resolve_device(torch, requested)
    snapshot.update(
        {
            "pytorch": str(torch.__version__),
            "selected_device": selected,
            "device": _device_details(torch, selected),
            "available_backends": {
                "cpu": True,
                "mps": torch.backends.mps.is_available(),
                "cuda": torch.cuda.is_available(),
            },
        }
    )
    return snapshot
