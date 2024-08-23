import inquirer
import subprocess
from typing import List, Union, Dict
from inquirer.themes import GreenPassion
from inquirer import Checkbox as QuestionCheckbox, List as QuestionList

from .banner import banner
from .drivers import Drivers
from .schemes import BuildOptions


answers_type = Dict[str, Union[str, List[str]]]


class Questionaire:
    @staticmethod
    def get_answers() -> BuildOptions:
        drivers = Drivers.auto_detection()

        answers: Questionaire.answers_type = {}
        quests: List[Union[QuestionCheckbox, QuestionList]] = [
            QuestionList(
                name='enable_multilib',
                message="1) Should I enable the multilib repository?",
                choices=["Yes", "No"],
                default="Yes",
                carousel=True
            ),
            QuestionList(
                name='update_arch_database',
                message="2) Update Arch DataBase?",
                choices=["Yes", "No"],
                default="Yes",
                carousel=True
            ),
            QuestionList(
                name='install_game_depends',
                message="3) Install game dependencies?",
                choices=["Yes", "No"],
                carousel=True
            ),
			QuestionList(
                name='install_social_media_depends',
                message="4) Install social-media dependencies?",
                choices=["Yes", "No"],
                carousel=True
            ),
            QuestionCheckbox(
                name='install_drivers',
                message="5) What drivers do you want to install?",
                choices=["Nvidia", "Intel", "AMD"],
                default=drivers,
                carousel=True
            ),
        ]

        for question in quests:
            subprocess.run("clear", shell=True)
            print(banner)
            answer = inquirer.prompt([question], theme=GreenPassion())
            answers.update(answer)

        return BuildOptions(
            enable_multilib=answers['enable_multilib'] == 'Yes',
            update_arch_database=answers['update_arch_database'] == 'Yes',
            install_game_depends=answers['install_game_depends'] == 'Yes',
			install_social_media_depends=answers['install_social_media_depends'] == 'Yes',
            install_drivers=len(answers['install_drivers']) > 0,
            intel_driver='Intel' in answers['install_drivers'],
            nvidia_driver='Nvidia' in answers['install_drivers'],
            amd_driver='AMD' in answers['install_drivers'],
        )
