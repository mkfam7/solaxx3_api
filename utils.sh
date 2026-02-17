get-username() {
  if [ -n "${API_USERNAME}" ]; then
    echo "${API_USERNAME}"
    return 0
  fi
  if [ $QUIET = 1 ]; then
    echo "No username has been provided. Remove the -q option or set the API_USERNAME variable." >&2
    exit 1
  else
    read -p "API user: "
    echo $REPLY
  fi
}

get-password() {
  if [ $GENERATE_PASSWORD = 1 ]; then
    echo $(openssl rand -base64 32 | tr -d '\n')
    return 0

  elif [ -n "${API_PASSWORD}" ]; then
    echo "${API_PASSWORD}"
    return 0

  elif [ $QUIET = 1 ]; then
    echo "No password has been provided. Remove the -q option or set the API_PASSWORD variable." >&2
    exit 2

  else
    read -s -p "API password: "
    echo $REPLY
    echo >&2
  fi
}
