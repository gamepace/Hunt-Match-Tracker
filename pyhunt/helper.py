from pathlib import Path, WindowsPath, PosixPath
import winreg
import vdf
import os
import xml.etree.ElementTree
import hashlib
import datetime
import re


from .structs import *

import pprint
pp = pprint.PrettyPrinter(indent=1)

#################################################################################################
### Helper Classes ##############################################################################
#################################################################################################
class steamHelper():
    def __init__(self) -> None:
        pass
    
    def get_steam_install_location(self) -> Path:
        """This function looks into the windows registry and finds the steam installation path.

        Returns:
            Path|None: This function either returns the steam installation path or returns None if the steam registry key is not found.
        """
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
            return Path(winreg.QueryValueEx(hkey, "InstallPath")[0])
        except:
            print(f'ERROR | Can not get steam path from registry')
            return None
    
    
    def get_steam_library_pathes(self) -> list[Path]:
        """This function returns all locations where steam apps are installed.

        Returns:
            list[Path] | None: This is a list of pathes to steam libraries or None if no libraries were found.
        """
        steam_path = self.get_steam_install_location()    
        
        if steam_path:
            # Resolve libraries   
            lib_vdf = vdf.load(open(steam_path.joinpath("steamapps/libraryfolders.vdf"), 'r'))
            libs = lib_vdf['libraryfolders']
            lib_pathes = [Path(libs[x]['path']).joinpath('steamapps') for x in libs]     
            
            if len(lib_pathes) >= 0:
                return lib_pathes
        
    
    
    def get_steam_installed_apps(self) -> list[steam_app]:
        """This function returns all installed steam apps on the system.

        Returns:
            list[steam_app] | None: List of steam app structures or None if no steam apps were found.
        """
        lib_pathes = self.get_steam_library_pathes()
        if lib_pathes:
            installed_apps = []
            
            for lib_path in lib_pathes:
                for app_manifest in os.scandir(lib_path):
                    if app_manifest.is_file() == True and app_manifest.name.endswith('.acf'):
                        app_manifest_vdf = vdf.load(open(lib_path.joinpath(app_manifest), 'r'))
                        installed_apps.append(
                            steam_app(
                                int(app_manifest_vdf['AppState']['appid']),
                                app_manifest_vdf['AppState']['name'],
                                int(app_manifest_vdf['AppState']['Universe']),
                                int(app_manifest_vdf['AppState']['buildid']),
                                str(Path(lib_path).joinpath("common", app_manifest_vdf['AppState']['installdir']).absolute()),
                            )
                        )
            if len(installed_apps) >= 0:
                return installed_apps
            
    
    def get_hunt_steam_app(self) -> steam_app:
        """This function finds Hunt: Showdown (594650).

        Returns:
            steam_app | None: Returns a steam app structure and None if Hunt: Showdown (594650) was not found.
        """
        apps = self.get_steam_installed_apps()
        
        if apps:
            for app in apps:
                if app.app_id == 594650:
                    return app

    
    def get_hunt_attributes(self) -> Path:
        """This function returns a path to the attributes.xml file of Hunt: Showdown.

        Returns:
            Path | None: Returns a Path Object to the Attributes.xml file or None if the file is not found. 
        """
        hunt = self.get_hunt_steam_app()        
        
        if hunt:
            attributes = Path(hunt.app_install_dir).joinpath('user/profiles/default/attributes.xml')
        
            if attributes.is_file() == True:
                return attributes
    
    
    def get_steam_current_user(self) -> steam_user:
        steam_path = self.get_steam_install_location()    

        if steam_path:
            # Resolve libraries   
            user_vdf = vdf.load(open(steam_path.joinpath("config/loginusers.vdf"), 'r'))

            if len(user_vdf['users']) > 0:
                for id in user_vdf['users']:
                    
                    user = user_vdf['users'][id]
                    if user['MostRecent'] == "1":
                        return steam_user(
                            int(id), 
                            user['AccountName'], 
                            user['PersonaName']
                        )
                
     
## Hunt Showdown Helper Class     
class huntHelper():
    def __init__(self) -> None: 
        pass
        
    def get_hunt_json_attributes(self, attributes_path:Path|WindowsPath|PosixPath) -> dict:
        tree = xml.etree.ElementTree.parse(attributes_path)
        root = tree.getroot()
        
        attributes = {}
        
        for item in root.findall('./Attr'):
            
            attribute_name = item.attrib['name']
            
            # Fix inconsisten naming by Crytex ¯\_(ツ)_/¯
            if "tooltip_downedbyteammate" in attribute_name:
                attribute_name = attribute_name.replace("tooltip_downedbyteammate", 'tooltipdownedbyteammate')
            elif "blood_line_name" in attribute_name:
                attribute_name = attribute_name.replace("blood_line_name", 'bloodlinename')

            
            # Split hierachies by delimiters
            if '/' in attribute_name:
                categories = attribute_name.split('/')
                
            elif '_' in attribute_name:
                categories = attribute_name.split('_')
            
            else:
                categories = None
                
            # Create nested hierachies
            if categories:  
                value_dictionary = {}
                for i, category in enumerate(reversed(categories)):
                    if i != 0:
                        value_dictionary = {category: value_dictionary}
                    else:
                        value_dictionary[category] = item.attrib['value']
                                                             
                attributes = merge_dicts(attributes, value_dictionary)
            
            # Pass plain attribute 
            else:
                attributes[item.attrib['name']] = item.attrib['value']
              
        return attributes

    def get_hunt_match_hash(self, json_attributes:dict) -> str:
        player_profileids = []
        
        region = json_attributes['Region']
        
        # Get player ids and sort
        for team_key in json_attributes['MissionBagPlayer']:
            for player_key in json_attributes['MissionBagPlayer'][team_key]:
                player = json_attributes['MissionBagPlayer'][team_key][player_key]
                player_profileids.append(player['profileid'])
                
        player_profileids.sort()
        
        # Combine string and hash
        match_string = f"{region}_{'_'.join(player_profileids)}"
        match_hash = hashlib.sha512(match_string.encode()).hexdigest()
        
        return match_hash
    
    def generate_player_messages(self, match_hash:str, committer:steam_user, json_attributes:dict) -> list[tuple[dict]]:
        messages = []
        
        # for each player
        for team in json_attributes['MissionBagPlayer']:
            for player in json_attributes['MissionBagPlayer'][team]:
                player_data = json_attributes['MissionBagPlayer'][team][player]
        
                key = {
                    "match_code": match_hash,
                    "event_code": hashlib.sha512(str(player_data['profileid']).encode()).hexdigest(),
                    "comitter_steam_id": committer.steam_id,
                    "comitter_steam_accountname": committer.steam_accountname,
                    "comitter_steam_personaname": committer.steam_personaname,
                }
                
                value = {
                    "utc_timestamp": datetime.datetime.utcnow().timestamp(),
                    "hunt_player_id": int(player_data['profileid']),
                    "hunt_player_personaname": player_data['bloodlinename'],
                    "hunt_player_mmr": int(player_data['mmr']),   
                }
                
                messages.append((key, value))
        
        return messages
    
    
    def generate_team_messages(self, match_hash:str, committer:steam_user, json_attributes:dict) -> list[tuple[dict]]:
        messages = []
        
        # For each team
        for team in json_attributes['MissionBagPlayer']:
            team_players = [] 
            team_data = json_attributes['MissionBagTeam'][team]
            
            for player in json_attributes['MissionBagPlayer'][team]:
                player_data = json_attributes['MissionBagPlayer'][team][player] 
                team_players.append({"hunt_player_id": int(player_data['profileid']), "hunt_player_personaname": player_data['bloodlinename']})


            team_playerids = [str(x['hunt_player_id']) for x in team_players]
            team_playerids.sort()
            team_hash = hashlib.sha512(str(f"{'_'.join(team_playerids)}").encode()).hexdigest()
            
            # Make Key
            key = {
                "match_code": match_hash,
                "event_code": team_hash,
                "comitter_steam_id": committer.steam_id,
                "comitter_steam_accountname": committer.steam_accountname,
                "comitter_steam_personaname": committer.steam_personaname       
            }
                      
            value = {
                "utc_timestamp": datetime.datetime.utcnow().timestamp(),
                "hunt_team_id": team_hash,
                "hunt_team_handicap": int(team_data['handicap']),
                "hunt_team_committer_flag": True if team_data['ownteam'].lower() == "true" else False,
                "hunt_team_invite_flag": True if team_data['isinvite'].lower() == "true" else False,
                "hunt_team_mmr": int(team_data['mmr']),
            }
            
            # Append Player IDs
            for i, x in enumerate(team_players):
                value[f"hunt_team_player_{i+1}_id"] = x['hunt_player_id']
                value[f"hunt_team_player_{i+1}_name"] = x['hunt_player_personaname']
            
            # Append Message
            messages.append((key, value))
        
        return messages 
    
    # Make match event
    def generate_match_message(self, match_hash:str, committer:steam_user, json_attributes:dict) -> tuple[dict]:
        key = {
            "match_code": match_hash,
            "event_code": match_hash,
            "comitter_steam_id": committer.steam_id,
            "comitter_steam_accountname": committer.steam_accountname,
            "comitter_steam_personaname": committer.steam_personaname       
        }
                    
        value = {
            "utc_timestamp": datetime.datetime.utcnow().timestamp(),
            "hunt_match_boss_butcher_flag": True if json_attributes['MissionBagBoss']['0'].lower() == "true" else False,
            "hunt_match_boss_spider_flag": True if json_attributes['MissionBagBoss']['1'].lower() == "true" else False,
            "hunt_match_boss_assassin_flag": True if json_attributes['MissionBagBoss']['2'].lower() == "true" else False,
            "hunt_match_boss_scrapbeak_flag": True if json_attributes['MissionBagBoss']['3'].lower() == "true" else False,
            "hunt_match_event_code": json_attributes.get('LastLiveEventIDLoaded'),
            "hunt_match_quickplay_flag": True if json_attributes['MissionBagIsQuickPlay'].lower() == "true" else False,
            "hunt_match_region_code": json_attributes['Region'],
            "hunt_match_cemetery_flag": True if json_attributes['PVEModeLastSelected']['cemetery'] != "-1" else False,
            "hunt_match_creek_flag": True if json_attributes['PVEModeLastSelected']['creek'] != "-1" else False,
            "hunt_match_civilwar_flag": True if json_attributes['PVEModeLastSelected']['civilwar'] != "-1" else False
        }
        
        return (key, value)

    # Make committer event log
    def generate_mission_event_messages(self, match_hash:str, committer:steam_user, json_attributes:dict) -> list[tuple[dict]]:
        messages = []
        
        for event in json_attributes['MissionBagEntry']:
            event_data = json_attributes['MissionBagEntry'][event]
            key = {
                "match_code": match_hash,
                "event_code": hashlib.sha512(f"{event}_{event_data['category']}_{event_data['reward']}".encode()).hexdigest(),
                "comitter_steam_id": committer.steam_id,
                "comitter_steam_accountname": committer.steam_accountname,
                "comitter_steam_personaname": committer.steam_personaname       
            }
               
            value = {
                "utc_timestamp": datetime.datetime.utcnow().timestamp(),
                "hunt_mission_event_bag_id": int(event),
                "hunt_mission_event_reward_id": int(event_data['reward']),
                "hunt_mission_event_reward_size": int(event_data['rewardSize']),
                "hunt_mission_event_ui_icon_1": event_data['iconPath'],
                "hunt_mission_event_ui_icon_2": event_data['iconPath2'],
                "hunt_mission_event_ui_name_1": event_data['uiName'],
                "hunt_mission_event_ui_name_2": event_data['uiName2'],
                "hunt_mission_event_descriptor_name": event_data['descriptorName'],
                "hunt_mission_event_descriptor_score": int(event_data['descriptorScore']),
                "hunt_mission_event_descriptor_type": int(event_data['descriptorType']),   
                "hunt_mission_event_category": event_data['category'],
                "hunt_mission_event_amount": int(event_data['amount'])  
            }
            
            messages.append((key, value))
        
        return messages
        
    
    # Make committer kill log
    def generate_match_event_messages(self, match_hash:str, committer:steam_user, json_attributes:dict) -> list[tuple[dict]]:
        messages = []                    
        
        for team in json_attributes['MissionBagPlayer']:
            for player in json_attributes['MissionBagPlayer'][team]:
                player_data = json_attributes['MissionBagPlayer'][team][player]
                
                other_player_id = player_data['profileid']
                other_player_name = player_data['bloodlinename']
                                           
                for attribute in player_data.keys():
                    if "tooltip" in attribute:                        
                        event_times = re.findall(r"~[0-9]{1,2}:[0-9]{1,2}", player_data[attribute])
                        event_clean_times = [x.replace('~', '') for x in event_times]
                        
                        for timestamp in event_clean_times:
                            minute, second = int(timestamp.split(':')[0]), int(timestamp.split(':')[1])
                                                        
                            key = {
                                "match_code": match_hash,
                                "event_code": hashlib.sha512(f"{timestamp}_{other_player_id}_{committer.steam_id}_{attribute}".encode()).hexdigest(),
                                "comitter_steam_id": committer.steam_id,
                                "comitter_steam_accountname": committer.steam_accountname,
                                "comitter_steam_personaname": committer.steam_personaname       
                            }
                            
                            value = {
                                "utc_timestamp": datetime.datetime.utcnow().timestamp(),
                                "match_event_hunt_player_id": int(other_player_id),
                                "match_event_hunt_player_name": other_player_name,
                                "match_event_name": attribute.replace('tooltip', ''),
                                "match_event_minute": int(minute),
                                "match_event_second": int(second)
                            }
                            
                            messages.append((key, value))
        
        return messages
    
#################################################################################################
### Helper Funcions #############################################################################
#################################################################################################

def merge_dicts(dict1, dict2):
    result = {}
    for key in set(dict1.keys()) | set(dict2.keys()):
        if key in dict1 and key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                result[key] = merge_dicts(dict1[key], dict2[key])
            else:
                result[key] = dict2[key]
        elif key in dict1:
            result[key] = dict1[key]
        else:
            result[key] = dict2[key]
    return result
