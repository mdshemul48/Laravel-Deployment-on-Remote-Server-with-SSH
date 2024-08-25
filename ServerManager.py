from paramiko import SSHClient, AutoAddPolicy, SFTPClient
import os
from dotenv import load_dotenv
import time
from DatabaseManage import DatabaseMannage
from CloudflareAPI import CloudflareAPI

load_dotenv()


class ConfigureServer:
    sftp: SFTPClient = None

    def __init__(self, remoteServerCredintials: dict):
        self.remoteServerCredintials = remoteServerCredintials
        # remote server credintials
        defaultRemotePort = os.getenv("REMOTE_PORT")
        defaultRemoteUsername = os.getenv("REMOTE_USERNAME")
        defaultRemotePassword = os.getenv("REMOTE_PASSWORD")

        # remote database software credintials
        self.databasePassword = os.getenv("SOFTWARE_DATABASE_PASSWORD")

        remoteHost = self.remoteServerCredintials["host"]
        remotePort = (
            self.remoteServerCredintials["port"]
            if "port" in self.remoteServerCredintials
            else defaultRemotePort
        )
        remoteUsername = (
            self.remoteServerCredintials["username"]
            if "username" in self.remoteServerCredintials
            else defaultRemoteUsername
        )
        remotePassword = (
            self.remoteServerCredintials["password"]
            if "password" in self.remoteServerCredintials
            else defaultRemotePassword
        )

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(remoteHost, remotePort, remoteUsername, remotePassword)
        self.sftp = self.ssh.open_sftp()

    def runCommand(self, command: str):
        try:
            _, stdout, stderr = self.ssh.exec_command(f'sudo bash -c "{command}"')
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                output = stdout.read().decode("utf-8")
                return output
            else:
                error = stderr.read().decode("utf-8")
                raise Exception(
                    f"Error executing command '{command}'. Exit status: {exit_status}\nError: {error}"
                )
        except Exception as e:
            raise Exception(f"An error occurred: {e}")


class ServerManager(ConfigureServer):
    def __init__(self, remoteServerCredintials: dict):
        super().__init__(remoteServerCredintials)

        githubUser = os.getenv("GITHUB_USER")
        githubApi = os.getenv("GITHUB_API")
        self.gitCredentialsContent = "https://{0}:{1}@github.com".format(
            githubUser, githubApi
        )
        self.softwareRepository = os.getenv("SOFTWARE_REPOSITORY")
        self.softwareDomain = os.getenv("SOFTWARE_MAIN_DOMAIN")

    def setSoftwareName(self, softwareName: str):
        self.softwareName = softwareName
        self.softwareLink = f"{self.softwareName}.{self.softwareDomain}"
        self.softwarePath = f"/var/www/html/{self.softwareName}/radius-circle"

    def setMainDomain(self, domainName: str):
        self.mainDomain = domainName
        pass

    def configureGit(self):

        try:
            self.runCommand("rm ~/.git-credentials")
        except:
            pass
        self.runCommand("git config --global credential.helper store")
        time.sleep(1)
        self.runCommand(f"echo '{self.gitCredentialsContent}' > ~/.git-credentials")
        self.runCommand("chmod 600 ~/.git-credentials")

    def removeGit(self):
        self.runCommand("rm ~/.git-credentials")
        self.runCommand("git config --global --unset credential.helper")

    def createDirectoryForNewSoftware(self):
        command = f"mkdir /var/www/html/{self.softwareName}"
        response = self.runCommand(command)
        return response

    def cloneProject(self):
        command = f"git clone {self.softwareRepository} {self.softwarePath}"
        response = self.runCommand(command)
        return response

    def composerInstall(self):
        command = f"cd {self.softwarePath} && composer install --no-interaction"
        response = self.runCommand(command)
        return response

    def createENV(self):
        commands = [
            f"cd {self.softwarePath}",
            "cp .env.example .env",
            f"sed -i 's/__database_name__/{self.softwareName}/g' .env",
            f"sed -i 's/__database_pass__/{self.databasePassword}/g' .env",
            f"sed -i 's/__base_url__/https://{self.softwareName}.{self.mainDomain}/g' .env",
        ]
        joinedCommand = " && ".join(commands)
        response = self.runCommand(joinedCommand)
        return response

    def laravelSetup(self):
        artisanCommands = [
            "php artisan migrate --seed",
            "php artisan backup:clean --disable-notifications",
            "php artisan key:generate",
            "chown -R www-data:www-data storage",
            "chmod -R 777 storage",
            "php artisan storage:link",
            "php artisan optimize:clear",
            "php artisan optimize",
        ]
        joinedCommand = " && ".join(artisanCommands)
        command = f"cd {self.softwarePath} && {joinedCommand}"
        response = self.runCommand(command)
        return response

    def createVirtualHost(self):
        virtualHost = """<VirtualHost *:80>
<Directory {0}/public>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    
        ServerName {1}
        ServerAdmin info@{1}
        DocumentRoot {0}/public

        ErrorLog ${{APACHE_LOG_DIR}}/error.log
        CustomLog ${{APACHE_LOG_DIR}}/access.log combined
        
</VirtualHost>""".format(
            self.softwarePath, self.softwareLink
        )
        command = f"echo '{virtualHost}' > /etc/apache2/sites-available/{self.softwareName}.conf"
        self.runCommand(command)
        self.runCommand(f"a2ensite {self.softwareName}.conf")
        self.runCommand("systemctl restart apache2")

    def createSupervisor(self):
        supervisorText = (
            f"[program:{self.softwareName}-worker]\n"
            "process_name=%(program_name)s_%(process_num)02d\n"
            f"command=php {self.softwarePath}/artisan queue:listen --tries=3\n"
            "autostart=true\n"
            "autorestart=true\n"
            "stopasgroup=true\n"
            "killasgroup=true\n"
            "user=root\n"
            "numprocs=2\n"
            "redirect_stderr=true\n"
            f"stdout_logfile={self.softwarePath}/worker.log\n"
            "stopwaitsecs=3600"
        )

        self.runCommand(f"cd /etc/supervisor/conf.d && touch {self.softwareName}.conf")
        self.runCommand(
            f"echo '{supervisorText}' > /etc/supervisor/conf.d/{self.softwareName}.conf"
        )
        self.runCommand("systemctl restart supervisor")
        self.runCommand("supervisorctl restart all")

    def createCronJob(self):
        cronJobText = (
            f"* * * * * php {self.softwarePath}/artisan schedule:run >> /dev/null 2>&1"
        )

        self.runCommand(f"crontab -l > mycron")
        self.runCommand(f"echo '{cronJobText}' >> mycron")
        self.runCommand(f"crontab mycron")
        self.runCommand(f"rm mycron")

    def enableCertBot(self):
        self.runCommand(
            f"sudo certbot --apache --non-interactive --agree-tos --redirect -d {self.softwareName}.{self.softwareDomain}"
        )
