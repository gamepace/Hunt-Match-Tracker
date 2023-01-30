use std::{thread, time::Duration};

//use log::{debug, error, info, warn};

// Execute main function
fn main() {

    // Setup config
    let attributes_path = "C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml";
    let mut n = 1;

    // TODO: Start loop
    while n <= 10 {
        println!("Attributes Path: {:?}", attributes_path);

        thread::sleep(Duration::from_secs(5));
        // TODO: Read attributes xml

        // TODO: Read steam file

        // TODO: Produce kafka message

        n += 1;
    }
}
