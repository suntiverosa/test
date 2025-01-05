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

    # Realizar la solicitud a la API de OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You will be provided with a sentence in any language and your task is to translate it into language indicated"},
            {
                "role": "user",
                "content": texto_usuario
            }
        ]
    )

    # Obtener la respuesta generada por la API
    response_content = completion.choices[0].message.content
    
# Verifica si el objeto tiene un método para convertirlo a un diccionario
    if hasattr(completion, "to_dict"):
        completion_dict = completion.to_dict()
    else:
        completion_dict = completion

    # Extrae la información de los tokens
    prompt_tokens = completion_dict["usage"]["prompt_tokens"]
    completion_tokens = completion_dict["usage"]["completion_tokens"]
    total_tokens = completion_dict["usage"]["total_tokens"]

    #Cálculo de costo total del token usado (Prompt+Completion)
    costo_input_token = 0.00000015
    costo_output_token = 0.000000075
    costo_chat = prompt_tokens * costo_input_token + completion_tokens * costo_output_token
    print(f"Costo Total del Token: ${costo_chat:.10f}")

    # Regarga
    recarga = 1

    # Saldo
    saldo = recarga - costo_chat

    print(f"Saldo: ${saldo:.10f}")



    print(f"Prompt Tokens: {prompt_tokens}")
    print(f"Completion Tokens: {completion_tokens}")
    print(f"Total Tokens: {total_tokens}")


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
