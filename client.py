from __future__ import print_function

import sys
import grpc

import directory_pb2, directory_pb2_grpc


def run():
    # recebe o nomeServidor:porta da stdin e cria o canal e o stub para o servidor de diretório
    nameAndPort = sys.argv[1]
    channel = grpc.insecure_channel(nameAndPort)
    stub = directory_pb2_grpc.DirectoryStub(channel)

    while (1):
        params = []
        try:
            params = input().split(",")
        except:
            # encontra EOF na stdin, cliente deve, então, terminar
            # "...Se o arquivo de entrada terminar sem o comando T apenas o cliente deve terminar, mantendo o servidor ativo..."
            channel.close()
            exit(0)

        if len(params) == 0:
            channel.close()
            exit(0)

        command = params[0]
        if command == "I" and len(params) == 4: # Comando de inserção do cliente de diretório
            # "...insere no servidor a chave ch, associada ao string e ao valor val..."
            response = stub.insert(
                directory_pb2.InsertRequest(
                    key=int(params[1]), desc=params[2], val=float(params[3])
                )
            )
            # "...escreve na saída padrão o valor de retorno do procedimento (0 ou 1)..."
            print(str(response.retval))
        elif command == "C" and len(params) == 2: # Comando de consulta do cliente de diretório
            # "...consulta o servidor pelo conteúdo associado à chave ch..."
            response = stub.read(directory_pb2.ReadRequest(key=int(params[1])))

            if response.val == 0:
                # "...apenas -1, caso a chave não seja encontrada..."
                print("-1")
            else:
                # "...escreve na saída o string e o valor, separados por uma vírgula..."
                print(response.desc + ",%7.4f" % response.val)
        elif command == "R" and len(params) == 3: # Comando de registro do cliente de diretório
            # "...dispara o procedimento de registro no servidor de diretórios independente, identificando o nome e o porto onde o servidor de integração se encontra..."
            response = stub.register(
                directory_pb2.RegisterRequest(
                    intServerName=params[1], intServerPort=int(params[2])
                )
            )
            # "...cliente deve escrever o valor de retorno recebido..."
            print(str(response.retval))
        elif command == "T": # Comando de término do cliente de diretório
            # "...sinaliza a terminação do servidor, escreve o valor de retorno e termina o cliente..."
            response = stub.terminate(directory_pb2.TerminateRequest())
            print(str(response.retval))

            channel.close()
            exit(0)


if __name__ == "__main__":
    run()
