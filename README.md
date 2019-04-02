# What it is

A DDNS service for Google Cloud DNS.

# Configuration

* Copy `docker-compose.example.yml` to `docker-compose.yml`. You shouldn't really need to change anything.
* Copy `config/config.example.yml` to `config/config.yml` and set zone and records to update.
* Copy your json auth file for GCP service account to `config/auth.json`.
* `docker-compose up`

# Environment variables

| Name                    | Description                                     | Default value           |
|-------------------------|-------------------------------------------------|-------------------------|
| `CONFIG_PATH`           | Path to config file with zones and records      | `config/config.yml`     |
| `AUTH_PATH`             | Path to json auth file for GCP service account  | `config/auth.json`      |
| `LAST_IP_PATH`          | Path to write a file to with your IP in it      | `config/last_ip.txt`    |
| `MY_IP_URL`             | URL to something that returns your IP address   | `http://ifconfig.co/ip` |

