#!/usr/bin/env python3
"""Tests for GPU detection logic (utils.gpu_detector).

GpuDetector is dependency-light (only stdlib + loguru), so these tests run
without inquirer/colorama. We feed representative ``lspci -nn`` output through a
monkeypatched ``_read_lspci`` and assert vendor + driver detection.
"""

import sys
from pathlib import Path

# Make the project root importable.
sys.path.insert(0, str(Path(__file__).parent.parent))

from Builder.utils.gpu_detector import (
    AMD,
    DetectedGpu,
    GpuDetector,
    INTEL,
    NVIDIA,
)


def _patch_lspci(monkeypatch, output: str) -> None:
    """Redirect GpuDetector._read_lspci to return ``output``."""
    monkeypatch.setattr(GpuDetector, "_read_lspci", staticmethod(lambda: output))


# ---------------------------------------------------------------------------
# detect_nvidia_driver: every supported generation
# ---------------------------------------------------------------------------

def test_nvidia_blackwell_gb202():
    driver, gen = GpuDetector.detect_nvidia_driver("NVIDIA Corporation GB202 [GeForce RTX 5090]")
    assert driver == "nvidia-open-dkms"
    assert gen == "Blackwell"


def test_nvidia_ada_ad102():
    driver, gen = GpuDetector.detect_nvidia_driver("AD102 [GeForce RTX 4090]")
    assert driver == "nvidia-open-dkms"
    assert gen == "Ada Lovelace"


def test_nvidia_ampere_ga102():
    driver, gen = GpuDetector.detect_nvidia_driver("GA102 [GeForce RTX 3090]")
    assert driver == "nvidia-open-dkms"
    assert gen == "Ampere"


def test_nvidia_turing_tu102():
    driver, gen = GpuDetector.detect_nvidia_driver("TU102 [GeForce RTX 2080 Ti]")
    assert driver == "nvidia-open-dkms"
    assert gen == "Turing"


def test_nvidia_pascal_gp104():
    driver, gen = GpuDetector.detect_nvidia_driver("GP104 [GeForce GTX 1080]")
    assert driver == "nvidia-580xx-dkms"
    assert gen == "Pascal"


def test_nvidia_maxwell_gm204():
    driver, gen = GpuDetector.detect_nvidia_driver("GM204 [GeForce GTX 970]")
    assert driver == "nvidia-580xx-dkms"
    assert gen == "Maxwell"


def test_nvidia_kepler_gk104():
    driver, gen = GpuDetector.detect_nvidia_driver("GK104 [GeForce GTX 760]")
    assert driver == "nvidia-470xx-dkms"
    assert gen == "Kepler"


def test_nvidia_fermi_gf110():
    driver, gen = GpuDetector.detect_nvidia_driver("GF110 [GeForce GTX 580]")
    assert driver == "nvidia-390xx-dkms"
    assert gen == "Fermi"


def test_nvidia_tesla_g92():
    driver, gen = GpuDetector.detect_nvidia_driver("G92 [GeForce 9800 GT]")
    assert driver == "nvidia-340xx-dkms"
    assert gen == "Tesla"


# ---------------------------------------------------------------------------
# detect_nvidia_driver: unsupported and unidentified
# ---------------------------------------------------------------------------

def test_nvidia_unsupported_curie_g73():
    driver, gen = GpuDetector.detect_nvidia_driver("G73 [GeForce 7600 GS]")
    assert driver == "unsupported"
    assert gen == "Curie"


def test_nvidia_unidentified_future_card():
    # A codename that does not exist yet must fall through gracefully.
    driver, gen = GpuDetector.detect_nvidia_driver("ZZ99 [Future Card 9999]")
    assert driver == "unidentified"
    assert gen == "Unknown"


# ---------------------------------------------------------------------------
# detect_all: vendor detection from lspci output
# ---------------------------------------------------------------------------

def test_detect_all_nvidia(monkeypatch):
    lspci = (
        "01:00.0 VGA compatible controller [0300]: NVIDIA Corporation "
        "AD104 [GeForce RTX 4070] [10de:2786]\n"
        "00:1f.6 Ethernet controller [0200]: ... \n"
    )
    _patch_lspci(monkeypatch, lspci)

    detected = GpuDetector.detect_all()

    assert NVIDIA in detected
    gpu = detected[NVIDIA]
    assert isinstance(gpu, DetectedGpu)
    assert gpu.vendor == NVIDIA
    assert "AD104" in gpu.name


def test_detect_all_amd(monkeypatch):
    lspci = (
        "08:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. "
        "[AMD/ATI] Navi 10 [Radeon RX 5600 XT] [1002:731f]\n"
    )
    _patch_lspci(monkeypatch, lspci)

    detected = GpuDetector.detect_all()

    assert AMD in detected
    assert detected[AMD].vendor == AMD
    assert "Navi" in detected[AMD].name


def test_detect_all_intel(monkeypatch):
    lspci = (
        "00:02.0 VGA compatible controller [0300]: Intel Corporation "
        "Alder Lake-S GT1 [UHD Graphics 770] [8086:3270]\n"
    )
    _patch_lspci(monkeypatch, lspci)

    detected = GpuDetector.detect_all()

    assert INTEL in detected
    assert detected[INTEL].vendor == INTEL
    assert "Alder Lake" in detected[INTEL].name


def test_detect_all_3d_controller_counts(monkeypatch):
    # Optimus / server dGPUs appear as "3D controller", not "VGA".
    lspci = (
        "00:02.0 VGA compatible controller [0300]: Intel Corporation UHD Graphics [8086:9a49]\n"
        "01:00.0 3D controller [0302]: NVIDIA Corporation GA106M "
        "[GeForce RTX 3060 Mobile] [10de:2520]\n"
    )
    _patch_lspci(monkeypatch, lspci)

    detected = GpuDetector.detect_all()

    assert INTEL in detected
    assert NVIDIA in detected
    assert AMD not in detected


def test_detect_all_multiple_first_wins(monkeypatch):
    # When two cards of the same vendor are present we keep the first one only.
    lspci = (
        "01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP104 [10de:1b80]\n"
        "02:00.0 VGA compatible controller [0300]: NVIDIA Corporation AD102 [10de:2684]\n"
    )
    _patch_lspci(monkeypatch, lspci)

    detected = GpuDetector.detect_all()

    assert list(detected.keys()) == [NVIDIA]
    assert "GP104" in detected[NVIDIA].name


def test_detect_all_empty(monkeypatch):
    _patch_lspci(monkeypatch, "")
    assert GpuDetector.detect_all() == {}


def test_detect_all_no_gpu(monkeypatch):
    lspci = (
        "00:1f.6 Ethernet controller [0200]: Intel Corporation I219-V [8086:15b7]\n"
        "00:1f.3 Audio device [0403]: Intel Corporation CM238 HD Audio [8086:a171]\n"
    )
    _patch_lspci(monkeypatch, lspci)
    assert GpuDetector.detect_all() == {}
