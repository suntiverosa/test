// *Establecer conexión WebSocket
const websocket = new WebSocket("ws://44.243.115.79:8000/ws/chat");

// Manejar eventos de WebSocket
websocket.onopen = () => console.log("Conexión WebSocket abierta");
websocket.onmessage = (event) => {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("p");
    messageElement.innerText = event.data;  // Mostrar mensaje recibido
    chatBox.appendChild(messageElement);
};

// Enviar un mensaje al servidor
document.getElementById("sendMessage").addEventListener("click", () => {
    const message = document.getElementById("message").value;
    websocket.send(message);  // Enviar mensaje al servidor
    document.getElementById("message").value = "";  // Limpiar el campo de entrada
});
