import camera
import socket
import network
import machine
import time

# WiFi Access Point Settings
SSID = 'ESP32-CAM'     # Your ESP32 will create this WiFi network
PASSWORD = '12345678'   # Password for the WiFi network

# Initialize the camera
camera.init(0)
camera.framesize(camera.FRAME_VGA)  # 640x480
camera.quality(10)

# Create Access Point
def create_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)
    while not ap.active():
        pass
    print('Access Point created')
    print('Network config:', ap.ifconfig())
    return ap.ifconfig()[0]

# HTML for the webpage
def webpage():
    html = """
    <html>
        <head>
            <title>ESP32-CAM Live Stream</title>
            <style>
                body {
                    text-align: center;
                    font-family: Arial;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <h1>ESP32-CAM Live Stream</h1>
            <img src="/stream" id="stream">
            <script>
                var img = document.getElementById("stream");
                function updateImage() {
                    img.src = "/stream?" + new Date().getTime();
                }
                setInterval(updateImage, 200);
            </script>
        </body>
    </html>
    """
    return html

# Start web server
def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)
        
        if 'GET /stream' in request:
            try:
                frame = camera.capture()
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: image/jpeg\r\n')
                conn.send('Content-Length: ' + str(len(frame)) + '\r\n')
                conn.send('\r\n')
                conn.send(frame)
            except:
                pass
        else:
            conn.send('HTTP/1.1 200 OK\r\n')
            conn.send('Content-Type: text/html\r\n')
            conn.send('\r\n')
            conn.send(webpage())
        
        conn.close()

# Main program
try:
    ip = create_ap()
    print(f'Web server started at http://{ip}')
    start_server()
except:
    machine.reset()