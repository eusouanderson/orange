import tkinter as tk
from PIL import ImageTk, Image


def girar_imagem():
    # Girar a imagem em 90 graus
    imagem_rotacionada = imagem_original.rotate(90)
    imagem_tk = ImageTk.PhotoImage(imagem_rotacionada)
    label_imagem.configure(image=imagem_tk)
    label_imagem.image = imagem_tk
    # Chamar a função novamente após 100ms para criar animação
    root.after(180, girar_imagem)


root = tk.Tk()

# Carregar a imagem usando o módulo PIL
imagem_original = Image.open("./src/Screenshots/orange.png")

# Criar um objeto ImageTk para exibir a imagem no Tkinter
imagem_tk = ImageTk.PhotoImage(imagem_original)

# Criar um widget Label para exibir a imagem
label_imagem = tk.Label(root, image=imagem_tk)
label_imagem.pack()

# Chamar a função para iniciar a animação de rotação
Button = tk.Button(root, command=girar_imagem)
Button.pack()

root.mainloop()
