#! /usr/bin/env bash

declare -r externalscripts=$(awk -F'=' '/ExternalScripts/{print $2}' /etc/zabbix/zabbix_proxy.conf || awk -F'=' '/ExternalScripts/{print $2}' /etc/zabbix/zabbix_server.conf || echo -n "/usr/lib/zabbix/externalscripts" | sed 's/ //g')

cd "${externalscripts}/VeeamBR-Zabbix-Template"
./collect.py "${@}"
