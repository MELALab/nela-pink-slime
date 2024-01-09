import logging
import os


class MakedirsRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    This is a custom RotatingFileHandler that makes a call to create the target logging directory, if needed.
    """

    def __init__(self, **kwargs):
        os.makedirs(os.path.dirname(kwargs['filename']), exist_ok=True)
        super().__init__(**kwargs)