#!/usr/bin/env bash

source .env
source utils.sh

PYTHON=python3
PIP=pip3

print-help() {
  echo "\
Usage: $0 [-h|--help] [-g|--generate-password] [-q|--quiet] [-u|--create-user] [-f] [--prestart COMMAND] [ADDRESS [PORT]]

Options:
    -h, --help
        Show this help and exit.
    -q
        Do not show any prompts.
    -g, --generate-password
        If --create-user, generate the user's password. Ignores the API_PASSWORD
        environment variable.
    -u, --create-user
        Create a new user. Takes its credentials from the API_USERNAME and
        API_PASSWORD environment variables, and if the variable does not exist
        prompts the user for missing values. If -q, it will print an error instead.
        If -g, the password will be generated.
    -f
        Force create the new user. This will delete any matching user in the database
        and create the new one.
    --prestart COMMAND
        The command to run just before starting the server.
    ADDRESS
        The address to serve on. Default, 'localhost'.
    PORT
        The port to serve on. Default: '8000'."
}

ARGS=$(getopt -o hqguf --long help,quiet,generate-password,create-user,prestart: -n "$0" -- "$@")
if [ $? -ne 0 ];
  then print-help | head -n 1; exit 1
fi

eval set -- "$ARGS"

quiet=0
generate_password=0
create_user=0
overwrite_param=""
prestart=""

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
    -u|--create-user)
      create_user=1
      shift ;;
    -f)
      overwrite_param="-f"
      shift;;
    --prestart)
      prestart="$2"
      shift 2;;
    --)
      shift
      break ;;
    *)
      print-help | head -n 1
      exit 1 ;;
  esac
done

host=${1:-"localhost"}
port=${2:-"8000"}


echo "Setting up database..."
python3 manage.py makemigrations solax_registers || exit 1
python3 manage.py migrate || exit 1

# Create superuser credentials if needed
if [ $create_user = 1 ]; then
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

if [ $create_user = 1 ] && [ $generate_password = 1 ]; then
  echo "You have created a new user successfully! The following are the credentials:"
  echo $DJANGO_SUPERUSER_USERNAME
  echo $DJANGO_SUPERUSER_PASSWORD
fi

$prestart
REST_API_ADDRESS=$host:$port gunicorn -c gunicorn_conf.py
