use std::{thread, time::Duration};

use log::{error, warn, info, debug};
use env_logger::Env;


// Execute main function
fn main() {
    // SETUP LOGGER
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    // Setup config
    let attributes_path = "C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml";
    info!(target: "Configuration", "Attributes Path: {:?}", attributes_path);
    
    // Start loop
    let mut n = 1;
    while n <= 10 {
        info!(target: "Monitoring", "Checking file: {:?}", attributes_path);
        thread::sleep(Duration::from_secs(5));
        // TODO: #2 Read attributes xml @kggx

        // TODO: #3 Read steam file @kggx

        // TODO: #4 Produce kafka message @kggx

        n += 1;
    }
}
