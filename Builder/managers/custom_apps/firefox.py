import glob
import os
import sqlite3
import subprocess
import time
import traceback
import uuid

from loguru import logger

from .base import AppConfigurer


class FirefoxConfigurer(AppConfigurer):
    def __init__(
        self,
        darkreader: bool,
        ublock: bool,
        twp: bool,
        unpaywall: bool,
        tampermonkey: bool,
    ):
        self.plugins = [
            (darkreader, "addon@darkreader.org.xpi"),
            (ublock, "uBlock0@raymondhill.net.xpi"),
            (twp, "{036a55b4-5e72-4d05-a06c-cba2dfcc134a}.xpi"),
            (unpaywall, "{f209234a-76f0-4735-9920-eb62507a54cd}.xpi"),
            (tampermonkey, "firefox@tampermonkey.net.xpi"),
            (True, "ATBC@EasonWong.xpi"),  # Always enable Adaptive Tab Bar Color
        ]

    def setup(self) -> None:
        logger.info("Start installing Firefox")
        error_msg = "Error installing firefox: {err}"
        try:
            self._init_firefox_profile()
            self._copy_profile()
            self._fetch_latest_plugins()
            self._install_firefox_gnome_theme()
            self._configure_theme_preferences()
            self._create_meowrch_bookmark()
            self._cleanup_plugins()
            logger.success("Firefox has been successfully installed!")
        except subprocess.CalledProcessError as e:
            logger.error(error_msg.format(err=e.stderr))
        except Exception:
            logger.error(error_msg.format(err=traceback.format_exc()))

    def _init_firefox_profile(self) -> None:
        subprocess.Popen(["timeout", "2", "firefox", "--headless"])
        time.sleep(3)

    def _copy_profile(self) -> None:
        # Profile initialization is handled by _init_firefox_profile
        # We no longer copy from misc/apps/firefox as we install everything fresh
        logger.info("Profile setup completed")

    def _install_firefox_gnome_theme(self) -> None:
        """Install Firefox GNOME Theme manually with auto-update system"""
        logger.info("Installing Firefox GNOME Theme...")

        # Get Firefox profile path
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]

        # Create chrome directory
        chrome_dir = os.path.join(path_profile, "chrome")
        os.makedirs(chrome_dir, exist_ok=True)

        # Clone or update the theme repository
        theme_repo_path = os.path.join(chrome_dir, "firefox-gnome-theme")

        if os.path.exists(theme_repo_path):
            # Update existing theme
            logger.info("Updating existing Firefox GNOME Theme...")
            subprocess.run(["git", "pull"], cwd=theme_repo_path, check=True)
        else:
            # Clone theme repository
            logger.info("Cloning Firefox GNOME Theme repository...")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/rafaelmardojai/firefox-gnome-theme.git",
                    theme_repo_path,
                ],
                check=True,
            )

        # Create userChrome.css
        user_chrome_path = os.path.join(chrome_dir, "userChrome.css")
        with open(user_chrome_path, "w") as f:
            f.write('@import "firefox-gnome-theme/userChrome.css";\n')

        # Create userContent.css
        user_content_path = os.path.join(chrome_dir, "userContent.css")
        with open(user_content_path, "w") as f:
            f.write('@import "firefox-gnome-theme/userContent.css";\n')

        # Set up auto-update system
        self._setup_theme_auto_update(theme_repo_path)

    def _configure_theme_preferences(self) -> None:
        """Configure Firefox preferences for theme and custom settings"""
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]

        # Create or update user.js with theme preferences
        user_js_path = os.path.join(path_profile, "user.js")

        # Theme and custom preferences
        preferences = [
            "// Firefox GNOME Theme preferences",
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
            'user_pref("svg.context-properties.content.enabled", true);',
            'user_pref("browser.theme.dark-private-windows", false);',
            'user_pref("widget.gtk.rounded-bottom-corners.enabled", true);',
            'user_pref("browser.uidensity", 0);',
            "",
            "// Custom theme preferences",
            'user_pref("gnomeTheme.extensions.adaptiveTabBarColour", true);  // Enable Adaptive Tab Bar Color support',
            'user_pref("gnomeTheme.tabAlignLeft", true);                      // Align tabs to left',
            'user_pref("gnomeTheme.normalWidthTabs", true);                   // Use normal width tabs',
            "",
            "// Extension preferences - Auto-enable ATBC",
            'user_pref("extensions.autoDisableScopes", 0);  // Auto-enable all extensions',
            'user_pref("extensions.enabledScopes", 15);  // Enable extensions in all scopes',
            'user_pref("xpinstall.signatures.required", false);  // Allow unsigned extensions',
            "",
            "// Startup settings - restore sessions",
            'user_pref("browser.startup.page", 3);  // Restore previous session',
            'user_pref("browser.sessionstore.resume_from_crash", true);',
            "",
            "// Disable extension welcome tabs and first-run pages",
            'user_pref("extensions.getAddons.showPane", false);',
            'user_pref("extensions.htmlaboutaddons.recommendations.enabled", false);',
            'user_pref("extensions.getAddons.discovery.api_url", "");',
            'user_pref("extensions.ui.dictionary.hidden", true);',
            'user_pref("extensions.ui.locale.hidden", true);',
            'user_pref("extensions.update.autoUpdateDefault", false);',
            "// Note: Tampermonkey welcome tab cannot be disabled programmatically",
            "",
        ]

        # Read existing user.js if it exists
        existing_prefs = []
        if os.path.exists(user_js_path):
            with open(user_js_path, "r") as f:
                existing_prefs = f.readlines()

        # Remove old theme preferences
        filtered_prefs = []
        skip_keys = [
            "toolkit.legacyUserProfileCustomizations.stylesheets",
            "svg.context-properties.content.enabled",
            "browser.theme.dark-private-windows",
            "widget.gtk.rounded-bottom-corners.enabled",
            "browser.uidensity",
            "gnomeTheme.",
            "browser.startup.homepage",
            "browser.startup.page",
            "extensions.webextensions.uuids",
            "browser.sessionstore.resume_from_crash",
        ]

        for line in existing_prefs:
            line_stripped = line.strip()
            if line_stripped.startswith("user_pref("):
                should_skip = any(key in line for key in skip_keys)
                if not should_skip:
                    filtered_prefs.append(line)
            elif not line_stripped.startswith("//"):
                filtered_prefs.append(line)

        # Write updated user.js
        with open(user_js_path, "w") as f:
            # Write existing non-theme preferences
            for line in filtered_prefs:
                f.write(line)

            # Write new theme preferences
            for pref in preferences:
                f.write(pref + "\n")

        logger.info("Firefox theme preferences configured")

    def _setup_theme_auto_update(self, theme_repo_path: str) -> None:
        """Set up automatic theme updates using systemd user timer"""
        logger.info("Setting up Firefox theme auto-update system...")

        # Create update script
        update_script_dir = os.path.expanduser("~/.local/bin")
        os.makedirs(update_script_dir, exist_ok=True)

        update_script_path = os.path.join(
            update_script_dir, "update-firefox-gnome-theme.sh"
        )

        update_script_content = f'''#!/bin/bash
# Firefox GNOME Theme Auto-Update Script

THEME_DIR="{theme_repo_path}"
LOG_FILE="$HOME/.local/share/firefox-theme-update.log"

echo "$(date): Checking for Firefox GNOME Theme updates..." >> "$LOG_FILE"

cd "$THEME_DIR" || exit 1

# Check if there are updates available
if git fetch && [[ $(git rev-list HEAD...origin/master --count) -gt 0 ]]; then
    echo "$(date): Updates found, updating theme..." >> "$LOG_FILE"
    git pull origin master
    echo "$(date): Firefox GNOME Theme updated successfully" >> "$LOG_FILE"
else
    echo "$(date): No updates available" >> "$LOG_FILE"
fi
'''

        with open(update_script_path, "w") as f:
            f.write(update_script_content)

        # Make script executable
        os.chmod(update_script_path, 0o755)

        # Create systemd user service
        systemd_user_dir = os.path.expanduser("~/.config/systemd/user")
        os.makedirs(systemd_user_dir, exist_ok=True)

        service_content = f"""[Unit]
Description=Firefox GNOME Theme Auto-Update

[Service]
Type=oneshot
ExecStart={update_script_path}
"""

        service_path = os.path.join(systemd_user_dir, "firefox-theme-update.service")
        with open(service_path, "w") as f:
            f.write(service_content)

        # Create systemd user timer (check for updates at startup and daily)
        timer_content = """[Unit]
Description=Firefox GNOME Theme Auto-Update Timer
Requires=firefox-theme-update.service

[Timer]
OnBootSec=2min
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""

        timer_path = os.path.join(systemd_user_dir, "firefox-theme-update.timer")
        with open(timer_path, "w") as f:
            f.write(timer_content)

        # Enable and start the timer
        try:
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            subprocess.run(
                ["systemctl", "--user", "enable", "firefox-theme-update.timer"],
                check=True,
            )
            subprocess.run(
                ["systemctl", "--user", "start", "firefox-theme-update.timer"],
                check=True,
            )
            logger.info("Firefox theme auto-update system configured successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to set up auto-update timer: {e}")

    def _fetch_latest_plugins(self) -> None:
        """Download latest versions of the plugins from official sources"""
        logger.info("Fetching latest plugins...")
        plugin_urls = {
            "addon@darkreader.org.xpi": "https://addons.mozilla.org/firefox/downloads/latest/darkreader/latest.xpi",
            "uBlock0@raymondhill.net.xpi": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi",
            "{036a55b4-5e72-4d05-a06c-cba2dfcc134a}.xpi": "https://addons.mozilla.org/firefox/downloads/latest/traduzir-paginas-web/latest.xpi",
            "{f209234a-76f0-4735-9920-eb62507a54cd}.xpi": "https://addons.mozilla.org/firefox/downloads/latest/unpaywall/latest.xpi",
            "firefox@tampermonkey.net.xpi": "https://addons.mozilla.org/firefox/downloads/latest/tampermonkey/latest.xpi",
            "ATBC@EasonWong.xpi": "https://addons.mozilla.org/firefox/downloads/latest/adaptive-tab-bar-colour/latest.xpi",
        }

        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]
        extension_dir = os.path.join(path_profile, "extensions")

        # Ensure extensions directory exists
        os.makedirs(extension_dir, exist_ok=True)

        for plugin_file, url in plugin_urls.items():
            try:
                logger.info(f"Downloading {plugin_file}...")
                plugin_path = os.path.join(extension_dir, plugin_file)
                cmd = ["curl", "-L", "--silent", "--fail", "-o", plugin_path, url]
                result = subprocess.run(
                    cmd, check=False, capture_output=True, text=True
                )

                if (
                    result.returncode == 0
                    and os.path.exists(plugin_path)
                    and os.path.getsize(plugin_path) > 0
                ):
                    logger.success(f"Successfully downloaded {plugin_file}")
                else:
                    logger.warning(f"Failed to download {plugin_file}, skipping...")

            except Exception as e:
                logger.error(f"Error downloading {plugin_file}: {e}")

    def _create_meowrch_bookmark(self) -> None:
        """Create Meowrch Wiki bookmark by adding to places.sqlite database"""
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]

        # Path to places.sqlite database
        places_db_path = os.path.join(path_profile, "places.sqlite")

        # Ensure Firefox is not running before modifying database
        subprocess.run(["pkill", "firefox"], check=False)
        time.sleep(2)  # Increased wait time

        try:
            conn = sqlite3.connect(places_db_path)
            cursor = conn.cursor()

            # Generate unique GUIDs
            place_guid = str(uuid.uuid4())
            bookmark_guid = str(uuid.uuid4())

            # Current timestamp in microseconds
            timestamp = int(time.time() * 1000000)

            logger.info(f"Adding bookmark with place_guid: {place_guid}")
            logger.info(f"Adding bookmark with bookmark_guid: {bookmark_guid}")

            # Step 1: Add URL to moz_places
            cursor.execute(
                """
INSERT OR REPLACE INTO moz_places 
                (url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date, guid)
                VALUES (?, ?, ?, 0, 0, 0, -1, ?, ?)
            """,
                (
                    "https://meowrch.github.io/",
                    "Meowrch Wiki",
                    "oi.buhtig.hcrwoem",  # reversed hostname
                    timestamp,
                    place_guid,
                ),
            )

            # Get the place_id
            cursor.execute(
                "SELECT id FROM moz_places WHERE url = ?",
                ("https://meowrch.github.io/",),
            )
            place_result = cursor.fetchone()

            if place_result:
                place_id = place_result[0]
                logger.info(f"Place ID: {place_id}")

                # Get toolbar folder id (correct GUID)
                cursor.execute(
                    "SELECT id FROM moz_bookmarks WHERE guid = ?", ("toolbar_____",)
                )
                toolbar_result = cursor.fetchone()

                if toolbar_result:
                    toolbar_id = toolbar_result[0]
                    logger.info(f"Toolbar ID: {toolbar_id}")

                    # Get current position in toolbar
                    cursor.execute(
                        "SELECT COUNT(*) FROM moz_bookmarks WHERE parent = ?",
                        (toolbar_id,),
                    )
                    position = cursor.fetchone()[0]
                    logger.info(f"Position: {position}")

                    # Step 2: Add bookmark to moz_bookmarks
                    cursor.execute(
                        """
INSERT OR REPLACE INTO moz_bookmarks 
                        (type, fk, parent, position, title, dateAdded, lastModified, guid)
                        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            place_id,
                            toolbar_id,
                            position,
                            "Meowrch Wiki",
                            timestamp,
                            timestamp,
                            bookmark_guid,
                        ),
                    )

                    conn.commit()
                    logger.success(
                        "Successfully added Meowrch Wiki to bookmarks toolbar"
                    )
                    
                    # Verify the bookmark was added
                    cursor.execute(
                        "SELECT id, parent, title, guid FROM moz_bookmarks WHERE parent = ?",
                        (toolbar_id,),
                    )
                    verification = cursor.fetchall()
                    logger.info(f"Toolbar bookmarks after addition: {verification}")
                    
                else:
                    logger.warning("Could not find bookmarks toolbar")
            else:
                logger.warning("Could not create place entry")

        except sqlite3.Error as e:
            logger.error(f"SQLite error while creating bookmark: {e}")
        except Exception as e:
            logger.error(f"Error creating bookmark: {e}")
        finally:
            if conn:
                conn.close()

        # Also ensure bookmarks toolbar is visible
        user_js_path = os.path.join(path_profile, "user.js")
        with open(user_js_path, "a") as f:
            f.write("\n// Show bookmarks toolbar\n")
            f.write('user_pref("browser.toolbars.bookmarks.visibility", "always");\n')

        logger.info("Meowrch Wiki bookmark configuration completed")

    def _cleanup_plugins(self) -> None:
        path_profile = glob.glob(
            os.path.expanduser("~/.mozilla/firefox/*.default-release")
        )[0]
        for enabled, plugin_file in self.plugins:
            if not enabled:
                try:
                    os.remove(os.path.join(path_profile, "extensions", plugin_file))
                except Exception:
                    pass
