<img src="/doc/logo.png" alt="drawing" width="200"/>
---

[![Build Status](https://travis-ci.com/canberk/greyd.svg?token=ps61NZDUMGbLxwyRfbF6&branch=master)](https://travis-ci.com/canberk/greyd)

Greyd is a location based android game application. The main goal is to increase the daily exercise of the players. Players try to collect feed within a certain period of time. Most bait-taken player winner the game.

#### Requirements
[Docker](https://www.docker.com/)  
[Docker compose](https://docs.docker.com/compose/)
<a href="https://www.geonames.org/login">GeoNames</a> Account for find city name to location. 

#### Usage

```sh
git clone https://github.com/canberk/greyd.git
cd greyd/
echo GEONAMES_USERNAME=${GEONAMES_USERNAME} > .env
docker-compose up --build
```

If you want to run tests:
```sh
docker-compose -f docker-compose.test.yml -p ci up -d --build
docker logs ci_app_1
docker logs ci_test_1
```