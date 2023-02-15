from .helper import *


####################################
# Logging Setup


####################################
class huntClient():
    def __init__(self) -> None:
        
        steam = steamHelper()
        attributes_path = steam.get_hunt_attributes()
        print(attributes_path)
        
        print('Hello World')
        input("Press any key to quit...")
        pass
        
    def monitor(self):
        # TODO: #8 Monitor attributes.xml @kggx
        pass

    def exit_procedure(self):
        # TODO: #7 Implement a exit procedure that saves the latest information. @kggx
        pass
