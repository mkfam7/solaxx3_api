# Rest API Gateway for Solar Inverter

## Overview
This project implements a Rest API Gateway that manages the data retrieved from a solar inverter.

> This module was tested with the [solaxx3](https://github.com/mkfam7/solaxx3) module which performed the data retrieval from the solar inverter.

## Prerequisites

This API recommends the following dependencies:

| Python | Django |
| ------ | ------ |
| 3.8    | 4.2    |
| 3.9    | 4.2    |
| 3.10   | 5.*    |
| 3.11   | 5.*    |
| 3.12   | 5.*    |
| 3.13   | 5.*    |

In addition, it requires:
- openssl
- bash

Project link: https://github.com/mkfam7/solaxx3_api


## Installation

Run the initial setup. Run `bash setup.sh --help` to view the existing parameters.

```bash
bash setup.sh
```

The password can be changed from the CLI using the following command:

```bash
python3 manage.py changepassword [USERNAME]
```

By default, `USERNAME` is the current username, `$USER`.

## Usage

### Starting the application

```
bash start.sh
```

or

```
bash start.sh HOSTNAME PORT
```

- **HOSTNAME** - the IP address or hostname of the server where the application is hosted.  
- **PORT** - the port on which the application is available.


If the application was started without parameters, it will become available
at http://localhost:8000. Otherwise, it will become available at the location
specified by the parameters.

Run `bash start.sh --help` for additional information.

---
### Stopping the application

To stop the application, press `Ctrl-C` from the console where the Django application is running.

---
### Customizing the columns in the database

Starting with version 1.1.1, the columns in the database can be configured in a JSON file
specified by the `COLUMNS_FILE` environment variable. If no such variable exists, the fallback
value is `columns.json`.

The configuration under the `minute_stats` key defines the columns for `/minute-stats/`,
while the `daily_stats` key defines the columns for `/daily-stats/`.

Each of these keys contains a list of dictionaries, each representing one column.
Each dictionary is structured as follows:

- `column_name`: The name of the column.
- `column_type`: The type of the column. Must be either `positive_small_integer`, `small_integer`, `integer`, or `float`.
- `nullable` (optional): Whether to store empty values as null in the database.
- `default` (optional): Any default value in case the user does not specify any value for a column value.
- `length` (optional): The length of a specified field. Recommended for `float` fields.

For the keys `nullable`, `default`, and `length`, a value of `N/A` could be used to indicate an empty value.

---
### Rest API administration

For administrative tasks, Django provides a useful web application at `http://host:port/admin`.

### Documentation
The API endpoint documentation can be found at `http://host:port/swagger-docs/`.

### Health check
The API provides a health check endpoint at `http://host:port/healthz`.
For now, it simply returns `healthy`.

---
### Endpoint structure

Each API endpoint supports the following three HTTP verbs: `GET`, `POST`, and `DELETE`.

#### GET

Query parameters:
- `before`, `after`: These query parameters provide filtering support based on the timestamp. Accepts ISO formats. If neither of these parameters are specified, the endpoint will act on the last pushed record.
- `fields`: Specifies the fields to return. If omitted, it defaults to all fields. Example on how to specify multiple fields:  
  `?fields=field1&fields=field2`


Other examples:

1. Get all records with all columns:
    `/minute-stats/?since=0001-01-01`

2. Retrieve all records for the `grid_voltage_t` field:  
    `/minute-stats/?fields=grid_voltage_t&since=0001-01-01`

3. Retrieve all records for the `grid_voltage_r` and `grid_voltage_t` fields:  
    `/minute-stats/?fields=grid_voltage_r&fields=grid_voltage_t&since=0001-01-01`

4. Query all available fields recorded before `2020-01-03`:  
    `/minute-stats/?before=2020-01-02`

5. Query all available fields recorded after `2020-01-01`:  
    `/minute-stats/?since=2020-01-02`

6. Query all available fields recorded between `2019-04-01` and `2020-09-30`, inclusive both ends:  
    `/minute-stats/?since=2019-04-01&before=2020-09-30`


#### POST

Query parameters:
- `overwrite`: Either `true` or `false` (defaults to `false` if omitted). Whether to overwrite any existing record with the given timestamp.

#### DELETE

Two actions can be done using a DELETE request: truncating, or deleting all records older than a given date.

The action is specified by the `action` parameter and can be either `truncate` or `delete_older_than`.
For `delete_older_than`, specify the timestamp to the `args` parameter.

Examples:
- `?action=truncate`
- `?action=delete_older_than&args=2022-01-01`


### Rest API endpoints

- `/minute-stats/`: stores data that has minute granularity. The timestamp field is `upload_time`, which is an ISO datetime.
- `/daily-stats/`: stores data that has daily granularity. The timestamp field is `upload_date`, which is an ISO date.

## Django configuration considerations

During setup a superuser is created for administrative purposes. Additional users may be created to operate over the same set of data.

The current implementation uses SQLite as a database.
