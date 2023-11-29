
from tabulate import tabulate
from os import stat
import requests
import json
from uuid import uuid4

class StockSimulator():
    def __init__(self):
        self.API_URL = 'https://brapi.dev/api/quote/'
        self.API_TOK = '?token=k1PhJxAncipKptdTMwrSUC'
        self.portfl = 0  # dinheiro na carteira
        self.fullym = 0  # dinheiro em ações
        self.dinamc = 0  # lucro dinâmico
        self.file_nm = 'stock.json'
        
        with open(self.file_nm,'r') as stock, open('money.txt','r') as money:
            # verifica os arquivo de "configuração"
            self.json_data = [] if stat(self.file_nm).st_size == 0 else json.load(stock) 
            self.portfl = 0.0 if stat('money.txt').st_size == 0 else float(money.read()) 
            
    def _savmony_(self):
        with open('money.txt','w') as file:
            file.write(f'{self.portfl}')

    def _mkfjson_(self,values):
        return {
            "uid": str(uuid4())[:5],
            "smb": values[0], "nom": values[1],
            "prc": values[2], "cmp": values[3],
            "ved": values[4], "dat": values[5], 
            "per": values[6], "qua": values[7], 
            "inv": values[8], "luc": values[9]
        }

    def _api_get_(self,code):
        with requests.get(f'{self.API_URL}{str(code)}/{self.API_TOK}') as req:
            if req.status_code == 200:
                #tratar erros da api nessa função
                return req.json()['results'][0]
        return False

    
    def buy(self, code, quantity):
        uid,data = self.find(code);
        api_data = self._api_get_(code)

        if api_data == False: return 1 # erro na api
    
        value_iv = float(api_data['regularMarketPrice'])*quantity
            
        if value_iv > self.portfl: return 2 # não tem dinheiro para comprar
        
        if uid == None:
            #não há registros de compra da ação
            self.json_data.append(self._mkfjson_([
                api_data["symbol"],
                api_data["shortName"][:10],
                float(api_data["regularMarketPrice"]),
                float(api_data["regularMarketPrice"]),
                value_iv,
                api_data["regularMarketTime"],
                api_data["regularMarketChangePercent"],
                int(quantity),
                value_iv, 0.0
            ]))
            
            with open(self.file_nm,'w') as file:
                json.dump(self.json_data,file)
            
        else:
            #já existe um registro, então, atualiza, quantidade comprada, preço/ação, e data
            with open(self.file_nm,'w') as file:
                self.json_data[uid]['qua'] = int(self.json_data[uid]['qua'])+int(quantity)
                self.json_data[uid]['inv'] = float(self.json_data[uid]['inv'])+value_iv
                self.json_data[uid]['prc'] = api_data["regularMarketPrice"]
                self.json_data[uid]['cmp'] = api_data["regularMarketPrice"]
                self.json_data[uid]['dat'] = api_data["regularMarketTime"]
                self.json_data[uid]['ved'] = value_iv
                json.dump(self.json_data,file)

        self.portfl -= value_iv
        self._savmony_() 
        self.upd()
        return 0
    
    def upd(self):
        with open(self.file_nm,'w') as file:
            dinamc_tmp = 0 #lucro dinamico temporahrio
            fullym_tmp = 0
            for key,data in enumerate(self.json_data):
                api_data = self._api_get_(data['smb'])
                ac_pric = api_data["regularMarketPrice"]
                ac_data = api_data["regularMarketTime"]
                ac_perc = api_data["regularMarketChangePercent"]

                self.json_data[key]['prc'] = float(ac_pric)
                self.json_data[key]['dat'] = ac_data
                self.json_data[key]['per'] = ac_perc
                self.json_data[key]['ved'] = float(ac_pric)*float(self.json_data[key]['qua'])
                self.json_data[key]['luc'] = (float(ac_pric)*int(self.json_data[key]['qua']))-float(self.json_data[key]['inv'])
                dinamc_tmp += float(self.json_data[key]['luc']) 
                fullym_tmp += float(self.json_data[key]['inv']) 
            
            json.dump(self.json_data,file)
            self.dinamc = float(dinamc_tmp)
            self.fullym = float(fullym_tmp)
        return True
    

    def sell(self,code,quantity=None):
        
        self.upd() #atualiza para não vender com preços desatualizados
        
        with open(self.file_nm,'w') as file:
           
            if code == '-1': #vende todas as ações
                for key,data in enumerate(self.json_data):
                    self.portfl += (float(data['prc']) * float(data['qua']))
                
                self.json_data = []
                self._savmony_()
                json.dump(self.json_data,file)
                return 1
            else:
                #vende apenas 'uma' ação, refatorar para vender individualmente cada pedaço da ação
                key, data = self.find(code)
                if key != None:
                    self.portfl += (float(data['prc']) * float(data['qua']))
                    self._savmony_()
                    del self.json_data[key]
                    json.dump(self.json_data,file)
                    return 2
        return 3

    def find(self, code):
        # função para uso interno
        if len(self.json_data) > 0 :
            for key, data in enumerate(self.json_data):
                if data['uid'].lower() == code.lower() or data['smb'].lower() == code.lower():
                    return key, data
        return None,None

    def lst(self):
        if len(self.json_data) > 0:
            h =  list(self.json_data[0].keys())
            d = []
            
            for idd,data in enumerate(self.json_data):
                tmp = []
                for val in data.values():
                    if isinstance(val,float):
                        tmp.append(f'{val:.2f} R$')
                    else:
                        tmp.append(val)
                d.append(tmp)
           
            print(tabulate(d, headers=[
                    'uuid','SYMB','NOME',
                    'PÇATL R$','PÇCMP R$','PÇVND R$','DTCMP','i%',
                    'QTDAD','RCIN R$','RCLC R$'], tablefmt="pretty"))
        
        else:
            print(10*'-')
    
    def add_money():
        #adcionar receita
        pass