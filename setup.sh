#!/usr/bin/env bash

source utils.sh

print-help() {
  echo "\
Usage: $0 [-h|--help] [-g|--generate-password] [-q|--quiet] [-n|--no-user] [-f]

Options:
    -h, --help
        Show this help and exit.
    -q
        Do not show any prompts.
    -g, --generate-password
        If --create-user, generate the user's password using openssl.
        Ignores the API_PASSWORD environment variable.
    -n, --no-user
        Do not create a new user. If missing, takes its credentials
        from the API_USERNAME and API_PASSWORD environment variables,
        and if the variable does not exist prompts the user for missing
        values. If -q, it will print an error instead. If -g, the user's
        password will be generated.
    -f
        Force create the new user. This will delete any matching user in the database
        and create the new one.
"
}

ARGS=$(getopt -o hqgnf --long help,quiet,generate-password,no-user -n "$0" -- "$@")
if [ $? -ne 0 ];
  then print-help | head -n 1; exit 1
fi

eval set -- "$ARGS"

quiet=0
generate_password=0
create_user=1
overwrite_param=""

while true; do
  case "$1" in
    -h|--help)
      print-help
      exit ;;
    -q|--quiet)
      quiet=1
      shift ;;
    -g|--generate-password)
      generate_password=1
      shift ;;
    -n|--no-user)
      create_user=0
      shift ;;
    -f)
      overwrite_param="-f"
      shift ;;
    --)
      shift
      break ;;
    *)
      print-help | head -n 1
      exit 1 ;;
  esac
done

PYTHON=python3
PIP=pip3

# Install required packages
echo "Upgrading pip..."
${PIP} install --upgrade pip

echo "Installing dependencies..."
${PIP} install -r "$($PYTHON get_dependency_file.py)" || exit 1

# Generate a Django secret key and make it available
echo "export SECRET_KEY=$(openssl rand -hex 100)" > .env
source .env

# Create superuser credentials
if [ $create_user = 1 ]; then
  echo "Setting up database..."
  ${PYTHON} manage.py makemigrations solax_registers || exit 1
  ${PYTHON} manage.py migrate || exit 1

  echo "Creating user..."
  DJANGO_SUPERUSER_USERNAME="$(QUIET=$quiet get-username)" || exit $?
  DJANGO_SUPERUSER_PASSWORD="$(\
    GENERATE_PASSWORD=$generate_password\
    QUIET=$quiet get-password
  )" || exit $?

  export DJANGO_SUPERUSER_USERNAME DJANGO_SUPERUSER_PASSWORD

  ${PYTHON} manage.py createsuperuser \
    --email test@example.com \
    --no-input $overwrite_param || exit 1
fi

# Collect the Django static files
echo "Collecting static files..."
${PYTHON} manage.py collectstatic --noinput
echo "Setup done!"

if [ $create_user = 1 ] && [ $generate_password = 1 ]; then
  echo "You have created a new user successfully! The following are the credentials:"
  echo ${DJANGO_SUPERUSER_USERNAME}
  echo ${DJANGO_SUPERUSER_PASSWORD}
fi
