import time
import json
from tornado import gen, httpclient
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.log import app_log
from tornado.options import define, options, parse_command_line
from tornado.web import asynchronous, Application, RequestHandler, URLSpec


DEBUG = True
PORT = 8888
FACEBOOK_URL = "http://api.facebook.com/restserver.php?format=json&method=links.getStats&urls={0}"
external_api_url = FACEBOOK_URL.format("http://globo.com")
nosso = 'http://localhost:3000/pedido'

HEADERS = {
    'Content-Type': 'application/json'
}


# Options
define("debug", default=DEBUG, help="Enable or disable debug", type=bool)
define("port", default=PORT, help="Run app on the given port", type=int)


def create_app():
    """
    Create instance of tornado.web.Application.
    """
    routes = [
        URLSpec(r'/async', MainHandlerAsync),
        URLSpec(r"/block", MainHandlerBlocking)
    ]
    return Application(routes, **options.as_dict())


class MainHandlerBlocking(RequestHandler):

    def get(self):
        req = httpclient.HTTPRequest(nosso+'5s', method='GET')
        # we could use something like requests or urllib here
        client = httpclient.HTTPClient()
        response = client.fetch(req)

        # do something with the response (response.body)
        self.finish("from block")


class MainHandlerAsync(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):
        # don't let the yield call confuse you, it's just Tornado helpers to make
        # writing async code a bit easier. This is the same as doing
        # client.fetch(req, callback=_some_other_helper_function)

        response = yield self.faz_req(1)
        print('depois 1')
        #response = yield self.faz_req(2)
        #print('depois 2')
        ### do something with the response (response.body)
        self.finish("from asynchronous")


    def faz_req(self, num):
        print('antes {}'.format(num))
        client = httpclient.AsyncHTTPClient()

        pedidos = [
            "Banoffee",
            "cha",
            "sanduiche"
        ]

        tasks = []
        for pedido in pedidos:
            pedido_json = json.dumps({"pedido": pedido})
            req = httpclient.HTTPRequest(nosso, headers=HEADERS, method='POST', body=pedido_json)
            tasks.append(gen.Task(client.fetch, req))
        return gen.Multi(tasks)



def main():
    """
    Run main loop.
    """
    parse_command_line()
    application = create_app()
    server = HTTPServer(application)
    server.listen(options['port'])
    app_log.info("Service is running at port {0}".format(options['port']))
    io_loop = IOLoop.instance()
    io_loop.start()


if __name__ == '__main__':
    main()
else:
    application = create_app()
