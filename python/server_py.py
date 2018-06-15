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

pedidos = [
    "Banoffee",
    "Brigadeiro",
    "Sanduiche",
    "Sanduiche"
]

pedidosTalita = [
    "Cha",
    "Tradicional",
    "Sanduiche"
]

# Options
define("debug", default=DEBUG, help="Enable or disable debug", type=bool)
define("port", default=PORT, help="Run app on the given port", type=int)


def create_app():

    routes = [
        URLSpec(r'/async', MainHandlerAsync),
        URLSpec(r'/block', MainHandlerBlocking),
        URLSpec(r'/garcom-asincrono', GarcomAsincrono),
        URLSpec(r'/garcom-sincrono', GarcomSincrono)
    ]
    return Application(routes, **options.as_dict())


class MainHandlerBlocking(RequestHandler):

    def get(self):

        for pedido in pedidos:
            pedido_json = json.dumps({"pedido": pedido})
            req = httpclient.HTTPRequest(nosso, headers=HEADERS, method='POST', body=pedido_json)
            client = httpclient.HTTPClient()
            response = client.fetch(req)

        self.finish("from block")

class GarcomSincrono(RequestHandler):

    def get(self):

        for pedido in pedidosTalita:
            pedido_json = json.dumps({"pedido": pedido})
            req = httpclient.HTTPRequest(nosso, headers=HEADERS, method='POST', body=pedido_json)
            client = httpclient.HTTPClient()
            response = client.fetch(req)

        self.finish("from block Talita")

class GarcomAsincrono(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):

        response = yield self.faz_req(1)
        print('depois 1')
        self.finish("from asynchronous")


    def faz_req(self, num):
        print('antes {}'.format(num))
        client = httpclient.AsyncHTTPClient()

        tasks = []
        for pedido in pedidosTalita:
            pedido_json = json.dumps({"pedido": pedido})
            req = httpclient.HTTPRequest(nosso, headers=HEADERS, method='POST', body=pedido_json)
            tasks.append(gen.Task(client.fetch, req))
        return gen.Multi(tasks)

class MainHandlerAsync(RequestHandler):

    @asynchronous
    @gen.engine
    def get(self):

        response = yield self.faz_req(1)
        print('depois 1')
        self.finish("from asynchronous")


    def faz_req(self, num):
        print('antes {}'.format(num))
        client = httpclient.AsyncHTTPClient()

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
