import time
from machine import Pin, I2C


# Pinos
pin_btn1 = 23
pin_imu4_i2c_sda = 21
pin_imu4_i2c_scl = 22
address_imu = 0x68

# Limites
time_limit = 5000  # Tempo máx da porta aberta em ms
temp_limit = 3.0  # Variação máxima de temperatura em °C

# Reg I2C imu
reg_pwr_mgmt_1 = 0x6B  # Registrador para gerenciar o modo de energia do IMU
reg_temp_out_h = 0x41  # Registrador para ler os dados de temperatura


def startImu(i2c):
    # Acorda o Imu
    i2c.writeto_mem(address_imu, reg_pwr_mgmt_1, b'\x00')


def readTemperature(i2c):
    # Lê os bytes de temperatura
    temp_data = i2c.readfrom_mem(address_imu, reg_temp_out_h, 2)
    temp_raw = (temp_data[0] << 8) | temp_data[1]

    if temp_raw >= 32768:  # Verifica se o valor é negativo
        temp_raw -= 65536

    # Converte para °C e retorna o valor
    return (temp_raw / 340.0) + 36.53


# Configurações iniciais de pinos
btn1 = Pin(pin_btn1, Pin.IN, Pin.PULL_DOWN)
i2c_bus = I2C(0, scl=Pin(pin_imu4_i2c_scl),
              sda=Pin(pin_imu4_i2c_sda), freq=400000)

startImu(i2c_bus)
print("Sistema de Monitoramento Inicializado")


temp_initial = readTemperature(i2c_bus)  # temperatura inicial para comparação

open_start_time = None  # marca o tempo quando a porta é aberta
alarm_door_active = False  # marca se o alarme da porta está ativo
alarm_temp_active = False  # rever esses comentárioss!!!!

while True:
    # Leituras
    btn1_state = btn1.value()
    temp_current = readTemperature(i2c_bus)

    # Lógica de tempo de porta aberta com limite de tempo
    if btn1_state == 0:  # Porta aberta
        if open_start_time is None:
            open_start_time = time.ticks_ms()  # Marca o tempo de abertura
        else:
            tempo_aberto = time.ticks_diff(time.ticks_ms(), open_start_time)
            if tempo_aberto >= time_limit and not alarm_door_active:
                print("ALERTA: Porta aberta por muito tempo!")
                alarm_door_active = True
    else:  # Porta Fechada
        open_start_time = None

    # Lógica de variação de temperatura com limite de variação
    temp_variation = temp_current - temp_initial
    if temp_variation >= temp_limit and not alarm_temp_active:
        print("ALERTA: Degradacao termica detectada!")
        alarm_temp_active = True

    # Reset dos alarmes quando a porta é fechada e a temperatura volta ao normal
    if btn1_state == 1 and temp_variation < temp_limit:
        if alarm_door_active or alarm_temp_active:
            print("Status: Sistema Normalizado.")
            alarm_door_active = False
            alarm_temp_active = False

            # Atualiza a referência térmica após normalizar o ambiente
            temp_initial = temp_current

    # pausa para evitar leituras excessivas
    time.sleep_ms(50)
