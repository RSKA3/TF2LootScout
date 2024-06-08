import sqlite3

from logger import setup_logger

class DB():
    def __init__(self, connection, log_file_path: str):
        
        self.logger = setup_logger(name = "DB", log_file=log_file_path)
        self.logger.log(level=20, msg="Init DB")

        self.connect = connection
        self.connect.row_factory = sqlite3.Row
        self.cursor = self.connect.cursor()

        self.init_item_tables()
    
    def init_item_tables(self, table_names: list = ["stn_bot_items", "new_stn_bot_items", "valuable_stn_bot_items"]) -> None:
        """Initialize the database by creating necessary tables if they do not exist."""

        for table_name in table_names:
            try:
                self.logger.log(level=20, msg=f"Initializing table {table_name}")
                self.cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        steamid TEXT NOT NULL,
                        assetid TEXT NOT NULL,
                        classid TEXT NOT NULL,
                        instanceid TEXT NOT NULL,
                        tradable INT,
                        craftable INT,
                        name TEXT NOT NULL,
                        quality TEXT,
                        type TEXT,
                        killstreaks INT,
                        sheen TEXT,
                        killstreaker TEXT,
                        paint TEXT,
                        spell TEXT,
                        effect TEXT,
                        parts TEXT
                    );
                    """)
                self.connect.commit()
                self.logger.log(level=20, msg=f"Table {table_name} initialized")
            except sqlite3.Error as e:
                self.logger.log(level=40, msg=f"Table {table_name} could not be initialized")

    def add_items(self, items: dict, column: str):
        for item in items:
            params = (item.steamid, item.assetid, item.classid, item.instanceid, item.tradable, item.craftable, item.name, item.quality, 
                    item.type, item.killstreaks, item.sheen, item.killstreaker, item.paint, item.spell, item.effect, item.parts)

            self.cursor.execute(f'INSERT INTO {column} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', params)

    def compare_items(self, items: dict, column: str) -> list:
        self.logger.log(level=20, msg="comparing items")
        new_items = []
        for item in items:
            if not self.check_if_item_exists(steamid=item.steamid, assetid=item.assetid, classid=item.classid, instanceid=item.instanceid, column=column):
                new_items.append(item)
        return new_items

    def check_if_item_exists(self, steamid: str, assetid: str, classid: str, instanceid: str, column: str) -> bool:
        """
        Checks if an item exists in the specified column of the database.

        This function queries the database to check if an item with the given attributes exists in the specified column.
        It returns True if the item exists, and False otherwise.

        Args:
            item (dict): Dictionary containing the item's attributes (steamid, assetid, classid, instanceid).
            column (str): Name of the column in the database to check.

        Returns:
            bool: True if the item exists, False otherwise.
        """

        params = (steamid, assetid, classid, instanceid)
        safe_column = column.replace('"', '""')
        result = self.cursor.execute(f'SELECT EXISTS (SELECT 1 FROM "{safe_column}" WHERE steamid = ? AND assetid = ? AND classid = ? AND instanceid = ?);', params)
        return bool(result.fetchone()[0])
    
    def delete_all_from_column(self, column: str) -> bool:
        """
        Deletes all records from the specified column in the database.

        This function attempts to delete all records from the specified column in the database.
        It logs the action at the INFO level before attempting the deletion. If the operation is successful, 
        it logs a success message and returns True. If an error occurs, it logs the error at the ERROR level 
        and returns False.

        Args:
            column (str): Name of the column in the database from which to delete all records.

        Returns:
            bool: True if the deletion was successful, False if an error occurred.
        """
        
        self.logger.log(level=20, msg=f"Deleting all records from {column}")
        try:
            # Ensure the column name is safely included in the query
            safe_column = column.replace('"', '""')
            self.cursor.execute(f'DELETE FROM "{safe_column}";')
            self.logger.log(level=20, msg=f"Successfully deleted all records from {column}")
            return True
        except Exception as e:
            self.logger.log(level=40, msg=f"Failed to delete all records from {column}: {e}")
            return False
            
    def database_to_dict(self, column: str) -> dict:
        """
        Fetches all records from the specified column in the database and returns them as a list of dictionaries.

        This function executes a SELECT query on the specified column, retrieves all rows, and converts each row into a dictionary.
        It logs the operation at the INFO level before execution and handles any errors by logging them at the ERROR level.

        Args:
            column (str): Name of the column in the database to select records from.

        Returns:
            dict: A list of dictionaries representing the rows in the specified column if successful, 
                or an empty list if an error occurs.
        """
        
        self.logger.log(level=20, msg=f"Fetching all records from {column}")
        try:
            # Ensure the column name is safely included in the query
            safe_column = column.replace('"', '""')
            # Fetch all records and convert each row to a dictionary
            rows = self.cursor.execute(f'SELECT * FROM "{safe_column}";').fetchall()
            result = [dict(row) for row in rows]
            self.logger.log(level=20, msg=f"Successfully fetched records from {column}")
            return result
        except Exception as e:
            # Log the error and return an empty list
            self.logger.log(level=40, msg=f"Error fetching records from {column}: {e}")
            return []
    
    def delete_from_column_where_steamid(self, column: str, steamid: str) -> bool:
        """ 
        Deletes records from the specified column in the database where the steamid matches.

        Args: 
            column (str): name of column in the database to delete from
            steamid (str): steamID64

        returns:
            bool: True if successful, False if something went wrong
        """
        
        self.logger.log(level=20, msg=f"Deleting all records from {column} where steamid: {steamid}")
        try:
            safe_column = column.replace('"', '""')
            self.cursor.execute(f'DELETE FROM "{safe_column}" WHERE steamid = ?;', (steamid,))
            self.logger.log(level=20, msg=f"Successfully deleted records from {column} where steamid: {steamid}")
            return True
        except Exception as e:
            self.logger.log(level=40, msg=f"Error deleting records from {column} where steamid: {steamid}: {e}")
            return False

    def test(self, column):
        result = self.cursor.execute(f"SELECT * FROM {column} WHERE spell == 'None';")
        result_result = result.fetchone()
        print(result_result)
        column = "new_stn_strange_bots"
        self.cursor.execute(f"INSERT INTO {column} ('steamid', 'assetid', 'classid', 'instanceid', 'tradable', 'craftable', 'name', 'quality', 'type', 'killstreaks', 'sheen', 'killstreaker', 'paint', 'spell', 'effect', 'parts') VALUES ({result_result});")