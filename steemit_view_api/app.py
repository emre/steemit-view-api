import requests
import re
from urllib.parse import urlparse
from flask import Flask, request, abort, jsonify


WHITELISTED_DOMAINS = ["steemit.com", "busy.org", "utopian.io"]


def get_view_count(post_url):

    parsed_url = urlparse(post_url)
    if parsed_url.netloc not in WHITELISTED_DOMAINS:
        return 0

    session = requests.session()
    session.headers.update({
        'accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'content-type': 'text/plain;charset=UTF-8',
        'Host': 'steemit.com',
        'Origin': 'https://steemit.com'
    })

    r = session.get("https://steemit.com")
    token = re.findall(b'"csrf":"(.*?)",', r.content)[0]

    r = session.post(
        'https://steemit.com/api/v1/page_view',
        json={"page": parsed_url.path, "csrf": token.decode("utf8")}
    )

    return r.json()["views"]

app = Flask(__name__)


@app.route("/")
def index():
    url = request.args.get("url")
    if not url:
        abort(404)

    return jsonify(count=get_view_count(url))