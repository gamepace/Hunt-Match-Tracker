from dataclasses import dataclass



# Steam Application
@dataclass
class steam_app:
    app_id:int
    app_name: str
    app_universe: int
    app_build_id:int
    app_install_dir: str
    
