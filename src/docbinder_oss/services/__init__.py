import logging
from rich.logging import RichHandler


if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

logging.getLogger("googleapiclient").setLevel(logging.WARNING)
