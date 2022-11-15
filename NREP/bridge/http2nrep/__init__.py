import socket, threading, time
from NREP.core.NREPClient import SimpleClient, SimpleBeaconManager, SimplePathTracer

class Bridge:
    upspeed = 0
    downspeed = 0
    tbuf = 1024

    def __init__(self, host: str, port: int, beacon_url: str, beacon_updates_rate: float=60, max_connections: int=100):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.beacon = SimpleBeaconManager(beacon_url)
        self.pathtracer = ()
        self.beacon_updates_rate = beacon_updates_rate
        threading.Thread(target=self.nodes_list_updater).start()
        self.socket.listen(max_connections)
        self.sessions = []
        threading.Thread(target=self.speedometer).start()
        while True:
            try:
                conn, addr = self.socket.accept()
                points, keys = SimpleBeaconManager.get_wpk(SimplePathTracer.trace_path(self.nodelist))
                self.sessions.append(Session(conn, points, keys))
            except:
                conn.close()

    def nodes_list_updater(self):
        while True:
            self.nodelist = self.beacon.get_nodes()
            time.sleep(self.beacon_updates_rate)
            
    def speedometer(self):
        while True:
            print("UpSpeed:", round(Bridge.upspeed/200,1), "\tDownSpeed:", round(Bridge.downspeed/200,1), "  ", end="\r")
            Bridge.upspeed = Bridge.downspeed = 0
            for i in self.sessions:
                if(not i.alive):
                    self.sessions.remove(i)
            time.sleep(0.2)

class Session():
    def __init__(self, conn: socket.socket, points: list, keys: list):
        self.buffer_size = Bridge.tbuf
        self.alive = True
        raw_hs = conn.recv(4096)
        if(len(raw_hs)==0):
            return
        hs = raw_hs.split()
        self._from = conn
        if(hs[0]==b"CONNECT"):
            self._to = SimpleClient(points, keys).connect(hs[1].decode())
            self._from.send(hs[2]+b" 200 Connection established\r\n\r\n")
        elif(hs[0] in [b"GET", b"POST", b"PUT", b"DELETE", b"HEAD", b"OPTIONS", b"TRACE", b"PATCH"]):
            self._to = SimpleClient(points, keys).connect(hs[4].decode()+":80")
            self._to.send(raw_hs)
        else:
            conn.close()
            return
        
        threading.Thread(target=self.rx).start()
        threading.Thread(target=self.tx).start()

    def close(self):
        self.alive = False
        self._from.close()
        self._to.close()

    def tx(self):
        try:
            while True:
                recv = self._from.recv(self.buffer_size)
                if(recv):
                    self._to.sendall(recv)
                    Bridge.upspeed += len(recv)
                else:
                    self._from.close()
                    self._to.close()
                    break
        except:
            self.close()

    def rx(self):
        try:
            while True:
                recv = self._to.recv(self.buffer_size)
                if(recv):
                    self._from.sendall(recv)
                    Bridge.downspeed += len(recv)
                else:
                    self._from.close()
                    self._to.close()
                    break
        except:
            self.close()

