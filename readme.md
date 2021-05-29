# Django ASGI python benchmarks ( rough )

[![Test Runs](https://github.com/allen-munsch/benchmark-django-fastapi/actions/workflows/workflow.yml/badge.svg?branch=main)][1]

[1]: https://github.com/allen-munsch/benchmark-django-fastapi/actions/

Feel free to open a PR if there is something missing, or if you'd like to see something tested.

# DJANGO 3.2 ASGI and Uvicorn are not production ready ( with caveats )

- https://forum.djangoproject.com/t/django-3-2-asgi-uvicorn-is-not-production-ready/8003

CAVEAT 1:

- unless the majority of your codebase is async capable, and you're using an async ORM, etc

CAVEAT 2 ( honk honk, I just want to try out fastapi ):

Keep the legacy code the same and run the WSGI app with ASGI mounted, using a werkzeug DispatcherMiddleware. That way all of the monkeypatched gevent/eventlet stuff basically works the same.

- https://github.com/allen-munsch/benchmark-django-fastapi/blob/main/slowasgi/asgi.py
- https://github.com/allen-munsch/benchmark-django-fastapi/blob/main/testdjango/wsgi_with_slow_api_mounted.py

Seems like the least invasive stepwards way to get rolling with ASGI/Fastapi inside of a Django app.

Anyone have any suggestions here? (hmm, looks like all the database stuff, would still be blocking?)

- https://github.com/rednaks/django-async-orm/discussions/9
- https://github.com/rednaks/django-async-orm/discussions/6


```
PYTHON_DEP_VARIATION="_django-async-orm.0.1.8"
SERVED_BY=gunicorn-eventlet-slowapi-wsgi-w2

ab -v all -n 10 -c 10 127.0.0.1:8000/slowapi/slowapi/sleep/ 

04:22:18 jmunsch@pop-os benchmark-django-fastapi ±|main ✗|→ ab -v all -n 10 -c 10 127.0.0.1:8000/slowapi/slowapi/sleep/
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /slowapi/slowapi/sleep/
Document Length:        143 bytes

Concurrency Level:      10
Time taken for tests:   6.064 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      2890 bytes
HTML transferred:       1430 bytes
Requests per second:    1.65 [#/sec] (mean)
Time per request:       6063.948 [ms] (mean)
Time per request:       606.395 [ms] (mean, across all concurrent requests)
Transfer rate:          0.47 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       0
Processing:  1008 4248 1243.8   5056    5056
Waiting:     1007 4247 1243.5   5054    5055
Total:       1008 4248 1243.9   5056    5057

Percentage of the requests served within a certain time (ms)
  50%   5056
  66%   5056
  75%   5056
  80%   5056
  90%   5057
  95%   5057
  98%   5057
  99%   5057
 100%   5057 (longest request)


time seq 1 10 | xargs -n1 -P 10 curl 127.0.0.1:8000/slowapi/slowapi/sleep/
```

### What's this about?

The purpose of the repo is to get a grasp on the state of various configuration setups, for **production ASGI django**, specifically migrating from django 2.2+ to django 3.2+, and layering in FastAPI.

From what I can see it is possible to do this in various ways.

However, I haven't been able to find any definitive answers on what might be a suitable configruation for a production environment.

The following knobs that can be configured:

- python version
- gunicorn
- gevent / eventlet
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


### which version have I tried deploying to production

previous performant production environment:

```
PYTHON_VERSION=3.6.13
SERVED_BY=gunicorn-eventlet-w10
```

FAILED:

```
# other attempt
PYTHON_VERSION=3.8.10
SERVED_BY=uvicorn-wsgimiddleware-with-cling
```

```
PYTHON_VERSION=3.8.10
SERVED_BY=asgi-with-static-gunicorn-w18
```


~~SUCCESS SO FAR~~ FAILED (although this would cost an extra $3,500 per month ):

![Screenshot from 2021-05-20 18-56-03](https://user-images.githubusercontent.com/33908344/119063076-d2a58900-b99d-11eb-97d8-ed662e65737c.png)


```
PYTHON_VERSION=3.8.10
SERVED_BY=asgi-with-static-gunicorn-w18
```

Started at:

- 14 performance L heroku web worker instances 
- 16 gunicorn workers each

Currently:
- scaled down heroku web workers to 10 
- 18 gunicorn workers each

FAILED ON PRODUCTION

![Screenshot from 2021-05-21 15-01-17](https://user-images.githubusercontent.com/33908344/119198834-a0ecfa80-ba4f-11eb-8439-b9558b03b886.png)


### tldr

Look at the artifacts zip of a test run: https://github.com/allen-munsch/benchmark-django-fastapi/actions

According to:
- https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#about-github-hosted-runners

The github runners use `Standard_DS2_v2` azure instances:
- https://docs.microsoft.com/en-us/azure/virtual-machines/dv2-dsv2-series#dsv2-series

Which:

| type | Size  | vCPU  | Memory: GiB | Temp storage (SSD) GiB | Max uncached disk throughput: IOPS/MBps | Expected network bandwidth (Mbps) |
| :------------- | :-: | :-: | :--: | :--: | :----: | :----: |
| Standard_DS2_v2 | 2 | 7 | 14 | 8 | 8000/64 (86) | 1500 |

### setup

```bash
pyenv install 3.8.10
pyenv local 3.8.10
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Then modify the `env.vars` for the test scenario.

```
# PYTHON_VERSION={3.6.13 | 3.8.10}
# SERVED_BY={gunicorn-eventlet | gunicorn-uvicornworker | 
#           uvicorn | asgi-with-static | uvicorn-wsgimiddleware-with-cling |
#           asgi-with-static-gunicorn-w18}
#
#
# default example

PYTHON_VERSION=3.8.10
SERVED_BY=asgi-with-static-gunicorn-w18
```

Build the django container:
```
export $(grep -v '^#' ./env.vars | xargs) && docker build \
-t "testdjango/web:$PYTHON_VERSION" \
--build-arg PYTHON_VERSION=$PYTHON_VERSION \
--build-arg PYTHON_DEP_VARIATION=$PYTHON_DEP_VARIATION 
-f "./docker/web/Dockerfile" ./
```

Start the environment, and migrate the dbs:

```
docker-compose --env-file ./env.vars up
docker-compose exec web bash -c ". /venv/bin/activate && python manage.py migrate"
docker-compose exec web bash -c ". /venv/bin/activate && python manage.py populate_test_db"
```

Run the tests:

```
docker-compose --env-file ./env.vars --profile load-test-run run load-test
```

Where are the knobs at the moment?

- https://github.com/allen-munsch/benchmark-django-fastapi/tree/main/docker/web
- https://github.com/allen-munsch/benchmark-django-fastapi/tree/main/testdjango
- https://github.com/allen-munsch/benchmark-django-fastapi/tree/main/env.vars

### uses k6

See load_tests/

- does a GET request to django admin/login
- sends a POST login request
- sends 2 GET api requests and returns a json responses of serialized data

### Results from running locally:

```
uname -a
Linux pop-os 5.8.0-7630-generic #32~1609193707~20.04~781bb80-Ubuntu SMP Tue Jan 5 21:23:50 UTC 2 x86_64 x86_64 x86_64 GNU/Linux

cat /proc/cpuinfo
model name	: Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz
cores 12

cat /proc/meminfo 
MemTotal:       32732864 kB
MemFree:         2180340 kB
MemAvailable:   20016776 kB

```

```
export SERVED_BY=gunicorn-eventlet
export PYTHON_VERSION=3.8.10
docker-compose --env-file ./env.vars up

06:54:46 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./env.vars --profile load-test-run run load-test
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

06:57:06 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./env.vars --profile load-test-run run load-test
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
docker-compose --env-file ./env.vars up

07:02:45 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file ./env.vars --profile load-test-run run load-test
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


07:51:57 (.venv) jmunsch@pop-os testdjango ±|master ✗|→ docker-compose --env-file --env-file ./env.vars --profile load-test-run run load-test
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

```
SERVED_BY=asgi-with-static

07:51:46 jmunsch@pop-os benchmark-django-fastapi ±|main ✗|→ docker-compose --env-file ./env.vars --profile load-test-run run load-test
WARNING: The PYTHON_VERSION variable is not set. Defaulting to a blank string.
WARNING: The WITH_APP variable is not set. Defaulting to a blank string.
Creating benchmark-django-fastapi_load-test_run ... done

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


running (1m00.6s), 00/10 VUs, 703 complete and 0 interrupted iterations
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

     checks.........................: 100.00% ✓ 7733 ✗ 0   
     data_received..................: 7.5 MB  124 kB/s
     data_sent......................: 975 kB  16 kB/s
     http_req_blocked...............: avg=2.6µs    min=1µs     med=1.84µs   max=393.38µs p(90)=2.73µs   p(95)=3.09µs  
     http_req_connecting............: avg=360ns    min=0s      med=0s       max=201µs    p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=86.17ms  min=12.17ms med=86.53ms  max=192.28ms p(90)=146.47ms p(95)=157.95ms
       { expected_response:true }...: avg=86.17ms  min=12.17ms med=86.53ms  max=192.28ms p(90)=146.47ms p(95)=157.95ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 3515
     http_req_receiving.............: avg=42.54µs  min=19.38µs med=39.78µs  max=364.05µs p(90)=62.46µs  p(95)=69.7µs  
     http_req_sending...............: avg=12.62µs  min=6.14µs  med=11.06µs  max=143.57µs p(90)=17.45µs  p(95)=25.32µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=86.12ms  min=12.11ms med=86.5ms   max=192.2ms  p(90)=146.43ms p(95)=157.89ms
     http_reqs......................: 3515    58.047508/s
     iteration_duration.............: avg=431.52ms min=86.16ms med=434.45ms max=763.54ms p(90)=731.52ms p(95)=747.95ms
     iterations.....................: 703     11.609502/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10

```

```
export SERVED_BY=fastapi-with-django-mounted-asgi

08:01:52 jmunsch@pop-os benchmark-django-fastapi ±|main ✗|→ docker-compose --env-file --env-file ./env.vars --profile load-test-run run load-test
WARNING: The WITH_APP variable is not set. Defaulting to a blank string.
Creating benchmark-django-fastapi_load-test_run ... done

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


running (1m00.4s), 00/10 VUs, 681 complete and 0 interrupted iterations
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

     checks.........................: 100.00% ✓ 7491 ✗ 0   
     data_received..................: 7.3 MB  120 kB/s
     data_sent......................: 944 kB  16 kB/s
     http_req_blocked...............: avg=2.67µs   min=1.08µs  med=1.92µs   max=463.33µs p(90)=2.91µs   p(95)=3.25µs  
     http_req_connecting............: avg=401ns    min=0s      med=0s       max=223.62µs p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=88.66ms  min=12.5ms  med=89.4ms   max=196.68ms p(90)=151.69ms p(95)=161.78ms
       { expected_response:true }...: avg=88.66ms  min=12.5ms  med=89.4ms   max=196.68ms p(90)=151.69ms p(95)=161.78ms
     http_req_failed................: 0.00%   ✓ 0    ✗ 3405
     http_req_receiving.............: avg=42.29µs  min=19.74µs med=40.04µs  max=393.34µs p(90)=61.48µs  p(95)=68.14µs 
     http_req_sending...............: avg=12.82µs  min=6.2µs   med=11.62µs  max=146.93µs p(90)=17.69µs  p(95)=20.35µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=88.6ms   min=12.44ms med=89.35ms  max=196.63ms p(90)=151.61ms p(95)=161.74ms
     http_reqs......................: 3405    56.330272/s
     iteration_duration.............: avg=443.96ms min=86.66ms med=434.47ms max=813.16ms p(90)=740.18ms p(95)=762.91ms
     iterations.....................: 681     11.266054/s
     vus............................: 9       min=1  max=9 
     vus_max........................: 10      min=10 max=10
```

```
export PYTHON_VERSION=3.8.10
export SERVED_BY=asgi-with-static-gunicorn-w18

08:03:12 jmunsch@pop-os benchmark-django-fastapi ±|main ✗|→ docker-compose --env-file ./env.vars --profile load-test-run run load-test
WARNING: The PYTHON_VERSION variable is not set. Defaulting to a blank string.
WARNING: The SERVED_BY variable is not set. Defaulting to a blank string.
Creating benchmark-django-fastapi_load-test_run ... done

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


running (1m00.4s), 00/10 VUs, 1670 complete and 0 interrupted iterations
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

     checks.........................: 100.00% ✓ 18370 ✗ 0   
     data_received..................: 18 MB   295 kB/s
     data_sent......................: 2.3 MB  38 kB/s
     http_req_blocked...............: avg=2.74µs   min=935ns   med=2.2µs    max=1.21ms   p(90)=3.18µs   p(95)=3.44µs  
     http_req_connecting............: avg=195ns    min=0s      med=0s       max=294.44µs p(90)=0s       p(95)=0s      
     http_req_duration..............: avg=35.99ms  min=12.25ms med=19.99ms  max=174.5ms  p(90)=93.95ms  p(95)=116.32ms
       { expected_response:true }...: avg=35.99ms  min=12.25ms med=19.99ms  max=174.5ms  p(90)=93.95ms  p(95)=116.32ms
     http_req_failed................: 0.00%   ✓ 0     ✗ 8350
     http_req_receiving.............: avg=48.18µs  min=20.01µs med=47.17µs  max=317.47µs p(90)=62.38µs  p(95)=66.43µs 
     http_req_sending...............: avg=14.34µs  min=6.29µs  med=14.02µs  max=105.53µs p(90)=18.82µs  p(95)=20.54µs 
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s       max=0s       p(90)=0s       p(95)=0s      
     http_req_waiting...............: avg=35.92ms  min=12.16ms med=19.93ms  max=174.44ms p(90)=93.9ms   p(95)=116.27ms
     http_reqs......................: 8350    138.306779/s
     iteration_duration.............: avg=180.68ms min=85.65ms med=101.01ms max=718.39ms p(90)=467.68ms p(95)=574.48ms
     iterations.....................: 1670    27.661356/s
     vus............................: 9       min=1   max=9 
     vus_max........................: 10      min=10  max=10
```


### optionally

- configure influxdb, grafana, and cronograf
- show grafana dashboards of test runs 
- point the test runner at a `test_review_app_url` and run the test against that app
    - after large enough instances network bandwidth quickly becomes the bottleneck
- can do distributed testing : https://k6.io/blog/running-distributed-tests-on-k8s/
