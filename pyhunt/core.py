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

