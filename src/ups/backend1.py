from nut2 import PyNUTClient

class session:
    def __init__(self, ups_name: str, host: str = "127.0.0.1", port: int = 3493):
        self.ups_name = ups_name
        self.client = PyNUTClient(host=host, port=port)
    
    def status(self) -> dict:
        return self.client.list_vars(self.ups_name)

if __name__ == "__main__":
    import json
    data = session("ecoEaton").status()
    data2 = json.dumps(data, indent=4)
    print(data2)