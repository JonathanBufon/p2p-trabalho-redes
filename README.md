# Sistema de Mensageria P2P (UDP)
Este projeto implementa um chat **peer-to-peer** utilizando o protocolo **UDP** em Python. O sistema permite comunicação direta entre múltiplos nós e encaminhamento de mensagens entre instâncias da aplicação.
## Requisitos
* Python 3 instalado
* Nenhuma biblioteca externa é necessária

Bibliotecas utilizadas (padrão do Python):
* `socket`
* `threading`
* `json`
* `sys`
* `os`
* `time`

## Estrutura do Sistema
Cada instância do programa representa um **nó da rede P2P**. Os nós se comunicam diretamente utilizando sockets UDP.
Exemplo de definição de nós no código:
```
"No_A": ('127.0.0.1', 5000)
"No_B": ('127.0.0.1', 5001)
"No_C": ('127.0.0.1', 5002)
```
Cada nó executa em uma porta diferente, permitindo que várias instâncias sejam executadas simultaneamente na mesma máquina.
## Execução
Para testar o funcionamento do sistema, execute **três instâncias** do programa em terminais separados.
### 1. Abrir os terminais
Abra **3 terminais** na pasta do projeto.
### 2. Executar a aplicação
Em cada terminal, execute o programa passando a porta desejada como argumento:
```bash
python chat_udp.py 5000   # Terminal 1 → No_A
python chat_udp.py 5001   # Terminal 2 → No_B
python chat_udp.py 5002   # Terminal 3 → No_C
```
Caso nenhum argumento seja informado, o programa exibirá a tabela de nós disponíveis e solicitará que o usuário digite a porta manualmente:
```
Portas disponíveis:
  No_A → 5000
  No_B → 5001
  No_C → 5002
Digite sua porta:
```
A porta informada determina automaticamente o nome do nó, conforme a tabela abaixo:
| Nó   | Endereço  | Porta |
| ---- | --------- | ----- |
| No_A | 127.0.0.1 | 5000  |
| No_B | 127.0.0.1 | 5001  |
| No_C | 127.0.0.1 | 5002  |

## Menu Principal
Após a inicialização, cada instância apresenta um menu interativo:
```
╔══════════════════════════════════════╗
║  No_A — porta 5000                   ║
╠══════════════════════════════════════╣
║  1. Enviar mensagem                  ║
║  2. Ver mensagens                    ║
║  3. Encaminhar mensagem              ║
║  0. Sair                             ║
╚══════════════════════════════════════╝
```
Quando houver mensagens não lidas, o contador é exibido ao lado da opção correspondente:
```
║  2. Ver mensagens (2 nova(s))        ║
```

### Opção 1 — Enviar mensagem
Solicita ao usuário:
* **Destinatário** — nome do nó de destino (ex: `No_B`, `No_C`)
* **Rota** — envio direto (`d`) ou via nó intermediário (`v`)
* **Texto** — conteúdo da mensagem

### Opção 2 — Ver mensagens
Exibe um submenu com as conversas separadas por remetente:
```
─── Conversas ─────────────────────────────────────
  0. Todas as mensagens
  1. Conversa com No_B (1 nova(s))
  2. Conversa com No_C
```
Ao selecionar um contato, apenas as mensagens daquele remetente são exibidas, com indicação de data/hora e o marcador `NOVA` para mensagens não lidas. Após a visualização, todas as mensagens exibidas são marcadas como lidas.

> **Atenção:** mensagens recebidas **não são exibidas automaticamente** na tela. Elas ficam armazenadas em fila e só aparecem ao selecionar esta opção.

### Opção 3 — Encaminhar mensagem
Exibe a lista de mensagens recebidas e permite ao usuário selecionar uma para encaminhar a outro nó. A mensagem encaminhada é entregue com a nota:
```
Encaminhado por No_B: [conteúdo original]
```
O pacote enviado terá o flag `foi_encaminhada` definido como `true`.

## Estrutura do Pacote
Cada mensagem trafega na rede como um objeto JSON com os seguintes campos:

| Campo               | Descrição                                              |
| ------------------- | ------------------------------------------------------ |
| `timestamp`         | Data e hora do envio (ex: `"23/03/2025 14:32:01"`)    |
| `remetente`         | Nome e porta de quem enviou                            |
| `destinatario_final`| Nome e porta do destinatário final                     |
| `conteudo`          | Texto da mensagem                                      |
| `foi_encaminhada`   | `false` se original, `true` se encaminhada             |

## Funcionamento
* As mensagens são enviadas via **UDP**.
* Cada nó pode enviar mensagens **diretamente** para outro nó ou **via nó intermediário**, simulando roteamento básico.
* O recebimento de mensagens ocorre em uma **thread separada**, sem interromper o menu ou a digitação do usuário.
* A fila de mensagens recebidas é protegida por **lock** para garantir segurança no acesso concorrente entre threads.
* Pacotes com JSON inválido ou destinatário desconhecido são descartados silenciosamente, sem derrubar a thread de leitura.

## Objetivo do Projeto
Este projeto demonstra conceitos fundamentais de:
* Comunicação em rede utilizando **sockets UDP**
* Sistemas **peer-to-peer (P2P)**
* Comunicação entre múltiplas instâncias de um programa
* Uso de **threads** para processamento simultâneo de envio e recebimento de mensagens
* Gerenciamento de **estado compartilhado** entre threads com uso de locks
* Serialização e desserialização de estruturas de dados via JSON
