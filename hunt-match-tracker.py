import pyhunt
import argparse
import textwrap


if __name__ == "__main__":
    # Commandline arguements
    cmd_args = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
        Hunt Match Tracker!
        ----------------------------------------------------------------------------
        This tool tracks Hunt: Showdown matches via the attributes.xml
        ----------------------------------------------------------------------------
        """)
    )
    cmd_args.add_argument('--debug', dest="debug", default=False, type=bool, help='Enable Debugging (default: False)')
    args = cmd_args.parse_args()
    
    # Set variables
    log_level = 'debug' if args.debug == True else 'info'
    
    # Client 
    client = pyhunt.core.huntClient(log_level=log_level)
    client.monitor()