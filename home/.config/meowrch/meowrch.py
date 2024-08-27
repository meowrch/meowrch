import logging
from argparse import ArgumentParser, RawTextHelpFormatter

from utils.other import notify
from utils.config import Config
from utils.theming import ThemeManager


def setting_args(parser: ArgumentParser):
	main_group = parser.add_argument_group('Required arguments')
	main_group.add_argument(
		'--action', 
		required=True, 
		help="The type of action you are trying to perform.\n" \
			"Types:\n" \
			"\"get\": Get the value from the config. When specifying this type, you need to specify an" \
			"additional argument \"--parameter\" with the name of the required parameter from the config\n" \

			"\"set-theme\": When specifying this type, you need to specify an additional argument \"--name\" with the name of the topic\n" \
			"\"set-wallpaper\": When specifying this type, you need to specify an additional argument \"--path\" with the path to the wallpaper.\n" \
			"If the path has not been passed, the current wallpaper will be set\n" \

			"\"set-random-wallpaper\": Random wallpapers are set, which are allowed in the theme.\n" \
			"\"select-wallpaper\": A Rofi menu with a selection of wallpapers and their subsequent installation.\n" \
			"\"select-theme\": Rofi menu with theme selection and its subsequent installation."
	)

	auxiliary_group = parser.add_argument_group('Auxiliary arguments')
	auxiliary_group.add_argument(
		'--parameter', 
		help='The requested object from the config. It is applied with the \"get\" action.'
	)
	auxiliary_group.add_argument(
		'--name', 
		help='The name of the theme for the action \"set-theme\"'
	)
	auxiliary_group.add_argument(
		'--path', 
		help='The path for the wallpaper for the action \"set-wallpaper\"'
	)


if __name__ == '__main__':
	logging.info("========================================== PROGRAM STARTED ==========================================")

	##==> Настройка принимаемых аргументов
	###############################################
	parser = ArgumentParser(description='Transform your meowch beyond recognition!', formatter_class=RawTextHelpFormatter)
	setting_args(parser)
	args = parser.parse_args()
	logging.debug(f"Passed arguments: {args}")

	##==> Инициализируем менеджер тем
	###############################################
	if args.action != "get": # Для ускорения обработки get запросов
		theme_manager = ThemeManager()

	##==> Обработка действий пользователя
	###############################################
	if args.action == "get":
		if args.parameter == "current-wallpaper":
			print(Config.get_current_wallpaper())
		elif args.parameter == "current-theme":
			print(Config.get_current_theme())
		else:
			logging.error(f"Unknown get parameter: {args.parameter}")

	elif args.action == "set-theme":
		if args.name:
			theme_manager.set_theme(args.name)
		else:
			logging.error("The \"name\" parameter is required for the \"set-theme\" action.")

	elif args.action == "set-current-theme":
		theme_manager.set_current_theme()

	elif args.action == "set-wallpaper":
		if args.path:
			theme_manager.set_wallpaper(args.path)
		else:
			theme_manager.set_current_wallpaper()

	elif args.action == "set-random-wallpaper":
		theme_manager.set_random_wallpaper()

	elif args.action == "select-wallpaper":
		theme_manager.select_wallpaper()

	elif args.action == "select-theme":
		theme_manager.select_theme()

	else:
		logging.debug(f"Unknown action: {args.action}")
		notify("Unknown action!", "Check the available actions with --help")

	logging.info("========================================== PROGRAM FINISHED ==========================================")
		