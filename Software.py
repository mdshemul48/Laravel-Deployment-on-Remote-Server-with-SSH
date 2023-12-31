from paramiko import SSHClient,AutoAddPolicy, SFTPClient,Transport
import os
from dotenv import load_dotenv
import time

load_dotenv()

class ServerManager:

    sftp: SFTPClient = None
    def __init__(self, remoteServerCredintials:dict):
        self.remoteServerCredintials = remoteServerCredintials

        remoteHost = self.remoteServerCredintials['host']
        remotePort = self.remoteServerCredintials['port']
        remoteUsername = self.remoteServerCredintials['username']
        remotePassword = self.remoteServerCredintials['password']


        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(remoteHost, remotePort, remoteUsername, remotePassword)
        self.sftp = self.ssh.open_sftp()
        self.shell = self.ssh.invoke_shell()

    def runCommand(self, command: str):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(f'sudo bash -c "{command}"')
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                output = stdout.read().decode('utf-8')
                return output
            else:
                error = stderr.read().decode('utf-8')
                raise Exception(f"Error executing command '{command}'. Exit status: {exit_status}\nError: {error}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
 
    
    def configureGit(self):
        git_credentials_content = "https://{0}:{1}@github.com".format(os.getenv("GITHUB_USER"), os.getenv("GITHUB_API"))
        try:
            self.runCommand("rm ~/.git-credentials")
        except:
            pass
        self.runCommand("git config --global credential.helper store")
        time.sleep(1)
        self.runCommand(f"echo '{git_credentials_content}' > ~/.git-credentials")
        self.runCommand("chmod 600 ~/.git-credentials")

    def removeGit(self):
        self.runCommand("rm ~/.git-credentials")
        self.runCommand("git config --global --unset credential.helper")
    
    def createDirectoryForNewSoftware(self, softwareName: str):
        command = f"mkdir /var/www/html/{softwareName}"
        response = self.runCommand(command)
        return response
    
    def cloneProject(self, softwareName: str, gitUrl: str):
        command = f"git clone {gitUrl} /var/www/html/{softwareName}/radius-circle"
        response = self.runCommand(command)
        return response
    
    def composerInstall(self, softwareName: str):
        command = f"cd /var/www/html/{softwareName}/radius-circle && composer install --no-interaction" 
        response = self.runCommand(command)
        return response
    
    def createENV(self, softwareName: str, databaseName: str,  databasePassword: str):
        commands = [
            f"cd /var/www/html/{softwareName}/radius-circle",
            "cp .env.example .env",
            f"sed -i 's/__database_name__/{databaseName}/g' .env",
            f"sed -i 's/__database_pass__/{databasePassword}/g' .env"
        ]
        joinedCommand = " && ".join(commands)
        response = self.runCommand(joinedCommand)
        return response

    def laravelSetup(self, softwareName: str):
        artisanCommands = [
            "php artisan migrate --seed",
            "php artisan backup:clean --disable-notifications",
            "php artisan key:generate",
            "chown -R www-data:www-data storage",
            "chmod -R 777 storage",
            "php artisan storage:link",
            "php artisan optimize:clear",
            "php artisan optimize"
        ]
        joinedCommand = " && ".join(artisanCommands)
        command = f"cd /var/www/html/{softwareName}/radius-circle && {joinedCommand}"
        response = self.runCommand(command)
        return response

if __name__ == "__main__":
    pass
    