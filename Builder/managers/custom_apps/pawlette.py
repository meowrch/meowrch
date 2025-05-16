import ast
import json
import subprocess
import traceback

from loguru import logger

from .base import AppConfigurer


class PawletteConfigurer(AppConfigurer):
    def setup(self) -> None:
        try:
            self._install_available_themes()
        except Exception:
            logger.error(f"Pawlette main setup error: {traceback.format_exc()}")

    def _parse_themes(self, raw: str) -> dict:
        """Пытается распарсить вывод разными способами"""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed JSON parse, trying literal eval")
            try:
                data = ast.literal_eval(raw)
                if isinstance(data, dict):
                    return data
                raise ValueError("Not a dictionary")
            except Exception:
                logger.error("All parsing attempts failed")
                raise

    def _install_available_themes(self) -> None:
        try:
            result = subprocess.run(
                ["pawlette", "get-available-themes"],
                capture_output=True,
                text=True,
                check=True,
            )

            try:
                themes = self._parse_themes(result.stdout.strip())
            except Exception:
                logger.error(traceback.format_exc())
                raise

            if not isinstance(themes, dict):
                raise ValueError("Expected dictionary of themes")

            for theme_name in themes:
                try:
                    self._install_theme(theme_name)
                except Exception as e:
                    logger.error(f"Skipping theme {theme_name}: {e}")
                    continue
        except Exception:
            logger.error(f"Theme data parsing failed: {traceback.format_exc()}")

    def _install_theme(self, theme_name: str) -> None:
        """Логика установки темы без изменений"""
        try:
            logger.info("Installing theme: {}", theme_name)
            subprocess.run(
                ["pawlette", "install-theme", theme_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.success(f"Theme {theme_name} installed")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Install failed: {e.stderr.strip() or 'Unknown error'}"
            ) from e
