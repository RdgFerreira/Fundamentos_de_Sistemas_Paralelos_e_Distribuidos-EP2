from concurrent import futures

import sys
import grpc
import threading

import integration_pb2, integration_pb2_grpc

# classe que implementa o servidor de integração
class Integration(integration_pb2_grpc.IntegrateServicer):
    def __init__(self, stop_event):
        self.db = {}                 # dicionário: chave de servidor de diretório -> nome:porta deste servidor de diretório
        self.stop_event = stop_event # inicialização de evento de parada do servidor

    def read(self, request, context): # Procedimento de consulta
        # caso default: "...retorna o string "ND" e um inteiro qualquer (p.ex., zero)..."
        name = "ND"
        port = 0
        # "...consulta um diretório local para ver se conhece a chave indicada..."
        if request.dirServerKey in self.db:
            nameAndPort = self.db[request.dirServerKey].split(":")
            # recupera o nome e a porta do servidor de diretório
            name = nameAndPort[0]
            port = int(nameAndPort[1])
        # responde com o identificador do servidor de diretório independente
        return integration_pb2.ReadReply(name=name, port=port)

    def register(self, request, context): # Procedimento de registro
        # Percorre as chaves recebidas do servidor de diretório e as insere (ou atualiza) no dicionário
        # do servidor de registro, associando-as ao nome e à porta do servidor de diretório
        for key in request.dirServerKeys:
            self.db[key] = request.dirServerName + ":" + str(request.dirServerPort)
        # "...Deve retornar o número de chaves recebidas ou zero..."
        return integration_pb2.RegisterReply(retval=len(request.dirServerKeys))

    def terminate(self, request, context): # Procedimento de terminação
        # Sinaliza o evento de parada do servidor
        self.stop_event.set()
        # responde com o número de chaves registradas até então
        return integration_pb2.TerminateReply(retval=len(self.db))


def serve():
    # inicializa o evento de parada do servidor
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # adiciona o serviço de integração ao servidor, inicializando a classe com o evento de parada
    integration_pb2_grpc.add_IntegrateServicer_to_server(
        Integration(stop_event), server
    )
    # Cria uma porta de escuta para o servidor de integração, que escuta em todas as interfaces de rede
    port = sys.argv[1]
    server.add_insecure_port("[::]:" + port)  # ou 0.0.0.0 (IPv4)
    server.start()
    # Aguarda o evento de parada do servidor, que, caso sinalizado, termina o servidor
    stop_event.wait()
    server.stop(0)


if __name__ == "__main__":
    serve()
