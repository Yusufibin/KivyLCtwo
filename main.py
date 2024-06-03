#!/usr/bin/env python

from kivy.app import App
from kivy.app import App
from kivy.uix.button import Button
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import os
from cryptography.fernet import Fernet

class MyApp(App):
    def build(self):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        btn = Button(text="Encrypt Files in Music Directory")
        btn.bind(on_release=self.encrypt_files)
        return btn

    def generate_key(self):
        key = Fernet.generate_key()
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
        music_dir = os.path.join(primary_external_storage_path(), 'Music')
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
        
        key = self.generate_key()  # Generate a new key

        for root, dirs, files in os.walk(music_dir):
            for file in files:
                file_path = os.path.join(root, file)
                self.encrypt_file(file_path, key)
                print(f"File encrypted: {file_path}")

if __name__ == '__main__':
    MyApp().run()
