from .helper import *
import time
import logging
import json

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


# Debug
import pprint
pp = pprint.PrettyPrinter(indent=1)


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
            
        # Is debug? 
        self.debug = True if self.logger.getEffectiveLevel() == 10 else False
            
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
        
        # Setup KAFKA config
        self.kafka_config = {   
            "bootstrap.servers": "kafka.b-raum.com:2095",
            "schema.registry.url": "https://kafka-schemaregistry.b-raum.com"
        }
           
        pass
    
    def product_messages(self, messages, topic, key_schema_file, value_schema_file):        
        key_schema = avro.load(key_schema_file)
        value_schema = avro.load(value_schema_file)
        
        producer = AvroProducer(
            self.kafka_config, 
            default_key_schema=key_schema,
            default_value_schema=value_schema
        )    
        for key, value in messages:
                        
            producer.produce(
                topic = topic,
                key = key,
                value = value        
            )
    
            producer.flush()
        
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
                self.json_attributes = self.hunt.get_hunt_json_attributes(self.attributes_path)       
                
                # If logging level is debug then export
                if self.debug == True:
                    self.logger.debug(f'Write json to {self.temp_directory.joinpath("attributes.json")} ...')
                    with open(self.temp_directory.joinpath("attributes.json"), 'w') as f:
                        json.dump(self.json_attributes, f, indent=1)

                # Check match hash and continue if new hash is found
                new_hash = self.hunt.get_hunt_match_hash(self.json_attributes)
                
                if new_hash != self.config.get("match_hash") or self.debug == True:
                    self.logger.info('New match hash was found!')
                    self.config['match_hash'] = new_hash
                    self.save_config()
                    
                    # Get currently logged in user
                    self.steam_user = self.steam.get_steam_current_user()
                    
                    # MAke player MMR feed
                    self.logger.info(f"huntshowdown_player_meta_{'dev' if self.debug == True else 'prod'}")
                    player_messages = self.hunt.generate_player_messages(new_hash, self.steam_user, self.json_attributes)
                    self.product_messages(
                        player_messages, 
                        f"huntshowdown_player_meta_{'dev' if self.debug == True else 'prod'}", 
                        Path("./avro/io.gamepace.huntshowdown.player.meta.key.avsc").absolute(),
                        Path("./avro/io.gamepace.huntshowdown.player.meta.value.avsc").absolute()
                    )   
                    
                    # Make team feed
                    self.logger.info(f"huntshowdown_team_meta_{'dev' if self.debug == True else 'prod'}")
                    team_messages = self.hunt.generate_team_messages(new_hash, self.steam_user, self.json_attributes)
                    self.product_messages(
                        team_messages, 
                        f"huntshowdown_team_meta_{'dev' if self.debug == True else 'prod'}", 
                        Path("./avro/io.gamepace.huntshowdown.team.meta.key.avsc").absolute(),
                        Path("./avro/io.gamepace.huntshowdown.team.meta.value.avsc").absolute()
                    )
                    
                    # Make match feed
                    self.logger.info(f"huntshowdown_match_meta_{'dev' if self.debug == True else 'prod'}")
                    match_message = self.hunt.generate_match_message(new_hash, self.steam_user, self.json_attributes)
                    self.product_messages(
                        [match_message], 
                        f"huntshowdown_match_meta_{'dev' if self.debug == True else 'prod'}", 
                        Path("./avro/io.gamepace.huntshowdown.match.meta.key.avsc").absolute(),
                        Path("./avro/io.gamepace.huntshowdown.match.meta.value.avsc").absolute()
                    )
                    
                    # Make event bags
                    self.logger.info(f"huntshowdown_mission_event_{'dev' if self.debug == True else 'prod'}")
                    mission_event_messages = self.hunt.generate_mission_event_messages(new_hash, self.steam_user, self.json_attributes)
                    self.product_messages(
                        mission_event_messages,
                        f"huntshowdown_mission_event_{'dev' if self.debug == True else 'prod'}", 
                        Path("./avro/io.gamepace.huntshowdown.mission.event.key.avsc").absolute(),
                        Path("./avro/io.gamepace.huntshowdown.mission.event.value.avsc").absolute()
                    )
                    
                    # Make match kill feed
                    self.logger.info(f"huntshowdown_match_event_{'dev' if self.debug == True else 'prod'}")
                    match_event_messages = self.hunt.generate_match_event_messages(new_hash, self.steam_user, self.json_attributes)
                    self.product_messages(
                        match_event_messages,
                        f"huntshowdown_match_event_{'dev' if self.debug == True else 'prod'}", 
                        Path("./avro/io.gamepace.huntshowdown.match.event.key.avsc").absolute(),
                        Path("./avro/io.gamepace.huntshowdown.match.event.value.avsc").absolute()
                    )
                    
                    self.logger.info(f"Finished processing new match.")
                 
                # Sleep until next check                               
                time.sleep(5 if self.debug == True else 180)
            
        except KeyboardInterrupt:
            self.exit_procedure()
            pass
      
    def exit_procedure(self):
        self.logger.info("Shutdown process...")
        
        self.logger.info("Saving latest state to file...")
        self.save_config()
        pass
    
