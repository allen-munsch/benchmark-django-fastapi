// docker pull loadimpact/k6
// update the load-test environment in docker-compose.yml
//
// export test_email=<your_stuff>
// export test_user_password=<your_stuff>
// export test_review_app_url=<your_stuff>
//
// docker-compose run load-test
// full debugging modify compose yaml
//     command: "run --http-debug='full' /app/load_tests/k6_test.js"

import encoding from "k6/encoding";
import http from "k6/http";
import { check, fail } from "k6";

// these can be set in docker/grafana/.env and passed along when the test is run
const email = __ENV.test_email;
const password = __ENV.test_user_password;
const reviewAppUrl = __ENV.test_review_app_url ? __ENV.test_review_app_url.replace(/\/+$/, "") : null;
const isAsyncEndpoint = __ENV.test_try_python_async;
const testScenario = __ENV.test_scenario_option || "easy";

email ||
fail("[__ENV.test_email is not defined, please add it to the 'load-test' environment in the docker-compose file]");
password ||
fail(
    "[__ENV.test_user_password is not defined, please add it to the 'load-test' environment in the docker-compose file]"
);

let stageOptions = {
    "easy": [
        { duration: "1m", target: 400 }, // below normal load
    ],
    "medium": [
        { duration: "1m", target: 50 },
        { duration: "1m", target: 60 },
        { duration: "1m", target: 70 },
        { duration: "1m", target: 80 },
        { duration: "1m", target: 90 },
        { duration: "1m", target: 0 },
    ],
    "medium-large": [
        { duration: "1m", target: 100 },
        { duration: "1m", target: 120 }, // normal peak load
        { duration: "1m", target: 140 },
        { duration: "1m", target: 160 }, // around the breaking point
        { duration: "1m", target: 180 },
        { duration: "1m", target: 0 }, // scale down. Recovery stage.
    ],
    "laptop-heater": [
        { duration: "1m", target: 200 },
        { duration: "1m", target: 500 },
        { duration: "1m", target: 700 },
        { duration: "1m", target: 900 },
        { duration: "1m", target: 1100 },
        { duration: "1m", target: 0 },
    ]
}

export let options = {
    stages: stageOptions[testScenario],
    // thresholds: {
    //   http_req_duration: ['p(99)<1500'], // 99% of requests must complete below 1.5s
    //   'logged in successfully': ['p(99)<1500'], // 99% of requests must complete below 1.5s
    // },
};
console.log(`SERVED_BY: ${__ENV.SERVED_BY}`);
console.log(`PYTHONV_VERSION: ${__ENV.PYTHON_VERSION}`);
console.log(`options: `);
console.log(JSON.stringify(options, null, 2));

export default function () {
    let urlPart = reviewAppUrl || "http://web:8000";
    const loginUrl = `${urlPart}/admin/login/`;
    const collegeApi = `${urlPart}/${isAsyncEndpoint ? "async_" : ""}api/clowncollege/`;
    const troupeApi = `${urlPart}/${isAsyncEndpoint ? "async_" : ""}api/troupe/`;
    let res1 = http.get(loginUrl);
    console.debug(res1);
    let csrf = res1.cookies.csrftoken[0].value;
    csrf || fail("FAILED TO SET CSRF");

    check(res1, {
        "has status 200": (r) => r.status === 200,
        "has cookie 'csrftoken'": (r) => r.cookies.csrftoken !== null,
    });

    let options1 = {
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrf,
        },
        redirects: 3,
    };

    http.post(loginUrl, `email=${email}&password=${password}&csrfmiddlewaretoken=${csrf}`, options1);

    let options = {
        headers: {
            "X-CSRFToken": csrf,
            Referer: loginUrl,
        },
        redirects: 3,
    };

    let res2 = http.get(loginUrl, options);
    check(res2, {
        "status is 200": (r) => r.status === 200,
    });

    const apiChecks = (apiName) => {
        let obj = {};
        obj[`${apiName}: status is 200`] = (r) => r.status === 200;
        obj[`${apiName}: count != null`] = (r) => r.json().count != null;
        obj[`${apiName}: next url exists`] = (r) => !!r.json().next;
        obj[`${apiName}: has results`] = (r) => r.json().results.length > 0;
        return obj;
    };

    let res3 = http.get(collegeApi, options);
    check(res3, apiChecks(collegeApi));

    let res4 = http.get(troupeApi, options);
    check(res4, apiChecks(troupeApi));

}
