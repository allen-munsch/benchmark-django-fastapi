# ASGI python benchmarks

Feel free to open a PR if there is something missing.

### what's this about?

The purpose of the repo is to get a grasp on the state of various configuration setups, for **production ASGI python**, specifically migrating from django 2.2+ to django 3.2+, and layering in FastAPI.



From what I can see it is possible to do this in various ways.

However, I haven't been able to find any definitive answers on what might be a suitable configruation for a production environment.

The following knobs that can be configured:

- python version
- gunicorn
- gevent (todo) / eventlet
- uvicorn
- UvicornWorker
- hypecorn (todo)
- daphne (todo)
- uvicorn WSGIMiddleware
- django get_asgi_application
- fast_api (todo)
- SqlAlchemy 1.4 asyncio plugin (todo)
- Tortoise ORM (todo)
- GINO (todo)
- django ORM
- django sync
- django async
- fastapi sync (todo)
- fastapi async (todo)

```bash
docker-compose up

pyenv install 3.8.10
pyenv local 3.8.10
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

export PYTHON_VERSION={3.6.13 | 3.8.10}
export SERVED_BY={gunicorn-eventlet | gunicorn-uvicornworker | uvicorn | asgi-with-static | uvicorn-wsgimiddleware-with-cling}

docker build -t "testdjango/web:$PYTHON_VERSION" -f "./docker/web/$PYTHON_VERSION.Dockerfile" ./
export PYTHON_VERSION=3.8.10 
export SERVED_BY=gunicorn-eventlet
docker-compose up
psql postgres://testdb:password@127.0.0.1:5432/ -c "create database testdb;"
docker-compose exec web python ./manage.py migrate
docker-compose exec web python ./manage.py populate_test_db

docker-compose --env-file ./docker/grafana/.env --profile load-test-run run load-test
# create the db
```


Results:

```
export SERVED_BY=gunicorn-eventlet
export PYTHON_VERSION=3.8.10
docker-compose up

06:54:46 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./docker/grafana/.env --profile load-test-run run load-test
Creating testdjango_load-test_run ... done

          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: /app/load_tests/k6_test.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration (incl. graceful stop):
           * default: Up to 10 looping VUs for 1m0s over 1 stages (gracefulRampDown: 30s, gracefulStop: 30s)


running (1m00.2s), 00/10 VUs, 771 complete and 0 interrupted iterations
default ✓ [======================================] 00/10 VUs  1m0s

     ✓ has status 200
     ✓ has cookie 'csrftoken'
     ✓ status is 200
     ✓ http://web:8000/api/clowncollege/: status is 200
     ✓ http://web:8000/api/clowncollege/: count != null
     ✓ http://web:8000/api/clowncollege/: next url exists
     ✓ http://web:8000/api/clowncollege/: has results
     ✓ http://web:8000/api/troupe/: status is 200
     ✓ http://web:8000/api/troupe/: count != null
     ✓ http://web:8000/api/troupe/: next url exists
     ✓ http://web:8000/api/troupe/: has results

     checks.........................: 100.00% ✓ 8481 ✗ 0   
     data_received..................: 8.5 MB  142 kB/s
     data_sent......................: 1.1 MB  18 kB/s
     http_req_blocked...............: avg=3µs      min=1.13µs  med=2.01µs   max=423.37µs p(90)=2.87µs   p(95)=3.39µs  
     http_req_connecting............: avg=310ns    min=0s      med=0s       max=163.3µs  p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=77.93ms  min=10.34ms med=18.28ms  max=512.33ms p(90)=249.7ms  p(95)=310.36ms
       { expected_response:true }...: avg=77.93ms  min=10.34ms med=18.28ms  max=512.33ms p(90)=249.7ms  p(95)=310.36ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 3855
     http_req_receiving.............: avg=45.13µs  min=22.53µs med=41.21µs  max=204.95µs p(90)=65.39µs  p(95)=74.09µs 
     http_req_sending...............: avg=15.66µs  min=6.54µs  med=13.21µs  max=75.95µs  p(90)=29.06µs  p(95)=32.2µs  
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=77.87ms  min=10.3ms  med=18.22ms  max=512.27ms p(90)=249.64ms p(95)=310.3ms 
     http_reqs......................: 3855    64.077807/s
     iteration_duration.............: avg=390.39ms min=86.28ms med=387.66ms max=802.41ms p(90)=653.93ms p(95)=695.89ms
     iterations.....................: 771     12.815561/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10
```

```
export SERVED_BY=gunicorn-uvicornworker
docker-compose up

06:57:06 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./docker/grafana/.env --profile load-test-run run load-test
Creating testdjango_load-test_run ... done

          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: /app/load_tests/k6_test.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration (incl. graceful stop):
           * default: Up to 10 looping VUs for 1m0s over 1 stages (gracefulRampDown: 30s, gracefulStop: 30s)


running (1m00.5s), 00/10 VUs, 661 complete and 0 interrupted iterations
default ✓ [======================================] 00/10 VUs  1m0s

     ✓ has status 200
     ✓ has cookie 'csrftoken'
     ✓ status is 200
     ✓ http://web:8000/api/clowncollege/: status is 200
     ✓ http://web:8000/api/clowncollege/: count != null
     ✓ http://web:8000/api/clowncollege/: next url exists
     ✓ http://web:8000/api/clowncollege/: has results
     ✓ http://web:8000/api/troupe/: status is 200
     ✓ http://web:8000/api/troupe/: count != null
     ✓ http://web:8000/api/troupe/: next url exists
     ✓ http://web:8000/api/troupe/: has results

     checks.........................: 100.00% ✓ 7271 ✗ 0   
     data_received..................: 7.2 MB  120 kB/s
     data_sent......................: 917 kB  15 kB/s
     http_req_blocked...............: avg=2.73µs   min=1.04µs  med=1.79µs   max=532.54µs p(90)=2.52µs   p(95)=3.01µs  
     http_req_connecting............: avg=382ns    min=0s      med=0s       max=215.78µs p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=91.37ms  min=12.02ms med=89.88ms  max=206.28ms p(90)=163.25ms p(95)=175.74ms
       { expected_response:true }...: avg=91.37ms  min=12.02ms med=89.88ms  max=206.28ms p(90)=163.25ms p(95)=175.74ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 3305
     http_req_receiving.............: avg=43.64µs  min=19.58µs med=40.15µs  max=248.24µs p(90)=66.01µs  p(95)=71.64µs 
     http_req_sending...............: avg=13.21µs  min=6.02µs  med=10.86µs  max=88.62µs  p(90)=26.21µs  p(95)=29.85µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=91.32ms  min=11.96ms med=89.82ms  max=206.25ms p(90)=163.17ms p(95)=175.68ms
     http_reqs......................: 3305    54.648443/s
     iteration_duration.............: avg=457.54ms min=91.32ms med=456.49ms max=805.73ms p(90)=771.12ms p(95)=786.94ms
     iterations.....................: 661     10.929689/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10

```

```
export SERVED_BY=uvicorn-wsgimiddleware-with-cling
docker-compose up

07:02:45 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./docker/grafana/.env --profile load-test-run run load-test
Creating testdjango_load-test_run ... done

          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: /app/load_tests/k6_test.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration (incl. graceful stop):
           * default: Up to 10 looping VUs for 1m0s over 1 stages (gracefulRampDown: 30s, gracefulStop: 30s)


running (1m00.4s), 00/10 VUs, 598 complete and 0 interrupted iterations
default ✓ [======================================] 00/10 VUs  1m0s

     ✓ has status 200
     ✓ has cookie 'csrftoken'
     ✓ status is 200
     ✓ http://web:8000/api/clowncollege/: status is 200
     ✓ http://web:8000/api/clowncollege/: count != null
     ✓ http://web:8000/api/clowncollege/: next url exists
     ✓ http://web:8000/api/clowncollege/: has results
     ✓ http://web:8000/api/troupe/: status is 200
     ✓ http://web:8000/api/troupe/: count != null
     ✓ http://web:8000/api/troupe/: next url exists
     ✓ http://web:8000/api/troupe/: has results

     checks.........................: 100.00% ✓ 6578 ✗ 0   
     data_received..................: 6.6 MB  109 kB/s
     data_sent......................: 829 kB  14 kB/s
     http_req_blocked...............: avg=3.47µs   min=1.04µs  med=2.17µs   max=603.08µs p(90)=3.91µs   p(95)=5.51µs  
     http_req_connecting............: avg=537ns    min=0s      med=0s       max=272.18µs p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=100.91ms min=10.17ms med=71.11ms  max=832.66ms p(90)=234.24ms p(95)=300.93ms
       { expected_response:true }...: avg=100.91ms min=10.17ms med=71.11ms  max=832.66ms p(90)=234.24ms p(95)=300.93ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 2990
     http_req_receiving.............: avg=52.28µs  min=18.16µs med=46.56µs  max=869.57µs p(90)=75.8µs   p(95)=92.83µs 
     http_req_sending...............: avg=15.83µs  min=6.27µs  med=13.4µs   max=433.59µs p(90)=25.65µs  p(95)=32.36µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=100.84ms min=10.12ms med=71.04ms  max=832.55ms p(90)=234.18ms p(95)=300.81ms
     http_reqs......................: 2990    49.522578/s
     iteration_duration.............: avg=505.37ms min=81.94ms med=376.82ms max=1.89s    p(90)=1.01s    p(95)=1.18s   
     iterations.....................: 598     9.904516/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10

```

```

export SERVED_BY=gunicorn-uvicornworker
echo test_try_python_async=true >> docker/grafana/.env


07:51:57 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./docker/grafana/.env --profile load-test-run run load-test
Creating testdjango_load-test_run ... done

          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: /app/load_tests/k6_test.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration (incl. graceful stop):
           * default: Up to 10 looping VUs for 1m0s over 1 stages (gracefulRampDown: 30s, gracefulStop: 30s)


running (1m00.6s), 00/10 VUs, 681 complete and 0 interrupted iterations
default ✓ [======================================] 00/10 VUs  1m0s

     ✓ has status 200
     ✓ has cookie 'csrftoken'
     ✓ status is 200
     ✓ http://web:8000/async_api/clowncollege/: status is 200
     ✓ http://web:8000/async_api/clowncollege/: count != null
     ✓ http://web:8000/async_api/clowncollege/: next url exists
     ✓ http://web:8000/async_api/clowncollege/: has results
     ✓ http://web:8000/async_api/troupe/: status is 200
     ✓ http://web:8000/async_api/troupe/: count != null
     ✓ http://web:8000/async_api/troupe/: next url exists
     ✓ http://web:8000/async_api/troupe/: has results

     checks.........................: 100.00% ✓ 7491 ✗ 0   
     data_received..................: 7.5 MB  123 kB/s
     data_sent......................: 953 kB  16 kB/s
     http_req_blocked...............: avg=2.64µs   min=1.02µs  med=1.79µs   max=597.15µs p(90)=2.51µs   p(95)=2.93µs  
     http_req_connecting............: avg=396ns    min=0s      med=0s       max=229.79µs p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=89.14ms  min=12.14ms med=84.2ms   max=250.6ms  p(90)=155.36ms p(95)=194.25ms
       { expected_response:true }...: avg=89.14ms  min=12.14ms med=84.2ms   max=250.6ms  p(90)=155.36ms p(95)=194.25ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 3405
     http_req_receiving.............: avg=42.75µs  min=18.51µs med=39.51µs  max=309.34µs p(90)=66.05µs  p(95)=70.84µs 
     http_req_sending...............: avg=13.05µs  min=6.01µs  med=11µs     max=78.29µs  p(90)=23.61µs  p(95)=29.31µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=89.08ms  min=12.07ms med=84.15ms  max=250.55ms p(90)=155.31ms p(95)=194.2ms 
     http_reqs......................: 3405    56.229413/s
     iteration_duration.............: avg=446.37ms min=92.25ms med=439.46ms max=792.3ms  p(90)=762.32ms p(95)=774.14ms
     iterations.....................: 681     11.245883/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10


```