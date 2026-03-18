from enum import Enum
import socket
import threading
import json
import sys
import os

# Tabela de referência porta -> nome do nó
TABELA_NOS = {
    5000: "No_A",
    5001: "No_B",
    5002: "No_C",
}

contatos = {
    "No_A": ('127.0.0.1', 5000),
    "No_B": ('127.0.0.1', 5001),
    "No_C": ('127.0.0.1', 5002),
}

# Fila de mensagens recebidas (thread-safe)
mensagens_recebidas = []
lock_mensagens = threading.Lock()


# Usuário define a porta ao iniciar
def obter_porta() -> int:
    if len(sys.argv) > 1:
        porta = int(sys.argv[1])
    else:
        print("Portas disponíveis:")
        for porta_ref, nome in TABELA_NOS.items():
            print(f"  {nome} → {porta_ref}")
        porta = int(input("\nDigite sua porta: "))
    return porta


# Identifica o nome do nó a partir da porta
def identificar_no(porta: int) -> str:
    nome = TABELA_NOS.get(porta)
    if nome is None:
        raise ValueError(f"Porta {porta} não encontrada na tabela de nós.")
    return nome
# ---

MINHA_PORTA = obter_porta()
MEU_NOME    = identificar_no(MINHA_PORTA)

print(f"\n✓ Iniciando como {MEU_NOME} na porta {MINHA_PORTA}\n")

meuSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
meuSocket.bind(('127.0.0.1', MINHA_PORTA))


def threadLeitura(sock):
    while True:
        dados, endereco = sock.recvfrom(1024)
        mensagem = json.loads(dados.decode())

        destinatario      = mensagem['destinatario_final']
        remetenteOriginal = mensagem['remetente']

        if destinatario['porta'] == MINHA_PORTA:
            # Armazena silenciosamente, sem exibir nada
            with lock_mensagens:
                mensagens_recebidas.append({
                    "de":       remetenteOriginal['nome'],
                    "endereco": str(endereco),
                    "conteudo": mensagem['conteudo'],
                    "lida":     False,
                })
        else:
            # Encaminha para o destino correto
            mensagem['foi_encaminhada'] = True
            mensagem['conteudo'] = (
                f"Encaminhado por {MEU_NOME} ({MINHA_PORTA}): {mensagem['conteudo']}"
            )

            nomeDestino     = destinatario['nome']
            enderecoDestino = contatos[nomeDestino]
            dadosParaEnviar = json.dumps(mensagem).encode('utf-8')
            sock.sendto(dadosParaEnviar, enderecoDestino)


def tela_enviar_mensagem():
    destinos_disponiveis = [n for n in contatos if n != MEU_NOME]

    print("\n─── Enviar Mensagem ───────────────────────────────")
    destino_nome  = input(f"Para quem enviar ({', '.join(destinos_disponiveis)}): ").strip()

    if destino_nome not in contatos or destino_nome == MEU_NOME:
        print("✗ Destinatário inválido.")
        return

    proximo_salto = input("Enviar direto (d) ou via outro nó (v)? ").strip().lower()
    texto         = input("Mensagem: ").strip()

    dados_destino_final = contatos[destino_nome]

    if proximo_salto == 'v':
        intermediarios     = [n for n in contatos if n != MEU_NOME and n != destino_nome]
        nome_intermediario = intermediarios[0]
        endereco_entrega   = contatos[nome_intermediario]
        via_info           = f"via {nome_intermediario}"
    else:
        endereco_entrega = dados_destino_final
        via_info         = "direto"

    nova_mensagem = {
        "remetente":          {"nome": MEU_NOME,      "porta": MINHA_PORTA},
        "destinatario_final": {"nome": destino_nome,  "porta": dados_destino_final[1]},
        "conteudo":           texto,
        "foi_encaminhada":    False,
    }

    dadosParaEnviar = json.dumps(nova_mensagem).encode('utf-8')
    meuSocket.sendto(dadosParaEnviar, endereco_entrega)
    print(f"✓ Mensagem enviada para {destino_nome} ({via_info}).")


def tela_ver_mensagens():
    print("\n─── Caixa de Entrada ──────────────────────────────")

    with lock_mensagens:
        if not mensagens_recebidas:
            print("  Nenhuma mensagem recebida.")
        else:
            novas = sum(1 for m in mensagens_recebidas if not m['lida'])
            print(f"  Total: {len(mensagens_recebidas)} mensagem(ns)  |  Novas: {novas}\n")

            for i, msg in enumerate(mensagens_recebidas, start=1):
                status = "NOVA" if not msg['lida'] else "   "
                print(f"  [{i}] {status}  De: {msg['de']} ({msg['endereco']})")
                print(f"       {msg['conteudo']}")
                print()
                msg['lida'] = True  # Marca como lida ao exibir

    input("  Pressione Enter para voltar ao menu...")


def menu_principal():
    while True:
        print(f"\n╔══════════════════════════════════════╗")
        print(f"║  {MEU_NOME} — porta {MINHA_PORTA}                  ║")
        print(f"╠══════════════════════════════════════╣")

        with lock_mensagens:
            novas = sum(1 for m in mensagens_recebidas if not m['lida'])

        notif = f" ({novas} nova(s))" if novas > 0 else ""
        print(f"║  1. Enviar mensagem                  ║")
        print(f"║  2. Ver mensagens{notif:<20}║")
        print(f"║  0. Sair                             ║")
        print(f"╚══════════════════════════════════════╝")
        opcao = input("  Escolha: ").strip()

        if opcao == '1':
            tela_enviar_mensagem()
        elif opcao == '2':
            tela_ver_mensagens()
        elif opcao == '0':
            print("Encerrando...")
            os._exit(0)
        else:
            print("✗ Opção inválida.")


# Inicialização
t = threading.Thread(target=threadLeitura, args=(meuSocket,), daemon=True)
t.start()

menu_principal()