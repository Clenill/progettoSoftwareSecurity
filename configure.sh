#!/bin/sh

PASSWORD_FILE="secrets/db_password"
mkdir -p secrets
touch "$PASSWORD_FILE"
chmod 600 "$PASSWORD_FILE"

echo "Choose a database password: "
stty -echo
read -r password
stty echo
echo ""
printf "%s" "$password" > "$PASSWORD_FILE"
echo "Done!"

