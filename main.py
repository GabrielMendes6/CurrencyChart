import tkinter as tk
from tkinter import ttk
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import StringIO
import mplcursors

# Função para buscar os dados das criptomoedas
def fetch_crypto_data(crypto):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=30&interval=daily'
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Função para buscar os dados das moedas tradicionais
def fetch_currency_data(from_symbol, to_symbol):
    api_key = 'sua_api_key_aqui'  # Coloque sua chave de API aqui
    function = 'FX_DAILY'
    url = f'https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&apikey={api_key}&datatype=csv'
    response = requests.get(url)
    data = pd.read_csv(StringIO(response.text))
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.rename(columns={'close': 'price'}, inplace=True)
    return data[['timestamp', 'price']]

# Função para plotar os dados
def plot_currency_data(currency, name, is_crypto):
    if is_crypto:
        data = fetch_crypto_data(currency)
    else:
        to_symbol = 'USD'
        if currency == 'USD':
            to_symbol = 'BRL'
        elif currency == 'EUR':
            to_symbol = 'BRL'
        data = fetch_currency_data(currency, to_symbol)
        
    # Criar uma nova janela do Tkinter para o gráfico
    graph_window = tk.Toplevel()
    graph_window.title(f'Histórico de {name}')
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['timestamp'], data['price'])
    ax.set_title(f'Histórico de {name} (últimos 30 dias)')
    ax.set_xlabel('Data')
    ax.set_ylabel('Preço de Fechamento')
    ax.grid(True)
    
    # Adicionar interatividade
    cursor = mplcursors.cursor(ax, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(f'{sel.target[1]:.2f}')
        sel.annotation.get_bbox_patch().set(fc="yellow", alpha=0.9)
        sel.annotation.set_bbox(dict(facecolor='yellow', edgecolor='black', boxstyle='round,pad=0.5'))
        sel.annotation.set_fontsize(12)
        sel.annotation.xy = (sel.target[0], sel.target[1])
        sel.annotation.set_position((0, 20))  # Ajuste a posição da anotação
    
    # Incorporar o gráfico na janela do Tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Função para fechar a janela quando a janela principal for fechada
    graph_window.protocol("WM_DELETE_WINDOW", graph_window.destroy)
    
    # Exibir a janela
    graph_window.mainloop()

# Função para pegar o valor do dropdown e plotar
def on_select(event):
    currency = currency_var.get()
    if currency == 'BTC':
        plot_currency_data('bitcoin', 'Bitcoin', True)
    elif currency == 'ETH':
        plot_currency_data('ethereum', 'Ethereum', True)
    elif currency == 'USD':
        plot_currency_data('USD', 'Dólar', False)
    elif currency == 'BRL':
        plot_currency_data('BRL', 'Real', False)
    elif currency == 'EUR':
        plot_currency_data('EUR', 'Euro', False)

# Criação da interface do usuário
root = tk.Tk()
root.title("Histórico de Moeda")

# Dropdown para selecionar a moeda
currency_var = tk.StringVar()
currency_dropdown = ttk.Combobox(root, textvariable=currency_var)
currency_dropdown['values'] = ('BTC', 'ETH', 'USD', 'BRL', 'EUR')
currency_dropdown.grid(column=0, row=0, padx=10, pady=10)
currency_dropdown.bind('<<ComboboxSelected>>', on_select)

# Iniciar a interface
root.mainloop()
