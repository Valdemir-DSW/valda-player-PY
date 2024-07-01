import tkinter as tk
from tkinter import ttk, messagebox
from pytube import Playlist, YouTube
from pydub import AudioSegment
import os
import threading
import configparser
from datetime import datetime
class YouTubeDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT DONW for valda player")
        self.iconbitmap(os.path.abspath("ytico.ico"))
        self.resizable(False,False)
        
        # Carregando configurações do arquivo config.ini
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.folder_path = self.config.get("Settings", "folder_path")
        
        # Configuração das abas
        self.notfy= 1
        self.logope = 0
        
        self.tabControl = ttk.Notebook(self)
        
        self.tab_individual = ttk.Frame(self.tabControl)
        self.tab_playlist = ttk.Frame(self.tabControl)
        
        self.tabControl.add(self.tab_individual, text='Download Individual')
        self.tabControl.add(self.tab_playlist, text='Download Playlist')
        
        self.tabControl.pack(expand=1, fill="both")
        self.log_display = tk.Text(self, width=80, height=4, bg="black", fg="green")
        self.log_display.pack(pady=20)
        # Inicialização das abas
        self.setup_individual_tab()
        self.setup_playlist_tab()
        
        # Atualiza as opções da combobox após inicializar todas as abas
        self.refresh_folders()
    
    def setup_individual_tab(self):
        label = tk.Label(self.tab_individual, text="Insira o URL do vídeo do YouTube:")
        label.pack(pady=5)
        
        self.url_entry_individual = tk.Entry(self.tab_individual, width=50)
        self.url_entry_individual.pack(pady=5)
        
        # Radio buttons para selecionar entre escolher ou criar uma pasta
        self.folder_option_individual = tk.StringVar(value="existing")
        
        self.radio_existing_individual = tk.Radiobutton(self.tab_individual, text="Escolher pasta existente", variable=self.folder_option_individual, value="existing", command=self.toggle_folder_option_individual)
        self.radio_existing_individual.pack(pady=5)
        
        self.radio_new_individual = tk.Radiobutton(self.tab_individual, text="Criar nova pasta", variable=self.folder_option_individual, value="new", command=self.toggle_folder_option_individual)
        self.radio_new_individual.pack(pady=5)
        
        # Combobox para escolher uma pasta existente
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(self.tab_individual, textvariable=self.folder_var, state="readonly", width=40)
        self.folder_combo.pack(pady=5)
        
        # Campo para criar nova pasta
        self.new_folder_entry = tk.Entry(self.tab_individual, width=40)
        self.new_folder_entry.pack(pady=5)
        
        download_button = tk.Button(self.tab_individual, text="Baixar", command=self.download_individual)
        download_button.pack(pady=10)
        
        # Barra de progresso
        self.progress_bar_individual = ttk.Progressbar(self.tab_individual, orient="horizontal", length=400, mode="determinate")
        self.progress_bar_individual.pack(pady=10)
    
    def setup_playlist_tab(self):
        label = tk.Label(self.tab_playlist, text="Insira o URL da playlist do YouTube:")
        label.pack(pady=5)
        
        self.url_entry_playlist = tk.Entry(self.tab_playlist, width=50)
        self.url_entry_playlist.pack(pady=5)
        
        # Radio buttons para selecionar entre escolher ou criar uma pasta
        self.folder_option_playlist = tk.StringVar(value="existing")
        
        self.radio_existing_playlist = tk.Radiobutton(self.tab_playlist, text="Escolher pasta existente", variable=self.folder_option_playlist, value="existing", command=self.toggle_folder_option_playlist)
        self.radio_existing_playlist.pack(pady=5)
        
        self.radio_new_playlist = tk.Radiobutton(self.tab_playlist, text="Criar nova pasta", variable=self.folder_option_playlist, value="new", command=self.toggle_folder_option_playlist)
        self.radio_new_playlist.pack(pady=5)
        
        # Combobox para escolher uma pasta existente
        self.playlist_folder_var = tk.StringVar()
        self.playlist_folder_combo = ttk.Combobox(self.tab_playlist, textvariable=self.playlist_folder_var, state="readonly", width=40)
        self.playlist_folder_combo.pack(pady=5)
        
        # Campo para criar nova pasta
        self.new_playlist_folder_entry = tk.Entry(self.tab_playlist, width=40)
        self.new_playlist_folder_entry.pack(pady=5)
        
        download_button = tk.Button(self.tab_playlist, text="Baixar Playlist", command=self.download_playlist)
        download_button.pack(pady=10)
        
        # Barra de progresso
        self.progress_bar_playlist = ttk.Progressbar(self.tab_playlist, orient="horizontal", length=400, mode="determinate")
        self.progress_bar_playlist.pack(pady=10)
    
    def refresh_folders(self):
        # Limpa as opções atuais da combobox e adiciona as pastas existentes
        folders = [name for name in os.listdir(self.folder_path) if os.path.isdir(os.path.join(self.folder_path, name))]
        self.folder_combo['values'] = folders
        self.playlist_folder_combo['values'] = folders
    
    def toggle_folder_option_individual(self):
        if self.folder_option_individual.get() == "existing":
            self.folder_combo.config(state="readonly")
            self.new_folder_entry.config(state="disabled")
        else:
            self.folder_combo.config(state="disabled")
            self.new_folder_entry.config(state="normal")
    
    def toggle_folder_option_playlist(self):
        if self.folder_option_playlist.get() == "existing":
            self.playlist_folder_combo.config(state="readonly")
            self.new_playlist_folder_entry.config(state="disabled")
        else:
            self.playlist_folder_combo.config(state="disabled")
            self.new_playlist_folder_entry.config(state="normal")
    
    def download_individual(self):
        url = self.url_entry_individual.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira o URL do vídeo do YouTube.")
            return
        
        selected_folder = self.folder_var.get()
        new_folder = self.new_folder_entry.get().strip()
        
        if self.folder_option_individual.get() == "new" and new_folder:
            destination_folder = os.path.join(self.folder_path, new_folder)
            os.makedirs(destination_folder, exist_ok=True)
            selected_folder = new_folder
        messagebox.showinfo("vai", f"iniciando o donwload")
        t = threading.Thread(target=self.download_mp3, args=(url, selected_folder, self.progress_bar_individual))
        t.start()

    
    def download_playlist(self):
        playlist_url = self.url_entry_playlist.get().strip()
        if not playlist_url:
            messagebox.showerror("Erro", "Por favor, insira o URL da playlist do YouTube.")
            return
        
        selected_folder = self.playlist_folder_var.get()
        new_folder = self.new_playlist_folder_entry.get().strip()
        
        if self.folder_option_playlist.get() == "new" and new_folder:
            destination_folder = os.path.join(self.folder_path, new_folder)
            os.makedirs(destination_folder, exist_ok=True)
            selected_folder = new_folder
        messagebox.showinfo("vai", f"iniciando o donwload")
        t = threading.Thread(target=self.download_playlist_mp3, args=(playlist_url, selected_folder, self.progress_bar_playlist))
        t.start()
    def log_message(self,message):
      
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {message}\n"
        
        # Escrever a mensagem de log no arquivo
        with open("app.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Atualizar o display de log
        self.log_display.insert(tk.END, log_entry)
        self.log_display.yview(tk.END)




    def download_mp3(self, url, selected_folder, progress_bar):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            out_file = stream.download()
            
            # Convertendo o arquivo para MP3 e movendo para a pasta selecionada
            base, _ = os.path.splitext(out_file)
            new_file = base + '.mp3'
            progress_bar["value"] = 44
            
            audio_clip = AudioSegment.from_file(out_file)
            audio_clip.export(new_file, format="mp3")
            
            os.remove(out_file)  # Remove o arquivo MP4
            
            destination_path = os.path.join(self.folder_path, selected_folder, os.path.basename(new_file))
            os.replace(new_file, destination_path)
            if self.notfy == 1:
             progress_bar["value"] = 100
             messagebox.showinfo("Sucesso", f"Download de {yt.title} completo!\nSalvo em: {destination_path}")
             self.log_message(f"Download de {yt.title} completo!\nSalvo em: {destination_path}")
            else: 
             self.log_message(f"Download de {yt.title} completo!\nSalvo em: {destination_path}")
        except Exception as e:
            self.log_message(e)
            #if "is age restricted, and can't be accessed without logging in." in e:
            self.log_message(f"{e} \nimpossível baixar este som,o vídeo em questão tem restrições de idade ou é umlink morto .Desculpe \n tentando baixar as próximas...")
           
          
        finally:
            progress_bar.stop()

    
    def download_playlist_mp3(self, playlist_url, selected_folder, progress_bar):
       # messagebox.showinfo("vai", f"iniciando o donwload")
        try:
            playlist = Playlist(playlist_url)
            total_videos = len(playlist.video_urls)
            progress_bar["maximum"] = total_videos
            self.notfy = 0
            for idx, url in enumerate(playlist.video_urls):
                self.download_mp3(url, selected_folder, progress_bar)
                progress_bar["value"] = idx + 1
            
            messagebox.showinfo("Sucesso", "Download da playlist completo!")
            self.notfy = 1
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao baixar a playlist: {e}")
            print(e)
        finally:
            progress_bar.stop()

# Inicialização do aplicativo
if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
