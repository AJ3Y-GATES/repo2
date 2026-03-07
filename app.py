from flask import Flask, render_template_string
from flask_socketio import SocketIO
import psutil
import threading
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "segredo"

# Força modo threading (mais estável)
socketio = SocketIO(app, async_mode="threading")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitoramento Tempo Real</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
</head>
<body style="font-family:Arial; background:#111; color:white; text-align:center;">

<h1>Dashboard em Tempo Real</h1>

<h2>CPU: <span id="cpu">0</span>%</h2>
<h2>RAM: <span id="ram">0</span>%</h2>
<h2>RAM TOTAL: <span id="ram_total">0</span>GB</h2>
<h2>DISCO : <span id="disk_percent">0</span>%</h2>
<h2>DISCO TOTAL: <span id="disk">0</span>GB</h2>

<script>
    const socket = io();

    socket.on("connect", function() {
        console.log("Conectado ao servidor");
    });

    socket.on("metricas", function(data) {
        document.getElementById("cpu").innerText = data.cpu;
        document.getElementById("ram").innerText = data.ram;
        document.getElementById("ram_total").innerText = data.ram_total;
        document.getElementById("disk_percent").innerText = data.disk_percent;
        document.getElementById("disk").innerText = data.disk;
    });
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

def enviar_metricas():
    while True:
        dados = {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "ram_total": round(psutil.virtual_memory().total / (1024 ** 3), 1),
            "disk_percent": psutil.disk_usage('/').percent,
            "disk": round(psutil.disk_usage('/').total / (1024 ** 3), 0)
        }
        socketio.emit("metricas", dados)
        time.sleep(0.5)

if __name__ == "__main__":
    threading.Thread(target=enviar_metricas, daemon=True).start()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

