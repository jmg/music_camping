cd /home/jmg/DESARROLLO/music_tesseract/;
NETIP=$(/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
python manage.py runserver "$NETIP:8000"