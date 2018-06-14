import json
from tornado import gen, httpclient
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.log import app_log
from tornado.options import define, options, parse_command_line
from tornado.web import asynchronous, Application, RequestHandler, URLSpec
from tornado.escape import json_decode

COZINHA = 'http://localhost:3000/pedido'

HEADERS = {
    'Content-Type': 'application/json'
}

# Aqui declaramos que o garçom assincrono deve realizar
# no maximo 1000 pedidos à cozinha por vez.
httpclient.AsyncHTTPClient.configure(None, max_clients=1000)

define('debug', default=True, help='Enable or disable debug', type=bool)
define('port', default=8888, help='Run app on the given port', type=int)


def criar_rotas():
    """Esta função é responsavel por criar as rotas do app do Tornado."""
    routes = [
        URLSpec(r'/garcom-sincrono', GarcomSincrono),
        URLSpec(r'/garcom-assincrono', MainHandlerAsync)
    ]

    return Application(routes, **options.as_dict())


class GarcomSincrono(RequestHandler):
    """Esta classe representa um garçom sincrono.

    Ele é sincrono, pois só consegue fazer um pedido à cozinha por vez.
    E também não atende outros clientes enquanto o pedido não ficar pronto.
    """

    def anotar_pedidos(self):
        """Esta função anota o pedido do cliente."""
        json_cliente = json_decode(self.request.body)
        return json_cliente.get("pedidos", [])

    def post(self):
        """Esta função representa a comunicação do cliente com o garçom sincrono.

        Foi optado por um 'POST', pois a comunicação com o garçom é
        uma solicitação de 'inserção' de dados. Para entender melhor, leia:
        https://pt.wikipedia.org/wiki/POST_(HTTP).

        Para realizar uma solicitação ao garçom, deve ser passado a ele:
        {
            'pedidos': [<uma lista de strings com os pedidos>]
        }
        """
        # Chama a função para anotar os pedidos
        pedidos = self.anotar_pedidos()

        # Lista de pedidos que ficaram prontos
        pedidos_prontos = []

        # Vai em cada um dos pedidos
        for pedido in pedidos:
            # Gera um json para se comunicar com a cozinha
            pedido_json = json.dumps({"pedido": pedido})
            # Escreve o pedido para a cozinha
            pedido_cozinha = httpclient.HTTPRequest(
                COZINHA, headers=HEADERS,
                method='POST', body=pedido_json
            )
            # Cria a conexão com a cozinha
            comunicacao_cozinha = httpclient.HTTPClient()
            # Faz o pedido em si
            pedido_pronto = comunicacao_cozinha.fetch(pedido_cozinha)
            # Adiciona o pedido à lista de pedidos prontos
            pedidos_prontos.append(pedido_pronto)

        self.finish("Aqui esta seus pedidos prontos: \n {}".format(
            ",".join(pedidos_prontos)
        ))


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
    """Função que reune os passos para subir o servidor."""
    # Chama a função que retorna as rotas do servidor.
    rotas = criar_rotas()

    # Cria o servidor passando as rotas.
    servidor = HTTPServer(rotas)

    # Inicia o servidor.
    servidor.listen()

    # Avisa a porta que o servidor esta escutando.
    app_log.info("Service is running at port {0}".format(options['port']))

    # Recupera a instancia do IOLoop
    io_loop = IOLoop.instance()

    # Inicia o IOLoop
    io_loop.start()


if __name__ == '__main__':
    """ Chama a função main somente quando se utiliza o comando:
    python3 <nome do arquivo>
    """
    main()
