<p align="center">
    <img src="./assets/logo.png" width="128px" height="128px"/>
</p>

Installation
============

```bash
poetry install
```

Portfolio monitoring
====================

A sample compose stack is available in `./docker-compose` directory.
A sample market order investment simulation is provided in `./docker-compose/config/investments_sample.yaml`

If you want the example to suit your need, edit this file with your market orders data.

Then
 - run `cd ./docker-compose && docker compose up -d`
 - navigate to http://localhost:3000/d/pyre-dashboard/pyre?orgId=1&refresh=auto&from=now%2Fd%2B9h&to=now
 - default grafana credentials are `admin` both for username and password

Usage
=====

```bash
poetry run pyre --help
```

Monthly DCA
-----------

```bash
# Simulate DCA investment strategy over 100 simulations
poetry run pyre simulate dca \
    --symbol URTH \ 
    --amount 3000 \
    --seed 50000 \
    --start-date 2024-06-01 \
    --duration 17 \
    -n 100  
```
