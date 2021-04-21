from datetime import date
from base64 import b64encode
import json
import unittest

from app import create_app, db
from app.models import Snippet, User
from core.date_utils import this_week


def make_api_headers(username, password=""):
    key = f"{username}:{password}".encode("utf-8")
    return {
        "Authorization": f"Basic {b64encode(key).decode('utf-8')}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


GET_TEST_ROUTES = [
    "/api/user",
    "/api/weeks/",
    "/api/weeks/current",
    "/api/weeks/2021/16",
]
POST_TEST_ROUTES = [
    "/api/weeks/current",
    "/api/weeks/2021/16",
]


class APITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.populate()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate(self):
        self.user = User(
            email="julius.caesar@example.com",
            name="Julius Caesar",
            password="rubicon",
            confirmed=True,
            member_since=date.today(),
        )
        db.session.add(self.user)
        db.session.commit()

    def post(self, route, headers=None, data=None):
        return self.client.post(
            route,
            headers=headers,
            content_type="application/json",
            data=data and json.dumps(data),
        )

    def get(self, route, headers=None):
        return self.client.get(
            route, headers=headers, content_type="application/json"
        )

    def valid_api_headers(self):
        return make_api_headers("julius.caesar@example.com", "rubicon")

    def invalid_api_headers(self):
        return make_api_headers("julius.caesar@example.com", "foobar")

    def test_login_no_credentials(self):
        for route in GET_TEST_ROUTES:
            resp = self.get(route)
            self.assertEqual(401, resp.status_code)
        for route in POST_TEST_ROUTES:
            resp = self.post(route)
            self.assertEqual(401, resp.status_code)

    def test_login_bad_credentials(self):
        for route in GET_TEST_ROUTES:
            resp = self.get(route, self.invalid_api_headers())
            self.assertEqual(401, resp.status_code)
        for route in POST_TEST_ROUTES:
            resp = self.post(route, self.invalid_api_headers())
            self.assertEqual(401, resp.status_code)

    def test_login_with_existing_token(self):
        resp = self.post("/api/login", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        token = resp.json["token"]
        resp = self.post("/api/login", headers=make_api_headers(token, ""))
        self.assertEqual(401, resp.status_code)

    def test_invalid_token(self):
        for route in GET_TEST_ROUTES:
            resp = self.get(route, make_api_headers("123"))
            self.assertEqual(401, resp.status_code)
        for route in POST_TEST_ROUTES:
            resp = self.post(route, make_api_headers("123"))
            self.assertEqual(401, resp.status_code)

    def test_valid_token(self):
        resp = self.post("/api/login", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        token = resp.json["token"]
        for route in GET_TEST_ROUTES:
            resp = self.get(route, make_api_headers(token))
            self.assertEqual(200, resp.status_code)

    def test_get_user(self):
        resp = self.get("/api/user", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.user.name, resp.json["name"])
        self.assertEqual(self.user.email, resp.json["email"])
        self.assertEqual(
            self.user.member_since,
            date.fromisoformat(resp.json["member_since"]),
        )

    def test_get_current_week_existing(self):
        (year, week) = this_week()
        Snippet.update(self.user.id, year, week, "foo", ["blue", "red"])
        resp = self.get("/api/weeks/current", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(year, resp.json["year"])
        self.assertEqual(week, resp.json["week"])
        self.assertEqual("foo", resp.json["text"])
        self.assertSetEqual({"blue", "red"}, set(resp.json["tags"]))

    def test_get_current_week_new(self):
        (year, week) = this_week()
        resp = self.get("/api/weeks/current", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(year, resp.json["year"])
        self.assertEqual(week, resp.json["week"])
        self.assertEqual("", resp.json["text"])
        self.assertListEqual([], resp.json["tags"])

    def test_get_week_invalid(self):
        (year, week) = this_week()
        year += 1
        resp = self.get(f"/api/weeks/{year}/{week}", self.valid_api_headers())
        self.assertEqual(400, resp.status_code)

    def test_get_week_new(self):
        resp = self.get("/api/weeks/2017/9", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(2017, resp.json["year"])
        self.assertEqual(9, resp.json["week"])
        self.assertEqual("", resp.json["text"])
        self.assertListEqual([], resp.json["tags"])

    def test_get_week_existing(self):
        Snippet.update(self.user.id, 2017, 9, "foo", ["blue", "red"])
        resp = self.get("/api/weeks/2017/9", self.valid_api_headers())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(2017, resp.json["year"])
        self.assertEqual(9, resp.json["week"])
        self.assertEqual("foo", resp.json["text"])
        self.assertSetEqual({"blue", "red"}, set(resp.json["tags"]))

    def test_update_current_week_new(self):
        # verify this week hasn't been written yet
        (year, week) = this_week()
        self.assertIsNone(Snippet.get_by_week(self.user.id, year, week))

        # use api to update this week
        json = {"text": "foo", "tags": ["blue", "red"]}
        resp = self.post("/api/weeks/current", self.valid_api_headers(), json)
        self.assertEqual(200, resp.status_code)

        # check that this week was updated properly
        snippet = Snippet.get_by_week(self.user.id, year, week)
        self.assertIsNotNone(snippet)
        self.assertEqual("foo", snippet.text)
        self.assertSetEqual(
            {"blue", "red"}, {tag.text for tag in snippet.tags}
        )
        self.assertEqual(year, snippet.year)
        self.assertEqual(week, snippet.week)

    def test_update_current_week_existing(self):
        # write current week
        (year, week) = this_week()
        Snippet.update(self.user.id, year, week, "foo", ["blue", "red"])
        self.assertIsNotNone(Snippet.get_by_week(self.user.id, year, week))

        # use api to update current week
        json = {"text": "bar", "tags": ["green"]}
        resp = self.post("/api/weeks/current", self.valid_api_headers(), json)
        self.assertEqual(200, resp.status_code)

        # ensure current week is updated properly
        updated = Snippet.get_by_week(self.user.id, year, week)
        self.assertIsNotNone(updated)
        self.assertEqual("bar", updated.text)
        self.assertSetEqual({"green"}, {tag.text for tag in updated.tags})
        self.assertEqual(year, updated.year)
        self.assertEqual(week, updated.week)

    def test_update_week_invalid(self):
        (year, week) = this_week()
        year += 1
        json = {"text": "bar", "tags": ["green"]}
        resp = self.post(
            f"/api/weeks/{year}/{week}", self.valid_api_headers(), json
        )
        self.assertEqual(400, resp.status_code)

    def test_update_week_new(self):
        # verify the week hasn't been written yet
        self.assertIsNone(Snippet.get_by_week(self.user.id, 2017, 9))

        # use api to update the week
        json = {"text": "foo", "tags": ["blue", "red"]}
        resp = self.post("/api/weeks/2017/9", self.valid_api_headers(), json)
        self.assertEqual(200, resp.status_code)

        # check that the week was updated properly
        snippet = Snippet.get_by_week(self.user.id, 2017, 9)
        self.assertIsNotNone(snippet)
        self.assertEqual("foo", snippet.text)
        self.assertSetEqual(
            {"blue", "red"}, {tag.text for tag in snippet.tags}
        )
        self.assertEqual(2017, snippet.year)
        self.assertEqual(9, snippet.week)

    def test_update_week_existing(self):
        # write the week
        Snippet.update(self.user.id, 2017, 9, "foo", ["blue", "red"])
        self.assertIsNotNone(Snippet.get_by_week(self.user.id, 2017, 9))

        # use api to update the week
        json = {"text": "bar", "tags": ["green"]}
        resp = self.post("/api/weeks/2017/9", self.valid_api_headers(), json)
        self.assertEqual(200, resp.status_code)

        # ensure current week is updated properly
        updated = Snippet.get_by_week(self.user.id, 2017, 9)
        self.assertIsNotNone(updated)
        self.assertEqual("bar", updated.text)
        self.assertSetEqual({"green"}, {tag.text for tag in updated.tags})
        self.assertEqual(2017, updated.year)
        self.assertEqual(9, updated.week)

    def test_get_weeks_empty(self):
        self.assertListEqual([], Snippet.get_all(self.user.id).all())
        resp = self.get("/api/weeks/", self.valid_api_headers())
        self.assertListEqual([], resp.json["weeks"])
        self.assertIsNone(resp.json["prev_url"])
        self.assertIsNone(resp.json["next_url"])
        self.assertEqual(0, resp.json["count"])

    def test_get_weeks_all(self):
        id1 = Snippet.update(self.user.id, 2017, 9, "foo", ["blue", "red"])
        id2 = Snippet.update(self.user.id, 2011, 18, "bar", ["green"])
        resp = self.get("/api/weeks/", self.valid_api_headers())
        self.assertEqual(2, resp.json["count"])
        weeks = resp.json["weeks"]
        self.assertSetEqual(
            {(2017, 9), (2011, 18)},
            {(snippet["year"], snippet["week"]) for snippet in weeks},
        )

    def test_get_weeks_tag_filter(self):
        Snippet.update(self.user.id, 2017, 9, "foo", ["blue", "red"])
        Snippet.update(self.user.id, 2011, 18, "bar", ["green"])
        resp = self.get("/api/weeks/?tag=blue", self.valid_api_headers())
        self.assertEqual(1, resp.json["count"])
        weeks = resp.json["weeks"]
        self.assertSetEqual(
            {(2017, 9)},
            {(snippet["year"], snippet["week"]) for snippet in weeks},
        )

    def test_get_weeks_pagination(self):
        self.app.config["LASTWEEK_SNIPPETS_PER_PAGE"] = 2
        Snippet.update(self.user.id, 2017, 9, "foo", ["blue", "red"])
        Snippet.update(self.user.id, 2011, 18, "bar", ["green"])
        Snippet.update(self.user.id, 2007, 29, "baz", [])

        year_week = lambda snippet: (snippet["year"], snippet["week"])
        year_weeks = lambda weeks: {year_week(snippet) for snippet in weeks}

        # first page
        resp = self.get("/api/weeks/", self.valid_api_headers())
        self.assertEqual(3, resp.json["count"])
        self.assertIsNone(resp.json["prev_url"])
        self.assertIsNotNone(resp.json["next_url"])
        self.assertSetEqual(
            {(2017, 9), (2011, 18)}, year_weeks(resp.json["weeks"])
        )

        # use link to go to the second page
        resp = self.get(resp.json["next_url"], self.valid_api_headers())
        self.assertEqual(3, resp.json["count"])
        self.assertIsNotNone(resp.json["prev_url"])
        self.assertIsNone(resp.json["next_url"])
        self.assertSetEqual({(2007, 29)}, year_weeks(resp.json["weeks"]))

        # use link to go back to the first page
        resp = self.get(resp.json["prev_url"], self.valid_api_headers())
        self.assertEqual(3, resp.json["count"])
        self.assertIsNone(resp.json["prev_url"])
        self.assertIsNotNone(resp.json["next_url"])
        self.assertSetEqual(
            {(2017, 9), (2011, 18)}, year_weeks(resp.json["weeks"])
        )
