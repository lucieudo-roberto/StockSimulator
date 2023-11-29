
from core import StockSimulator
import os

def clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


def main():
    stk_sml = StockSimulator()
    stk_sml.upd()
    cmd_lst = ['buy','sell','find','update','exit','cls']
    msg = ''

    while True:
        clear()
        print('\n')
        print(f'SALDO R$: {stk_sml.portfl:.2f}')
        print(f'IVSTD R$: {stk_sml.fullym:.2f}')
        print(f'COTAS R$: {stk_sml.dinamc:.2f}')
        
        stk_sml.lst()
        cmd = input(f'[ StockSimulator < {msg} >]: ').split(' ')
        
        if cmd[0].lower() in cmd_lst:
            if cmd[0].lower() == 'buy':
                status = stk_sml.buy(cmd[1],int(cmd[2]))
                if status == 1: msg = 'API-ER' # api error 
                if status == 2: msg = 'SME-R$' # sem saldo
                if status == 0: msg = 'TRS-DN' # transação feita
               
            if cmd[0].lower() == 'sell':
                status = stk_sml.sell(cmd[1])
                if status == 1: msg = 'VND-AL' # todas as ações vendidas 
                if status == 2: msg = 'VND-ON' # uma ação vendida
                if status == 3: msg = 'VND-ER' # ação não vendida
               
            if cmd[0] == 'cls': clear()
            if cmd[0] == 'update': stk_sml.upd()
            if cmd[0] == 'exit': return True
main()