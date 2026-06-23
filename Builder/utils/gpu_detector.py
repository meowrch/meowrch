import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Tuple

from loguru import logger


# Vendor identifiers shared with the driver managers and the survey.
NVIDIA = "nvidia"
INTEL = "intel"
AMD = "amd"
NONE = "none"


@dataclass
class DetectedGpu:
    """Information about a single detected GPU."""

    vendor: str  # one of NVIDIA / INTEL / AMD
    name: str    # human-readable GPU name (everything after the vendor name)


class GpuDetector:
    """Detect GPUs and the recommended NVIDIA driver package.

    The NVIDIA generation table mirrors ``checkNvidia`` from
    ``nvidiainstall.sh`` (Tesla -> Blackwell). Returns the AUR/pacman package
    base name (``nvidia-open-dkms``, ``nvidia-580xx-dkms`` ...) or
    ``unsupported`` / ``unidentified``.
    """

    # Ordered list of (codename_substrings, generation, driver package).
    # Codenames follow https://www.techpowerup.com/gpu-specs/. Order matters:
    # the most recent generations are listed first.
    NVIDIA_GENERATIONS: List[Tuple[Tuple[str, ...], str, str]] = [
        (("GB10", "GB20"), "Blackwell", "nvidia-open-dkms"),
        (("GH10",), "Hopper", "nvidia-open-dkms"),
        (("AD10",), "Ada Lovelace", "nvidia-open-dkms"),
        (("GA10",), "Ampere", "nvidia-open-dkms"),
        (("TU10", "TU11"), "Turing", "nvidia-open-dkms"),
        (("GV10",), "Volta", "nvidia-580xx-dkms"),
        (("GP10",), "Pascal", "nvidia-580xx-dkms"),
        (("GM10", "GM20"), "Maxwell", "nvidia-580xx-dkms"),
        (
            ("EXK107", "GK10", "GK11", "GK18", "GK20", "GK21"),
            "Kepler",
            "nvidia-470xx-dkms",
        ),
        (("EXMF1", "GF10", "GF11"), "Fermi", "nvidia-390xx-dkms"),
        (("Kal-El", "Tegra 2", "Wayne"), "VLIW Vec4", "nvidia-390xx-dkms"),
        (
            (
                "C77", "C78", "C79", "C7A", "G80", "G84", "G86", "G92",
                "G94", "G96", "G98", "ION", "C87", "C89", "GT20", "GT21",
            ),
            "Tesla",
            "nvidia-340xx-dkms",
        ),
        # Curie / Rankine / Kelvin / Celsius / Fahrenheit are not supported by
        # any packaged driver anymore. Kept for explicit detection so we can
        # give a clear error message instead of falling through to
        # "unidentified".
    ]

    UNSUPPORTED_GENERATIONS: Dict[Tuple[str, ...], str] = {
        ("C51", "C61", "C67", "C68", "C73", "G70", "G71", "G72", "G73",
         "NV40", "NV41", "NV42", "NV43", "NV44", "NV45", "NV48", "RSX"): "Curie",
        ("NV30", "NV31", "NV34", "NV35", "NV36", "NV37", "NV38", "NV39"): "Rankine",
        ("NV20", "NV25", "NV28", "NV2A"): "Kelvin",
        ("Crush1", "NV10", "NV11", "NV15", "NV17", "NV18"): "Celsius",
        ("NV4", "NV5"): "Fahrenheit",
    }

    @staticmethod
    def _read_lspci() -> str:
        try:
            result = subprocess.run(
                ["lspci", "-nn"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Failed to run lspci: {e}")
            return ""

    @staticmethod
    def detect_all() -> Dict[str, DetectedGpu]:
        """Detect every VGA/3D controller on the system.

        Returns a dict keyed by vendor (``nvidia``/``intel``/``amd``). If the
        same vendor appears on multiple devices the first one wins, which is
        enough for driver selection purposes.
        """
        lspci_output = GpuDetector._read_lspci()
        if not lspci_output:
            return {}

        detected: Dict[str, DetectedGpu] = {}
        # Only look at VGA compatible and 3D controllers. lspci formats these
        # as "VGA compatible controller [0300]: ..." so we match the controller
        # type without the trailing class code/colon.
        gpu_line_re = re.compile(
            r"^\S+\s+(VGA compatible controller|3D controller)", re.M
        )

        for match in gpu_line_re.finditer(lspci_output):
            line = lspci_output[match.start(): lspci_output.find("\n", match.start())]
            vendor = NONE
            name = line

            # Vendor detection relies on the explicit vendor fragments lspci
            # emits, not loose substring matches: e.g. "compatible" contains
            # "ATI" and would otherwise mis-detect every card as AMD.
            if "NVIDIA" in line.upper():
                vendor = NVIDIA
                name = re.sub(r".*NVIDIA Corporation\s*", "", line)
            elif "[AMD/ATI]" in line or "Advanced Micro Devices" in line:
                vendor = AMD
                name = re.sub(
                    r".*(Advanced Micro Devices|ATI Technologies).*?\[AMD/ATI\]\s*",
                    "", line,
                )
            elif "Intel Corporation" in line:
                vendor = INTEL
                name = re.sub(r".*Intel Corporation\s*", "", line)

            if vendor != NONE and vendor not in detected:
                detected[vendor] = DetectedGpu(vendor=vendor, name=name.strip())

        return detected

    @staticmethod
    def detect_nvidia_driver(gpu_name: str) -> Tuple[str, str]:
        """Map an NVIDIA GPU name to (driver_package, generation).

        Returns ``(driver, generation)`` where ``driver`` is one of the
        ``nvidia-*-dkms`` packages, ``unsupported`` or ``unidentified``.
        """
        for codenames, generation, driver in GpuDetector.NVIDIA_GENERATIONS:
            if any(code in gpu_name for code in codenames):
                return driver, generation

        for codenames, generation in GpuDetector.UNSUPPORTED_GENERATIONS.items():
            if any(code in gpu_name for code in codenames):
                return "unsupported", generation

        return "unidentified", "Unknown"
