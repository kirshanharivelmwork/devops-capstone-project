#!/usr/bin/env bash
# Capture real HTTP request/response evidence from a running Accounts service.
set -euo pipefail

base_url="${ACCOUNTS_BASE_URL:-http://127.0.0.1:8000}"
mkdir -p evidence

create_body='{"name":"Taylor Morgan","email":"taylor.morgan@example.com","address":"123 Main Street, Edinburgh","phone_number":"0131-555-0123"}'
create_file="evidence/rest-create-done"
printf "%s\n" "\$ curl -i -X POST ${base_url}/accounts -H 'Content-Type: application/json' -d '${create_body}'" > "$create_file"
curl -sS -i -X POST "${base_url}/accounts" \
  -H 'Content-Type: application/json' \
  -d "$create_body" | tee -a "$create_file"
echo

account_id=$(python - "$create_file" <<'PY'
import json
import sys
text = open(sys.argv[1], encoding="utf-8").read()
body = text[text.rfind("{"):]
# The command printed above contains request JSON; the final JSON object
# is the real CREATE response body returned by the running service.
data = json.loads(body)
assert isinstance(data.get("id"), int), "CREATE did not return an account ID"
print(data["id"])
PY
)

list_file="evidence/rest-list-done"
printf "%s\n" "\$ curl -i -X GET ${base_url}/accounts" > "$list_file"
curl -sS -i -X GET "${base_url}/accounts" | tee -a "$list_file"
echo

read_file="evidence/rest-read-done"
printf "%s\n" "\$ curl -i -X GET ${base_url}/accounts/${account_id}" > "$read_file"
curl -sS -i -X GET "${base_url}/accounts/${account_id}" | tee -a "$read_file"
echo

update_body='{"name":"Taylor Morgan Updated","email":"taylor.morgan@example.com","address":"456 High Street, Edinburgh","phone_number":"0131-555-0199"}'
update_file="evidence/rest-update-done"
printf "%s\n" "\$ curl -i -X PUT ${base_url}/accounts/${account_id} -H 'Content-Type: application/json' -d '${update_body}'" > "$update_file"
curl -sS -i -X PUT "${base_url}/accounts/${account_id}" \
  -H 'Content-Type: application/json' \
  -d "$update_body" | tee -a "$update_file"
echo

delete_file="evidence/rest-delete-done"
delete_body="{\"id\":${account_id}}"
printf "%s\\n" "\\$ curl -i -X DELETE ${base_url}/accounts -H 'Content-Type: application/json' -d '${delete_body}'" > "$delete_file"
curl -sS -i -X DELETE "${base_url}/accounts" \\
  -H 'Content-Type: application/json' \\
  -d "$delete_body" | tee -a "$delete_file"
echo

printf 'Saved genuine REST API evidence files in evidence/:\n'
ls -l evidence/rest-*-done
