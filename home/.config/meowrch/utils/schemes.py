import logging
from pathlib import Path
from typing import List, Any
from dataclasses import dataclass, field
from abc import abstractmethod

from vars import SESSION_TYPE


@dataclass(kw_only=True)
class BaseOption:
	_id: str
	xorg_needed: bool = field(default=True)
	wayland_needed: bool = field(default=True)

	def apply(self, theme_name: str) -> None:
		if SESSION_TYPE == "wayland" and not self.wayland_needed:
			logging.debug(f"Setting the {self._id} config is omitted! This is not required for wayland!")
			return
		elif SESSION_TYPE == "x11" and not self.xorg_needed:
			logging.debug(f"Setting the {self._id} config is omitted! This is not required for x11!")
			return

		self._run(theme_name)

	@abstractmethod
	def _run(self, theme_name: str) -> Any: ...


@dataclass
class Theme:
	name: str
	available_wallpapers: List[Path]
	icon: Path
