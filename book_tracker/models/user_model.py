import hashlib
import logging
import os

from flask_login import UserMixin #might resolve in venv
from sqlalchemy.exc import IntegrityError

from book_tracker.db import db
from book_tracker.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)

#create, class fields, add methods etc.... 