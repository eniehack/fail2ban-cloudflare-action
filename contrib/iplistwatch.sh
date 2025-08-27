#!/bin/sh

inotifywait -m -e 'CLOSE_WRITE' --format '%w%f %e' "$IP_FILE" |
while read -r file action; do
    echo "$action on $file"
    rulegen "$IP_FILE" | ruledeploy --stdin
done