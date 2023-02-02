// Standard Crates
use std::{thread, time::Duration, path::{PathBuf}};

use std::fs::File;
use std::io::BufReader;

// Custom Crates
use log::{error, warn, info, debug};
use env_logger::Env;

extern crate steamlocate;
use steamlocate::{SteamDir, SteamApp};

use xml::{reader::{EventReader, XmlEvent}, attribute::OwnedAttribute};
use json;
// Structs
struct SteamHuntGame {
    hunt_path: PathBuf,
    hunt_user: u64,
    hunt_attributes: PathBuf,
}


// functions
fn find_hunt_config() -> SteamHuntGame {
    
    let mut steamdir = SteamDir::locate().unwrap();

    let hunt_app: &SteamApp = match steamdir.app(&594650) {
        Some(app) => app,
        None => panic!("Couldn't locate Garry's Mod on this computer!")
    };

    let user_id: u64 = match hunt_app.last_user {
        Some(last_user) => u64::from(last_user).clone(),
        _ => 0
    };

    // Attributes File
    let mut hunt_attributes = PathBuf::new();

    hunt_attributes.push(hunt_app.path.clone());
    hunt_attributes.push("user\\profiles\\default\\attributes.xml");


    let hunt_config: SteamHuntGame = SteamHuntGame { hunt_path: hunt_app.path.clone(), hunt_user: user_id, hunt_attributes: hunt_attributes};    
    return hunt_config;
}


fn read_hunt_attributes(hunt_attributes:PathBuf) {
    info!(target: "Processing", "Reading hunt attributes...");
    
    let file = File::open(hunt_attributes).unwrap();
    let parser = xml::EventReader::new(file);

    let json = json::object!{};

    // TODO: Convert to message
    for event in parser {
        match event {
            Ok(XmlEvent::StartElement {attributes, ..}) => {
                if attributes.len() == 2 {
                    
                    // Parse XML events to JSON
                    let event_name = &attributes[0].value;
                    let event_categories = event_name.split_terminator('/');
                    let event_value = &attributes[1].value;
                    let event_json = json::object!{};
                    
                    // Loop over categories
                    for event_category in event_categories.clone().enumerate() {
                        if event_category.0 == event_categories.clone().count() - 1 {
                            // Assign value to json
                            println!("End: {:?}", event_category.1);
                        }
                        else {
                            // Append new level to json
                            println!("Not End: {:?}", event_category.1);
                        }

                    }

                }
            }
            Err(e) => {}
            _ => {}
        }
    

    }  
    
    // Return attributes as json
    

}

// fn compute_match_hash(players) {
//     // Compute the hash for all players in the match.
//     // Lower ordered playername -> sha256

//     // return hash
//}
    

// Execute main function
fn main() {
    // SETUP LOGGER
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    // Setup config
    let mut hunt_config: SteamHuntGame = find_hunt_config();
    
    // Start loop
    let mut n = 1;
    while n <= 10 {
        info!(target: "Monitoring", "Checking file: {:?}", hunt_config.hunt_attributes);
    
        // TODO: #2 Read attributes xml @kggx
        if hunt_config.hunt_attributes.is_file() {
            read_hunt_attributes(hunt_config.hunt_attributes.clone());
        }
        

        // TODO: #3 Read steam file @kggx

        // TODO: #4 Produce kafka message @kggx

        n += 1;
        thread::sleep(Duration::from_secs(5));
    }
}
