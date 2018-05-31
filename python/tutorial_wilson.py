import json
from tornado.ioloop import IOLoop
from tornado.web import (
    Application,
    RequestHandler,
    asynchronous
)
from tornado import gen

from tornado.httpclient import AsyncHTTPClient


async def get_http_result():
    url = 'https://raw.githubusercontent.com/backstage/functions/master/package.json'
    response = await AsyncHTTPClient().fetch(url, validate_cert=False)
    data = json.loads(response.body)
    return {
        'heey': data['name'],
    }


class HelloWorldHandler(RequestHandler):

    @asynchronous
    async def get(self):
        print("entrouuu")
        response = await AsyncHTTPClient().fetch("https://www.google.com.br/")
        print("saiuuu")
        self.write("response.body")


if __name__ == "__main__":
    app = Application([
        (r"/", HelloWorldHandler),
    ], debug=True)
    app.listen(8889)
    IOLoop.current().start()
