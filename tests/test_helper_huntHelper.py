from .context import pyhunt

import pathlib
import os

########################################################################
### Helper Tests #######################################################
########################################################################
# Needs Steam and Hunt: Showdown to be installed locally.
    
def test_get_hunt_json_attributes():
    steam = pyhunt.steamHelper()
    attributes_path = steam.get_hunt_attributes()
    hunt = pyhunt.huntHelper()
    result = hunt.get_hunt_json_attributes(attributes_path)
    variable_type = type(result)
    assert variable_type == dict and len(result.keys()) > 50
    
def test_get_hunt_match_hash():
    steam = pyhunt.steamHelper()
    attributes_path = steam.get_hunt_attributes()
    hunt = pyhunt.huntHelper()
    json_attributes = hunt.get_hunt_json_attributes(attributes_path)
    result = hunt.get_hunt_match_hash(json_attributes)
    print(len(result))
    variable_type = type(result)
    assert variable_type == str and len(result) == 128
    
