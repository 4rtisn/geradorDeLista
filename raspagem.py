import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--enable-chrome-browser-cloud-management")
chrome_options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=chrome_options)

def extrair_telefones(driver):
    telefones = []
    try:
        cartao_empresas = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "VkpGBb"))
        )
        for cartao in cartao_empresas:
            texto_cartao = cartao.text.strip()
            padrao_telefone = re.compile(r'\(?\d{2}\)?\s?\d{4,5}-\d{4}')
            telefones_encontrados = padrao_telefone.findall(texto_cartao)

            for telefone in telefones_encontrados:
                if telefone not in telefones_existentes:
                    telefones.append(telefone)
                    telefones_existentes.add(telefone)
                    salvar_telefone(telefone)
                    print(telefone)
    except (NoSuchElementException, TimeoutException) as e:
        print("Nenhum elemento encontrado ou a página demorou muito para carregar.")
    return telefones

def salvar_telefone(telefone):
    with open('numeros.txt', 'a') as f:
        f.write(telefone + '\n')

def clicar_proximo(driver):
    for _ in range(5):  # Try up to 5 times
        try:
            botao_proxima = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "pnnext"))
            )
            botao_proxima.click()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(3)
    return False

def verificar_captcha(driver):
    try:
        captcha_text = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//form[@action='/sorry/index']//div[contains(text(), 'Nossos sistemas detectaram tráfego incomum')]"))
        )
        return True
    except (NoSuchElementException, TimeoutException):
        return False

telefones_existentes = set()
if os.path.exists('numeros.txt'):
    with open('numeros.txt', 'r') as f:
        for linha in f:
            telefones_existentes.add(linha.strip())

with open('alvo.json', 'r', encoding='utf-8') as f:
    locais = json.load(f)

try:
    for estado, cidades in locais.items():
        for cidade, bairros in cidades.items():
            for bairro in bairros:
                tipo_empresa = "Oficina Mecânica"
                local_empresa = f"{bairro}, {cidade}, {estado}"

                url = (f"https://www.google.com/search?sca_esv=9384466e02e87e88&tbs=lf:1,lf_ui:2&tbm=lcl&q={tipo_empresa}+{local_empresa}"
                       "&rflfq=2&num=20&sa=X&ved=2ahUKEwidzNGanZ-GAxVpq5UCHR5ZBqEQjGp6BAgfEAE&biw=1366&bih=641&dpr=2&rlst=f"
                       "#rlfi=hd:;si:;mv:[[-23.6052574,-46.749922299999994],[-23.6414883,-46.8048072]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:2")

                print(f"Acessando URL: {url}")
                driver.get(url)
                time.sleep(3)

                while True:
                    if verificar_captcha(driver):
                        print("CAPTCHA detectado. Parando a execução.")
                        driver.quit()
                        exit()

                    try:
                        telefones = extrair_telefones(driver)

                        if not clicar_proximo(driver):
                            print(f"Não há mais resultados para {local_empresa}.")
                            break
                    except Exception as e:
                        print(f"Erro inesperado: {e}")
                        break
finally:
    driver.quit()
    print("Raspagem concluída. Dados salvos em numeros.txt.")
