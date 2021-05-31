#! /usr/bin/env bash

declare -r externalscripts=$(awk -F'=' '/ExternalScripts/{print $2}' /etc/zabbix/zabbix_proxy.conf || echo -n "/usr/lib/zabbix/externalscripts" | sed 's/ //g')

cd "${externalscripts}/veeam-br-zabbix-template"
./collect.py "${@}"
