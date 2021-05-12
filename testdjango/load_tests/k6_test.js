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

const email = __ENV.test_email;
const password = __ENV.test_user_password;
const reviewAppUrl = __ENV.test_review_app_url ? __ENV.test_review_app_url.replace(/\/+$/, "") : null;

email ||
fail("[__ENV.test_email is not defined, please add it to the 'load-test' environment in the docker-compose file]");
password ||
fail(
    "[__ENV.test_user_password is not defined, please add it to the 'load-test' environment in the docker-compose file]"
);

export let options = {
    stages: [
        { duration: "1m", target: 10 }, // below normal load
        // { duration: "1m", target: 100 },
        // { duration: "1m", target: 120 }, // normal load
        // { duration: "1m", target: 140 },
        // { duration: "1m", target: 160 }, // around the breaking point
        // { duration: "1m", target: 180 },
        // { duration: "1m", target: 0 }, // scale down. Recovery stage.
    ],
    // stages: [
    //   { duration: "1m", target: 25 }, // below normal load
    //   { duration: "1m", target: 100 },
    //   { duration: "1m", target: 150 }, // normal load
    //   { duration: "1m", target: 300 },
    //   { duration: "1m", target: 600 }, // around the breaking point
    //   { duration: "1m", target: 900 },
    //   { duration: "1m", target: 1200 },
    //   { duration: "1m", target: 0 }, // scale down. Recovery stage.
    // ],
    // thresholds: {
    //   http_req_duration: ['p(99)<1500'], // 99% of requests must complete below 1.5s
    //   'logged in successfully': ['p(99)<1500'], // 99% of requests must complete below 1.5s
    // },
};

export default function () {
    let urlPart = reviewAppUrl || "http://web:8000";
    const loginUrl = `${urlPart}/admin/login/`;
    const collegeApi = `${urlPart}/api/clowncollege/`;
    const troupeApi = `${urlPart}/api/troupe/`;
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
