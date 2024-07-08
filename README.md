# Data API

**Warning:** *This API is not suitable for production. It is meant for home use.* It implements some basic securities, including basic authentication and session authentication. However, it does not completely support CSRF.

Project link: [https://github.com/mkfam7/solaxx3_api][project_link]

[project_link]: https://github.com/mkfam7/solaxx3_api


This API stores data from the inverter. It supports multiple users with permissions to only one set of data. It currently uses an SQLite database but can be configured otherwise.

## Prerequisites

1. First of all, install the requirements.

    ```bash
    pip3 install -r requirements.txt
    ```

2. For encryption, generate a secret key using the following command:
    ```bash
    echo "SECRET_KEY=$(openssl rand -base64 100)" > .env
    ```

3. Create the table schemas, by running the following command:

    ```bash
    python3 manage.py migrate
    ```

4. To be able to authenticate in API requests, create a superuser (user that has all permissions):

    ```bash
    python3 manage.py createsuperuser
    ```

    You will be asked for a username, an optional email, and a password.  
    In case you forgot your password, use this syntax to change it:

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

### API Documentation

This API has provided a Swagger documentation for API endpoints. To access it, go to `/swagger-docs/` endpoint.

### Functionality

The API is divided into two groups: every-minute data and every-day data. Each category has two endpoints. One works with all data stored and is called the history endpoint, and the other works with one record that represents the last record inserted and is called the last record endpoint.

### History endpoints

#### GET
All GET behavior is manipulated through query parameters. These are the available parameters:

- `stats`  
This parameter is mandatory and represents which fields to return. Use the word `all` to represent all fields.  
Examples:  
    - `/solax/minute-stats/?stats=all`
    - `/solax/minute-stats/?stats=upload_time&stats=grid_voltage_t`

- `before` (optional)  
This parameter is used to filter data with an `upload_time` less than or equal to the given date. This may be combined with the `since` parameter.

- `since` (optional)  
This parameter is used to filter data with an `upload_time` greater than or equal to the given date. This may be combined with the `before` parameter. To return all data, do not specify the `before` and `since` parameters.  
Examples:  
    - `solax/minute-stats/?stats=all&before=2020-01-01&after=1970-05-29`
    - `solax/minute-stats/?stats=all&after=1970-05-29`
    - `solax/minute-stats/?stats=all&before=2020-01-01`
    - `solax/minute-stats/?stats=all`

#### POST
POST requests have both a request body and an optional query parameter.

The request body is the record to insert. The API will not add the record if any fields are missing or invalid.

The optional query parameter `force`, which can be either `true` or `false`, is used to specify whether the API should stop if a record with an existing upload time exists in the database. If the value is `true`, it overwrites the existing record. If this parameter is not specified, the default is `false`.

#### DELETE

Delete requests have only query parameters to control the functionality. The query parameters are as follows:

- `actopm`  
This parameter controls what action to make. If the value is `truncate`, it will delete all data managed by the endpoint. If the value is `delete_older_than`, it will delete all data older than or equal to a given date.

- `args` (optional)  
The parameters which are given to various delete actions. No parameters are needed for `truncate` action. For action `delete_older_than`, a date must be given to filter and delete the data.  
Examples:
    - `solax/minute-stats/?action=truncate`
    - `solax/minute-stats/?action=delete_older_than&args=1999-11-31`

### Last record endpoints

The last record endpoints support many of the same operations as [history endpoints](#history-endpoints) except for the following:

- `DELETE` operations are not permitted.
- `GET` query parameters `since` and `before` are removed.
- `POST` query parameter `force` is removed; it will always have the value of `true`