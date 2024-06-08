from inventory import Inventory
from database import DB
from item import Item_methods
from notifications import Notifications
from stn import Stn
from logger import setup_logger, clear_log_file, is_days_since_last_clear, store_last_cleared_date
from helpers import check_if_file_exists

from requests import codes
from time import sleep
from sys import exit
import sqlite3
import configparser
import os
import json

def get_app_path(env_var: str) -> str:
    """
    Gets app path by environment variable, if not set, returns current file directory
    
    Args:
        env_var (str): path_to_where_program_is_located

    Returns:
        str: path_to_where_program_is_located
    """
    app_path = os.getenv(env_var)
    if app_path is None:
        print(f"Environment variable {env_var} is not set")
        app_path = os.getcwd() + "/"
    print(f"App path is: {app_path}")
    return app_path

def load_config(file_path: str) -> configparser.ConfigParser:
    """
    Loads the configuration file from the specified file path.

    Args:
        file_path (str): The path to the configuration file.

    Raises:
        FileExistsError: If the configuration file does not exist.

    Returns:
        configparser.ConfigParser: The loaded configuration parser object.
    """
    if not check_if_file_exists(file_path):
        raise FileExistsError("Please setup config.ini file")
    
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def setup_logging(log_file_path: str, config_file_path: str, last_clear: str, days_between_clear: int):
    """
    Sets up logging, sends logger message, checks if its been certain amount of days since last logger clear
    

    """
    logger = setup_logger(name="Valorizer", log_file=log_file_path)
    logger.log(level=20, msg="Logger setup, started running")
    
    if is_days_since_last_clear(last_clear=last_clear, days_between_clear=days_between_clear):
        print("Clearing log file")
        clear_log_file(log_file = log_file_path)
        store_last_cleared_date(config_file=config_file_path)
    
    return logger

def init_variables(config: configparser.ConfigParser, app_path: str) -> dict:
    """
    Initializes variables from config
    
    Args:
        config (configparser.ConfigParser): config.ini loaded as configparser instance
        app_path (str): path_to_this_program
    
    Returns:
        dict: All the variables in config.ini as keys and values
    """
    app_data_path = app_path + config.get("Paths", "app_data")
    
    variables = {
        # Settings
        "is_first_run": config.get("Settings", "is_first_run"),
        "send_telegram_message": config.get("Settings", "send_telegram_message"),
        # Paths
        "app_data_path": app_data_path,
        "log_file_path": app_data_path + config.get("Paths", "log"),
        "database_file_path": app_data_path + config.get("Paths", "database"),
        "bots_file_path": app_data_path + config.get("Paths", "bots"),
        # Table
        "all_items_table": config.get("Table", "all_items"),
        "new_items_table": config.get("Table", "new_items"),
        "valuable_items_table": config.get("Table", "valuable_items"),
        "stn_table": config.get("Table", "stn"),
        # Valuable
        "valuable_sheens": [sheen.strip() for sheen in config.get("Valuable", "sheens").split(",")],
        "valuable_killstreakers": [killstreaker.strip() for killstreaker in config.get("Valuable", "killstreakers").split(',')],
        "valuable_parts": [part.strip() for part in config.get("Valuable", "parts").split(',')],
        "valuable_paints": [paint.strip() for paint in config.get("Valuable", "paints").split(',')],
        # Qualities
        "parts": [part.strip() for part in config.get("Qualities", "parts").split(",")],
        # STN
        "stn_api_key": config.get("STN", "api_key"),
        # Telegram
        "telegram_message_max_length": config.getint("Telegram", "message_max_length") if config.get("Settings", "send_telegram_message") else None,
        "telegram_token": config.get("Telegram", "token") if config.get("Settings", "send_telegram_message") else None,
        "telegram_chat_id": config.get("Telegram", "chat_id") if config.get("Settings", "send_telegram_message") else None, 
        # Logger
        "logger_last_cleared_date": config.get("Logger", "last_cleared_date"),
        "logger_days_between_clear": config.getint("Logger", "days_between_clear")
    }
    
    return variables

def create_connections(database_file_path):
    connect = sqlite3.connect(database=database_file_path)
    cursor = connect.cursor()
    return connect, cursor

def initialize_classes(connect, variables):
    database = DB(connection=connect, log_file_path=variables["log_file_path"])
    inventory = Inventory(
        parts=variables["parts"],
        valuable_parts=variables["valuable_parts"],
        valuable_paints=variables["valuable_paints"],
        valuable_sheens=variables["valuable_sheens"],
        valuable_killstreakers=variables["valuable_killstreakers"]
    )
    item = Item_methods(
        parts=variables["parts"],
        valuable_parts=variables["valuable_parts"],
        valuable_paints=variables["valuable_paints"],
        valuable_sheens=variables["valuable_sheens"],
        valuable_killstreakers=variables["valuable_killstreakers"]
    )
    notifications = Notifications(token=variables["telegram_token"], chat_id=variables["telegram_chat_id"])
    stn = Stn(connect=connect, table=variables["stn_table"], api_key=variables["stn_api_key"], log_file_path=variables["log_file_path"])
    
    return database, inventory, item, notifications, stn

def fetch_bots(bots_file_path):
    with open(bots_file_path, 'r') as file:
        bots = json.load(file)["STN"]
    if not bots:
        print(f"Please provide some steamids in {bots_file_path}")
        exit()
    return bots

def process_bots(bots, database, inventory, item, stn, logger, tables):
    all_valuable_items = []
    tries = 0

    for bot in bots:
        steamid = bot["id"]
        name = bot["name"]
        inv, status = inventory.fetch_inventory(steam_id=steamid)
        
        if tries > 2:
            logger.log(level=40, msg=f"Tried {tries} times to fetch inventory: {status}, exiting...")
            exit(1)
        
        if status != codes.ok:
            if status == codes.too_many_requests:
                tries += 1
                logger.log(level=30, msg=f"Couldn't load steamid inventory: {status}, sleeping for 30s")
                sleep(30)
            elif status == codes.internal_server_error:
                logger.log(level=30, msg=f"Internal server error: {status}, exiting...")
                exit(1)
            else:
                tries += 1
                logger.log(level=30, msg=f"Could not load steamid: {steamid} inventory: {status}")
            continue
        
        logger.log(level=20, msg=f"Successfully fetched: {steamid} inventory: {status}")
        tries = 0

        inv = inventory.map_inventory(inventory=inv, steamid=steamid, name=name)
        new_items = database.compare_items(inv, tables["all_items_table"])
        database.add_items(new_items, tables["new_items_table"])
        database.delete_from_column_where_steamid(tables["all_items_table"], steamid)
        database.add_items(inv, tables["all_items_table"])
        valuable_items = item.find_valuable_items(items=new_items)
        database.add_items(valuable_items, tables["valuable_items_table"])
        
        all_valuable_items.extend(valuable_items)
    
    logger.log(level=20, msg=f"Successfully ran through all steamids, found {len(all_valuable_items)} valuable items")
    return all_valuable_items

def send_telegram_notifications(notifications, valuable_items, stn, telegram_message_max_length):
    messages = [f"{len(valuable_items)} valuable items"]
    for item in valuable_items:
        message = f"\nNAME: {item.name}"
        stn_item = stn.search(item.name)
        link = stn.create_item_link(stn_item["name"]) if stn_item else None

        if link:
            message = f"{message}, LINK: {link}"
        message = f"{message}\n"
        messages.append(message)

    notifications.send_messages(messages=messages, max_length=telegram_message_max_length)

def main():
    env = 'VALORIZER_APP_PATH'
    app_path = get_app_path(env)
    config_file_path = os.path.join(app_path, "data/config.ini")
    config = load_config(config_file_path)
    
    variables = init_variables(config, app_path)
    logger = setup_logging(log_file_path=variables["log_file_path"], config_file_path=config_file_path, last_clear= variables["logger_last_cleared_date"], days_between_clear=variables["logger_days_between_clear"])

    connect, cursor = create_connections(variables["database_file_path"])
    database, inventory, item, notifications, stn = initialize_classes(connect, variables)
    
    bots = fetch_bots(variables["bots_file_path"])
    bots = [bots[0]]
    database.delete_all_from_column(variables["new_items_table"])
    
    all_valuable_items = process_bots(bots, database, inventory, item, stn, logger, variables)
    connect.commit()
    
    if all_valuable_items:
        print(f"Found {len(all_valuable_items)} valuable items")
        for item in all_valuable_items:
            print(item)
        if variables["send_telegram_message"]:
            send_telegram_notifications(notifications, all_valuable_items, stn, variables["telegram_message_max_length"])
        else:
            print(f"No telegram will be sent, to change this, update 'Settings' -> 'send_telegram_message' in {variables['bots_file_path']}")
    else:
        print("Did not find any valuable items")
    
if __name__ == "__main__":
    main()
