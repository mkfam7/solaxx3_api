# Rest API Gateway for Solax Inverter

## Overview
This project implements a Rest API Gateway that manages the data retrieved from a solar inverter.

> This module was tested with the [solaxx3](https://github.com/mkfam7/solaxx3) module which performed the data retrieval from the solar inverter.

## Prerequisites
- django 4.2+
- python 3.10+
- openssl
- bash


Project link: [https://github.com/mkfam7/solaxx3_api][project_link]

[project_link]: https://github.com/mkfam7/solaxx3_api

## Installation

Run the initial setup:

```bash
bash setup.sh
```

During the setup, the user will be prompted for:
- **username** - the admin username
- **password** - the password of the admin user
- **email** - the email where the admin notifications should be sent to

The password can be changed from the CLI using the following command:
```bash
python3 manage.py changepassword [USERNAME]
```

## Usage

### Start the application
    ```bash
    bash start.sh
    ```
    or

    ```bash
    bash start.sh HOSTNAME PORT
    ```

   > **HOSTNAME** - the IP Address or the Hostname of the server where the application is hosted.  
   > **PORT** - the port on which the application is available.

   If the application was started without parameters, it will become available at http://localhost:8000. Otherwise, it will become available at the location specified by the parameters.

---
### Stop the application
Fron the console where the Django application is running:  
Press `Ctrl-C`.

---
### Rest API application
#### Administration

For administrative tasks, Django provides a useful web application at `http://host:port/admin`.

#### Documentation
The API documentation can be found at `http://host:port/swagger-docs/`

---
### Rest API
#### Historical data endpoints
#####  `/minute-stats/` : all historical data with minute granularity

Examples:

1. Retrieve all historical data for the `grid_voltage_t` field:  
    [GET] `/minute-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve all historical data for the `grid_voltage_r` and `grid_voltage_t` fields:  
    [GET] `/minute-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields:  
    [GET] `/minute-stats/?fields=all`

4. Query all available fields recorded before `2020-01-03`:  
    [GET] `/minute-stats/?fields=all&before=2020-01-02`

5. Query all available fields recorded after `2020-01-01`:  
    [GET] `/minute-stats/?fields=all&since=2020-01-02`

6. Query all available fields recorded between `2019-04-01` and `2020-09-30`:  
    [GET] `/minute-stats/?fields=all&since=2019-04-01&before=2020-09-30`
7. Insert a record (if a record with the same timestamp does not exist):  
    [POST] `/minute-stats/`

8. Insert a record with overwrite:  
    [POST] `/minute-stats/?overwrite=true`

9. Delete all data managed by the `minute-stats` endpoint:  
    [DELETE] `/minute-stats/?action=truncate`

10. Delete all data managed by the `minute-stats` endpoint which are older than `2020-01-01`:  
    [DELETE] `/minute-stats/?action=delete_older_than&args=2019-12-31`

---
##### `/daily-stats/`: historical data aggregated by day

Examples:

1. Retrieve all historical data for the `grid_voltage_t` field:  
    [GET] `/daily-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve all historical data for the `grid_voltage_r` and `grid_voltage_t` fields:  
    [GET] `/daily-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields:  
    [GET] `/daily-stats/?fields=all`

4. Query all available fields recorded before `2020-01-03`:  
    [GET] `/daily-stats/?fields=all&before=2020-01-02`

5. Query all available fields recorded after `2020-01-01`:  
    [GET] `/daily-stats/?fields=all&since=2020-01-02`

6. Query all available fields recorded between `2019-04-01` and `2020-09-30`:  
    [GET] `/daily-stats/?fields=all&since=2019-04-01&before=2020-09-30`
7. Insert a record (if a record with the same timestamp does not exist):  
    [POST] `/daily-stats/`

8. Insert a record with overwrite:  
    [POST] `/daily-stats/?overwrite=true`

9. Delete all data managed by the `daily-stats` endpoint:  
    [DELETE] `/daily-stats/?action=truncate`

10. Delete all data managed by the `daily-stats` endpoint which are older than `2020-01-01`:  
    [DELETE] `/daily-stats/?action=delete_older_than&args=2019-12-31`

---
#### Latest data endpoints
##### `/last-minute-stats/`: the most recent retrieved stats  

Examples:
1. Retrieve the last record for the `grid_voltage_t` field:  
    [GET] `/last-minute-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve the last record for the `grid_voltage_r` and `grid_voltage_t` fields:    
    [GET] `/last-minute-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields:  
    [GET] `/last-minute-stats/?fields=all`

4. Insert a record:  
    [POST] `/last-minute-stats/`

---
##### `/last-day-stats/` : the most recent retrieved stats aggregated by day (so far)

Examples:

1. Retrieve the last record for the `grid_voltage_t` field:  
    [GET] `/last-day-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve the last record for the `grid_voltage_r` and `grid_voltage_t` fields:    
    [GET] `/last-day-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields:  
    [GET] `/last-day-stats/?fields=all`

4. Insert a record:  
    [POST] `/last-day-stats/`

## Django configuration considerations

During setup a superuser is created for administrative purposes. Additional users may be created to operate over the same set of data.  
The current implementation uses SQLite as a database.
