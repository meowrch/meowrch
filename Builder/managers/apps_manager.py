from .custom_apps.firefox import FirefoxConfigurer
from .custom_apps.grub import GrubConfigurer
from .custom_apps.pawlette import PawletteConfigurer
from .custom_apps.plymouth import PlymouthConfigurer
from .custom_apps.sddm import SDDMConfigurer
from .custom_apps.vscode import VSCodeConfigurer
from .custom_apps.mewline import MewlineConfigurer


class AppsManager:
    @staticmethod
    def configure_plymouth(allow_grub_config: bool = True) -> None:
        PlymouthConfigurer(allow_grub_config=allow_grub_config).setup()

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
        vot: bool,
    ) -> None:
        FirefoxConfigurer(
            darkreader=darkreader,
            ublock=ublock,
            twp=twp,
            unpaywall=unpaywall,
            vot=vot,
        ).setup()

    @staticmethod
    def configure_grub() -> None:
        GrubConfigurer().setup()

    @staticmethod
    def configure_pawlette() -> None:
        PawletteConfigurer().setup()

    @staticmethod
    def configure_mewline() -> None:
        MewlineConfigurer().setup()