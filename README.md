# raspberry-pi-zero-w-linux-digital-photo-frame

Python based digital photo frame aimed at running on a Linux Raspberry Pi Zero W.

<h1>Why?</h1>

Over the years I have accumulated thousands of digital photographs which get saved, stored, organised and backed up (always do your backups!).  I realised that very rarely were these photographs being viewed, so I decided that a digital photo frame was required so myself and my wife would get to see random photographs fro our collection, all day, every day.

Not keen on buying a small digital photo frame with limited features (I don't want to have to squint to see the photos!), I decided instead to build my own using an old laptop screen I happened to have lying around.  I wanted to build something where the feature set could easily be expanded over time. With the amount of e-waste now going to landfill, I thought it would also be nice to make use of laptop screens which would otherwise be disposed of with the rest of a broken laptop.

<h1>What features does the current code offer?</h1>

<ul>
<li>Photos can be displayed either full screen or in polaroid mode (see the photos/videos to get a feel for this).</li>
<li>Display automatically rotates the photos depending on how frame is oriented.</li>
<li>You can choose to display of 1, 2 or 3 polaroids on screen before they start to 'stack' up.</li>
<li>You can choose how long a photograph is displayed for before moving to the next.</li>
<li>The frames screen automatically turns of when a person has not been detected nearby within a customisable timeframe.</li>
<li>To aid initial setup, the frame acts as a wifi access point in order to connect it to your own wifi.</li>
<li>Photographs may be uploaded directly to the frame from any device with a web browser.</li>
<li>Integration into other open source projects such as the <a href="https://www.asterisk.org" target="_blank">Digium Asterisk<a> telecommunications system - when someone calls my landline, their details and a photograph appear on the frame.</li>
</ul>

<h1>Videos</h1>

Check out our YouTube channel to see some videos of the digital photo frame in action:

COMING SOON

<h1>Parts list and costs</h1>

<ul>
<li>1x laptop screen out of an old broken laptop  - £0</li>
<li>1x laptop screen controller for your particular laptop screen - £</li>
<li>1x Custom made wooden frame to make it all look nice - £</li>
<li>1x Raspberry Pi Zero W - £</li>
<li>1x 16GB Micro SD card with SD card adapter - £</li>
<li>1x 10A 5v power supply - £</li>
<li>1x RCWL-0516 microwave radar motion sensor to detect presence of a person to turn on the frame - £</li>
<li>2x tilt switch to detect orientation of the frame - £</li>
<li>1x voltage regulator - £</li>
<li>1x ?mm tactile switch to act as the turn off button - £</li>
<li>1x ?mm tactile switch to act as the factory reset button - £</li>
<li>1x ? ohm resistor - £</li>
<li>1x male power connector - £</li>
<li>1x female power connector - £</li>
<li>1x 3 pin male/female JST connector to connect the RCWL-0516 to the voltage regulator and Raspberry Pi Zero W - £</li>
<li>1x 6 pin male JST connector to provide power from the screen controller to the Raspberry Pi Zero W- £</li>
<li>1x ?cm HDMI lead ? - £</li>
<li>1x gromet</li>
<li>Assorted lengths of wire ("Good news everyone") - £</li>
</ul>

<h1>Other key software projects incorporated into the design</h1>

<ul>
<li><a href="https://www.raspberrypi.org/software/operating-systems" target="_blank">https://www.raspberrypi.org/software/operating-systems</a></li>
<li><a href="https://savannah.gnu.org/git/?group=screen" target="_blank">https://savannah.gnu.org/git/?group=screen</a></li>
<li><a href="https://github.com/CyberShadow/autossh" target="_blank">https://github.com/CyberShadow/autossh</a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="https://gitlab.com/DarkElvenAngel/initramfs-splash" target="_blank">https://gitlab.com/DarkElvenAngel/initramfs-splash</a></li>
<li><a href="" target="_blank"></a></li>
<li><a href="https://github.com/jasbur/RaspiWiFi" target="_blank">https://github.com/jasbur/RaspiWiFi</a></li>
</ul>

<h1>Key server software packages used externally to provide various features and functions</h1>

<ul>
<li><a href="https://www.asterisk.org" target="_blank">https://www.asterisk.org</a></li>
<li><a href="" target="_blank"></a></li>
</ul>
