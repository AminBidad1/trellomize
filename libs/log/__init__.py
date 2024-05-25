import logging
from settings import ROOT_DIR

log = logging.getLogger(name="TRELLOMIZE")
logging.basicConfig(filename=ROOT_DIR.joinpath("database").joinpath("logs.txt").resolve(),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s: %(levelname)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S%z",
                    level=logging.DEBUG)

