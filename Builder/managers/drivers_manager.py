import traceback
import subprocess
from typing import List
from loguru import logger

from .package_manager import PackageManager


class DriversManager:
	@staticmethod
	def get_gpu_vendor() -> str:
		try:
			output = subprocess.check_output("lspci | grep -E 'VGA|3D'", shell=True).decode()
			if "NVIDIA" in output:
				return "Nvidia"
			elif "AMD" in output:
				return "AMD"
			elif "Intel" in output:
				return "Intel"
		except Exception:
			logger.error(f"Error processing GPU vendor: {traceback.format_exc()}")

		return "unknown"

	@staticmethod
	def get_cpu_vendor() -> str:
		try:
			output = subprocess.check_output("lscpu", shell=True).decode()
			if "GenuineIntel" in output:
				return "Intel"
			elif "AuthenticAMD" in output:
				return "AMD"
		except Exception:
			logger.error(f"Error processing CPU vendor: {traceback.format_exc()}")

		return "unknown"

	@staticmethod
	def auto_detection() -> List[str]:
		cpu = DriversManager.get_cpu_vendor()
		gpu = DriversManager.get_gpu_vendor()
		drivers_for = [cpu, gpu]

		if "unknown" in drivers_for:
			drivers_for.remove("unknown")

		return drivers_for

	@staticmethod
	def install_intel_drivers() -> None:
		PackageManager.install_packages(
			packages_list=[
				"lib32-mesa", "vulkan-intel", "lib32-vulkan-intel", 
				"vulkan-icd-loader", "lib32-vulkan-icd-loader", "intel-media-driver",
				"libva-intel-driver", "xf86-video-intel"
			]
		)

	@staticmethod
	def install_amd_drivers() -> None:
		PackageManager.install_packages(
			packages_list=[
				"lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon", 
				"vulkan-icd-loader", "lib32-vulkan-icd-loader"
			]
		)

	@staticmethod
	def install_nvidia_drivers() -> None:
		PackageManager.install_packages(
			packages_list=[
				"nvidia-dkms", "nvidia-utils", "lib32-nvidia-utils",
				"nvidia-settings", "vulkan-icd-loader", "lib32-vulkan-icd-loader",
				"lib32-opencl-nvidia", "opencl-nvidia", "libxnvctrl"
			]
		)
