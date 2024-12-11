from requests_html import HTMLSession

# Crie uma sessão HTML
session = HTMLSession()

# URL da página da rádio
url = "https://www.radio-ao-vivo.com/antena-1"

# Envie a requisição para carregar a página, incluindo a execução de JavaScript
response = session.get(url)

# Aguarde até que o JavaScript seja executado, caso necessário
response.html.render()

# Agora, tente encontrar o link do stream de áudio
audio_tag = response.html.find("audio", first=True)  # Procura pela tag <audio>
if audio_tag:
    audio_url = audio_tag.attrs.get('src')
    print(f"Stream de áudio encontrado: {audio_url}")
else:
    print("Não foi possível encontrar o stream de áudio.")
