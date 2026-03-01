from nut2 import PyNUTClient # type: ignore

client = PyNUTClient(host="localhost", port=3493)

ups = client.list_ups()
print("UPS list:", ups)

upsname = "ecoEaton"
status = client.list_vars(upsname)
print("UPS vars:", status)
