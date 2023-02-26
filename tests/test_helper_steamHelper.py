from .context import pyhunt

import pathlib
import os

########################################################################
### Helper Tests #######################################################
########################################################################
# Needs Steam and Hunt: Showdown to be installed locally.

def test_get_steam_install_location():
    steam = pyhunt.steamHelper()
    result = steam.get_steam_install_location()
    
    variable_type = type(result)
    assert (variable_type == pathlib.WindowsPath or variable_type == pathlib.PosixPath or result is None)

    
def test_get_steam_library_pathes():
    steam = pyhunt.steamHelper()
    result = steam.get_steam_library_pathes()
    
    variable_type = type(result)
    entry_type = type(result[0])
    assert (variable_type == list and (entry_type == pathlib.WindowsPath or entry_type == pathlib.PosixPath) or result is None)
    

def test_get_steam_installed_apps():
    steam = pyhunt.steamHelper()
    result = steam.get_steam_installed_apps()
    
    variable_type = type(result)
    entry_type = type(result[0])
    
    assert (variable_type == list and (entry_type == pyhunt.steam_app) or result is None)
    

def test_get_hunt_steam_app():
    steam = pyhunt.steamHelper()
    result = steam.get_hunt_steam_app()
    
    variable_type = type(result)

    
    assert (variable_type == pyhunt.steam_app or result is None)
    

def test_get_hunt_attributes():
    steam = pyhunt.steamHelper()
    result = steam.get_hunt_attributes()
    
    variable_type = type(result)
    result.is_file()
    assert ((variable_type == pathlib.WindowsPath or variable_type == pathlib.PosixPath) and result.is_file()) or result is None


def test_get_steam_current_user():
    steam = pyhunt.steamHelper()
    result = steam.get_steam_current_user()
    print(result)
    
    if result is not None:
        variable_type = type(result)
        assert(result is None or (variable_type == pyhunt.steam_user) and type(result.steam_id) == int and type(result.steam_accountname) == str and type(result.steam_personaname) == str)
    else:
        assert(result is None)