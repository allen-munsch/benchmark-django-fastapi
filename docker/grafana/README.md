```
docker-compose --profile local-dev up
docker-compose --env-file ./docker/local/grafana/.env --profile load-test up

docker-compose --env-file ./docker/local/grafana/.env --profile load-test-run run
```
