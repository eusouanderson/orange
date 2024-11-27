import os
import json
from functools import lru_cache
from pathlib import Path

# Determinar o diretório correto para salvar configurações do usuário
def get_config_dir():
    if os.name == 'nt':  # Verifica se é Windows
        return Path(os.getenv('APPDATA')) / 'MeuApp'
    else:  # Linux e outros sistemas UNIX-like
        return Path.home() / '.config' / 'MeuApp'

# Criar o diretório caso não exista
config_dir = get_config_dir()
config_dir.mkdir(parents=True, exist_ok=True)

# Caminho completo para o arquivo de configuração
config_file = config_dir / 'config.json'

# Função para salvar as configurações do usuário
@lru_cache(maxsize=None)
def save_settings(background_color, font_size, button_color):
    settings = {
        'background_color': background_color,
        'font_size': font_size,
        'button_color': button_color
    }
    try:
        with open(config_file, 'w') as f:
            json.dump(settings, f)
        print(f"Configurações salvas em {config_file}")
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

# Função para carregar as configurações salvas
@lru_cache(maxsize=None)
def load_settings():
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        print("Nenhuma configuração encontrada.")
        return None
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return None


