RPiPythonMotion
===============

Modifications of brainflakes' sterling work implementing motion in Python
original script by brainflakes, improved by pageauc, peewee2 and Kesthal

http://www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235

Use raspi-config to enable camera support if necessary:

     sudo raspi-config

Install the prerequisites:

    sudo apt-get install python-imaging-tk

Copy the init script into place

    sudo cp pymotion /etc/init.d/pymotion
    sudo cp default_pymotion /etc/default/pymotion

Make the Output directory:

    mkdir /home/pi/MOTION/

Copy the picam binary into place:

    sudo cp picam.py /usr/local/bin/

Enable the init script:

    sudo insserv pymotion
    sudo /etc/init.d/pymotion start

Alternate script:
JBeale and waveform80 have written a very fast implementation which produces B&W images very quickly.
http://www.raspberrypi.org/phpBB3/viewtopic.php?p=470488#p470488
Stop pymotion and install the prereqs:

    sudo /etc/init.d/pymotion stop
    sudo apt-get install python-opencv python-numpy

Install the picamera Pure Python code: 

    cd /home/pi
    git clone "https://github.com/waveform80/picamera"
    cd picamera
    sudo make install

Copy this into place over /usr/local/bin/picam.py:

    cd /home/pi/RPiPythonMotion
    sudo cp purepicam.py /usr/local/bin/picam.py

Restart pymotion:

    sudo /etc/init.d/pymotion start
