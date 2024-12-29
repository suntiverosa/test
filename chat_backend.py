from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

import os
from openai import OpenAI
from dotenv import load_dotenv

def openai_translate(texto_usuario):
    # Cargar la clave API desde el archivo .env
    load_dotenv()

    # Solicitar al usuario que ingrese una palabra o frase en español
    # texto_usuario = input("Introduce una palabra o frase en español para traducir al chino: ")

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You will be provided with a sentence in spanish, and your task is to translate it into Chinese. If the sentence provide is not spanish send a message ESCRIBA EN ESPAÑOL"},
            {
                "role": "user",
                "content": texto_usuario
            }
        ]
    )

    #print(completion.choices[0].message)

    response_content = completion.choices[0].message.content

    return(response_content.strip())

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

#Se agrego porque la pagina web no cargaba 28/11/2024
@app.get("/")
def read_root():
    return {"message": "Welcome to the c3po ML-Chat"}
#Fin de la agregación

# Almacenar clientes conectados
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Recibir mensaje del cliente

            #Translate
            data_ai = openai_translate(data)

            await manager.broadcast(data)  # Enviar el mensaje a todos los clientes conectados
            await manager.broadcast(data_ai)  # Enviar el mensaje a todos los clientes conectados
    except WebSocketDisconnect:
        manager.disconnect(websocket)  # Eliminar cliente al desconectar
