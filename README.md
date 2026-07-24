# Processo Seletivo – Intensivo Maker | IoT

## Etapa Prática – Sistemas Embarcados

### Identificação do Candidato

- **Nome completo:** Henrique Oliveira Rodrigues
- **GitHub:** https://github.com/henrique0rodrigues

---

## Visão Geral da Solução

O objetivo deste projeto é fornecer uma solução de monitoramento embarcado para auditoria e controle de qualidade em ambientes refrigerados, estufas ou painéis elétricos. O sistema foi desenvolvido para identificar falhas de isolamento físico (porta aberta por muito tempo) e anomalias térmicas (sobreaquecimento), disparando alertas via terminal serial (UART) em tempo real.

O usuário interage com o sistema abrindo/fechando a porta através de um botão de fim de curso e alterando a temperatura ambiente simulada. Quando o ambiente retorna às condições seguras de operação, o sistema reporta a normalização e reinicia seu ciclo de vigilância.

---

## Arquitetura do Sistema Embarcado

A arquitetura lógica do firmware foi projetada como uma máquina de estados não-bloqueante, garantindo que o microcontrolador monitore múltiplos sensores em paralelo sem perder sincronicidade.

```text
[ Boot do ESP32 ] 
       │
       ▼
[ Inicialização I2C + UART ] ──► (Emite: "Sistema de Monitoramento Inicializado")
       │
       ▼
[ Coleta de Referência Térmica Inicial ]
       │
       ▼
┌──► [ Loop Principal (Ciclo de 50 ms) ] ────────────────────────┐
│      ├── Leitura Contínua do Sensor de Porta (GPIO 23)         │
│      ├── Leitura Contínua do Sensor MPU6050 (I2C)              │
│      │                                                         │
│      ├── Avaliação de Tempo (ticks_ms):                        │
│      │    └── Porta aberta ≥ 5000ms? ──► [ Alarme de Porta ]   │
│      │                                                         │
│      ├── Avaliação de Gradiente (ΔT):                          │
│      │    └── ΔT ≥ +3.0 °C? ───────────► [ Alarme Térmico ]    │
│      │                                                         │
│      └── Avaliação de Normalização:                            │
│           └── Porta Fechada AND ΔT < +3.0 °C? ──► [ Normaliza ]│
└────────────────────────────────────────────────────────────────┘
```
---

## Componentes Utilizados na Simulação

- ESP32 DevKit C v4: Unidade de processamento central responsável pela lógica de controle, temporização e comunicação serial.

- MPU6050: Utilizado para ler os dados brutos de temperatura do ambiente e converter para graus Celsius, monitorando o gradiente térmico do ambiente.

- Push Button: Configurado com resistor de Pull-down interno, simulando o estado da porta: 1 = Fechado/Pressionado e 0 = Aberto/Solto.

---

## Decisões Técnicas Relevantes

Para garantir um código limpo, estável e alinhado aos requisitos de automação, as seguintes estratégias foram adotadas:

- Clean Code e Constantes: Evitou-se o uso de "números mágicos" no código. Todos os pinos GPIO, limites de tempo/temperatura e endereços de registradores foram definidos em constantes no topo do arquivo, facilitando a legibilidade e manutenção.

- Lógica Não-Bloqueante: O uso de `time.sleep()` longos foi substituído por temporização assíncrona com `time.ticks_ms()` e `time.ticks_diff()`. Isso permite que o sistema continue monitorando a temperatura do sensor em tempo real enquanto cronometra o tempo da porta aberta sem congelar o processador.

- Comunicação I2C Direta: Em vez de importar bibliotecas externas pesadas para o MPU6050, optou-se pela leitura e escrita nativa nos registradores I2C do sensor e conversão matemática via código.

- Controle de Mensagens Seriais: Foram implementadas variáveis booleanas de controle para que os alertas sejam impressos apenas no instante do disparo. Isso evita a inundação do terminal serial com mensagens repetidas a cada loop de 50 ms.

- Atualização Dinâmica da Referência: Ao retornar ao normal, o firmware atualiza a temperatura base de referência para o novo patamar estabilizado do ambiente, prevenindo alarmes falsos após a recuperação de uma falha térmica.

---

## Resultados Obtidos

O sistema embarcado foi validado com sucesso e apresentou o seguinte comportamento final:

- Alinhamento ao Wokwi CI: A saída serial respondeu perfeitamente ao tempo e formatação das mensagens, sendo aprovada sem falhas no pipeline automatizado.

- Disparo Preciso dos Alarmes: O alerta de exposição prolongada é acionado exatamente ao atingir 5000 ms (5 segundos) de porta aberta, e o alarme térmico dispara prontamente perante elevações bruscas de temperatura (variação +3.0°C).

- Restauração e Normalização Segura: O sistema comprovou sua confiabilidade ao retornar ao estado normal apenas quando ambas as condições de risco foram cessadas simultaneamente.

---