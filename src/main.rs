// Standard Crates
use std::{thread::{self}, time::Duration, path::{PathBuf}};
use std::fs::File;

// Custom Crates
use log::{error, warn, info, debug};
use env_logger::Env;

extern crate steamlocate;
use steamlocate::{SteamDir, SteamApp};
use keyvalues_parser::Vdf;

use xml::{reader::{XmlEvent}, EventReader};
use serde_json::{json, Value, Map};

///////////////////////////////////////////////////////////////////////////////////////////
// Structs
struct SteamHuntGame {
    hunt_path: PathBuf,
    hunt_last_steam_id: u64,
    hunt_attributes: PathBuf,
}

struct SteamUser {
    steam_id: u64,
    steam_personaname: String,
    steam_accountname: String
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////

fn get_steam_user_by_id(id: u64) -> SteamUser {
    let steamdir: SteamDir = SteamDir::locate().unwrap();    

    // Profiles
    let mut steam_profiles:PathBuf = PathBuf::new();
    steam_profiles.push(steamdir.path.clone());
    steam_profiles.push("config\\loginusers.vdf");
    


    let vdf_text = std::fs::read_to_string(steam_profiles).unwrap();
    let vdf = Vdf::parse(&vdf_text).unwrap();

    for value in vdf.value.unwrap_obj().iter() {
        let key = value.0;
        let obj = value.1;
        
        // Last User
        if key == id.to_string().as_str()  {
            let value = &obj[0].clone().unwrap_obj(); 
            let personaname = value.get("PersonaName").unwrap()[0].get_str().unwrap();
            let accountname = value.get("AccountName").unwrap()[0].get_str().unwrap();
            return SteamUser {steam_id: id, steam_personaname: String::from(personaname), steam_accountname: String::from(accountname)};   
        }
    }

    return SteamUser {steam_id: id, steam_personaname: String::from(""), steam_accountname: String::from("") };    
}


// Functions
fn find_hunt_config() -> SteamHuntGame {
    let mut steamdir: SteamDir = SteamDir::locate().unwrap();

    // Get Hunt
    let hunt_app: &SteamApp = match steamdir.app(&594650) {
        Some(app) => app,
        None => panic!("Couldn't locate Garry's Mod on this computer!")
    };

    // Get User Id
    let user_id: u64 = match hunt_app.last_user {
        Some(last_user) => u64::from(last_user).clone(),
        _ => 0
    };

    // Attributes File
    let mut hunt_attributes:PathBuf = PathBuf::new();

    hunt_attributes.push(hunt_app.path.clone());
    hunt_attributes.push("user\\profiles\\default\\attributes.xml");

    return SteamHuntGame { hunt_path: hunt_app.path.clone(), hunt_last_steam_id: user_id, hunt_attributes: hunt_attributes};
}

fn parse_xml_to_json(xml_parser: EventReader<File>) -> Map<String, Value> {
    let mut json_result = json!({});
    let mut json_result = Map::new();

    // Loop over envery
    for event in xml_parser {
        match event {
            Ok(XmlEvent::StartElement {attributes, .. }) => {
                // Is valid key
                if attributes.len() == 2 {
                    json_result.entry(attributes.clone()[0].value.to_string()).or_insert_with(|| Value::from(attributes.clone()[1].value.to_owned()));
                }
            },
            Err(_e) => {},   
            _ => (),
        }
    }
    
    return json_result;
}


fn read_hunt_attributes(hunt_attributes:PathBuf) -> Map<String, Value> {
    info!(target: "Processing", "Reading attributes.xml ...");
    
    let file: File = File::open(hunt_attributes).unwrap();
    let parser: EventReader<File> = xml::EventReader::new(file);

    info!(target: "Processing", "Parse XML to JSON...");
    let json_parsed = parse_xml_to_json(parser);
    // Temp to file
    std::fs::write(
        "tmp/attributes.json", 
        serde_json::to_string_pretty(&json_parsed).unwrap()
    ).unwrap();

    return json_parsed;
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Execute main function
fn main() {
    // SETUP LOGGER
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    // Setup config
    let hunt_config: SteamHuntGame = find_hunt_config();
    let mut steam_user:SteamUser;
    let mut hunt_attributes: Map<String, Value>;

    // Start loop
    let mut n = 1;
    while n <= 1 {
        info!(target: "Monitoring", "Checking file: {:?}", hunt_config.hunt_attributes);
    
        // Read attributes xml
        if hunt_config.hunt_attributes.is_file() {
            hunt_attributes = read_hunt_attributes(hunt_config.hunt_attributes.clone());
        }
        // Read steam profile file
        steam_user = get_steam_user_by_id(hunt_config.hunt_last_steam_id);

        // TODO: #5 Read player match results (user) @kggx

        // TODO: #4 Produce kafka message @kggx

        n += 1;
        thread::sleep(Duration::from_secs(5));
    }
}
