import time
import math
from tornado import gen, httpclient
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.log import app_log
from tornado.options import define, options, parse_command_line
from tornado.web import asynchronous, Application, URLSpec
import json

from tornado.web import RequestHandler
from tornado.concurrent import return_future
# from tornado.gen import

DEBUG = True
PORT = 8888

# Options
define("debug", default=DEBUG, help="Enable or disable debug", type=bool)
define("port", default=PORT, help="Run app on the given port", type=int)



def create_app():
    """
    Create instance of tornado.web.Application.
    """
    routes = [
        URLSpec(r'/async15', SuggiroCafeDetail)
    ]
    return Application(routes, **options.as_dict())



class SuggiroCafeDetail(RequestHandler):

  @asynchronous
  @gen.coroutine  # isto marca que esta função utilizará o IOLoop (async) em algum momento
  def get(self):
    stored_data1 = yield self.get_coffee_info2()  # operação de IO "lenta", por isso yield
    stored_data = yield self.get_coffee_info()  # operação de IO "lenta", por isso yield
    self.write(str(stored_data))

  @return_future  # aqui, marcando que esta função será coordenada pelo IOLoop
  def get_coffee_info(self, callback=None):  # aqui, precisa passar a funçao callback=None, o Tornado vai criar uma função de callback
    print("10")
    time.sleep(10)
    result = "math.factorial(90000)"  # operação lenta
    callback(result)  # no final, voce passa a resposta ao callback, e não return

  @return_future  # aqui, marcando que esta função será coordenada pelo IOLoop
  def get_coffee_info2(self, callback=None):  # aqui, precisa passar a funçao callback=None, o Tornado vai criar uma função de callback
    print("15")
    time.sleep(150)
    result = "math.factorial(90000)"  # operação lenta
    callback(result)  # no final, voce passa a resposta ao callback, e não return

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
