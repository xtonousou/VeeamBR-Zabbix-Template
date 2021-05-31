#! /usr/bin/env bash
# Author: Sotirios Roussis - sroussis@space.gr
# Dependencies: curl, jq

declare -r cdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

umask 0077
source "${cdir}/.env"

function veeam_auth() {
    curl -s -X POST -k "https://${VEEAM_HOST}:9419/api/oauth2/token" \
        -H  "accept: application/json" \
        -H  "x-api-version: ${VEEAM_API_VERSION}" \
        -H  "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=password&username=${VEEAM_USERNAME}&password=${VEEAM_PASSWORD}&refresh_token=&code=&use_short_term_refresh="
    return 0
}

function veeam_refresh() {
    curl -s -X POST -k "https://${VEEAM_HOST}:9419/api/oauth2/token" \
        -H  "accept: application/json" \
        -H  "x-api-version: ${VEEAM_API_VERSION}" \
        -H  "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=refresh_token&username=&password=&refresh_token=${1}&code=&use_short_term_refresh="
    return 0
}

function lock_file() {
    while :; do
        if [ -f "${1}.lock" ]; then
            sleep 0.5
            continue
        fi
        break
    done

    touch "${1}.lock"
    return 0
}

function unlock_file() {
    rm -f "${1}.lock"
    return 0
}

function cleanup() {
    rm -f "${VEEAM_CACHE_FILE}" "${VEEAM_CACHE_FILE}.lock"
}

function main() {
    declare sleep_time=300

    while :; do
        if ! grep -q -i "refresh_token" "${VEEAM_CACHE_FILE}" &>/dev/null; then
            lock_file "${VEEAM_CACHE_FILE}"
            veeam_auth >| "${VEEAM_CACHE_FILE}"
            unlock_file "${VEEAM_CACHE_FILE}"
        fi

        sleep_time=$(jq -r -M '.["expires_in"]' "${VEEAM_CACHE_FILE}")
        sleep_time=$(( sleep_time - 60 ))
        sleep "${sleep_time}"

        lock_file "${VEEAM_CACHE_FILE}"
        veeam_refresh "$(jq -r -M '.["refresh_token"]' "${VEEAM_CACHE_FILE}")" >| "${VEEAM_CACHE_FILE}"
        unlock_file "${VEEAM_CACHE_FILE}"
    done

    return 0
}

trap cleanup EXIT

main
exit "${?}"
