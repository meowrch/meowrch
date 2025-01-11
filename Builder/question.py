from typing import Dict, List, Union

import inquirer
from colorama import Fore
from inquirer import Checkbox as QuestionCheckbox
from inquirer import List as QuestionList
from managers.drivers_manager import DriversManager
from packages import CUSTOM
from utils.banner import clear_and_banner
from utils.schemes import BuildOptions, AurHelper


class Question:
    answers_type = Dict[str, Union[str, List[str]]]

    @staticmethod
    def _choose_custom_packages() -> None:
        selected_packages = {}
        complete_btn_text = Fore.GREEN + "Complete the survey"

        while True:
            clear_and_banner()

            selected_counts = {
                category: sum(
                    1 for pkg in packages.values() if getattr(pkg, "selected", False)
                )
                for category, packages in CUSTOM.items()
            }

            category_question = inquirer.List(
                "category",
                message="8) Select a category of packages and choose the ones you want",
                choices=list(
                    category
                    + f" | {Fore.YELLOW}Selected: {selected_counts[category]}"
                    for category in CUSTOM.keys()
                )
                + [complete_btn_text],
                carousel=True,
            )

            category_answer = inquirer.prompt([category_question])
            selected_category = category_answer["category"].split(" | ")[0]

            if selected_category == complete_btn_text:
                break

            package_choices = sorted(
                [(name, info) for name, info in CUSTOM[selected_category].items()],
                key=lambda item: not item[1].recommended,
            )

            package_choices = [
                f"{name} | {Fore.YELLOW + 'Recommended' + Fore.RESET + ' | ' if info.recommended else ''}{info.description}"
                for name, info in package_choices
            ]
            previous_selection = [
                f"{name} | {Fore.YELLOW + 'Recommended' + Fore.RESET + ' | ' if info.recommended else ''}{info.description}"
                for name, info in CUSTOM[selected_category].items()
                if info.selected
            ]

            clear_and_banner()

            package_question = inquirer.Checkbox(
                "packages",
                message=f'Choose the packages from category "{selected_category}"',
                choices=package_choices,
                default=previous_selection,
                carousel=True,
            )

            package_answer = inquirer.prompt([package_question])
            selected_packages = [
                pkg.split(" | ")[0] for pkg in package_answer["packages"]
            ]
            for name, info in CUSTOM[selected_category].items():
                if name in selected_packages:
                    info.selected = True
                else:
                    info.selected = False

    @staticmethod
    def get_answers():
        drivers = DriversManager.auto_detection()
        answers: Question.answers_type = {}
        firefox_choices = [
            f"Dark Reader | {Fore.YELLOW}Changes light themes to dark themes on all sites",
            f"uBlock Origin | {Fore.YELLOW}Blocks ads",
            f"TWP | {Fore.YELLOW}Translator for text and whole pages",
            f"Unpaywall | {Fore.YELLOW}View paid article content",
            f"Tamper Monkey | {Fore.YELLOW}Custom Script Manager. {Fore.RED}"
                "(Used by me to translate videos in real time)"
        ]

        quests: List[Union[QuestionCheckbox, QuestionList]] = [
            QuestionList(
                name="make_backup",
                message="1) Want to backup your configurations?",
                choices=["Yes", "No"],
                default="Yes",
                carousel=True,
            ),
            QuestionCheckbox(
                name="install_wm",
                message="2) Which window manager do you want to install?",
                choices=["hyprland", "bspwm"],
                default=["bspwm", "hyprland"],
                carousel=True,
            ),
            QuestionList(
                name="aur_helper",
                message="3) What kind of AUR helper do you want to have?",
                choices=["yay", "paru"],
                default="paru",
                carousel=True,
            ),
            QuestionList(
                name="enable_multilib",
                message="4) Should I enable the multilib repository?",
                choices=["Yes", "No"],
                default="Yes",
                carousel=True,
            ),
            QuestionList(
                name="update_arch_database",
                message="5) Update Arch DataBase?",
                choices=["Yes", "No"],
                default="Yes",
                carousel=True,
            ),
            QuestionCheckbox(
                name="install_drivers",
                message="6) What drivers do you want to install?",
                choices=["Nvidia", "Intel", "AMD"],
                default=drivers,
                carousel=True,
            ),
            QuestionCheckbox(
                name="ff_plugins",
                message="7) Would you like to add useful plugins for firefox?",
                choices=firefox_choices,
                default=firefox_choices,
                carousel=True,
            ),
        ]

        for question in quests:
            clear_and_banner()
            answer = inquirer.prompt([question])
            answers.update(answer)

        Question._choose_custom_packages()
        answers["ff_plugins"] = [
            i.split(" | ")[0] for i in answers["ff_plugins"]
        ]

        if answers["aur_helper"] == "paru":
            aur_helper = AurHelper.PARU
        else:
            aur_helper = AurHelper.YAY

        return BuildOptions(
            make_backup=answers["make_backup"] == "Yes",
            install_bspwm="bspwm" in answers["install_wm"],
            install_hyprland="hyprland" in answers["install_wm"],
            aur_helper=aur_helper,
            enable_multilib=answers["enable_multilib"] == "Yes",
            update_arch_database=answers["update_arch_database"] == "Yes",
            install_drivers=len(answers["install_drivers"]) > 0,
            intel_driver="Intel" in answers["install_drivers"],
            nvidia_driver="Nvidia" in answers["install_drivers"],
            amd_driver="AMD" in answers["install_drivers"],
            ff_darkreader="Dark Reader" in answers["ff_plugins"],
            ff_ublock="uBlock Origin" in answers["ff_plugins"],
            ff_twp="TWP" in answers["ff_plugins"],
            ff_unpaywall="Unpaywall" in answers["ff_plugins"],
            ff_tampermonkey="Tamper Monkey" in answers["ff_plugins"]
        )
