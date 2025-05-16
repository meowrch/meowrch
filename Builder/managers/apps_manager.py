from .custom_apps.firefox import FirefoxConfigurer
from .custom_apps.grub import GrubConfigurer
from .custom_apps.pawlette import PawletteConfigurer
from .custom_apps.plymouth import PlymouthConfigurer
from .custom_apps.sddm import SDDMConfigurer
from .custom_apps.vscode import VSCodeConfigurer


class AppsManager:
    @staticmethod
    def configure_plymouth() -> None:
        PlymouthConfigurer().setup()

    @staticmethod
    def configure_sddm() -> None:
        SDDMConfigurer().setup()

    @staticmethod
    def configure_code() -> None:
        VSCodeConfigurer().setup()

    @staticmethod
    def configure_firefox(
        darkreader: bool,
        ublock: bool,
        twp: bool,
        unpaywall: bool,
        tampermonkey: bool,
    ) -> None:
        FirefoxConfigurer(
            darkreader=darkreader,
            ublock=ublock,
            twp=twp,
            unpaywall=unpaywall,
            tampermonkey=tampermonkey,
        ).setup()

    @staticmethod
    def configure_grub() -> None:
        GrubConfigurer().setup()

    @staticmethod
    def configure_pawlette() -> None:
        PawletteConfigurer().setup()
