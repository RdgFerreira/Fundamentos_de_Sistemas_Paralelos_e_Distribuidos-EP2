from concurrent import futures

import sys
import grpc
import socket
import threading

# importa os arquivos gerado pelo compilador de gRPCs tanto do servidor de diretório 
# quanto do servidor de integração, para ser usado no comando de registro
import directory_pb2, directory_pb2_grpc, integration_pb2, integration_pb2_grpc

# classe que implementa o servidor de diretório
class Directory(directory_pb2_grpc.DirectoryServicer):
   
   def __init__(self, stop_event, port):
      self.db = {}                        # dicionário: chave -> {"desc": string de descrição, "val": float de valor}
      self.stop_event = stop_event        # inicialização de evento de parada do servidor
      self.name = str(socket.getfqdn("")) # nome do deste servidor de diretório
      self.port = port                    # porta deste servidor de diretório
   
   def insert(self, request, context): # Procedimento de inserção
        retValue = 0
        # Se a chave já existe, retorna 1 para o cliente
        if request.key in self.db: retValue = 1

        # Insere ou atualiza o campo da chave enviada pelo cliente com os respectivos valores
        self.db[request.key] = {"desc": request.desc, "val":  request.val}

        return directory_pb2.InsertReply(retval=retValue)
   
   def read(self, request, context): # Procedimento de consulta
       # Valores de retorno default, caso não encontre a chave
       desc = ""
       val = 0

       # Se a chave existe, retorna os conteúdos de descrição e valor associados a ela, atualizando os valores padrão acima
       if request.key in self.db:
           db_instance = self.db[request.key]
           desc = db_instance["desc"]
           val = db_instance["val"]

       # envia a resposta para o cliente 
       return directory_pb2.ReadReply(desc=desc, val=val)
   
   def register(self, request, context): # Procedimento de registro
       # Cria o canal e o stub para o servidor de integração, usando o nome e a porta recebidos do cliente
       intChannel = grpc.insecure_channel(request.intServerName + ":" + str(request.intServerPort))
       intStub = integration_pb2_grpc.IntegrateStub(intChannel)

       # Usa este stub criado para chamar o procedimento de registro do servidor de integração
       # Aqui, o servidor de diretório age como um cliente do servidor de integração
       response = intStub.register(integration_pb2.RegisterRequest(
           dirServerName = self.name,
           dirServerPort = int(self.port),
           dirServerKeys = list(self.db.keys())
        ))
       
       # Retorna a resposta do servidor de integração para o cliente
       return directory_pb2.RegisterReply(retval=response.retval)

   def terminate(self, request, context): # Procedimento de terminação
        # Sinaliza o evento de parada do servidor
        self.stop_event.set()
        # "...o servidor deve responder com um inteiro igual ao número de chaves armazenadas até então e terminar sua execução depois da resposta..."
        return directory_pb2.TerminateReply(retval=len(self.db))


def serve():
   # inicializa o evento de parada do servidor
   stop_event = threading.Event()
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
   port = sys.argv[1]
   # adiciona o serviço de diretório ao servidor, inicializando a classe com o evento de parada e a porta passada via linha de comando
   directory_pb2_grpc.add_DirectoryServicer_to_server(Directory(stop_event, port), server)
   # Cria uma porta de escuta para o servidor de diretório, que escuta em todas as interfaces de rede
   server.add_insecure_port('[::]:' + port) # ou 0.0.0.0 (IPv4)
   server.start()
   # Aguarda o evento de parada do servidor, que, caso sinalizado, termina o servidor
   stop_event.wait()
   server.stop(0)

if __name__ == '__main__': serve()
