from .helper import *
import datetime
import time
import keyboard
import logging

# Debug
import json

######################################################################################################

class huntClient():
    def __init__(self, log_level:str='INFO') -> None:
        # Initialize Logger
        self.logger = logging.Logger('Hunt Match Tracker')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        level = logging.getLevelName(log_level.upper())
        self.logger.setLevel(level)
        self.logger.info('Initialized Logger...')
        
        # Initialize Client
        self.logger.info('Initialize Client...')
        self.steam = steamHelper()
        self.hunt = huntHelper()
        
        self.logger.info('Get Hunt: Showdow attributes.xml path...')
        self.attributes_path = self.steam.get_hunt_attributes()
                    
        pass
        
    def monitor(self):
        # Monitor attributes.xml 
        # TODO: #11 Implement a better quitting process @kggx
        while True:
            self.logger.info('Monitor attributes.xml (Hold ESC to quit!) ...')
            if keyboard.is_pressed('esc'):
                # TODO: #9 Quit routine @kggx
                break
            
            # Read attributes
            self.logger.info('Parse Hunt: Showdown attributes.xml to json ...')
            self.json_attributes = self.hunt.get_hunt_json_attributes(self.attributes_path)       
            
            # If logging level is debug then export
            if self.logger.getEffectiveLevel() == 10:
                # TODO: #10 Fix issue with debug location @kggx
                temp_attributes = Path("./tmp/attributes.json")
                self.logger.debug(f'Write json to {temp_attributes.absolute()} ...')
                with open(temp_attributes, 'w') as f:
                    json.dump(self.json_attributes, f, indent=1)
                    
            time.sleep(5)

            # TODO: #12 Transform json attributes @kggx
            
            # TODO: #13 Implement match meta parsing @kggx
            
            # TODO: #5 Implement player results @kggx
            
            
        pass

    def exit_procedure(self):
        # TODO: #7 Implement a exit procedure that saves the latest information. @kggx
        pass
    
