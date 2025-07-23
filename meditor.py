#libs
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import keyword
import os
import random

#global variables
current_file = None  # Path of the currently opened file
backup_file = "meditor_backup.txt"  # Temp file for auto-saving

# Constants
WINDOW_TITLE = "Meu Editor - 2025 by Migdal Eder"
BG_COLOR = "black"
FG_COLOR = "#90EE90"  # Light green
CURSOR_COLOR = "#90EE90"
FONT = "Courier"
INITIAL_FONT_SIZE = 20
MAX_FONT_SIZE = 48
MIN_FONT_SIZE = 16
KEY_SOUND_FILES = ["sounds/tw1.wav", "sounds/tw2.wav", "sounds/tw3.wav"]
ENTER_SOUND_FILE = "sounds/return.wav"
SCROLL_UP_SOUND_FILE = "sounds/scroll1.wav"
SCROLL_DOWN_SOUND_FILE = "sounds/scroll2.wav"
PADDING = 72

#menu functions
def novo_arquivo(text):
    """Clear the text widget to start a new file."""
    global current_file
    if text.get(1.0, tk.END).strip():
        if messagebox.askyesno("Novo", "Salvar antes de criar novo?"):
            salvar_arquivo(text)
    text.delete(1.0, tk.END)
    current_file = None
    save_backup(text)

def abrir_arquivo(text):
    """Open a file and load its content into the text widget."""
    global current_file
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt *.py"), ("All Files", "*.*")])
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text.delete(1.0, tk.END)
                text.insert(tk.END, file.read())
            current_file = filepath
            save_backup(text)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")

def salvar_arquivo(text):
    """Save the text widget content to a file."""
    global current_file
    if current_file:
        try:
            with open(current_file, 'w', encoding='utf-8') as file:
                file.write(text.get(1.0, tk.END))
            save_backup(text)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
    else:
        salvar_como(text)

def salvar_como(text):
    """Save as a new file."""
    global current_file
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
    if filepath:
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(text.get(1.0, tk.END))
            current_file = filepath
            save_backup(text)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")

def fechar_arquivo(text):
    """Close the current file, prompting to save if modified."""
    if text.get(1.0, tk.END).strip():
        if messagebox.askyesno("Fechar", "Salvar antes de fechar?"):
            salvar_arquivo(text)
    text.delete(1.0, tk.END)
    global current_file
    current_file = None
    save_backup(text)

def toggle_fullscreen(root):
    """Toggle fullscreen mode."""
    is_fullscreen = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not is_fullscreen)

def zoom_in(text, font_size):
    """Increase font size up to MAX_FONT_SIZE."""
    new_size = font_size.get() + 2
    if new_size <= MAX_FONT_SIZE:
        font_size.set(new_size)
        text.configure(font=(FONT, new_size))

def zoom_out(text, font_size):
    """Decrease font size down to MIN_FONT_SIZE."""
    new_size = font_size.get() - 2
    if new_size >= MIN_FONT_SIZE:
        font_size.set(new_size)
        text.configure(font=(FONT, new_size))

def sobre_popup():
    """Show About popup with author and license."""
    messagebox.showinfo("Sobre", "2025 - Criado por Migdal Eder\nLicença: GNU GPL v3")

def play_sound(sound):
    """Play the keystroke sound."""
    sound.play()

def save_backup(text):
    """Save text content to a backup file."""
    try:
        with open(backup_file, 'w', encoding='utf-8') as file:
            file.write(text.get(1.0, tk.END))
    except Exception as e:
        print(f"Erro ao salvar backup: {e}")

def toggle_bold(text):
    """Toggle bold on selected text."""
    try:
        current_tags = text.tag_names("sel.first")
        if "bold" in current_tags:
            text.tag_remove("bold", "sel.first", "sel.last")
        else:
            text.tag_add("bold", "sel.first", "sel.last")
    except tk.TclError:
        pass

def toggle_italic(text):
    """Toggle italic on selected text."""
    try:
        current_tags = text.tag_names("sel.first")
        if "italic" in current_tags:
            text.tag_remove("italic", "sel.first", "sel.last")
        else:
            text.tag_add("italic", "sel.first", "sel.last")
    except tk.TclError:
        pass

def choose_font(text, font_family, font_size):
    """Custom popup to choose font family and size."""
    popup = tk.Toplevel(text.master)
    popup.title("Escolher Fonte")
    popup.configure(bg=BG_COLOR)

    tk.Label(popup, text="Family:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0)
    family_entry = tk.Entry(popup, bg=BG_COLOR, fg=FG_COLOR)
    family_entry.insert(0, font_family.get())
    family_entry.grid(row=0, column=1)

    tk.Label(popup, text="Size:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0)
    size_entry = tk.Entry(popup, bg=BG_COLOR, fg=FG_COLOR)
    size_entry.insert(0, str(font_size.get()))
    size_entry.grid(row=1, column=1)

    def apply_font():
        new_family = family_entry.get() or FONT
        try:
            new_size = int(size_entry.get())
        except ValueError:
            new_size = INITIAL_FONT_SIZE
        font_family.set(new_family)
        font_size.set(new_size)
        text.configure(font=(new_family, new_size))
        text.tag_configure("bold", font=(new_family, new_size, "bold"))
        text.tag_configure("italic", font=(new_family, new_size, "italic"))
        popup.destroy()

    tk.Button(popup, text="Aplicar", command=apply_font, bg=BG_COLOR, fg=FG_COLOR).grid(row=2, columnspan=2)

def handle_keystroke(event, text, key_sounds, enter_sound):
    if event.keysym == 'Return':
        if enter_sound:
            play_sound(enter_sound)
    else:
        if key_sounds:
            random_sound = random.choice(key_sounds)
            play_sound(random_sound)
    return None

def handle_mouse_wheel(event, scroll_sound):
    if scroll_sound:
        play_sound(scroll_sound)
    return None



#main function
def main():
    try:
        pygame.mixer.init()
        key_sounds = [pygame.mixer.Sound(file) for file in KEY_SOUND_FILES]
        enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
        scroll_up_sound = pygame.mixer.Sound(SCROLL_UP_SOUND_FILE)
        scroll_down_sound = pygame.mixer.Sound(SCROLL_DOWN_SOUND_FILE)
    except pygame.error as e:
        print(f"Erro ao carregar sons: {e}. Continuando sem som.")
        key_sounds = enter_sound = scroll_up_sound = scroll_down_sound = None

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.configure(bg=BG_COLOR)

    font_family = tk.StringVar(value=FONT)
    font_size = tk.IntVar(value=INITIAL_FONT_SIZE)
    retro_var = tk.BooleanVar(value=False)

    text = tk.Text(root, bg=BG_COLOR, fg=FG_COLOR,
                   font=(font_family.get(), font_size.get()),
                   insertbackground=CURSOR_COLOR, insertwidth=10,
                   wrap="word", undo=True,
                   borderwidth=0, highlightthickness=0, highlightbackground=BG_COLOR)
    text.pack(expand=True, fill="both", padx=PADDING, pady=PADDING)

    text.tag_configure("bold", font=(font_family.get(), font_size.get(), "bold"))
    text.tag_configure("italic", font=(font_family.get(), font_size.get(), "italic"))

    if key_sounds or enter_sound:
        text.bind("<Any-KeyPress>", lambda event: handle_keystroke(event, text, key_sounds, enter_sound))

    if scroll_up_sound:
        root.bind("<Button-4>", lambda event: handle_mouse_wheel(event, scroll_up_sound))
    if scroll_down_sound:
        root.bind("<Button-5>", lambda event: handle_mouse_wheel(event, scroll_down_sound))

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Menu Arquivo
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Arquivo", menu=file_menu)
    file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=lambda: novo_arquivo(text))
    file_menu.add_command(label="Abrir", accelerator="Ctrl+O", command=lambda: abrir_arquivo(text))
    file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=lambda: salvar_arquivo(text))
    file_menu.add_command(label="Salvar Como", accelerator="Ctrl+Shift+S", command=lambda: salvar_como(text))
    file_menu.add_command(label="Fechar", accelerator="Ctrl+W", command=lambda: fechar_arquivo(text))
    file_menu.add_command(label="Sair", accelerator="Ctrl+Q", command=root.quit)

    # Menu Foco
    focus_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Foco", menu=focus_menu)
    focus_menu.add_command(label="Tela Cheia", accelerator="F11", command=lambda: toggle_fullscreen(root))
    focus_menu.add_command(label="Zoom +", accelerator="Ctrl++", command=lambda: zoom_in(text, font_size))
    focus_menu.add_command(label="Zoom -", accelerator="Ctrl+-", command=lambda: zoom_out(text, font_size))

    # Menu Formato
    format_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Formato", menu=format_menu)
    format_menu.add_command(label="Negrito", accelerator="Ctrl+B", command=lambda: toggle_bold(text))
    format_menu.add_command(label="Itálico", accelerator="Ctrl+I", command=lambda: toggle_italic(text))
    format_menu.add_command(label="Fonte...", command=lambda: choose_font(text, font_family, font_size))

    # Menu Sobre
    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Sobre", menu=about_menu)
    about_menu.add_command(label="Informações", command=sobre_popup)

    # Binds de shortcuts
    root.bind("<Control-n>", lambda event: novo_arquivo(text))
    root.bind("<Control-o>", lambda event: abrir_arquivo(text))
    root.bind("<Control-s>", lambda event: salvar_arquivo(text))
    root.bind("<Control-Shift-s>", lambda event: salvar_como(text))
    root.bind("<Control-w>", lambda event: fechar_arquivo(text))
    root.bind("<Control-q>", lambda event: root.quit())
    root.bind("<F11>", lambda event: toggle_fullscreen(root))
    root.bind("<Control-plus>", lambda event: zoom_in(text, font_size))
    root.bind("<Control-minus>", lambda event: zoom_out(text, font_size))
    root.bind("<Control-b>", lambda event: toggle_bold(text))
    root.bind("<Control-i>", lambda event: toggle_italic(text))

    root.mainloop()

if __name__ == "__main__":
    main()