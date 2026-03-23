import socket
import threading
import json
import sys
import os
import time

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

mensagens_recebidas = []
lock_mensagens = threading.Lock()


def obter_porta() -> int:
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    print("Portas disponíveis:")
    for porta_ref, nome in TABELA_NOS.items():
        print(f"  {nome} → {porta_ref}")
    return int(input("\nDigite sua porta: "))


def identificar_no(porta: int) -> str:
    nome = TABELA_NOS.get(porta)
    if nome is None:
        raise ValueError(f"Porta {porta} não encontrada na tabela de nós.")
    return nome


MINHA_PORTA = obter_porta()
MEU_NOME    = identificar_no(MINHA_PORTA)

print(f"\n✓ Iniciando como {MEU_NOME} na porta {MINHA_PORTA}\n")

meuSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
meuSocket.bind(('127.0.0.1', MINHA_PORTA))


def threadLeitura(sock):
    while True:
        try:
            dados, endereco = sock.recvfrom(4096)
            mensagem = json.loads(dados.decode())

            destinatario      = mensagem.get('destinatario_final', {})
            remetenteOriginal = mensagem.get('remetente', {})

            if not destinatario:
                continue

            if destinatario.get('porta') == MINHA_PORTA:
                with lock_mensagens:
                    mensagens_recebidas.append({
                        "de":        remetenteOriginal.get('nome', '?'),
                        "endereco":  str(endereco),
                        "conteudo":  mensagem.get('conteudo', ''),
                        "timestamp": mensagem.get('timestamp', ''),
                        "lida":      False,
                    })
            else:
                nome_destino = destinatario.get('nome')
                if nome_destino not in contatos:
                    continue

                mensagem['foi_encaminhada'] = True
                mensagem['conteudo'] = (
                    f"Encaminhado por {MEU_NOME} ({MINHA_PORTA}): {mensagem['conteudo']}"
                )

                sock.sendto(json.dumps(mensagem).encode('utf-8'), contatos[nome_destino])

        except json.JSONDecodeError:
            pass
        except Exception:
            pass


def tela_enviar_mensagem():
    destinos_disponiveis = [n for n in contatos if n != MEU_NOME]

    print("\n─── Enviar Mensagem ───────────────────────────────")
    destino_nome = input(f"Para quem enviar ({', '.join(destinos_disponiveis)}): ").strip()

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
        "timestamp":          time.strftime("%d/%m/%Y %H:%M:%S"),
        "remetente":          {"nome": MEU_NOME,     "porta": MINHA_PORTA},
        "destinatario_final": {"nome": destino_nome, "porta": dados_destino_final[1]},
        "conteudo":           texto,
        "foi_encaminhada":    False,
    }

    meuSocket.sendto(json.dumps(nova_mensagem).encode('utf-8'), endereco_entrega)
    print(f"✓ Mensagem enviada para {destino_nome} ({via_info}).")


def tela_encaminhar_mensagem():
    with lock_mensagens:
        if not mensagens_recebidas:
            print("\n  Nenhuma mensagem para encaminhar.")
            input("  Pressione Enter para voltar...")
            return

        print("\n─── Encaminhar Mensagem ───────────────────────────")
        for i, msg in enumerate(mensagens_recebidas, start=1):
            print(f"  [{i}] De: {msg['de']} ({msg['timestamp']})")
            print(f"       {msg['conteudo']}")
            print()

    escolha = input("  Número da mensagem para encaminhar (0 para cancelar): ").strip()
    if not escolha.isdigit() or escolha == '0':
        return

    idx = int(escolha) - 1
    with lock_mensagens:
        if idx < 0 or idx >= len(mensagens_recebidas):
            print("✗ Índice inválido.")
            return
        msg_original = mensagens_recebidas[idx]

    destinos_disponiveis = [n for n in contatos if n != MEU_NOME and n != msg_original['de']]
    if not destinos_disponiveis:
        print("✗ Nenhum destinatário disponível.")
        return

    print(f"\n  Encaminhar para ({', '.join(destinos_disponiveis)}): ", end='')
    destino_nome = input().strip()

    if destino_nome not in destinos_disponiveis:
        print("✗ Destinatário inválido.")
        return

    dados_destino_final = contatos[destino_nome]

    nova_mensagem = {
        "timestamp":          time.strftime("%d/%m/%Y %H:%M:%S"),
        "remetente":          {"nome": MEU_NOME,     "porta": MINHA_PORTA},
        "destinatario_final": {"nome": destino_nome, "porta": dados_destino_final[1]},
        "conteudo":           f"Encaminhado por {MEU_NOME}: {msg_original['conteudo']}",
        "foi_encaminhada":    True,
    }

    meuSocket.sendto(json.dumps(nova_mensagem).encode('utf-8'), dados_destino_final)
    print(f"✓ Mensagem encaminhada para {destino_nome}.")


def tela_ver_mensagens():
    print("\n─── Conversas ─────────────────────────────────────")

    contatos_disponiveis = [n for n in contatos if n != MEU_NOME]

    print("  0. Todas as mensagens")
    for i, nome in enumerate(contatos_disponiveis, start=1):
        with lock_mensagens:
            novas = sum(1 for m in mensagens_recebidas if m['de'] == nome and not m['lida'])
        notif = f" ({novas} nova(s))" if novas > 0 else ""
        print(f"  {i}. Conversa com {nome}{notif}")

    escolha = input("\n  Selecione: ").strip()

    if escolha == '0':
        filtro = None
    elif escolha.isdigit() and 1 <= int(escolha) <= len(contatos_disponiveis):
        filtro = contatos_disponiveis[int(escolha) - 1]
    else:
        print("✗ Opção inválida.")
        return

    print()
    with lock_mensagens:
        msgs_filtradas = [
            m for m in mensagens_recebidas
            if filtro is None or m['de'] == filtro
        ]

        if not msgs_filtradas:
            print("  Nenhuma mensagem.")
        else:
            for i, msg in enumerate(msgs_filtradas, start=1):
                status = "NOVA" if not msg['lida'] else "   "
                print(f"  [{i}] {status}  De: {msg['de']}  às {msg['timestamp']}")
                print(f"       {msg['conteudo']}")
                print()
            for msg in msgs_filtradas:
                msg['lida'] = True

    input("  Pressione Enter para voltar ao menu...")


def menu_principal():
    while True:
        with lock_mensagens:
            novas = sum(1 for m in mensagens_recebidas if not m['lida'])

        notif = f" ({novas} nova(s))" if novas > 0 else ""

        print(f"\n╔══════════════════════════════════════╗")
        print(f"║  {MEU_NOME} — porta {MINHA_PORTA}                  ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  1. Enviar mensagem                  ║")
        print(f"║  2. Ver mensagens{notif:<20}║")
        print(f"║  3. Encaminhar mensagem              ║")
        print(f"║  0. Sair                             ║")
        print(f"╚══════════════════════════════════════╝")
        opcao = input("  Escolha: ").strip()

        if opcao == '1':
            tela_enviar_mensagem()
        elif opcao == '2':
            tela_ver_mensagens()
        elif opcao == '3':
            tela_encaminhar_mensagem()
        elif opcao == '0':
            print("Encerrando...")
            os._exit(0)
        else:
            print("✗ Opção inválida.")


t = threading.Thread(target=threadLeitura, args=(meuSocket,), daemon=True)
t.start()

menu_principal()
