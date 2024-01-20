# Laravel Deployment Automation Script

## Overview

This automation script streamlines the deployment of Laravel projects on remote servers, providing a convenient and efficient way to set up and configure your applications. The script leverages SSH for secure communication with the server and integrates various tasks seamlessly.

## Features

- **Database Initialization**: The script automatically creates a database using the credentials provided in the `.env` file.
- **Cloudflare DNS Setup**: It generates a subdomain with the Laravel host server's IP on Cloudflare, enhancing accessibility.
- **SSH Remote Server Access**: Utilizing the Python Paramiko package, the script establishes an SSH connection to the remote server.
- **GitHub Integration**: Login credentials stored in the `.env` file facilitate easy access to your GitHub account.
- **Directory and Project Cloning**: The script creates a new directory for the software inside the server's HTML/www folder and clones the project from GitHub.
- **Composer Installation**: Installs all required vendors for the Laravel project using Composer.
- **Environment Configuration**: Generates the `.env` file for the Laravel project, ensuring proper environmental settings.
- **Laravel Setup Commands**: Executes essential Laravel setup commands such as migrate, seed, optimize, key:generate, and storage:link using `php artisan`.
- **Apache VirtualHost Configuration**: Sets up a virtual host for Apache to enable proper functioning with the subdomain.
- **Supervisor Integration**: Adds Supervisor to manage Laravel tasks, ensuring robust and consistent performance.
- **Cron Job Addition**: Incorporates a cron job for scheduled tasks within the Laravel application.
- **Certbot SSL Certificate**: Enables Certbot for the automatic provision of SSL certificates, enhancing security.

## Environment Variables
- Clone the repository.
- Install required Python modules using `pip install -r requirements.txt`.
- Set up the required environment variables in the `.env` file.
- Set the following environment variables in the `.env` file:

```dotenv
# Remote default user password
SOFTWARE_MAIN_DOMAIN=
REMOTE_USERNAME=
REMOTE_PASSWORD=
REMOTE_PORT=22

# Database initialization on the remote MySQL server
DATABASE_HOST_USER=
DATABASE_HOST_PASSWORD=

# Remote server software database password for root MySQL
# This will be used by the Laravel application to connect with the database. Default name is root
SOFTWARE_DATABASE_PASSWORD=

# GitHub credentials
GITHUB_USER=
GITHUB_API=
SOFTWARE_REPOSITORY=

# Cloudflare credentials
CLOUDFLARE_TOKEN=
CLOUDFLARE_ZONE=
```
## MySQL Configuration
Before running the deployment script, ensure that your MySQL server is configured to allow remote connections. By default, MySQL may be set to bind only to the localhost, restricting remote access. To enable remote connections, follow these steps:

1. **Open MySQL Configuration File:**

   Locate and open your MySQL configuration file. This file is often named my.cnf or my.ini and is typically found in the MySQL installation directory.
2. **Update Bind Address:**

   Find the bind-address parameter in the configuration file and change its value to `0.0.0.0` or the specific IP address of your server.

   Example:
      ```dotenv
      bind-address = 0.0.0.0
      ```
      If you want to allow connections from specific IP addresses, you can set the bind address accordingly.
3. **Restart MySQL Server:**

    Save the changes to the configuration file and restart the MySQL server to apply the new settings.
   ```console
    foo@bar:~$ sudo systemctl restart mysql
   ```
By ensuring that MySQL is not bound exclusively to localhost, you enable remote access and allow the Laravel deployment script to interact with the MySQL server from your remote machine.

**Note:** Be cautious about opening up MySQL to remote connections for security reasons. Consider restricting access to specific IP addresses and using strong authentication mechanisms.

## Running the Application
After completing the deployment script and setting up your Laravel project, you can run the application using the following command:
```console
 foo@bar:~$ uvicorn main:app --reload
```

Once the application is running, open your web browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger documentation and interactive API documentation. This interface provides a user-friendly way to explore and test your API endpoints.

Feel free to explore and test the various endpoints exposed by your FastAPI application using the Swagger UI.

## Note
Ensure that you have valid and secure credentials in the `.env` file, protecting sensitive information. This script aims to simplify the deployment process, making it efficient and consistent across different environments. Feel free to contribute and enhance the functionality as needed.

**Happy Deploying**

