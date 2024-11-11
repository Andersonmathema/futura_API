from selenium import webdriver as opcoesSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from dotenv import load_dotenv
import os




def carregar_selenium():
    #navegador = opcoesSelenium.Chrome()
    chrome_options = opcoesSelenium.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Necessário para Windows
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    navegador = opcoesSelenium.Chrome(options=chrome_options)
    return navegador
    
    
#navegador = carregar_selenium()


def login(navegador):    
    # Obter os valores das variáveis de ambiente
    password = os.getenv('PASSWORD')
    documento = os.getenv('DOCUMENTO')
    navegador.get('https://sed.educacao.sp.gov.br/')
    time.sleep(5)
    navegador.find_element(By.ID, 'name').send_keys('rg' + documento + 'sp')
    time.sleep(2)
    navegador.find_element(By.ID, 'senha').send_keys(password)
    time.sleep(2)
    try:
        navegador.find_element(By.ID, 'botaoEntrar').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="sedUiModalWrapper_1body"]/ul/li[1]/a').click()
    except Exception as e:
        print(e)
    

def num_linhas(navegador):
    table = navegador.find_element(By.XPATH, '//*[@id="tabelaDados"]/tbody')
    lines = table.find_elements(By.TAG_NAME, 'tr')
    num_lines = len(lines) 
    return num_lines 


def acesso_turma():
    navegador = carregar_selenium()
    time.sleep(2)
    login(navegador)    
    time.sleep(3)
    
    try:
        wait = WebDriverWait(navegador, 10)
        menu_filter = wait.until(EC.presence_of_element_located((By.ID, 'decorMenuFilterTxt')))
        menu_filter.send_keys('Minhas Turmas')
        time.sleep(2)
        menu_filter.send_keys(Keys.ENTER)
        time.sleep(2)
        
        # Turmas
        numero_linhas = num_linhas(navegador)  
        dados = []    
        for serie in range(1, numero_linhas + 1):
            turma = navegador.find_element(By.XPATH, f'//*[@id="tabelaDados"]/tbody/tr[{serie}]/td[3]').text    
            navegador.find_element(By.XPATH, f'//*[@id="tabelaDados"]/tbody/tr[{serie}]/td[6]/a').click()
            time.sleep(2)
            pegaDropDown = navegador.find_element(By.NAME, 'tbAlunos_length')
            itemSelecionado = Select(pegaDropDown)
            itemSelecionado.select_by_visible_text('100')
            time.sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="tbAlunos"]/thead/tr/th[2]').click()
            time.sleep(2)
            navegador.find_element(By.XPATH, '//*[@id="tbAlunos"]/thead/tr/th[8]').click()
            time.sleep(2)
            tabela = navegador.find_element(By.ID, 'tbAlunos')
            time.sleep(2)
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')          
            time.sleep(2)
            
            for linha_atual in linhas:
                colunas = linha_atual.find_elements(By.TAG_NAME, 'td')
                linha_dados = [coluna.text for coluna in colunas]
                linha_dados.append(turma)
                dados.append(linha_dados)  
            
            cabecalho_elementos = linhas[0].find_elements(By.TAG_NAME, 'th')
            cabecalho = [coluna.text for coluna in cabecalho_elementos]
            time.sleep(2)
            cabecalho.append('Turma')
            time.sleep(2)
            
            df = pd.DataFrame(dados, columns=cabecalho)
            df = df.drop(columns=['Reiniciar Senha', 'Visualizar', 'Nº de chamada'])    
            df = df.dropna(how='all')
            time.sleep(2)
            # Voltar, mas não está funcionando
            #navegador.find_element(By.XPATH, '//*[@id="Alunos"]/div[1]/input').click()
            menu_filter = wait.until(EC.presence_of_element_located((By.ID, 'decorMenuFilterTxt')))
            menu_filter.send_keys('Minhas Turmas')
            time.sleep(2)
            menu_filter.send_keys(Keys.ENTER)
            
            time.sleep(2)
        df.to_csv('file.csv', index=False)
        # print(df)
        
    
    except Exception as e:
        print(e)

if __name__ == '__main__':
    load_dotenv()
    acesso_turma()
