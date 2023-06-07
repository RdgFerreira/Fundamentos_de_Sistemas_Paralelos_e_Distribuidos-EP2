from __future__ import print_function
import os

import sys
import grpc

# importa os arquivos gerado pelo compilador de gRPCs tanto do servidor de integração 
# quanto do servidor de diretório, para ser usado no comando de registro
import integration_pb2, integration_pb2_grpc, directory_pb2, directory_pb2_grpc


def run():
    # cria o canal e stub para servidor de integração, a partir do nome:porta recebidos via linha de comando
    nameAndPort = sys.argv[1]
    intChannel = grpc.insecure_channel(nameAndPort) # "integration channel"
    intStub = integration_pb2_grpc.IntegrateStub(intChannel) # "integration stub"

    while 1:
        # mesmo processamento da stdin do cliente de diretório
        params = []
        try:
            params = input().split(",")
        except:
            intChannel.close()
            exit(0)

        if len(params) == 0:
            intChannel.close()
            exit(0)

        command = params[0]

        if command == "C" and len(params) == 2: # Comando de consulta do cliente de integração
            # "...consulta o servidor de integração pela chave ch, que deve responder com o identificador de um servidor de diretório independente..."
            # O identificador, na variável response, vem com dois campos, name e port
            response = intStub.read(
                integration_pb2.ReadRequest(dirServerKey=int(params[1]))
            )

            # Recupera o nome e a porta do servidor de diretório que da resposta da consulta ao servidor de integração
            name = response.name
            port = response.port
            if name == "ND": # "...Se a resposta for "ND", esse string deve ser escrito na saída..."
                print(name)
            else: # "...executa uma consulta àquele servidor indentificado na resposta e escreve na saída o valor de retorno..."
                # criação do canal e stub para o servidor de diretório
                dirChannel = grpc.insecure_channel(name + ":" + str(port))
                dirStub = directory_pb2_grpc.DirectoryStub(dirChannel)

                # Procedimento de consulta do servidor de diretório, usando o stub recém criado
                response = dirStub.read(directory_pb2.ReadRequest(key=int(params[1])))
                # fecha o canal do servidor de diretório após receber a resposta
                dirChannel.close()
                if response.val == 0:
                    print("-1")
                else:
                    print(response.desc + ",%7.4f" % response.val)

        elif command == "T": # Comando de término do cliente de integração
            # "...sinaliza a terminação do servidor, escreve o valor de retorno e termina o cliente..."
            response = intStub.terminate(integration_pb2.TerminateRequest())
            print(str(response.retval))
            intChannel.close()
            exit(0)


if __name__ == "__main__":
    run()
