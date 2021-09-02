#!/bin/bash
. /home/pi/.bashrc
/usr/bin/screen -S reverse-ssh-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 13333:localhost:22 frame@frame.enframed.co.uk
/usr/bin/screen -S reverse-vnc-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 13332:localhost:5900 frame@frame.enframed.co.uk
/usr/bin/screen -S reverse-web-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 13331:localhost:80 -N -p 2222 frame@frame.enframed.co.uk
/usr/bin/screen -S x11vnc -c /etc/.reverse-ssh-screen -d -m /usr/bin/sudo -u pi /usr/bin/x11vnc -xkb -noxrecord -noxfixes -noxdamage -forever


