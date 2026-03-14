from enum import Enum
import socket
import threading
import json

MINHA_PORTA = 5000

meuSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
meuSocket.bind(('127.0.0.1', MINHA_PORTA))

mensagemDireta = {
    "remetente": {"nome": "No_A", "porta": 5000},
    "destinatario_final": {"nome": "No_C", "porta": 5002},
    "conteudo": "Olá, No_C!",
    "foi_encaminhada": False,
} # mock de testes

contatos = {
    "No_A": ('127.0.0.1', 5000),
    "No_B": ('127.0.0.1', 5001),
    "No_C": ('127.0.0.1', 5002),
}

def threadLeitura(sock):
    while True:
        dados, endereco = sock.recvfrom(1024)
        mensagemDireta = json.loads(dados.decode())

        destinatario = mensagemDireta['destinatario_final']
        remetenteOriginal = mensagemDireta['remetente']

        if destinatario['porta'] == MINHA_PORTA:
            print(f"\nRecebido de {endereco}: {dados.decode()}")
            pass
        else:
            mensagemDireta['foi_encaminhada'] = True
            print(f"\nRemetente Original: {remetenteOriginal}")
            mensagemDireta['conteudo'] = f"\nEncaminhado por {MINHA_PORTA}: {mensagemDireta['conteudo']}"

            nomeDestino = destinatario['nome']
            enderecoDestino = contatos[nomeDestino]
            dadosParaEnviar = json.dumps(mensagemDireta).encode('utf-8')

            meuSocket.sendto(dadosParaEnviar, enderecoDestino)
            pass

t = threading.Thread(target=threadLeitura, args=(meuSocket,))
t.start()

while True:
    print("\n--- Menu de Envio ---")
    destino_nome = input("Para quem enviar (No_B, No_C): ")
    proximo_salto = input("Enviar direto (d) ou via outro nó (v)? ")
    texto = input("Mensagem: ")

    dados_destino_final = contatos[destino_nome]
    if proximo_salto == 'v':
        nome_intermediario = "No_B"
        endereco_entrega = contatos[nome_intermediario]
    else:
        endereco_entrega = dados_destino_final

    nova_mensagem = {
        "remetente": {"nome": "No_A", "porta": MINHA_PORTA},
        "destinatario_final": {"nome": destino_nome, "porta": dados_destino_final[1]},
        "conteudo": texto,
        "foi_encaminhada": False
    }

    dadosParaEnviar = json.dumps(nova_mensagem).encode('utf-8')
    meuSocket.sendto(dadosParaEnviar, endereco_entrega)
    print(f"--- Mensagem enviada para {destino_nome} via {endereco_entrega} ---")