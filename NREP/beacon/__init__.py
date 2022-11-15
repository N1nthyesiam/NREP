import socket, uvicorn, threading, json, time
from Crypto.Hash import MD2
from fastapi import Request, FastAPI, APIRouter
from NREP.core.NREPClient import SimpleClient
from NREP.utils.logpong import Debug as debug
from NREP.utils.spec import adict
from NREP.core.package import get_nodes_from_listing

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
		self.clean_interval = config.clean_interval
		with open(config.nodelist, "r") as file:
			self.nodelist = json.load(file)
		self.last_update = time.time()
		
	def list_node(self, reg: str, loc: str, host: str, port: str, pubk: str):
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
		threading.Thread(target=self.cleaner).start()
		uvicorn.run(self.app, host=self.host, port=self.port)

	def cleaner(self):
		while True:
			nodes = get_nodes_from_listing(self.nodelist)
			for node in nodes:
				try:
					SimpleClient([f'{nodes[node]["host"]}:{nodes[node]["port"]}'], [nodes[node]["publickey"]]).connect(f'{self.host}:{self.port}')
				except:
					del self.nodelist[nodes[node]['region']][nodes[node]['location']][node]

			time.sleep(self.clean_interval)

	async def check_node(self, request: Request):
		data = adict(await request.json())
		return json.dumps(data.node in get_nodes_from_listing(self.nodelist))

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

