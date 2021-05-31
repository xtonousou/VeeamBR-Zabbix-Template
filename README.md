# VEEAM Backup & Replication RESTful API Zabbix Template

## Compatibility

This is currently tested on **Veeam Backup & Replication 11** build 11.0.0.837 with RESTful API version **1.0-rev1**.

## Requirements

You need to install the following packages on your system: `python3`, `python3-pip`, `curl`, `jq`, `bash`, `sudo`.
When you have python3 and python3-pip installed, run the following command to install required python modules: `pip3 install -r requirements.txt`.

## Usage

* Place the project's directory inside `/usr/lib/zabbix/externalscripts/` or whatever directory you have specified inside `/etc/zabbix/zabbix_proxy.conf`.
* Create a privileged user for the Veeam authentication (on Veeam Backup Server). Make sure to test the user first by logging into Veeam and checking the Jobs' status.
* Link `veeam_monitor.sh` to external scripts directory like so: `ln -s /usr/lib/zabbix/externalscripts/veeam-br-zabbix-template/veeam_monitor.sh /usr/lib/zabbix/externalscripts/veeam_monitor.sh`. You may need to change the `/usr/lib/zabbix/externalscripts/` part if this is defined elsewhere.
* Copy the file `env.sample` to another file called **exactly** `.env` inside the project's directory and change the values.
* Give the following permissions to the scripts: `chmod u=rwx,g=r,o= collect.py credential-manager.sh veeam_monitor.sh ; chown zabbix:zabbix collect.py credential-manager.sh veeam_monitor.sh ; chmod 0400 .env`.
* Enable the cron specified inside `crontab.txt` for **root** user.

This is an example of `.env` file:

```plain
VEEAM_USERNAME=veeam_mon_svc
VEEAM_PASSWORD=MyAw3s0m3P@ssw0rd
VEEAM_HOST=veeam-bkp.local
VEEAM_API_VERSION=1.0-rev1
VEEAM_CACHE_FILE=/tmp/.zabbix-veeam.json
```

The script can either be deployed on Zabbix Server or Zabbix Proxy.

### Notes

The script does not verify the certificate when it requests data from the Veeam API. If you have signed certificates, it is highly recommended to change the `verify=False` argument to `verify=True` inside `collect.py` script.

Do not delete the `VEEAM_CACHE_FILE` manually, let the `credential-manager.sh` script handle this. If you need to delete the file, just kill the process of `credential-manager.sh` script. To re-run the `credential-manager.sh` issue the following snippet:

```bash
sudo -u zabbix /bin/bash /usr/lib/zabbix/externalscripts/veeam-br-zabbix-template/credential-manager.sh &
disown
ps auxf | grep credential-manager.sh | grep -v grep  # verify that the process is running
```

## Troubleshooting

Check the API connection from the Zabbix Server/Proxy using the below command.

```bash
curl -s -k https://<veeam-ip>:9419/swagger
```

