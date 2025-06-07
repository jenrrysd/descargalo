import http.server, socket
import socketserver
import os
import sys
from urllib.parse import unquote, quote

##################
def get_local_ip():
    try:
        # Crear un socket temporal para obtener la IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conectar a un servidor externo
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback a localhost
##################

class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):

    def list_directory(self, path):
        try:
            # Listar contenido del directorio
            files = os.listdir(path)
            files.sort(key=lambda a: a.lower())

            # Obtener la IP del servidor, linea de abajo agregado
            # server_ip = getattr(self.server, 'local_ip', '0.0.0.0')

            # Generar HTML completo
            html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Directorio: {self.path}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 2;
            margin: 1em auto;
            max-width: 800px;
            padding: 0 20px;
            background-color: rgb(144, 226, 148);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        a {{
            color: #1c1586;
            text-decoration: none;
            display: block;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        a:hover {{
            background-color: #f5f5f5;
            text-decoration: underline;
        }}
        .dir::before {{
            content: "📁 ";
        }}
        .file::before {{
            content: "📄 ";
        }}

        
        .download-btn {{
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.8em;
        }}
        .download-btn:hover {{
            background-color: #45a049;
        }}
        .file-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}


    </style>
</head>
<body>
    <h1>Directorio: {self.path}</h1>
    <ul>"""

            # Enlace al directorio padre (si no es raíz y no es la carpeta compartida)
            # Aseguramos que el enlace ".." no lleve fuera de la carpeta compartida
            if self.path != '/':
                # Obtener la ruta del directorio padre en el contexto del servidor
                parent_path = '/'.join(self.path.split('/')[:-1])
                if parent_path == '': # Si estamos en /algo, el padre es /
                    parent_path = '/'
                html += f'<li><a href="{quote(parent_path)}" class="dir">[Directorio padre]</a></li>'


            # Listar cada elemento
            for name in files:
                fullpath = os.path.join(path, name)
                displayname = name
                # Codificar el nombre del archivo o directorio para la URL
                # Pero la URL que se construye debe ser relativa a la ruta actual del navegador
                # Por ejemplo, si estoy en /fotos y name es 'vacaciones', el link debe ser 'vacaciones' (no '/fotos/vacaciones')
                quoted_name = quote(name)

                if os.path.isdir(fullpath):
                    html += f'<li><a href="{quoted_name}" class="dir">{displayname}/</a></li>'

                else:
                    html += f'''
                    <li>
                        <div class="file-container">
                            <a href="{quoted_name}" class="file" target="_blank">{displayname}</a>
                            <a href="{quoted_name}" class="download-btn" download>Descargar</a>
                        </div>
                    </li>'''

            html += """</ul>
    </body>
    </html>"""


            # --- CAMBIOS AQUÍ ---
            # 1. Enviar la respuesta y cabeceras
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode('utf-8')))) # Asegurar que Content-Length es del HTML codificado
            self.end_headers()

            # 2. Escribir el contenido HTML directamente en self.wfile
            self.wfile.write(html.encode('utf-8'))
            return None #<-- linea agregada
            # --- FIN CAMBIOS ---

            return None # list_directory no debe devolver un valor en esta implementación
        except Exception as e:
            self.send_error(500, f"Error al listar directorio: {str(e)}")
            return None

    def translate_path(self, path):
        # Manejar correctamente caracteres especiales en rutas
        # La decodificación se hace aquí, antes de que os.path.join lo use.
        path = http.server.SimpleHTTPRequestHandler.translate_path(self, path)
        return path # translate_path ya decodifica con unquote internamente en su implementación base

def main():
    try:
        folder_path = input("Ingresa la ruta de la carpeta que quieres compartir: ").strip()

        if not os.path.isdir(folder_path):
            print(f"\nError: La ruta '{folder_path}' no existe o no es una carpeta válida.")
            sys.exit(1)

        # Asegúrate de usar una ruta absoluta para el cambio de directorio
        absolute_folder_path = os.path.abspath(folder_path)
        os.chdir(absolute_folder_path)

        PORT = 8090
        HOST = '0.0.0.0'
        LOCAL_IP = get_local_ip()  # Obtener la IP real, agregado

        print(f"\n✅ Servidor listo en:")
        print(f"   • Local: http://127.0.0.1:{PORT}")
        print(f"   • Host local: http://{LOCAL_IP}:{PORT}")  # Mostrar la IP real, linea agregada
        # Obtener la IP local de forma más robusta
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80)) # Conecta a un servidor externo (no envía datos)
        # local_ip = s.getsockname()[0]
        # s.close()

        # print(f"   • Red: http://{HOST}:{PORT}")
        print(f"\n📂 Compartiendo: {os.getcwd()}")
        print("\n🛑 Presiona Ctrl+C para detener el servidor\n")
        

        with socketserver.TCPServer((HOST, PORT), CustomRequestHandler) as httpd:
            #httpd.local_ip = LOCAL_IP  # Guardar la IP en el servidor, linea agregado
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServidor detenido correctamente.")
                sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()