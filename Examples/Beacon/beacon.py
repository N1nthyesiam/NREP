from NREP.beacon import Beacon
from NREP.utils.spec import Config

config = Config('beacon_config.json')
node = Beacon(config)