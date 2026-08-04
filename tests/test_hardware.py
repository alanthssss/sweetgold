from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from beehive.hardware import configure_torch, requested_device, resolve_device


class _Backend:
    def __init__(self, available=False, built=False):
        self._available = available
        self._built = built

    def is_available(self):
        return self._available

    def is_built(self):
        return self._built


class _Torch:
    def __init__(self, *, cuda=False, mps=False):
        self.cuda = _Backend(cuda)
        self.backends = type("Backends", (), {"mps": _Backend(mps, mps)})()
        self.default_device = None

    def set_default_device(self, device):
        self.default_device = device


class HardwareTests(unittest.TestCase):
    def test_auto_prefers_cuda_then_mps_then_cpu(self):
        self.assertEqual(resolve_device(_Torch(cuda=True, mps=True), "auto"), "cuda")
        self.assertEqual(resolve_device(_Torch(mps=True), "auto"), "mps")
        self.assertEqual(resolve_device(_Torch(), "auto"), "cpu")

    def test_explicit_unavailable_accelerator_does_not_silently_fallback(self):
        with self.assertRaisesRegex(RuntimeError, "CUDA was requested"):
            resolve_device(_Torch(), "cuda")
        with self.assertRaisesRegex(RuntimeError, "MPS was requested"):
            resolve_device(_Torch(), "mps")

    def test_configure_torch_sets_the_process_default(self):
        torch = _Torch(mps=True)
        with patch.dict(os.environ, {"SWEETGOLD_DEVICE": "mps"}):
            self.assertEqual(configure_torch(torch), "mps")
        self.assertEqual(torch.default_device, "mps")

    def test_invalid_environment_device_is_rejected(self):
        with patch.dict(os.environ, {"SWEETGOLD_DEVICE": "quantum"}):
            with self.assertRaisesRegex(ValueError, "unsupported device"):
                requested_device()


if __name__ == "__main__":
    unittest.main()
