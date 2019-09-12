"""
    SmartAPI Web Server Entry Point

        > python index.py

"""

import datetime
import logging
import os.path

from tornado.ioloop import IOLoop
from utils.api_monitor import update_uptime_status
from utils.versioning import backup_and_refresh

import config
from biothings.web.index_base import main
from biothings.web.settings import BiothingESWebSettings

WEB_SETTINGS = BiothingESWebSettings(config=config)


def schedule_daily_job():
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    midnight = datetime.datetime.combine(tomorrow, datetime.time.min)

    def wrapper():
        try:
            backup_and_refresh()
            update_uptime_status()
        except BaseException:
            logging.exception("Failed daily job.")
        schedule_daily_job()
    IOLoop.current().add_timeout(midnight.timestamp(), wrapper)


if __name__ == '__main__':
    (SRC_PATH, _) = os.path.split(os.path.abspath(__file__))
    STATIC_PATH = os.path.join(SRC_PATH, 'static')
    schedule_daily_job()
    main(WEB_SETTINGS.generate_app_list(),
         app_settings={"cookie_secret": config.COOKIE_SECRET},
         debug_settings={"static_path": STATIC_PATH},
         use_curl=True)
