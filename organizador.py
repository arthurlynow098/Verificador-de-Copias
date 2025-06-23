import os
import shutil
from PIL import Image
import imagehash
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import sys
import traceback
from datetime import datetime

def process_images(input_dir, tolerance, custom_duplicate_folder_name, custom_original_prefix, log_widget=None, status_callback=None):
    def log_message(message):
        if log_widget:
            log_widget.after(0, lambda: log_widget.insert(tk.END, message + "\n"))
            log_widget.after(0, lambda: log_widget.see(tk.END))
        else:
            print(message)

    def update_status(message):
        if status_callback:
            status_callback(message)

    log_message("Preparando para processar imagens...")
    update_status("Estado: A preparar...")

    if not os.path.isdir(input_dir):
        log_widget.after(0, lambda: messagebox.showerror("Erro de Diretório", f"O diretório '{input_dir}' não existe. Por favor, verifique o caminho."))
        log_message(f"Erro: O diretório '{input_dir}' não existe.")
        update_status("Estado: Erro de Diretório")
        return

    if not custom_duplicate_folder_name:
        custom_duplicate_folder_name = "duplicatas"
    output_duplicate_dir = os.path.join(input_dir, custom_duplicate_folder_name)
    os.makedirs(output_duplicate_dir, exist_ok=True)

    image_files_data = []
    supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')

    log_message(f"Iniciando o processamento de imagens no diretório: '{input_dir}'")
    update_status("Estado: A recolher imagens...")

    for filename in os.listdir(input_dir):
        if filename == custom_duplicate_folder_name:
            continue

        filepath = os.path.join(input_dir, filename)

        if os.path.isfile(filepath) and filename.lower().endswith(supported_extensions):
            try:
                img = Image.open(filepath)
                img_hash = imagehash.average_hash(img)
                image_files_data.append({"path": filepath, "hash": img_hash, "original_filename": filename})
            except Exception as e:
                log_message(f"Aviso: Não foi possível processar a imagem '{filename}'. Erro: {e}")
        else:
            if os.path.isfile(filepath):
                log_message(f"A ignorar o ficheiro '{filename}' pois não é uma imagem suportada.")

    if not image_files_data:
        log_widget.after(0, lambda: messagebox.showinfo("Nenhuma Imagem", "Nenhuma imagem suportada encontrada no diretório especificado. Nada para processar."))
        log_message("Nenhuma imagem suportada encontrada no diretório especificado. Nada para processar.")
        update_status("Estado: Nenhuma imagem encontrada")
        return

    processed_indices = set()
    duplicate_groups = []

    log_message(f"\nA identificar grupos de imagens semelhantes com tolerância de {tolerance}...")
    update_status("Estado: A identificar duplicatas...")

    for i, img_data1 in enumerate(image_files_data):
        if i in processed_indices:
            continue

        current_group = [img_data1]
        processed_indices.add(i)

        for j, img_data2 in enumerate(image_files_data):
            if i != j and j not in processed_indices:
                if img_data1["hash"] - img_data2["hash"] <= tolerance:
                    current_group.append(img_data2)
                    processed_indices.add(j)

        duplicate_groups.append(current_group)

    log_message(f"Total de grupos de imagens identificados (incluindo imagens únicas): {len(duplicate_groups)}")

    card_number_counter = 1
    total_duplicates_moved = 0

    log_message("\nA iniciar a renomeação e movimentação de ficheiros...")
    update_status("Estado: A organizar ficheiros...")

    for group in duplicate_groups:
        original_img_data = group[0]
        original_path = original_img_data["path"]
        original_filename = original_img_data["original_filename"]
        base_name, ext = os.path.splitext(original_filename)

        if not custom_original_prefix:
            custom_original_prefix = "cartao"
        new_original_base_name = f"{custom_original_prefix}_{card_number_counter:03d}"
        new_original_filename = f"{new_original_base_name}{ext}"
        new_original_path = os.path.join(os.path.dirname(original_path), new_original_filename)

        try:
            shutil.move(original_path, new_original_path)
            log_message(f"Original renomeado: '{original_filename}' para '{new_original_filename}'")
            card_number_counter += 1
        except Exception as e:
            log_message(f"Erro crítico ao renomear '{original_filename}'. Não foi possível processar as suas duplicatas. Erro: {e}")
            continue

        for i in range(1, len(group)):
            duplicate_img_data = group[i]
            duplicate_path = duplicate_img_data["path"]
            duplicate_filename = duplicate_img_data["original_filename"]
            dup_base_name, dup_ext = os.path.splitext(duplicate_filename)

            new_duplicate_filename = f"{new_original_base_name}-copia{dup_ext}"
            new_duplicate_path = os.path.join(output_duplicate_dir, new_duplicate_filename)

            try:
                shutil.move(duplicate_path, new_duplicate_path)
                log_message(f"Duplicado movido: '{duplicate_filename}' para '{new_duplicate_filename}' em '{output_duplicate_dir}'")
                total_duplicates_moved += 1
            except Exception as e:
                log_message(f"Erro ao mover/renomear duplicado '{duplicate_filename}'. Erro: {e}")

    final_message = f"\n------------------------------------\n" \
                    f"Processamento concluído!\n" \
                    f"Imagens originais renomeadas sequencialmente no diretório '{input_dir}'.\n" \
                    f"Total de {total_duplicates_moved} duplicatas movidas para a pasta '{output_duplicate_dir}'.\n" \
                    f"As duplicatas foram nomeadas com base nos seus originais.\n" \
                    f"------------------------------------"
    log_message(final_message)
    log_widget.after(0, lambda: messagebox.showinfo("Processamento Concluído", final_message))
    update_status("Estado: Concluído!")


class ImageOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Imagens")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6)
        self.style.configure("TEntry", padding=5)
        self.style.configure("TLabelFrame", background="#f0f0f0", font=("Helvetica", 11, "bold"), foreground="#333333")
        self.style.configure("Status.TLabel", font=("Helvetica", 10, "italic"), foreground="#555555")


        self.image_folder_var = tk.StringVar()
        self.image_folder_var.set(os.path.expanduser("~/Desktop/minhas_imagens"))

        self.tolerance_var = tk.IntVar()
        self.tolerance_var.set(80)

        self.custom_duplicate_folder_name_var = tk.StringVar()
        self.custom_duplicate_folder_name_var.set("duplicatas")

        self.custom_original_prefix_var = tk.StringVar()
        self.custom_original_prefix_var.set("cartao")

        self.processing_thread = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="ORGANIZADOR DE IMAGENS COM DUPLICATAS",
                               font=("Helvetica", 18, "bold"), foreground="#0056b3")
        title_label.grid(row=0, column=0, columnspan=2, pady=15)

        dir_frame = ttk.LabelFrame(main_frame, text="Diretório das Imagens", padding="10 10 10 10")
        dir_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Entry(dir_frame, textvariable=self.image_folder_var, width=60, state="readonly").grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(dir_frame, text="Procurar", command=self.browse_directory).grid(row=0, column=1)

        custom_names_frame = ttk.LabelFrame(main_frame, text="Personalização de Nomes", padding="10 10 10 10")
        custom_names_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(custom_names_frame, text="Nome da pasta de duplicatas:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(custom_names_frame, textvariable=self.custom_duplicate_folder_name_var, width=40).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(custom_names_frame, text="Prefixo das imagens originais:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(custom_names_frame, textvariable=self.custom_original_prefix_var, width=40).grid(row=1, column=1, sticky="ew", padx=5)

        tolerance_frame = ttk.LabelFrame(main_frame, text="Tolerância de Similaridade", padding="10 10 10 10")
        tolerance_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.tolerance_slider = ttk.Scale(tolerance_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                         variable=self.tolerance_var, length=400,
                                         command=self.update_tolerance_label)
        self.tolerance_slider.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        ttk.Label(tolerance_frame, text="Ajuste para maior precisão (0=idênticas, 100=muito semelhantes)").grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)

        self.tolerance_value_label = ttk.Label(tolerance_frame, text=f"Valor Atual: {self.tolerance_var.get()}")
        self.tolerance_value_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))

        self.start_button = ttk.Button(main_frame, text="INICIAR PROCESSAMENTO",
                                       command=self.start_processing, style="Accent.TButton")

        self.style.configure("Accent.TButton", background="#28a745", foreground="white", font=("Helvetica", 12, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#218838")])

        self.start_button.grid(row=4, column=0, columnspan=2, pady=25, ipadx=20, ipady=10)

        self.status_label = ttk.Label(main_frame, text="Estado: Pronto", style="Status.TLabel")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 5))

        log_frame = ttk.LabelFrame(main_frame, text="Registos de Processamento", padding="10 10 10 10")
        log_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=10)
        main_frame.grid_rowconfigure(7, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=15, state="disabled", wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)


    def update_tolerance_label(self, val):
        self.tolerance_value_label.config(text=f"Valor Atual: {int(float(val))}")

    def browse_directory(self):
        directory_selected = filedialog.askdirectory(initialdir=self.image_folder_var.get())
        if directory_selected:
            self.image_folder_var.set(directory_selected)
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            messagebox.showinfo("Diretório Selecionado", f"Diretório alterado para:\n{directory_selected}")


    def start_processing(self):
        input_dir = self.image_folder_var.get()
        tolerance = self.tolerance_var.get()
        custom_duplicate_folder_name = self.custom_duplicate_folder_name_var.get().strip()
        custom_original_prefix = self.custom_original_prefix_var.get().strip()

        if not input_dir:
            messagebox.showwarning("Entrada Inválida", "Por favor, selecione um diretório de imagens.")
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: A iniciar...")


        self.processing_thread = threading.Thread(target=self._run_processing_in_thread,
                                                  args=(input_dir, tolerance, custom_duplicate_folder_name, custom_original_prefix))
        self.processing_thread.start()

        self.check_processing_status()

    def _run_processing_in_thread(self, input_dir, tolerance, custom_duplicate_folder_name, custom_original_prefix):
        self.root.after(0, lambda: self.log_text.config(state="normal"))

        try:
            process_images(input_dir, tolerance, custom_duplicate_folder_name, custom_original_prefix, self.log_text, self._update_status_label_from_thread)
        except Exception as e:
            error_message = f"Ocorreu um erro durante o processamento:\n{e}\n{traceback.format_exc()}"
            self.root.after(0, lambda: messagebox.showerror("Erro de Processamento", error_message))
            self.root.after(0, lambda: self.log_text.insert(tk.END, f"\nErro: {error_message}\n"))
            self.root.after(0, lambda: self.status_label.config(text="Estado: Erro"))
        finally:
            self.root.after(0, lambda: self.log_text.config(state="disabled"))

    def _update_status_label_from_thread(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))


    def check_processing_status(self):
        if self.processing_thread and self.processing_thread.is_alive():
            self.root.after(100, self.check_processing_status)
        else:
            self.start_button.config(state=tk.NORMAL)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = f"[{now}] Exceção não capturada:\n"
    error_message += "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    log_file_path = "organizador_imagens_erro.log"
    try:
        with open(log_file_path, "a") as f:
            f.write(error_message + "\n" + "="*80 + "\n\n")
        messagebox.showerror("Erro Crítico",
                             f"Ocorreu um erro crítico e inesperado. Por favor, verifique o ficheiro de log em:\n{log_file_path}\n"
                             "O programa irá fechar.")
    except Exception as e:
        print(f"Erro ao escrever no ficheiro de log: {e}")
        print(error_message)
    
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerApp(root)
    root.mainloop()
