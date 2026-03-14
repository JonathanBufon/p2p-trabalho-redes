# Sistema de Mensageria P2P (UDP)

Este projeto implementa um chat **peer-to-peer** utilizando o protocolo **UDP** em Python. O sistema permite comunicação direta entre múltiplos nós e encaminhamento de mensagens entre instâncias da aplicação.

## Requisitos

* Python 3 instalado
* Nenhuma biblioteca externa é necessária

Bibliotecas utilizadas (padrão do Python):

* `socket`
* `threading`
* `json`

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

### 2. Configurar o nó

Antes de iniciar cada instância, altere no arquivo `main.py` o valor da constante:

```
MINHA_PORTA
```

Configure a porta de acordo com o nó desejado:

| Nó   | Endereço  | Porta |
| ---- | --------- | ----- |
| No_A | 127.0.0.1 | 5000  |
| No_B | 127.0.0.1 | 5001  |
| No_C | 127.0.0.1 | 5002  |

### 3. Executar a aplicação

Em cada terminal, execute:

```bash
python main.py
```

Cada instância iniciada representará um nó independente da rede.

## Funcionamento

* As mensagens são enviadas via **UDP**.
* Cada nó pode enviar mensagens diretamente para outro nó.
* Caso necessário, o sistema pode **encaminhar mensagens entre nós**, simulando roteamento básico em uma rede distribuída.

## Objetivo do Projeto

Este projeto demonstra conceitos fundamentais de:

* Comunicação em rede utilizando **sockets UDP**
* Sistemas **peer-to-peer (P2P)**
* Comunicação entre múltiplas instâncias de um programa
* Uso de **threads** para processamento simultâneo de envio e recebimento de mensagens
