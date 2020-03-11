
# Jaguar
A chat application

![Jaguar](https://img00.deviantart.net/0a9d/i/2010/343/9/6/jaguar_by_alannahily-d34ju3t.jpg)

## Branches

### master
[![Build Status](https://travis-ci.com/Carrene/jaguar.svg?token=HWnTqWuJD5Ap9uCZHQqx&branch=master)](https://travis-ci.com/Carrene/jaguar)
[![Coverage Status](https://coveralls.io/repos/github/Carrene/jaguar/badge.svg?branch=master&t=JBn3pI)](https://coveralls.io/github/Carrene/jaguar?branch=master)

Setting up development Environment on Linux
----------------------------------

### Install Project (edit mode)

#### Working copy

```bash

cd /path/to/workspace
git clone git@github.com:Carrene/jaguar.git
cd jaguar
pip install -e .

```
 
### Setup Database

#### Configuration

```yaml

db:
  url: postgresql://postgres:postgres@localhost/jaguar_dev
  test_url: postgresql://postgres:postgres@localhost/jaguar_test
  administrative_url: postgresql://postgres:postgres@localhost/postgres

oauth:
  secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=\n
  application_id: 1
  url: http://localhost:8080

storage:
  local_directory: %(root_path)s/data/assets
  base_url: http://localhost:8080/assets
  
```

#### Remove old abd create a new database **TAKE CARE ABOUT USING THAT**

```bash

jaguar db create --drop --mockup

```

And or

```bash

jaguar db create --drop --basedata 

```

#### Drop old database: **TAKE CARE ABOUT USING THAT**

```bash

jaguar [-c path/to/config.yml] db --drop

```

#### Create database

```bash

jaguar [-c path/to/config.yml] db --create

```

Or, you can add `--drop` to drop the previously created database: **TAKE CARE ABOUT USING THAT**

```bash

jaguar [-c path/to/config.yml] db create --drop

```

### Testing the websocket server

To start the websocket server run the following command:

```bash
jaguar websocket start
```

To route the messages from the `worker queue` to right `WebSocket` connection, 
use the following command:

```bash
jaguar router start
```

As a client you can recieve the message enqueued by the `wscat` cli app. Like:

```bash
wscat -c ws://localhost:8085?token=$(jaguar token create 2 `panda access-token create -s email -- 2 1`)
```

when given access token, panda must be running.

```bash
cd path/to/panda
./gunicorn
```

Run jaguar REST API server
```bash
cd path/to/jaguar
./gunicorn
```

To enqueue the message, run the following command:

```bash
curl -XSEND localhost:8084/apiv1/targets/1/messages \
    -H"Authorization: $(jaguar token create 2 `panda access-token create -s email title avatar -- 2 1`)" \
    -F"body=abc" \
    -F"mimetype=text/plain"
```

**NOTE:** If you want to get by another user, notice you enter `sudo -u <username>` before the commands. like:

```bash
jaguar token create 2 `panda access-token create -s email -- 2 1`
```

