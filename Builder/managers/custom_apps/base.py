class AppConfigurer:
    """Base class for application configurers"""
    def setup(self) -> None:
        raise NotImplementedError