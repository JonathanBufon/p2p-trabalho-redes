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
python main.py 5000   # Terminal 1 → No_A
python main.py 5001   # Terminal 2 → No_B
python main.py 5002   # Terminal 3 → No_C
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

Exibe todas as mensagens recebidas, indicando quais são novas com o marcador `NOVA`. Após a visualização, todas as mensagens exibidas são marcadas como lidas.

> **Atenção:** mensagens recebidas **não são exibidas automaticamente** na tela. Elas ficam armazenadas em fila e só aparecem ao selecionar esta opção.

## Funcionamento

* As mensagens são enviadas via **UDP**.
* Cada nó pode enviar mensagens **diretamente** para outro nó ou **via nó intermediário**, simulando roteamento básico.
* O recebimento de mensagens ocorre em uma **thread separada**, sem interromper o menu ou a digitação do usuário.
* A fila de mensagens recebidas é protegida por **lock** para garantir segurança no acesso concorrente entre threads.

## Objetivo do Projeto

Este projeto demonstra conceitos fundamentais de:

* Comunicação em rede utilizando **sockets UDP**
* Sistemas **peer-to-peer (P2P)**
* Comunicação entre múltiplas instâncias de um programa
* Uso de **threads** para processamento simultâneo de envio e recebimento de mensagens
* Gerenciamento de **estado compartilhado** entre threads com uso de locks