#!/usr/bin/python3
import argparse, os, sys, logging
from service import install, uninstall, upgrade, dry_run
from configure import configure

parser = argparse.ArgumentParser(description='This script is to manage SS8 DCG Kubernetes resources.')
parser.add_argument('-f', '--file', type=str, required=True,
                    help='Deployment value yaml file')
parser.add_argument('-i', '--initialize', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Setup cluster for first time install')
parser.add_argument('-d', '--initialize_database', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Create or upgrade database')
parser.add_argument('-u', '--upgrade', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Upgrade deployment')
parser.add_argument('--install', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Deploy DCG services')
parser.add_argument('--uninstall', type=str, required=False, nargs='?', default="False", const="services",
                    help='Uninstall DCG services')
parser.add_argument('--status', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Show status of DCG services resources')
parser.add_argument('-v', '--verbose', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Enable verbose')
parser.add_argument('--dry_run', type=bool, required=False, nargs='?', default=False, const=True,
                    help='Test yaml')
parser.add_argument('-l', '--log_level', type=int, required=False, default=3, help="Set log output level: [0: critical, 1: error, 2: warning, 3: info, 4: debug \n]")
args = parser.parse_args()

log_file_location = "DCG-deployment.log"
log_file_encoding = 'utf-8'

def set_log_level(level):
    if ( level <= 0 ):
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", 
                level=logging.CRITICAL, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.CRITICAL)
    elif ( level == 1):
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", 
                level=logging.ERROR, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.ERROR)
    elif ( level == 2):
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", 
                level=logging.WARNING, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.WARNING)
    elif ( level == 3):
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", 
                level=logging.INFO, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.INFO)
    elif ( level >= 4 ):
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s",
                level=logging.DEBUG, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.DEBUG)
    else:
        if(args.verbose):
            logging.basicConfig(
                format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", 
                level=logging.INFO, 
                handlers=[
                    logging.FileHandler(log_file_location),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(format="%(asctime)s [%(name)s:%(levelname)s] %(message)s", filename=log_file_location, level=logging.INFO)

if (__name__ == "__main__"):
    set_log_level(args.log_level)
    logger = logging.getLogger("DCG-DEPLOYMENT")
    
    if(args.initialize):
        logger.info("Initializing SS8 Kubernetes objects")
        config = configure(args.file, logger)
        config.configure_labels()
        config.configure_resource_quota()
    else:
        logger.debug("Not initializing SS8 kubernetes objects")

    if(args.install):
        task = install(args.file, logger, init=args.initialize_database)
    elif(args.uninstall != "False"):
        task = uninstall(args.file, logger, task=args.uninstall)
    # elif(args.upgrade):
    #     task = upgrade(args.file, logger, init=args.initialize_database)
    elif(args.status):
        task = status(logger)
    elif(args.dry_run):
        task = dry_run(args.file, logger)
    else:
        print("No task was assgin, Endding process.")
        logger.warning("No task was assgin, Endding process.")
        exit(0)
    task.run()
