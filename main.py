import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import yt_dlp
import os
import pandas as pd


class MusicaDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Musica Downloader - DogyMaster")
        self.root.geometry("500x300")

        # Botón para cargar Excel
        self.excel_button = tk.Button(root, text="Seleccionar Excel con URLs", command=self.select_excel)
        self.excel_button.pack(pady=10)

        # Formato de descarga
        self.format_label = tk.Label(root, text="Selecciona formato de descarga:")
        self.format_label.pack(pady=5)

        self.format_var = tk.StringVar(value="mp3")
        self.format_menu = ttk.Combobox(root, textvariable=self.format_var, values=["mp3", "mp4"], state="readonly")
        self.format_menu.pack(pady=5)

        # Botón para elegir carpeta
        self.folder_button = tk.Button(root, text="Seleccionar carpeta destino", command=self.select_folder)
        self.folder_button.pack(pady=10)

        # Botón para iniciar descarga
        self.download_button = tk.Button(root, text="Descargar canciones", command=self.start_download_screen)
        self.download_button.pack(pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Variables
        self.output_folder = None
        self.urls = []

    def select_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                df = pd.read_excel(file_path)
                if "URL" in df.columns:
                    self.urls = df["URL"].dropna().tolist()
                    messagebox.showinfo("Excel cargado", f"Se encontraron {len(self.urls)} URLs para descargar.")
                else:
                    messagebox.showerror("Error", "El Excel debe tener una columna llamada 'URL'.")
            except Exception as e:
                messagebox.showerror("Error al leer Excel", str(e))

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            messagebox.showinfo("Carpeta seleccionada", f"Los archivos se guardarán en:\n{folder}")

    def start_download_screen(self):
        if not self.urls:
            messagebox.showerror("Error", "Primero selecciona un Excel con URLs.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Por favor selecciona una carpeta de destino.")
            return

        # Configurar barra de progreso
        self.progress["maximum"] = len(self.urls)
        self.progress["value"] = 0

        # Lanzar descarga en hilo
        threading.Thread(target=self.download_videos).start()

    def download_videos(self):
        formato = self.format_var.get()
        folder = self.output_folder

        for i, url in enumerate(self.urls, start=1):
            ydl_opts = {
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'noplaylist': True,
            }

            if formato == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:  # mp4
                ydl_opts.update({'format': 'bestvideo+bestaudio/best'})

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                messagebox.showerror("Error en descarga", f"No se pudo descargar {url}\n{str(e)}")

            # Actualizar progreso
            self.progress["value"] = i
            self.root.update_idletasks()

        messagebox.showinfo("Éxito", "Todas las descargas se completaron 🎶")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicaDownloaderApp(root)
    root.mainloop()
