from pathlib import Path
import winreg
import vdf
import os


from .structs import *

################################################################################################

class steamHelper():
    def __init__(self) -> None:
        pass
    
    def get_steam_install_location(self) -> Path|None:
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
    
    
    def get_steam_library_pathes(self) -> list[Path] | None:
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
        
    
    
    def get_steam_installed_apps(self) -> list[steam_app] | None:
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
            
    
    def get_hunt_steam_app(self) -> steam_app | None:
        """This function finds Hunt: Showdown (594650).

        Returns:
            steam_app | None: Returns a steam app structure and None if Hunt: Showdown (594650) was not found.
        """
        apps = self.get_steam_installed_apps()
        
        if apps:
            for app in apps:
                if app.app_id == 594650:
                    return app

    
    def get_hunt_attributes(self) -> Path | None:
        """This function returns a path to the attributes.xml file of Hunt: Showdown.

        Returns:
            Path | None: Returns a Path Object to the Attributes.xml file or None if the file is not found. 
        """
        hunt = self.get_hunt_steam_app()        
        
        if hunt:
            attributes = Path(hunt.app_install_dir).joinpath('user/profiles/default/attributes.xml')
        
            if attributes.is_file() == True:
                return attributes
        

 
class huntHelper():
    def __init__(self) -> None:
        pass
        
    
if __name__ == "__main__":
    sh = steamHelper()
    hunt = sh.get_hunt_steam_app()
    attributes = sh.get_hunt_attributes()
    