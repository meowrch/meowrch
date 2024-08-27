import re
import shutil
import logging
import traceback
import subprocess
from typing import List
from pathlib import Path
from dataclasses import dataclass, field

from .schemes import BaseOption
from .other import overcopy, generate_theme
from vars import MEOWRCH_THEMES, OOMOX_TEMPLATES, OOMOX_COLORS, BASE_CONFIGS, HOME, SESSION_TYPE


@dataclass
class CopyOption(BaseOption):
	name: str
	path_to: str
	is_dir: bool = field(default=False)

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists():
			if self.is_dir and cfg_path.is_dir() or not self.is_dir and cfg_path.is_file():
				overcopy(cfg_path, self.path_to)
				return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)


@dataclass
class CopyOrGenOption(BaseOption):
	name: str
	path_to: str
	template_name: str

	def _run(self, theme_name: str) -> None:
		oomox_colors_path = OOMOX_COLORS(theme_name)
		template_path = OOMOX_TEMPLATES / self.template_name
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)
			return

		if template_path.exists():
			if oomox_colors_path.exists():
				generated_theme = generate_theme(
					template_name=self.template_name,
					oomox_colors=oomox_colors_path,
				)

				if generated_theme is not None:
					with open(self.path_to, "w") as file:
						file.write(generated_theme)	
					return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"!" \
			f"There is no \"{self.name}\" file in the theme folder. No generation option."
		)


@dataclass
class TmuxCfgOption(BaseOption):
	name: str
	path_to: str
	base_config_name: str

	def _run(self, theme_name: str) -> None:
		tmux: Path = self.path_to
		custom_prefs: Path = MEOWRCH_THEMES / theme_name / self.name
		tmux_base: Path = BASE_CONFIGS / self.base_config_name

		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if tmux_base.exists():
			with open(tmux, "w") as f:
				with open(tmux_base, "r") as b:
					f.write(b.read())
				f.write("\n\n")
				with open(custom_prefs, "r") as c:
					f.write(c.read())
		else:
			overcopy(custom_prefs, tmux)

		try:
			if subprocess.run(["pgrep", "tmux"], stdout=subprocess.PIPE).stdout.decode().strip():
				subprocess.run(["tmux", "source", str(tmux)], check=True)
		except Exception:
			logging.warning("Failed to update the theme for tmux in an open session.")


@dataclass
class DunstOption(BaseOption):
	name: str
	path_to: str
	apply_theme: bool

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)

			if self.apply_theme:
				subprocess.Popen(
					['killall', '-HUP', 'dunst'],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True
				)

			return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)


@dataclass
class CavaOption(BaseOption):
	name: str
	path_to: str
	apply_theme: bool

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)

			if self.apply_theme:
				subprocess.Popen(
					['pkill', '-USR1', 'cava'],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True
				)

			return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)


@dataclass
class FishOption(BaseOption):
	name: str
	path_to: str
	apply_theme: bool

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)

			if self.apply_theme:
				subprocess.Popen(
					['fish', '-c', 'echo "y" | fish_config theme save meowrch'],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True
				)

			return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)


@dataclass
class KittyOption(BaseOption):
	name: str
	path_to: str
	template_name: str
	apply_theme: bool

	def apply_kitty_theme(self) -> None:
		if self.apply_theme:
			try:
				result = subprocess.run(['pgrep', 'kitty'], capture_output=True, text=True, check=True)
				pids = result.stdout.strip().split('\n')
				for pid in pids:
					try:
						subprocess.run(['kill', '-SIGUSR1', pid])
					except Exception:
						logging.warning(f"Failed to reload kitty with pid {pid}")
			except Exception:
				logging.warning("Failed to reload kitty.")

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		oomox_colors_path = OOMOX_COLORS(theme_name)
		template_path = OOMOX_TEMPLATES / self.template_name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)
			self.apply_kitty_theme()
			return

		if template_path.exists():
			if oomox_colors_path.exists():
				generated_theme = generate_theme(
					template_name=self.template_name,
					oomox_colors=oomox_colors_path,
				)

				if generated_theme is not None:
					with open(self.path_to, "w") as file:
						file.write(generated_theme)	

					self.apply_kitty_theme()
					return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)

@dataclass
class WaybarCfgOption(BaseOption):
	name: str
	path_to: str
	reload: bool

	def _run(self, theme_name: str) -> None:
		cfg_path = MEOWRCH_THEMES / theme_name / self.name
		
		if not self.path_to.parent.exists():
			logging.error(
				f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
				f"The config cannot be copied to the path \"{self.path_to}\""
			)
			return

		if cfg_path.exists() and cfg_path.is_file():
			overcopy(cfg_path, self.path_to)

			if self.reload:
				try:
					wb_exists = subprocess.run(['pgrep', '-x', 'waybar'], capture_output=True, text=True).stdout
					if wb_exists:
						subprocess.run(['pkill', '-SIGUSR2', 'waybar'], check=True)
				except Exception:
					logging.warning("Failed to reload waybar.")

			return

		logging.error(
			f"Theme \"{theme_name}\" has not been applied to \"{self._id}\"! " \
			f"There is no {'folder' if self.is_dir else 'file'} \"{self.name}\" in the theme folder"
		)

@dataclass
class GTKOption(BaseOption):
	gtk4_template_name: str
	gtk2_cfg: Path
	gtk3_cfg: Path
	gtk4_cfg: Path

	def generate_gtk_2_3(self, path_to_theme: Path, oomox_colors_path: str, theme_name: str) -> bool:
		try:
			subprocess.check_output(["which", "oomox-cli"])
		except subprocess.CalledProcessError:
			logging.error("GTK theme is not installed. A dependency is required - \"oomox\"")
			return False

		try:
			subprocess.run(
				["oomox-cli", oomox_colors_path, "-o", theme_name, "-m", "all", "-d", "true"],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL, 
				check=True
			)
		except Exception:
			logging.error(f"GTK theme is not installed. Failed to generate gtk 2/3 theme: {traceback.format_exc()}")
			return False

		return True

	def generate_gtk_4(self, path_to_theme: Path, gtk4_template: Path, oomox_colors_path: Path) -> bool:
		if not (OOMOX_TEMPLATES / gtk4_template).exists():
			logging.error(f"GTK4 theme is not installed. Template file not found: {gtk4_template}")
			return False
		
		gtk3_path: Path = path_to_theme / "gtk-3.0"
		gtk4_path: Path = path_to_theme / "gtk-4.0"

		generated_gtk4 = generate_theme(template_name=self.gtk4_template_name, oomox_colors=oomox_colors_path)
		if generated_gtk4 is not None:
			if gtk3_path.exists():
				shutil.copytree(str(gtk3_path), str(gtk4_path))
				(gtk4_path/"gtk.gresource").unlink(missing_ok=True)
				(gtk4_path/"gtk.gresource.xml").unlink(missing_ok=True)
				if (gtk4_path/"dist").exists():
					shutil.rmtree(gtk4_path/"dist")
			else:
				gtk4_path.mkdir(parents=True, exist_ok=True)

			with open(str(gtk4_path / "gtk.css"), "w") as file:
				file.write(generated_gtk4)
			
			with open(str(gtk4_path / "gtk-dark.css"), "w") as file:
				file.write(generated_gtk4)
		else:
			logging.warning("The GTK4 theme is not installed due to an unknown error!")
			return False

		return True

	def apply_gtk_themes(self, gtk_configs: List[Path], theme_name: str):
		for gtk_cfg in gtk_configs:
			if not gtk_cfg.parent.exists():
				logging.warning(f"The theme cannot be applied to the \"{gtk_cfg.name}\" file, because the path \"{str(gtk_cfg)}\" does not exist")

			if not gtk_cfg.exists():
				gtk_cfg.touch()

			with open(gtk_cfg, "r") as file:
				content = file.read()
			
			if f"gtk-theme-name={theme_name}" in content:
				continue
			elif "gtk-theme-name=" in content:
				new_content = re.sub(r"gtk-theme-name=.*", f"gtk-theme-name={theme_name}", content)
				with open(gtk_cfg, "w") as file:
					file.write(new_content)
			else:
				with open(gtk_cfg, "a") as file:
					file.write(f"gtk-theme-name={theme_name}\n")

		##==> Установка темы в реальном времени
		############################################
		if SESSION_TYPE == "wayland":
			try:
				subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name], check=True)
			except Exception:
				logging.warning("Failed to set theme with gsettings")
		elif SESSION_TYPE == "x11":
			xsettingsd_config: Path = HOME / ".config" / "xsettingsd" / "xsettingsd.conf"
			if xsettingsd_config.exists():
				with open(xsettingsd_config, "r") as file:
					content = file.read()
				
				if f"Net/ThemeName \"{theme_name}\"" in content:
					return
				elif content.startswith("Net/ThemeName"):
					new_content = re.sub(r"Net/ThemeName .*", f"Net/ThemeName \"{theme_name}\"", content)
					with open(xsettingsd_config, "w") as file:
						file.write(new_content)
				else:
					with open(xsettingsd_config, "a") as file:
						file.write(f"Net/ThemeName \"{theme_name}\"")
						
				try:
					subprocess.run(["killall", "-HUP", "xsettingsd"], check=True)
				except Exception:
					logging.warning("Failed to set theme with xsettingsd")

	def _run(self, theme_name: str) -> None:
		oomox_colors_path: Path = OOMOX_COLORS(theme_name)
		theme_name: str = f"meowrch-{theme_name}"
		path_to_theme: Path = HOME / ".themes" / theme_name

		if not oomox_colors_path.exists():
			logging.error(f"GTK theme is not installed. There is no \"{oomox_colors_path}\" file.")
			return

		##==> Генерация GTK2/3 (Пропускаем если сгенерирована)
		##############################################################
		if not path_to_theme.exists():
			gtk23 = self.generate_gtk_2_3(path_to_theme, str(oomox_colors_path), theme_name)
			if not gtk23:
				return

		##==> Генерация GTK4 (Пропускаем если сгенерирована)
		############################################
		if not (path_to_theme / "gtk-4.0").exists():
			gtk4 = self.generate_gtk_4(path_to_theme, self.gtk4_template_name, oomox_colors_path)

			if not gtk4:
				return

		##==> Применение тем
		############################################
		self.apply_gtk_themes(
			gtk_configs=[self.gtk2_cfg, self.gtk3_cfg, self.gtk4_cfg],
			theme_name=theme_name,
		)
