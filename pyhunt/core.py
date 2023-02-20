from .helper import *
import datetime
import time
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
        
        # Initialize Hunt-Match-Tracker Config
        self.config_directory = Path().home().joinpath('Documents/Hunt Match Tracker')
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        self.temp_directory = self.config_directory.joinpath("temp")
        self.temp_directory.mkdir(parents=True, exist_ok=True)
        
        self.config_filepath = self.config_directory.joinpath("state.json")
        self.load_config()
            
        self.logger.info('Get Hunt: Showdow attributes.xml path...')
        self.attributes_path = self.steam.get_hunt_attributes()
                    
        pass
     
    def load_config(self):
        try:
            if self.config_filepath.is_file():
                with open(self.config_filepath, 'r') as f:
                    self.config = json.loads(f.read())
                    pass
            else:
                self.logger.info('No config file found. Creating new one.')
                self.config = {"match_hash": ""}
                self.save_config()
                pass
            
        except:
            self.logger.warning('Unknown error reading config file.', exc_info=True)
            self.config = {"match_hash": ""}
            self.save_config()
            pass
            
            
    def save_config(self):
        with open(self.config_filepath, 'w') as f:
            json.dump(self.config, f)
        
        pass
        
    def monitor(self):
        # Monitor attributes.xml 
        try:
            while True:
                
                self.logger.info('Monitor attributes.xml (Press CTRL+C to quit!) ...')
                
                # Read attributes
                self.logger.info('Parse Hunt: Showdown attributes.xml to json ...')
                self.json_attributes = self.hunt.get_hunt_json_attributes(self.attributes_path)       
                
                # If logging level is debug then export
                if self.logger.getEffectiveLevel() == 10:
                    self.logger.debug(f'Write json to {self.temp_directory.joinpath("attributes.json")} ...')
                    with open(self.temp_directory.joinpath("attributes.json"), 'w') as f:
                        json.dump(self.json_attributes, f, indent=1)

                # TODO: #12 Transform json attributes @kggx
                
                # TODO: #13 Implement match meta parsing @kggx
                
                # TODO: #5 Implement player results @kggx
            
                time.sleep(5)
            
        except KeyboardInterrupt:
            self.exit_procedure()
            pass
      
    def exit_procedure(self):
        self.logger.info("Shutdown process...")
        
        self.logger.info("Saving latest state to file...")
        self.save_config()
        pass
    
