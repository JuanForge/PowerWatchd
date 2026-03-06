import socket

class session:
    def __init__(self, ups_name: str, host: str = "127.0.0.1", port: int = 3493, timeout: int|float = 1.5):
        self.sock = socket.create_connection((host, port))
        self.sock.settimeout(timeout)
        self.ups_name = ups_name
    
    def _decoder(self, data: str):
        d = {}
        for line in data.splitlines():
            if line.startswith("VAR "):
                parts = line.split(" ", 3)
                d[parts[2]] = parts[3][1:-1]
        return d
    
    def status(self):
        self.sock.sendall(f"LIST VAR {self.ups_name}\n".encode("utf-8"))
        data = b""
        while True:
            chunk = self.sock.recv(2048)
            data += chunk
            if f"END LIST VAR {self.ups_name}".encode("utf-8") in data:
                return self._decoder(data.decode().replace(f"BEGIN LIST VAR {self.ups_name}", "", 1).replace(f"END LIST VAR {self.ups_name}", "", 1))
    
    def close(self):
        self.sock.close()

if __name__ == "__main__":
    import time
    import json
    session2 = session("ecoEaton", "127.0.0.1", 3493)
    liste = []
    last:str = ""
    for i in range(1):
        start_time = time.perf_counter()
        last:str =  session2.status()
        end_time = time.perf_counter()
        liste.append(end_time  - start_time)
    
    for i in liste:
        print(i)
    print(json.dumps(last, indent=4))
    session2.close()