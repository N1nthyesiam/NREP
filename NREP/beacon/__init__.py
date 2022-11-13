import socket, uvicorn, json, time
from Crypto.Hash import MD2
from fastapi import Request, FastAPI, APIRouter
from NREP.core.NREPClient import SimpleClient
from NREP.utils.logpong import Debug as debug
from NREP.utils.spec import adict

class Beacon:
	def __init__(self, config):
		debug.log("Initializing Beacon...")
		self.config = config
		self.configurate(self.config)
		self.setup()
		debug.log('Beacon started successful!')
		debug.log(f'Running on {self.host} port {self.port}')

	def configurate(self, config):
		self.location = config.location
		self.app = FastAPI()
		self.router = APIRouter()
		self.host = socket.gethostbyname(config.host)
		self.port = config.port
		with open(config.nodelist, "r") as file:
			self.nodelist = json.load(file)
		self.last_update = time.time()
		
	def list_node(self, reg, loc, host, port, pubk):
		SimpleClient([f'{host}:{port}'], [pubk]).connect(f'{self.host}:{self.port}')
		md2 = MD2.new()
		md2.update(reg.encode()+loc.encode()+host.encode()+port.encode())
		name = md2.hexdigest()
		self.nodelist[reg][loc][name] = {
			"host": host,
			"port": port,
			"publickey": pubk
		}
		self.last_update = time.time()
			
	def setup(self):
		self.router.add_api_route("/nodes", self.get_nodes, methods=["GET"])
		self.router.add_api_route("/enroll", self.enroll, methods=["POST"])
		# self.router.add_api_route("/check", self.check, methods=["POST"])
		self.router.add_api_route("/lastupdate", self.get_last_update, methods=["GET"])
		self.app.include_router(self.router)
		uvicorn.run(self.app, host=self.host, port=self.port)

	async def get_last_update(self):
		return self.last_update

	async def get_nodes(self):
		return self.nodelist

	async def enroll(self, request: Request):
		data = adict(await request.json())
		region, location = data.location.split("-")
		host = data.host
		port = data.port
		public_key = data.pubk
		self.list_node(region, location, host, port, public_key)

