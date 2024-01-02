import requests


class CloudflareAPI:
    def __init__(self, token:str, zoneID: str):
        self.token = token
        self.zoneID = zoneID
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def createDNSRecord(self, name: str, ip: str):
        data = {
            "type": "A",
            "name": name,
            "content": ip,
            "ttl": 1,
            "proxied": False
        }

        url = f"https://api.cloudflare.com/client/v4/zones/{self.zoneID}/dns_records"
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def search(self, name: str):

        url = f"https://api.cloudflare.com/client/v4/zones/{self.zoneID}/dns_records?name={name}"
        response = requests.get(url, headers=self.headers)
        return response.json()
