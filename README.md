# Data API

**Warning:** *This API is not yet in its production phase. Therefore the API is not yet secure. However, it supports basic and session authentication using cookies. It currently does not completely support CSRF.*

Project link: [https://github.com/mkfam7/solaxx3_api][project_link]

[project_link]: https://github.com/mkfam7/solaxx3_api


This API stores data from the inverter. It supports multiple users with permissions to only one set of data. It currently uses an SQLite database but can be configured otherwise.

## Prerequisites

1. Install the requirements.

    ```bash
    pip3 install -r requirements.txt
    ```

2. For encrypting passwords and other data, generate a secret key using the following command:
    ```bash
    echo "SECRET_KEY=$(openssl rand -base64 100)" > .env
    ```

3. To create the table schemas, run the following in the project directory:

    ```bash
    python3 manage.py migrate
    ```

4. To be able to authenticate in API requests, create a superuser (user that has all permissions):

    ```bash
    python3 manage.py createsuperuser
    ```

    You will be asked for a username, optional email, and password.  
    In case you forgot your password, use this syntax to change your password:

    ```bash
    python3 manage.py changepassword [USERNAME]
    ```

    By default, `USERNAME` is `admin`.

5. To ensure proper handling of templates and static files, run the following command:

   ```bash
   python3 manage.py collectstatic
   ```

## Usage

### Starting/stopping the server

To start the server, run the following:

```bash
python3 manage.py runserver [TARGET]
```

`TARGET` is the place where to run the server; the default is `localhost:8000` or `127.0.0.1:8000`. If one omits the port from `TARGET`, it defaults to `8000`.

To stop the server, press `Ctrl-C`.

### The admin section

For administrative tasks, Django has provided a useful web application. To access this application, navigate to `/admin` endpoint.

### Documentation

This API has provided a Swagger documentation for API endpoints. To access it, go to `/swagger-docs/` endpoint.
