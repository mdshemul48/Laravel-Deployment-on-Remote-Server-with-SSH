def makeSupervisor(name):
    return (
        f"[program:{name}-worker]\n"
        "process_name=%(program_name)s_%(process_num)02d\n"
        f"command=php /var/www/html/{name}/radius-circle/artisan queue:listen --tries=3\n"
        "autostart=true\n"
        "autorestart=true\n"
        "stopasgroup=true\n"
        "killasgroup=true\n"
        "user=root\n"
        "numprocs=2\n"
        "redirect_stderr=true\n"
        f"stdout_logfile=/var/www/html/{name}/radius-circle/worker.log\n"
        "stopwaitsecs=3600"
    )

def makeVartualHost(name, url):
    return f"<VirtualHost *:80>\n\
    <Directory /var/www/html/{name}/radius-circle/public>\n\
        Options FollowSymLinks MultiViews\n\
        AllowOverride All\n\
        Require all granted\n\
    </Directory>\n\
    \n\
    ServerName {url}\n\
    ServerAdmin info@{url}\n\
    DocumentRoot /var/www/html/{name}/radius-circle/public\n\
    \n\
    ErrorLog ${{APACHE_LOG_DIR}}/error.log\n\
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined\n\
    \n\
</VirtualHost>\n\
"