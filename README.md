# tf2_valorizer
tf2_valorizer is a script that gets items from tf2 steam inventories adds them to a database and compares them to previous ones to get the new ones. It checks the new items for valuable items and sends a notification to your phone through telegram.

## Installation

1. Fork the repo
2. Pip install -r /path/to/requirements.txt

## Usage
1. Add your own STN.eu api key and telegram token and chatid to config.ini
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