from fastapi import FastAPI
from pydantic import BaseModel
from ServerManager import ServerManager
from DatabaseManage import DatabaseMannage
from CloudflareAPI import CloudflareAPI
import os, time

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

        databaseMannage = DatabaseMannage(
            softwareCredentials.hostAddress,
            os.getenv("DATABASE_HOST_USER"),
            os.getenv("DATABASE_HOST_PASSWORD"),
        )
        databaseMannage.create_database(softwareCredentials.softwareName)

        if softwareCredentials.softwareName not in databaseMannage.databases():
            raise Exception("Database creation failed.")

        cloudflareAPI = CloudflareAPI(
            os.getenv("CLOUDFLARE_TOKEN"), os.getenv("CLOUDFLARE_ZONE")
        )
        cloudflareAPI.createDNSRecord(
            softwareCredentials.softwareName, softwareCredentials.hostAddress
        )

        serverMenager = ServerManager(
            {
                "host": softwareCredentials.hostAddress,
            }
        )

        serverMenager.setSoftwareName(softwareCredentials.softwareName)
        serverMenager.setMainDomain(os.getenv("SOFTWARE_MAIN_DOMAIN"))
        serverMenager.configureGit()
        serverMenager.createDirectoryForNewSoftware()
        serverMenager.cloneProject()
        serverMenager.composerInstall()
        serverMenager.createENV()
        serverMenager.laravelSetup()
        serverMenager.createVirtualHost()
        serverMenager.createSupervisor()
        serverMenager.createCronJob()
        serverMenager.enableCertBot()
        serverMenager.removeGit()

        endTime = time.time()
        totalRunTime = endTime - startTime

        return {
            "status": "ok",
            "softwareName": softwareCredentials.softwareName,
            "softwareLink": f"https://{softwareCredentials.softwareName}.{os.getenv('SOFTWARE_MAIN_DOMAIN')}",
            "totalRunTime": totalRunTime,
            "message": "Software created successfully.",
        }
    except Exception as e:
        print(e)
        return {"status": "error", "echo": "Software creation failed.", "error": str(e)}
