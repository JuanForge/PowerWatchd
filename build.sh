sudo apt install build-essential
sudo apt install python3
sudo apt install python3-venv
sudo apt install python3-gi python3-gi-cairo gir1.2-glib-2.0 gir1.2-gio-2.0 libgirepository1.0-dev

gcc -O3 -Wall -fPIC -shared -o ./libbuzzer_iopl.so ./src/buzzer.c

python3 -m venv --system-site-packages .venv