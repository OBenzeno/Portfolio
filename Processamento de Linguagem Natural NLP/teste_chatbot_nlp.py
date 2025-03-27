import nltk
from nltk.chat.util import Chat, reflections
from textblob import TextBlob
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Baixar recursos do NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Definir padrões de diálogo
pares = [
    [r'oi|olá|e aí', ['Olá!', 'Oi! Como posso ajudar?', 'E aí!']],
    [r'como (você|vc) está?', ['Estou bem, obrigado! E você?', 'Tudo ótimo!']],
    [r'quem (é|e) (você|vc)\?', ['Sou um chatbot criado para ajudar!', 'Me chame de Pyhelper!']],
    [r'qual (é|e) seu objetivo\?', ['Meu objetivo é conversar e ajudar com dúvidas simples!']],
    [r'(.*) (idade|anos)', ['Sou um programa, não tenho idade!']],
    [r'(.*) (nome|chama)', ['Meu nome é ChatPy!']],
    [r'(.*) ajuda(.*)', ['Posso tentar ajudar! O que você precisa?']],
    [r'(.*) (obrigado|valeu|agradeço)', ['De nada!', 'Por nada!', 'Disponha!']],
    [r'sair|tchau|até mais', ['Até logo!', 'Tchau! Volte sempre!']],
    [r'(.*)', ['Não entendi bem. Pode reformular?', 'Interessante... Conte mais!']]
]

# Criar o chatbot
chatbot = Chat(pares, reflections)

# Função para análise de sentimento
def analisar_sentimento(texto):
    # Dicionário de palavras em português
    palavras_positivas = {'adoro', 'amo', 'incrível', 'excelente', 'maravilhoso'}
    palavras_negativas = {'odeio', 'péssimo', 'horrível', 'ruim'}
    
    texto = texto.lower()
    positivas = sum(p in texto for p in palavras_positivas)
    negativas = sum(p in texto for p in palavras_negativas)
    
    if positivas > negativas:
        return "Parece que você está feliz! 😊"
    elif negativas > positivas:
        return "Parece que você está chateado. 😔"
    else:
        return "Não consigo detectar um sentimento claro. 🤔"

# Interface gráfica
class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("ChatBot - Diálogo Homem-Máquina")
        master.geometry("500x600")
        
        # Configurar cores
        bg_color = "#f0f0f0"
        btn_color = "#4CAF50"
        
        master.configure(bg=bg_color)
        
        # Área do chat
        self.chat_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=20)
        self.chat_area.configure(state='disabled')
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        # Entrada de mensagem
        self.user_input = tk.Entry(master, width=40)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)
        self.user_input.bind("<Return>", self.send_message)
        
        # Botão enviar
        self.send_button = tk.Button(master, text="Enviar", command=self.send_message, bg=btn_color, fg="white")
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Botão análise de sentimento
        self.sentiment_button = tk.Button(master, text="Análise de Sentimento", command=self.analyze_sentiment, bg="#2196F3", fg="white")
        self.sentiment_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Mensagem inicial
        self.display_message("Pyhelper", "Olá! Eu sou o Pyhelper. Como posso te ajudar hoje?")
    
    def display_message(self, sender, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)
    
    def send_message(self, event=None):
        user_message = self.user_input.get()
        if user_message.lower() in ['sair', 'tchau', 'até mais']:
            self.display_message("Você", user_message)
            self.display_message("Pyhelper", "Até logo! Foi bom conversar com você!")
            self.master.after(2000, self.master.destroy)
            return
        
        if user_message.strip() != "":
            self.display_message("Você", user_message)
            response = chatbot.respond(user_message)
            self.display_message("Pyhelper", response)
            self.user_input.delete(0, tk.END)
    
    def analyze_sentiment(self):
        user_message = self.user_input.get()
        if user_message.strip() != "":
            sentiment = analisar_sentimento(user_message)
            self.display_message("Análise", sentiment)
        else:
            messagebox.showwarning("Aviso", "Digite uma mensagem antes de analisar o sentimento.")

# Iniciar o chat
if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatGUI(root)
    root.mainloop()