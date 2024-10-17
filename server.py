# UFPa_PPGEE - COMPUTAÇÃO EM NUVEM _ Exercicio 04
# Professor: Glauco Estácio Gonçalves -- https://github.com/glaucogoncalves/pta
# Aluno: Abrahão Leite Ferreira.  Matrícula: 20230047003

# Imports  ---------------------------------------------------------------------------
import socket # Responsavel por criar um ponto de conexao com outras maquinas
import os
import signal
import sys

# Instanciando o servidor ------------------------------------------------------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SOCK_STREAM = TCP / SOCK_DGRAM = UDP # AF_INET = IPv4

HOST = '127.0.0.1' # ip de da interface de loopback
PORT = 11550 # Essa porta foi informada no pdf do professor
FILES_PATH = "./pta-server/files" # variavel para o caminho dos arquivos

server.bind((HOST, PORT))
server.listen()
print(f"Server escutando na porta: {PORT} com o IP: {HOST}")

# Lendo a lista de usuarios
with open("./pta-server/users.txt", "r") as file:
    users = file.read().split()
 
# Formato da mensagem de pedido = |SEQ_NUM|COMMAND|ARGS|
# Apenas as mensagens CUMP e PEGA possuem um argumento

# Funcao de tratamento do cliente ----------------------------------------------------
def client_conection(connection, address):
    # Mensagens possı́veis: CUMP, LIST, PEGA e TERM
    print(f"Conexão estabelecida com {address}")
    seq_num = 0 # Iniciando a variavel SEQ_NUM (número de sequência)
    
    # Recebe a mensagem do cliente
    f_message = connection.recv(1024).decode()
    print(f"Mensagem recebida: {f_message}")
    
    # Parsing da mensagem
    parts = f_message.split(" ")
    seq_num = parts[0]
    f_command = parts[1]
    f_args = parts[2:] if len(parts) > 2 else None

    # Verifica se o comando inicial é o CUMP
    if f_command != "CUMP":
        # Se o primeiro comando não for CUMP, deve encerrar a conexão
        connection.send(f"{seq_num} NOK".encode())
        connection.close()
        print(f"Conexão com {address} encerrada (comando inválido)")
        return
 
    if f_args[0] in users:  # Verifica se o cliente é válido
        connection.send(f"{seq_num} OK".encode())

        while True:
            # Recebe a mensagem do cliente
            message = connection.recv(1024).decode()
            if not message:
                break

            # Parsing da mensagem
            parts = message.split(" ")
            seq_num = parts[0]
            command = parts[1]
            args = parts[2:] if len(parts) > 2 else None

            # Tratar o comando LIST (listar arquivos)
            if command == "LIST":
                files = os.listdir(FILES_PATH)  # Lista arquivos no diretório do servidor
                if files:
                    response = f"{seq_num} ARQS {len(files)} " + ",".join(files)
                    connection.send(response.encode())
                else:
                    connection.send(f"{seq_num} NOK".encode())

            # Tratar o comando PEGA (requisição de arquivo)
            elif command == "PEGA":
                filename = args[0]
                file_path = f"{FILES_PATH}/{filename}"
                if os.path.exists(file_path):
                    filesize = os.path.getsize(file_path)

                    header = f"{seq_num} ARQ {filesize} "
                    connection.send(header.encode())  
                    
                    with open(file_path, "rb") as f:
                        while True:
                            file_data = f.read(1024)  # Enviar o arquivo em blocos de 1024 bytes
                            if not file_data:
                                break
                            connection.send(file_data)  # Envia o bloco de dados

                    print(f"Arquivo {filename} enviado com sucesso.")
                else:
                    connection.send(f"{seq_num} NOK".encode())

            # Tratar o comando TERM (fechamento)
            elif command == "TERM":
                connection.send(f"{seq_num} OK".encode())
                break

            # Tratar comandos inválidos
            else:
                connection.send(f"{seq_num} NOK".encode())

        connection.close()
        print(f"Conexão encerrada com {address}")

    else:
        # Cliente inválido, envia NOK e fecha a conexão
        connection.send(f"{seq_num} NOK".encode())
        connection.close()
        print(f"Conexão com {address} encerrada (cliente inválido)")


# Comando para fechar o servidor -----------------------------------------------------
def signal_handler(sig, frame):
    print("Encerrando o servidor...")
    server.close()  # Fechando o socket do servidor
    sys.exit(0)

# Configurando o handler de sinal
signal.signal(signal.SIGINT, signal_handler)

# Loop do servidor -------------------------------------------------------------------
while True:
    client_conn, client_addr = server.accept()
    client_conection(client_conn, client_addr)


# Materiais usados para fazer esse trabalho
# Tutorial para criar um servidor Pyhton
# https://community.revelo.com.br/como-criar-um-servidor-em-python/
#
# Como enviar e receber arquivos com sockets 
# https://www.youtube.com/watch?v=j4Drn47pc3o