# TF2LootScout
`TF2LootScout` is a script that extracts TF2 items from STN.eu bot Steam inventories, adds them to an SQLite database, and compares them with previously stored items to identify new and valuable items. It scans for valuable items among the new additions and sends notifications to your phone via Telegram.

## Installation

1. Fork the repo.
2. Install the required packages: 
```sh
   pip install -r /path/to/requirements.txt
```

## Usage
1. Add your own STN.eu API key (`api_key`), Telegram token (`token`) and chat ID (`chat_id`) to `data/config.ini`.
2. Run the script:
```sh
   python run.py
```

#### Cronjob
To run the program every half hour, replace the paths and add the following entry to your crontab (`crontab -e`):

```crontab
VALORIZER_APP_PATH=/path/tp/TF2LootScout/
*/30 * * * * /path/to/python3 /path/to/TF2LootScout/run.py >> /path/to/TF2LootScout/data/cron.log 2>&1
```

You can set the environment variable VALORIZER_APP_PATH; otherwise, it defaults to the current directory.

## License

[MIT](https://choosealicense.com/licenses/mit/)