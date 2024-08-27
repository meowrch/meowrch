
class InvalidSession(Exception):
	session: str
	def __init__(self, session: str) -> None:
		self.session = session

	def __str__(self):
		return f"Invalid session: {self.session}"
		

class NoThemesToInstall(Exception):
	def __str__(self):
		return "Missing Themes. You must provide at least one."


class NoConfigFile(Exception):
	def __str__(self):
		return "Missing config file. Please create and customize config.yaml"