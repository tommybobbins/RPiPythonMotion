RPiPythonMotion
===============

Modifications of brainflakes' sterling work implementing motion in Python
# original script by brainflakes, improved by pageauc, peewee2 and Kesthal
# www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235

Use raspi-config to enable camera support if necessary:
    sudo raspi-config

Install the prerequisites:
    sudo apt-get install python-imaging-tk

Copy the init script into place
    sudo cp pymotion /etc/init.d/pymotion
    sudo cp default_pymotion /etc/default/pymotion

Enable the init script
    insserv pymotion

Copy the picam binary into place:
    sudo cp picam.py /usr/local/bin/

Make the Output directory:
    mkdir /home/pi/MOTION/

