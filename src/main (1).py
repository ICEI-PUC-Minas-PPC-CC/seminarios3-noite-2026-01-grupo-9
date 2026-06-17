# =========================
# TRADUTOR LIBRAS
# =========================

import pyaudiowpatch as pyaudio
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk

# Corrige PyAudio
sr.Microphone.get_pyaudio = lambda self: pyaudio

# Reconhecimento
reconhecedor = sr.Recognizer()

# =========================
# JANELA
# =========================

janela = tk.Tk()
janela.title("Tradutor Libras")
janela.geometry("900x600")
janela.configure(bg="white")

# =========================
# TEXTO
# =========================

texto = tk.Label(
    janela,
    text="Fale alguma coisa...",
    font=("Arial", 28),
    bg="white",
    fg="black",
    wraplength=800
)

texto.pack(pady=30)

# =========================
# IMAGEM
# =========================

imagem = Image.open("oi.png")

imagem = imagem.resize((300, 300))

foto = ImageTk.PhotoImage(imagem)

imagem_label = tk.Label(
    janela,
    image=foto,
    bg="white"
)

imagem_label.pack(pady=20)

# =========================
# FUNÇÃO OUVIR
# =========================

def ouvir():

    with sr.Microphone() as source:

        reconhecedor.adjust_for_ambient_noise(
            source,
            duration=1
        )

        texto.config(
            text="Pode falar..."
        )

        janela.update()

        while True:

            try:

                audio = reconhecedor.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=6
                )

                frase = reconhecedor.recognize_google(
                    audio,
                    language="pt-BR"
                )

                texto.config(
                    text=frase
                )

                janela.update()

            except sr.UnknownValueError:

                texto.config(
                    text="Não entendi..."
                )

                janela.update()

            except sr.WaitTimeoutError:

                texto.config(
                    text="Esperando você falar..."
                )

                janela.update()

            except Exception as erro:

                texto.config(
                    text=f"Erro: {erro}"
                )

                janela.update()

# =========================
# INICIAR
# =========================

janela.after(100, ouvir)

# =========================
# MAIN LOOP
# =========================

janela.mainloop()