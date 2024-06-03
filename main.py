#!/usr/bin/env python

from kivy.app import App
from kivy.uix.button import Button
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import os

class MyApp(App):
    def build(self):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        btn = Button(text="Create File in Music Directory")
        btn.bind(on_release=self.create_file)
        return btn

    def create_file(self, instance):
        music_dir = os.path.join(primary_external_storage_path(), 'Music')
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
        
        file_path = os.path.join(music_dir, 'myfile.txt')
        with open(file_path, 'w') as f:
            f.write("Hello, this is a test file.")
        print(f"File created at: {file_path}")

if __name__ == '__main__':
    MyApp().run()
