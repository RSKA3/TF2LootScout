# tf2_valorizer
tf2_valorizer is a script that extracts TF2 items from Steam inventories, adds them to an SQLite database, and compares them with previously stored items to identify new and valuable items. It scans for valuable items among the new additions and sends notifications to your phone via Telegram.

## Installation

1. Fork the repo
2. Pip install -r /path/to/requirements.txt

## Usage
1. Add your own STN.eu api key and telegram token and chatid to data/config.ini
2. Run valorizer.py

### Cronjob:
Replace paths and add this to crontab -e to run the program every half hour
1. VALORIZER_APP_PATH=/path/tp/tf2_valorizer/
2. */30 * * * * /path/to/python3 /path/to/tf2_valorizer/valorizer.py >> /path/to/tf2_valorizer/data/cron.log 2>&1

You can set the environement variable VALORIZER_APP_PATH otherwise just defaults to current directory

## Contributing

WRITE SOMETHING

## License

[MIT](https://choosealicense.com/licenses/mit/)