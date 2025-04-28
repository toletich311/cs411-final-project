import logging
import math
import os
import time
from typing import List

from book_tracker.models.book_model import Books
from book_tracker.utils.logger import configure_logger
from book_tracker.utils.google_books_api import search_books

##might have to import more from api



logger = logging.getLogger(__name__)
configure_logger(logger)

#create class and add fields + methods 