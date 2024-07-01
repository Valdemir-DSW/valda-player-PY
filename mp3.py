import os
import io
import threading
import tkinter as tk
from tkinter import filedialog, Listbox, Button,ttk,messagebox, Label, colorchooser, Menu, Scale, HORIZONTAL, Checkbutton, IntVar
from tkinter import PhotoImage
from pygame import mixer
import configparser
from mutagen.mp3 import MP3
import pygame
import zipfile
from PIL import Image, ImageTk
import shutil
import subprocess
class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("valda-Player By Valdemir")
        self.root.iconbitmap(os.path.abspath("base.ico"))
        self.root.resizable(False,True)
        
        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        
        self.folder_path = ""
        self.current_folder = ""
        self.previous_folders = []
        self.music_list = []
        self.is_playing = False
        self.current_music_path = ""
        self.play_all_base = IntVar()
        self.play_all_selected = IntVar()
        
        self.load_config()
        
        # Inicializa o mixer do pygame
        mixer.init()
        
        # Cria a menubar
        menubar = Menu(root)
        root.config(menu=menubar)
        
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=settings_menu)
        settings_menu.add_command(label="Selecionar Pasta Base", command=self.select_folder)
        settings_menu.add_command(label="Selecionar Cor de Fundo", command=self.select_bg_color)
        settings_menu.add_command(label="Selecionar Cor do Texto", command=self.select_text_color)
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Gravar para Pendrive ou disco", command=self.start_copy)
        file_menu.add_command(label="BAIXAR DO YT", command=self.YTMP3)
        file_menu.add_command(label="organizar minhas musicas", command=self.org)
        file_menu.add_command(label="Atualizar lista", command=self.up)
        file_menu.add_command(label="importar para pasta base outra pasta externa", command=self.selecionar_pasta)
        file_menu.add_command(label="importar músicas de um arquivo .zip", command=self.zipimport)

        # Botão para voltar à pasta anterior
        self.back_button = Button(root, text="<< Voltar", command=self.go_back)
        self.back_button.pack(pady=10,padx=1)
        
        
        # Lista de pastas
        self.folder_listbox = Listbox(root, width=50, height=20, bg=self.bg_color, fg=self.text_color)
        self.folder_listbox.pack(side="left", fill="both", expand=True)
        self.folder_listbox.bind("<<ListboxSelect>>", self.on_folder_select)
        
        # Lista de músicas
        self.music_listbox = Listbox(root, width=50, height=20, bg=self.bg_color, fg=self.text_color)
        self.music_listbox.pack(side="left", fill="both", expand=True)
        self.music_listbox.bind("<<ListboxSelect>>", self.on_music_select)
        
        # Rótulo da música atual
        self.current_music_label = Label(root, text="Nenhuma música selecionada", bg=self.bg_color, fg=self.text_color)
        self.current_music_label.pack(pady=10)
        
        # Botões de controle de música
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        self.play_button = Button(control_frame, text="Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=1, padx=10)
        
        self.stop_button = Button(control_frame, text="Stop", command=self.stop_music)
        self.stop_button.grid(row=0, column=2, padx=10)
        
        self.previous_button = Button(control_frame, text="<<", command=self.previous_music)
        self.previous_button.grid(row=0, column=0, padx=10)
        
        self.next_button = Button(control_frame, text=">>", command=self.next_music)
        self.next_button.grid(row=0, column=3, padx=10)
        self.volume_slider = tk.Scale(control_frame, from_=0, to=100, orient='horizontal', command=self.set_volume)
        self.volume_slider.set(50)  # Volume inicial 50%
        self.volume_slider.grid(row=6, column=5, padx=10)
        ttk.Label(control_frame, text="Volume").grid(row=6, column=4, padx=10)
        
        self.play_all_base_button = Checkbutton(control_frame, text="Tocar Tudo (Pasta Base)", variable=self.play_all_base, state=tk.DISABLED)
        self.play_all_base_button.grid(row=0, column=4, padx=10)
        
        self.play_all_selected_button = Checkbutton(control_frame, text="Tocar Tudo (Pasta Selecionada)", variable=self.play_all_selected)
        self.play_all_selected_button.grid(row=0, column=5, padx=10)
        
        # Linha do tempo
        self.timeline = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=400)
        self.timeline.pack(pady=10)
        
        # Atualização da linha do tempo
        self.update_timeline()

        # Carrega a pasta base salva, se houver
        if self.folder_path:
            self.load_folders(self.folder_path)
    def YTMP3(self):
       # messagebox.showinfo("info",f"selecione para baixar/salvar dentro da pasta\n {self.folder_path}\n \npara aparecer dentro do player\nApos os donwloads clique para atualizar lista no menu Arquivo!")
        exe = os.path.abspath("yt/ytdonw.exe")
        subprocess.Popen(exe)

    def org(self):
       # messagebox.showinfo("info",f"selecione para baixar/salvar dentro da pasta\n {self.folder_path}\n \npara aparecer dentro do player\nApos os donwloads clique para atualizar!")
        #subprocess.Popen(self.folder_path)  
        subprocess.Popen(f'explorer "{self.folder_path}"')
    def load_config(self):
        self.config.read(self.config_file)
        if 'Settings' in self.config:
            self.folder_path = self.config['Settings'].get('folder_path', '')
            self.bg_color = self.config['Settings'].get('bg_color', 'white')
            self.text_color = self.config['Settings'].get('text_color', 'black')
            self.root.configure(background=self.bg_color)  
        else:
            self.folder_path = os.path.join(os.getenv('USERPROFILE'), 'Music')
            self.bg_color = 'white'
            self.text_color = 'black'
            self.save_config()

    def up(self):
            self.load_folders(self.folder_path)
    def save_config(self):
        self.config['Settings'] = {
            'folder_path': self.folder_path,
            'bg_color': self.bg_color,
            'text_color': self.text_color
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.save_config()
            self.load_folders(self.folder_path)
        
    def load_folders(self, path):
        self.folder_listbox.delete(0, tk.END)
        self.music_listbox.delete(0, tk.END)
        self.current_folder = path
        self.previous_folders.append(path)
        
        self.music_list = []
        
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                self.folder_listbox.insert(tk.END, item)
            elif item.lower().endswith(".mp3"):
                self.music_listbox.insert(tk.END, item)
                self.music_list.append(item_path)
    
    def on_folder_select(self, event):
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            selected_folder = self.folder_listbox.get(selected_index)
            folder_path = os.path.join(self.current_folder, selected_folder)
            self.load_folders(folder_path)
    
    def on_music_select(self, event):
        selected_index = self.music_listbox.curselection()
        if selected_index:
            selected_music = self.music_listbox.get(selected_index)
            self.current_music_label.config(text=selected_music)
            self.current_music_path = self.music_list[selected_index[0]]
            self.update_play_button()
    
    def toggle_play(self):
        if self.is_playing:
            self.pause_music()
        else:
            self.play_music()
    
    def play_music(self):
        if self.current_music_path:
            mixer.music.load(self.current_music_path)
            mixer.music.play()
            self.is_playing = True
            self.update_play_button()
            mixer.music.set_endevent(pygame.USEREVENT)
            self.root.after(1000, self.check_music_end)  # Verifica se a música terminou a cada segundo
            

    def set_volume(self,val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)
    def pause_music(self):
        mixer.music.pause()
        self.is_playing = False
        self.update_play_button()
    
    def stop_music(self):
        mixer.music.stop()
        self.is_playing = False
        self.update_play_button()
        self.timeline.set(0)
    
    def previous_music(self):
        selected_index = self.music_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            self.music_listbox.selection_clear(0, tk.END)
            self.music_listbox.selection_set(selected_index[0] - 1)
            self.music_listbox.event_generate("<<ListboxSelect>>")
            self.play_music()
    
    def next_music(self):
        selected_index = self.music_listbox.curselection()
        if selected_index and selected_index[0] < len(self.music_list) - 1:
            self.music_listbox.selection_clear(0, tk.END)
            self.music_listbox.selection_set(selected_index[0] + 1)
            self.music_listbox.event_generate("<<ListboxSelect>>")
            self.play_music()

  

    def load_music_files(self, folder):
        # Carregue todos os arquivos de música da pasta especificada
        self.music_files = [
            os.path.join(folder, file) 
            for file in os.listdir(folder) 
            if file.lower().endswith('.mp3')
        ]
        self.current_index = 0

    def check_music_end(self):
        print(self.play_all_selected.get())
        if self.play_all_selected.get() == 1:
            if not self.is_playing:
                return
            if pygame.mixer.music.get_busy():
                self.root.after(1000, self.check_music_end)
            else:
                self.next_music()
    def selecionar_pasta(self):
        pasta_origem = filedialog.askdirectory(title="Selecione a pasta a ser copiada")
        if pasta_origem:
            # Criar uma cópia da pasta
            pasta_destino = self.folder_path  # Substitua com o caminho desejado
            try:
                shutil.copytree(pasta_origem, os.path.join(pasta_destino, os.path.basename(pasta_origem)))
                tk.messagebox.showinfo("Sucesso", "Pasta copiada com sucesso!")
            except Exception as e:
                tk.messagebox.showerror("Erro", f"Ocorreu um erro ao copiar a pasta: {str(e)}")
    def go_back(self):
        if len(self.previous_folders) > 1:
            self.previous_folders.pop()  # Remove o diretório atual
            parent_folder = self.previous_folders.pop()  # Obtém o diretório anterior
            self.load_folders(parent_folder)

    def select_bg_color(self):
        color = colorchooser.askcolor(title="Selecionar Cor de Fundo")[1]
        if color:
            self.bg_color = color
            self.update_colors()
            self.save_config()
    
    def select_text_color(self):
        color = colorchooser.askcolor(title="Selecionar Cor do Texto")[1]
        if color:
            self.text_color = color
            self.update_colors()
            self.save_config()

    def update_colors(self):
        self.folder_listbox.config(bg=self.bg_color, fg=self.text_color)
        self.music_listbox.config(bg=self.bg_color, fg=self.text_color)
        self.current_music_label.config(bg=self.bg_color, fg=self.text_color)
        self.root.configure(background=self.bg_color)  
    
    def update_play_button(self):
        if self.is_playing:
            self.play_button.config(text="Pause")
        else:
            self.play_button.config(text="Play")
        
        if self.current_music_path:
            try:
                audio = MP3(self.current_music_path)
                if audio.tags and 'APIC:' in audio.tags:
                    artwork = audio.tags['APIC:'].data
                    image = Image.open(io.BytesIO(artwork))
                else:
                    raise KeyError("'APIC:' tag not found")
            except KeyError as e:
                print(f"Error loading artwork: {e}")
                image = Image.open(os.path.abspath("base.png"))
            except Exception as e:
                print(f"Error: {e}")
                image = Image.open(os.path.abspath("base.png"))
            
            image.thumbnail((75, 75))
            photo = ImageTk.PhotoImage(image)
            self.play_button.config(image=photo, compound="top")
            self.play_button.image = photo
    
    def update_timeline(self):
        if self.is_playing and self.current_music_path:
            current_pos = mixer.music.get_pos() / 1000  # posição atual em segundos
            audio = MP3(self.current_music_path)
            total_length = audio.info.length  # duração total em segundos
            self.timeline.config(to=total_length)
            self.timeline.set(current_pos)
        self.root.after(1000, self.update_timeline)  # Atualiza a linha do tempo a cada segundo
  

    # Função para selecionar a pasta base ou pastas específicas
    def select_folders(self):
        folder = filedialog.askdirectory()
        if not folder:
            return None
        return folder

    # Função para iniciar a cópia de arquivos
    def select_pendrives(self):
        selected_pendrives = []

        def add_pendrive():
            drive_letter = filedialog.askdirectory(title="Selecione o Pendrive")
            if drive_letter:
                selected_pendrives.append(drive_letter)
                pendrives_listbox.insert(tk.END, drive_letter)

        def confirm_selection():
            self.pendrive_paths = selected_pendrives
            pendrives_window.destroy()

        pendrives_window = tk.Toplevel(self.root)
        pendrives_window.title("Selecionar Pendrives")
        pendrives_window.iconbitmap(os.path.abspath("base.ico"))
        pendrives_window.resizable(False, False)
        pendrives_window.grab_set()

        add_button = tk.Button(pendrives_window, text="Adicionar Pendrive", command=add_pendrive)
        add_button.pack(pady=5)

        pendrives_listbox = tk.Listbox(pendrives_window, selectmode=tk.MULTIPLE)
        pendrives_listbox.pack(pady=5)

        confirm_button = tk.Button(pendrives_window, text="Confirmar", command=confirm_selection)
        confirm_button.pack(pady=5)


    # Função para selecionar pastas específicas dentro da pasta base
    def select_specific_folders(self):
        folders = filedialog.askdirectory(initialdir=self.folder_path)
        if not folders:
            return None
        return folders

 

    # Função para selecionar múltiplas pastas específicas dentro da pasta base
    def select_specific_folders(self):
        folders = filedialog.askdirectory(initialdir=self.folder_path, mustexist=True, multiple=True)
        if not folders:
            return None
        return folders



    # Função para iniciar a cópia de arquivos
    def start_copy(self):
        self.copy_window = tk.Toplevel(self.root)
        self.copy_window.title("Copiar para Pendrive")
        self.copy_window.iconbitmap(os.path.abspath("base.ico"))
        self.copy_window.resizable(False, False)
        self.copy_window.attributes("-topmost", True) # Dá maior prioridade à janela de cópia

        tk.Label(self.copy_window, text="Selecione os Pendrives:").pack(pady=5)
        pendrive_button = tk.Button(self.copy_window, text="Selecionar Pendrives", command=lambda: self.select_pendrive_button(self.copy_window))
        pendrive_button.pack(pady=5)

        tk.Label(self.copy_window, text="Escolha a opção de cópia:").pack(pady=5)
        ttk.Radiobutton(self.copy_window, text="Copiar toda a Pasta Base", variable=self.play_all_base, value=1).pack(anchor=tk.W)
        ttk.Radiobutton(self.copy_window, text="Selecionar Pastas Específicas", variable=self.play_all_base, value=0).pack(anchor=tk.W)

        confirm_button = tk.Button(self.copy_window, text="Confirmar", command=lambda: self.confirm_selection(self.copy_window))
        confirm_button.pack(pady=5)

        self.copy_window_elements = {
            "pendrive_button": pendrive_button,
            "confirm_button": confirm_button
        }


    def select_pendrive_button(self, window):
        pendrives = self.select_pendrives()
        if pendrives:
            self.copy_window_elements["pendrive_button"].config(text=f"Pendrives selecionados", state="disabled")
            self.pendrive_paths = pendrives

    def zipimport(self):

        def selecionar_arquivo_zip():
            arquivo_zip = filedialog.askopenfilename(title="Selecione o arquivo ZIP", filetypes=[("Arquivos ZIP", "*.zip")])
            if arquivo_zip:
                entry_zip.delete(0, tk.END)
                entry_zip.insert(0, arquivo_zip)

        def iniciar_extracao():
            arquivo_zip = entry_zip.get()
            nome_pasta = entry_nome_pasta.get()

            if not arquivo_zip or not nome_pasta:
                messagebox.showerror("Erro", "Por favor, selecione um arquivo ZIP e digite um nome para a nova pasta.")
                return

            # Iniciar a extração em uma thread separada
            extracao_thread = threading.Thread(target=extrair_zip, args=(arquivo_zip, nome_pasta))
            extracao_thread.start()

        def extrair_zip(arquivo_zip, nome_pasta):
            try:
                # Criar a nova pasta dentro de self.folder_path
                nova_pasta = os.path.join(self.folder_path, nome_pasta)
                os.makedirs(nova_pasta, exist_ok=True)

                # Extrair o arquivo ZIP
                with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    progress['maximum'] = total_files

                    for i, file in enumerate(file_list, start=1):
                        zip_ref.extract(file, nova_pasta)
                        progress['value'] = i
                        progress.update_idletasks()  # Atualizar a barra de progresso

                messagebox.showinfo("Sucesso", f"Arquivo ZIP extraído para '{nome_pasta}' com sucesso!")

            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao extrair o arquivo ZIP: {str(e)}")

        # Configuração da janela principal
        ruteszip = tk.Tk()
        ruteszip.title("Extrair arquivo ZIP")
        ruteszip.iconbitmap(os.path.abspath("base.ico"))
        ruteszip.resizable(False, False)
        ruteszip.attributes("-topmost", True) # Dá maior prioridade à janela de cópia

        # Frame para a seleção do arquivo ZIP e nome da nova pasta
        frame_selecao = tk.Frame(ruteszip)
        frame_selecao.pack(pady=20)

        label_zip = tk.Label(frame_selecao, text="Arquivo ZIP:")
        label_zip.grid(row=0, column=0, padx=10)

        entry_zip = tk.Entry(frame_selecao, width=50)
        entry_zip.grid(row=0, column=1, padx=10)

        btn_selecionar_zip = tk.Button(frame_selecao, text="Selecionar ZIP", command=selecionar_arquivo_zip)
        btn_selecionar_zip.grid(row=0, column=2, padx=10)

        label_nome_pasta = tk.Label(frame_selecao, text="Nome da nova pasta:")
        label_nome_pasta.grid(row=1, column=0, padx=10, pady=10)

        entry_nome_pasta = tk.Entry(frame_selecao, width=50)
        entry_nome_pasta.grid(row=1, column=1, padx=10, pady=10)

        # Botão para extrair o ZIP
        btn_extrair = tk.Button(ruteszip, text="Extrair ZIP", command=lambda: iniciar_extracao())
        btn_extrair.pack(pady=10)

        # Barra de progresso
        progress = ttk.Progressbar(ruteszip, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress.pack(pady=10)

        # Rodar o loop principal
        ruteszip.mainloop()


    def confirm_selection(self, window):
        if self.play_all_base.get() == 1:
            # Copiar toda a pasta base
            folder_to_copy = self.folder_path
            self.show_copy_window(folder_to_copy)
        else:
            # Selecionar pastas específicas dentro da pasta base
            self.select_specific_folders()

    def select_specific_folders(self):
        specific_folders_window = tk.Toplevel(self.copy_window)
        specific_folders_window.title("Selecionar Pastas Específicas")
        specific_folders_window.iconbitmap(os.path.abspath("base.ico"))
        specific_folders_window.resizable(False,True)
        specific_folders_window.grab_set()

        folders = []
        for folder in os.listdir(self.folder_path):
            folder_path = os.path.join(self.folder_path, folder)
            if os.path.isdir(folder_path):
                folders.append(folder)

        self.selected_folders = []
        for folder in folders:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(specific_folders_window, text=folder, variable=var)
            chk.pack(anchor=tk.W)
            self.selected_folders.append((folder, var))

        confirm_button = tk.Button(specific_folders_window, text="Confirmar", command=lambda: self.confirm_folder_selection(specific_folders_window))
        confirm_button.pack(pady=5)
    
   
    def confirm_folder_selection(self, window):
        selected_folders = [os.path.join(self.folder_path, folder) for folder, var in self.selected_folders if var.get()]
        window.destroy()
        if selected_folders:
            self.show_copy_window(selected_folders)

    def show_copy_window(self, folder_to_copy):
        for widget in self.copy_window.winfo_children():
            widget.destroy()

        progress_label = tk.Label(self.copy_window, text="toque para iniciar...")
        progress_label.pack(pady=10)

        progress = ttk.Progressbar(self.copy_window, orient="horizontal", length=300, mode="determinate")
        progress.pack(pady=10)

        copy_button = tk.Button(self.copy_window, text="Iniciar Cópia", command=lambda: self.copy_files(folder_to_copy, self.pendrive_paths, progress, progress_label))
        copy_button.pack(pady=10)


    # Função para copiar arquivos
    def copy_files(self, src, dest_list, progress, progress_label):
        file_list = []

        if isinstance(src, list):
            for folder in src:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_list.append((file, os.path.relpath(os.path.join(root, file), self.folder_path)))
        else:
            for root, dirs, files in os.walk(src):
                for file in files:
                    file_list.append((file, os.path.relpath(os.path.join(root, file), self.folder_path)))

        total_files = len(file_list)
        copied_files = 0

        for file, rel_path in file_list:
            for dest in dest_list:
                dest_file_path = os.path.join(dest, rel_path)
                dest_folder_path = os.path.dirname(dest_file_path)
                os.makedirs(dest_folder_path, exist_ok=True)
                shutil.copy2(os.path.join(self.folder_path, rel_path), dest_file_path)

            copied_files += 1
            progress['value'] = (copied_files / total_files) * 100
            progress.update()
            progress_label.config(text=f"Copiando arquivos... ({copied_files}/{total_files})")
            if copied_files == total_files:
                progress_label.config(text=f"Concluído com sucesso... ({copied_files}/{total_files})")





if __name__ == "__main__":
    root = tk.Tk()
    app = MP3Player(root)
    root.mainloop()
