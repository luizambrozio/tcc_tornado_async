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

"""Ativa o DEBUG do servidor, isto é, ele irá reiniciar toda hora que
o arquivo é modificado."""
define('debug', default=True, help='Enable or disable debug', type=bool)

"""Define a porta que o servidor irá subir."""
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

    def realiza_pedido_cozinha(self, pedido_json):
        """Esta função se comunica com a cozinha e realiza o pedido.

        Para utiliza-la, deve-se passar um json com o pedido.
        """
        # Escreve o pedido para a cozinha
        pedido_cozinha = httpclient.HTTPRequest(
            COZINHA, headers=HEADERS,
            method='POST', body=pedido_json
        )
        # Cria a conexão com a cozinha
        comunicacao_cozinha = httpclient.HTTPClient()

        return comunicacao_cozinha.fetch(pedido_cozinha)

    def realiza_pedidos_cozinha(self, pedidos):
        pedidos_prontos = []
        # Vai em cada um dos pedidos
        for pedido in pedidos:
            # Gera um json para se comunicar com a cozinha
            pedido_json = json.dumps({"pedido": pedido})
            # Realiza o pedido à cozinha
            pedido_pronto = self.realiza_pedido_cozinha(pedido_json)
            # Adiciona o pedido à lista de pedidos prontos
            pedidos_prontos.append(pedido_pronto)

        return pedidos_prontos


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
        pedidos_prontos = self.realiza_pedidos_cozinha(pedidos)

        self.finish("Aqui esta seus pedidos prontos: \n {}".format(
            ",".join(pedidos_prontos)
        ))


class GarcomAssincrono(RequestHandler):
    """Esta classe representa um garçom assincrono.

    Ele é assincrono, pois só consegue fazer diversos pedidos à cozinha.
    E também atende outros clientes enquanto o pedido não ficar pronto.
    """

    def anotar_pedidos(self):
        """Esta função anota o pedido do cliente."""
        json_cliente = json_decode(self.request.body)
        return json_cliente.get("pedidos", [])

    @asynchronous
    @gen.engine
    def post(self):
        """Esta função representa a comunicação do cliente com o garçom assincrono.

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

        pedidos_prontos = yield self.realiza_pedidos_cozinha(pedidos)

        self.finish("Aqui esta seus pedidos prontos: \n {}".format(
            ",".join(pedidos_prontos)
        ))

    def recuperar_comunicacao_cozinha(self):
        """Esta função recupera o cria a comunicação com a cozinha.

        A comunicação pode ser recuperada pois pode já estar acontecendo.
        Já que o metodo é assincrono, não precisa esperar o pedido terminar
        para fazer outro, pode 'adicionar' o pedido na comunicação ja aberta.
        """
        if not hasattr(self, 'comunicacao_cozinha'):
            self.comunicacao_cozinha = httpclient.AsyncHTTPClient()
        return self.comunicacao_cozinha

    def realiza_pedido_cozinha(self, pedido_json):
        """Esta função se comunica com a cozinha e realiza o pedido.

        Para utiliza-la, deve-se passar um json com o pedido.
        """
        # Escreve o pedido para a cozinha
        pedido_cozinha = httpclient.HTTPRequest(
            COZINHA, headers=HEADERS,
            method='POST', body=pedido_json
        )
        # Cria ou recupera a conexão com a cozinha
        comunicacao_cozinha = self.recuperar_comunicacao_cozinha()

        return gen.Task(comunicacao_cozinha.fetch, pedido_cozinha)

    def realiza_pedidos_cozinha(self, pedidos):
        pedidos_sendo_preparados = []
        for pedido in pedidos:
            pedido_json = json.dumps({"pedido": pedido})
            pedidos_sendo_preparados.append(
                self.realiza_pedido_cozinha(pedido_json)
            )
        return gen.Multi(pedidos_sendo_preparados)


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
