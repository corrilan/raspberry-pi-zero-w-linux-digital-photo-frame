#!/bin/bash
. /home/pi/.bashrc

if ! screen -ls | grep -q "reverse"
    then
	    /usr/bin/screen -S reverse-ssh-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 11113:localhost:22 user@frame.yourdomain.com
	    /usr/bin/screen -S reverse-vnc-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 11112:localhost:5900 user@frame.yourdomain.com
	    /usr/bin/screen -S reverse-web-enframed -c /etc/.reverse-ssh-screen -d -m autossh -R 11111:localhost:80 -N -p 2222 user@frame.yourdomain.com
	    /usr/bin/screen -S x11vnc -c /etc/.reverse-ssh-screen -d -m /usr/bin/sudo -u pi /usr/bin/x11vnc -xkb -noxrecord -noxfixes -noxdamage -forever
    else echo "Screen Currently Running"
fi
