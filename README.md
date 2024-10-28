# Rest API gateway for Solax Inverter

## Overview
This application implements a Rest API Gateway that manages the data retrieved from a solar inverter.

> This module was tested together with the [solaxx3](https://github.com/mkfam7/solaxx3) module which performed the data retrieval from the solar inverter.

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
- **email** - the email where the admin notifications should be sent

The password can be changed using the following command:
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
Press `Ctrl-C`.

---
### Rest API application  
#### Administration

  For administrative tasks, Django provides a useful web application at `http://host:port/admin.`

#### Documentation
The Swagger documentation can be found at `http://host:port/swagger-docs/`

---
### Rest API
#### Historical data endpoints
#####  `/minute-stats/` : all historical data with minute granularity

Examples:

1. Retrieve all historical data for the `grid_voltage_t`  
    [GET] `/solax/minute-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve all historical data for the `grid_voltage_r` and `grid_voltage_t`  
    [GET] `/solax/minute-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields  
    [GET] `/solax/minute-stats/?fields=all`

4. Query all available fields before 2020-01-03  
    [GET] `/solax/minute-stats/?fields=all&before=2020-01-02`

5. Query all available fields after 2020-01-01  
    [GET] `/solax/minute-stats/?fields=all&since=2020-01-02`

6. Query all available fields between 2019-04-01 and 2020-09-30  
    [GET] `/solax/minute-stats/?fields=all&since=2019-04-01&before=2020-09-30`

7. Insert a record (if no record with the given time exists)  
    [POST] `/solax/minute-stats/`

8. Insert a record with overwrite  
    [POST] `/solax/minute-stats/?overwrite=true`

9. Delete all data managed by `minute-stats`  
    [DELETE] `/solax/minute-stats/?action=truncate`

10. Delete all data managed by `minute-stats` older than 2020-01-01  
    [DELETE] `/solax/minute-stats/?action=delete_older_than&args=2019-12-31`

---
##### `/daily-stats/`: historical data aggregated by day

Examples:

1. Retrieve all historical data for the `grid_voltage_t`  
    [GET] `/solax/daily-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve all historical data for the `grid_voltage_r` and `grid_voltage_t`  
    [GET] `/solax/daily-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields  
    [GET] `/solax/daily-stats/?fields=all`

4. Query all available fields before 2020-01-03  
    [GET] `/solax/daily-stats/?fields=all&before=2020-01-02`

5. Query all available fields after 2020-01-01  
    [GET] `/solax/daily-stats/?fields=all&since=2020-01-02`

6. Query all available fields between 2019-04-01 and 2020-09-30  
    [GET] `/solax/daily-stats/?fields=all&since=2019-04-01&before=2020-09-30`

7. Insert a record (if no record with the given time exists)  
    [POST] `/solax/daily-stats/`

8. Insert a record with overwrite  
    [POST] `/solax/daily-stats/?overwrite=true`

9. Delete all data managed by `daily-stats`  
    [DELETE] `/solax/daily-stats/?action=truncate`

10. Delete all data managed by `daily-stats` older than 2020-01-01  
    [DELETE] `/solax/daily-stats/?action=delete_older_than&args=2019-12-31`

---
#### Latest data endpoints
##### `/last-minute-stats/`: the most recent retrieved stats  

Examples:
1. Retrieve the last record for the `grid_voltage_t`  
    [GET] `/solax/last-minute-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve the last record for the `grid_voltage_r` and `grid_voltage_t`  
    [GET] `/solax/last-minute-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields  
    [GET] `/solax/last-minute-stats/?fields=all`

4. Insert a record
    [POST] `solax/last-minute-stats/`

---
##### `/last-day-stats/` : the most recent retrieved stats aggregated by day (so far)

Examples:
1. Retrieve the last record for the `grid_voltage_t`  
    [GET] `/solax/last-day-stats/?fields=upload_time&fields=grid_voltage_t`

2. Retrieve the last record for the `grid_voltage_r` and `grid_voltage_t`  
    [GET] `/solax/last-day-stats/?fields=upload_time&fields=grid_voltage_r&fields=grid_voltage_t`

3. Query all available fields  
    [GET] `/solax/last-day-stats/?fields=all`

4. Insert a record
    [POST] `solax/last-day-stats/`

## Django configuration considerations

The application supports multiple users who can operate over the same set of data. The current implementation uses SQLite as a database.
