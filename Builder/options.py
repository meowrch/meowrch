import os
from creators.builder import SystemConfiguration


class UserInterface:
    @staticmethod
    def start():
        UserInterface.welcome_banner()
        install_params = UserInterface.get_params()
        SystemConfiguration.start(*install_params)

    @staticmethod
    def welcome_banner():
        os.system("sh Builder/assets/startup.sh")        

    @staticmethod
    def is_verify_response(text) -> bool:
        if "y" in text.lower():
            return True
        else:
            return False

    @staticmethod
    def get_params():
        print("1) Install all dotfiles? [Y/n]: ", end="")
        option_1 = UserInterface.is_verify_response(input())
        
        print("2) Update Arch DataBase? [Y/n] ", end="")
        option_2 = UserInterface.is_verify_response(input())

        print("3) Install BSPWM Dependencies? [Y/n] ", end="")
        option_3 = UserInterface.is_verify_response(input())

        print("4) Install Dev Dependencies? [Y/n] ", end="")
        option_4 = UserInterface.is_verify_response(input())
        
        print("5) Install Nvidia & Intel Drivers? [Y/n] ", end="")
        option_5 = UserInterface.is_verify_response(input())

        print("6) Install custom GRUB theme? [Y/n] ", end="")
        option_6 = UserInterface.is_verify_response(input())

        return [option_1, option_2, option_3, option_4, option_5, option_6]
