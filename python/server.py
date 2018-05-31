import tornado.ioloop
import tornado.web
from tornado import gen
import time
import math

class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        print('factorial de 150000')
        x = math.factorial(150000)
        print(x)
        self.write('factorial de 150000')

class SecondHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        print('factorial de 300000')
        x = math.factorial(300000)
        print(x)
        self.write('factorial de 300000')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/second", SecondHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()
