#!/usr/bin/env python
# -*- coding: utf-8 -*-
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import time
import sys

def printVelas(velas, f):
    vela0 = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
    vela1 = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
    vela2 = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
    vela3 = 'g' if velas[3]['open'] < velas[3]['close'] else 'r' if velas[3]['open'] > velas[3]['close'] else 'd'
    f.write(vela0 + "     " + vela1 + "     " + vela2 + "     " + vela3 + "\n")
    var0 = float(velas[0]['close']) - float(velas[0]['open'])
    var1 = float(velas[1]['close']) - float(velas[1]['open'])
    var2 = float(velas[2]['close']) - float(velas[2]['open'])
    var3 = float(velas[3]['close']) - float(velas[3]['open'])
    f.write('{:10.8f}'.format(var0) + " " + '{:10.8f}'.format(var1) + " " + '{:10.8f}'.format(var2) + " " + '{:10.8f}'.format(var3) + "\n")

def Payout(par):
    API.subscribe_strike_list(par, 1)
    while True:
        d = API.get_digital_current_profit(par, 1)
        if d != False:
            d = round(int(d) / 100, 2)
            break
        time.sleep(1)
    API.unsubscribe_strike_list(par, 1)

    return d

API = IQ_Option(email, senha)
API.connect()

# modo = raw_input(' PRACTICE / REAL ?? ')
modo = "PRACTICE"

API.change_balance(modo)  # PRACTICE / REAL

if API.check_connect():
    print(' Conectado com sucesso!')
else:
    print(' Erro ao conectar')
    input('\n\n Aperte enter para sair')
    sys.exit()

operacao = 2

par = raw_input(' Indique uma paridade para operar: ')
valor_entrada = float(input(' Indique um valor para entrar: '))
valor_entrada_b = float(valor_entrada)

martingale = 0

wins = 0
looses = 0
HIT = 0

lucro = 0
payout = Payout(par)

jogada = 0

now = datetime.now()
fileName = now.strftime("%d%m%Y-%H%M%S-") + par + "-" + modo
f = open(fileName, "w")

while True:
    minutos = float(((datetime.now()).strftime('%M')))
    segundos = float(((datetime.now()).strftime('%S')))
    # print(">> " + str(segundos) )
    # f.write(str(segundos)+"\n")
    if(segundos == 26):
        f.write("-------Entrando ------- " + par + " " + modo + "\n")
        f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
        dir = False
        velas = API.get_candles(par, 60, 4, time.time())

        vela = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
        dir = 'put' if vela == 'g' else 'call'
        if dir:
            status, id = API.buy(valor_entrada_b, par, dir, 1)
            f.write(">> dir: " + dir+"\n")
            time.sleep(30)
            result = API.check_win_v3(id)
            f.write("Rodada: " + str(jogada) + "\n")
            f.write("Entrada: " + str(valor_entrada_b) + " martingale: " + str(martingale) + "\n")
            f.write("Resultado: " + result["option-closed"]["msg"]["result"]+"\n")

            if(result["option-closed"]["msg"]["result"] == 'loose'):
                looses = looses + 1
                lucro = lucro - valor_entrada_b
                if martingale < 2:
                    valor_entrada_b = valor_entrada_b * 2
                    martingale = martingale + 1
                else:
                    f.write(" ----------> HIT!!! <---------- "+"\n")
                    valor_entrada_b = float(valor_entrada)
                    martingale = 0
                    HIT = HIT + 1
            elif result["option-closed"]["msg"]["result"] == 'equal':
                f.write("empate"+"\n")
            else:
                wins = wins + 1
                lucro = lucro + result["option-closed"]["msg"]["profit_amount"] - valor_entrada_b
                martingale = 0
                valor_entrada_b = 2 if modo == "REAL" else float(valor_entrada)
                f.write("Lucro: " + str(result["option-closed"]["msg"]["profit_amount"])+"\n")
            f.write("Caixa: " + str(lucro)+"\n")
            f.write("Placar-> wins: " + str(wins) + " , looses: " + str(looses) + " , hits: " + str(HIT)+"\n")
            printVelas(velas, f)
            jogada = jogada + 1
            # f.write(str(velas)+"\n")
        f.write("\n")

    # trocar para REAL caso 10 jogadas, 0 hits, wins > looses
    if(jogada == 10 and wins > 5 and martingale < 2 and HIT == 0):
        f.write("--> TROCANDO PARA REAL \n")
        modo = "REAL"
        wins = 0
        looses = 0
        lucro = 0
        valor_entrada_b = 2
        API.change_balance(modo)

    if(HIT == 1 and modo == "REAL"):
        f.write("--> STOP LOSS \n")
        f.write("--> TROCANDO PARA PRACTICE \n")
        modo = "PRACTICE"
        wins = 0
        looses = 0
        lucro = 0
        valor_entrada_b = float(valor_entrada)
        API.change_balance(modo)
    # HIT , voltar pra PRACTICE

    # Voltar para PRACTICE caso caixa * 5 > valor_entrada
    if(modo == "REAL" and lucro > 6):
        f.write("--> STOP GAIN \n")
        f.write("--> TROCANDO PARA PRACTICE \n")
        modo = "PRACTICE"
        wins = 0
        looses = 0
        lucro = 0
        valor_entrada_b = float(valor_entrada)
        API.change_balance(modo)


    if(segundos == 15 and (minutos == 30 or minutos == 0)):
        modo = "PRACTICE"
        martingale = 0
        wins = 0
        looses = 0
        HIT = 0
        lucro = 0
        jogada = 0
        valor_entrada_b = float(valor_entrada)
        f.write("------>> REINICIANDO PLACAR -- A CADA 30 MIN -- \n")
        API.change_balance(modo)
        time.sleep(0.5)
    f.flush()
    time.sleep(0.5)
f.close()