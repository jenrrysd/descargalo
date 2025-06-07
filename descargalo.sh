#!/bina/bash
#
read -p "escribe la ruta o la carpeta que quieres compartir: " ruta
cd $ruta && python3 -m http.server 8080 --bind 0.0.0.0

