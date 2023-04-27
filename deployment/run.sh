#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

BASE_DIR="$(dirname "$(readlink -f "$0")")"

INVENTORY_FILE="${BASE_DIR}/inventory.ini"
PLAYBOOK_FILE="${BASE_DIR}/tasks.yml"


#
# Launch the Ansible
#
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_NOCOWS=True
export ANSIBLE_STDOUT_CALLBACK=debug

ansible-playbook \
    --inventory "${INVENTORY_FILE}" \
    "${PLAYBOOK_FILE}"
