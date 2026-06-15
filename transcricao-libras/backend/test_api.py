import json
import urllib.request

data = {
    "texto": "Teste de transcrição pelo terminal",
    "idioma": "pt-BR",
    "duracao_ms": 1500,
    "confianca": 0.95,
    "session_id": "test-session-1234"
}

req = urllib.request.Request(
    "http://localhost:8000/api/transcricoes",
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as response:
        print("POST STATUS:", response.status)
        print("POST RESPONSE:", response.read().decode("utf-8"))
except Exception as e:
    print("POST ERROR:", e)

try:
    with urllib.request.urlopen("http://localhost:8000/api/estatisticas") as response:
        print("GET STATS STATUS:", response.status)
        print("GET STATS RESPONSE:", response.read().decode("utf-8"))
except Exception as e:
    print("GET STATS ERROR:", e)
