from fastapi import FastAPI
from pydantic import BaseModel
from ServerManager import ServerManager
from DatabaseManage import DatabaseMannage
from CloudflareAPI import CloudflareAPI
import os,time

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "echo": "build by shimul. CHILL Software up and running..."}


class SoftwareCredentials(BaseModel):
    softwareName: str
    hostAddress: str


@app.post("/deploy-software")
def create_software(softwareCredentials: SoftwareCredentials):
    try:
        startTime = time.time()
        
        databaseMannage = DatabaseMannage(softwareCredentials.hostAddress, 
            os.getenv("DATABASE_HOST_USER"), 
            os.getenv("DATABASE_HOST_PASSWORD"))
        databaseMannage.create_database(softwareCredentials.softwareName)
        print("Database Created")
        cloudflareAPI = CloudflareAPI(os.getenv("CLOUDFLARE_TOKEN"), os.getenv("CLOUDFLARE_ZONE"))
        cloudflareAPI.createDNSRecord(softwareCredentials.softwareName, softwareCredentials.hostAddress)
        print("DNS Created")
        serverMenager = ServerManager({ 
            "host": softwareCredentials.hostAddress,
        })
        
        serverMenager.setSoftwareName(softwareCredentials.softwareName)
        print("Software Name Set")
        serverMenager.configureGit()
        print("Git Configured")
        serverMenager.createDirectoryForNewSoftware()
        print("Directory Created")
        serverMenager.cloneProject()
        print("Project Cloned")
        serverMenager.composerInstall()
        print("Composer Installed")
        serverMenager.createENV()
        print("ENV Created")
        serverMenager.laravelSetup()
        print("Laravel Setup")
        serverMenager.createVirtualHost()
        print("Virtual Host Created")
        serverMenager.createSupervisor()
        print("Supervisor Created")
        serverMenager.createCronJob()
        print("Cron Job Created")
        serverMenager.enableCertBot()
        print("Certbot Enabled")
        serverMenager.removeGit()
        print("Git Removed")
        
        endTime = time.time()
        totalRunTime = endTime - startTime
        
        
        return {"status": "ok", 
            "softwareName": softwareCredentials.softwareName, 
            "softwareLink": f"https://{softwareCredentials.softwareName}.{os.getenv('SOFTWARE_MAIN_DOMAIN')}",
            "totalRunTime": totalRunTime,
            "message": "Software created successfully."
    }
    except Exception as e:
        print(e)
        return {"status": "error", "echo": "Software creation failed.", "error": str(e)}