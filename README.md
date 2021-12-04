# raspberry-pi-zero-w-linux-digital-photo-frame

Python based digital photo frame aimed at running on a Linux Raspberry Pi Zero W.

<h1>Why?</h1>

Over the years I have accumulated around 12000 digital photographs (40GB worth) which get saved, stored, organised and backed up (always do your backups!).  I realised that very rarely were these photographs being viewed, so I decided that a digital photo frame was required so myself and my wife would get to see random photographs from our collection, all day, every day.  I also wanted to make a frame for our parents so they could enjoy the latest photographs of their new grandchild.

Not keen on buying a small digital photo frame with limited features (I don't want to have to squint to see the photos!), I decided instead to build my own using an old laptop screen I happened to have lying around.  I wanted to build something where the feature set could easily be expanded over time. With the amount of e-waste now going to landfill, I thought it would also be nice to make use of laptop screens which would otherwise be disposed of with the rest of a broken laptop.

<h1>Security</h1>

With everything we hear online about the insecurity of IoT (Internet of Things) devices, whatever I implemented, I wanted to make it as secure and safe for the owner as possible.  Unfortunately most manufacturers seem to throw security into the mix as an afterthought, if at all.  I have therefore taken the following precautions from the outset:

<ul>
<li>SSH (Secure Shell) with pre shared keys used for all communications between photo frame and server infrastructure.</li>
<li>Valid SSL certificates in use for all externally accessible web services.</li>
<li>Web services accessible only on the frames local network are not SSL encrypted due to decreased risk and also that I was unable to find a way to obtain autorenewing <a href="https://www.letsencrypt.org" target="_blank">Let's Encrypt</a> certificates for the frames local IP address.  It would also entail non techy users having to open up ports on their firewall.</li>
<li>Very strong passwords used for all system usernames/databases etc.  By strong, I mean 64 characters of random gibberish.</li>
<li>I have used a weaker password for the sharing feature as non techy family members will need to type it in - perhaps this can be adapted to use 2FA in the future.</li>
</ul>

I urge you to think about security as a priority with your own implementation of the photo frame.

<h1>What features does the current code offer?</h1>

<ul>
<li>Photographs can be displayed either full screen or in polaroid mode (see the photographs/videos to get a feel for this).</li>
<li>Display automatically rotates the photographs depending on how frame is oriented.</li>
<li>You can choose to display of 1, 2 or 3 polaroids on screen before they start to 'stack' up.</li>
<li>You can choose how long a photograph is displayed for before moving to the next.</li>
<li>The screen automatically turns off when a person has not been detected nearby within a customisable timeframe.</li>
<li>To aid initial setup, the frame acts as a wifi access point in order to connect it to your own wifi.</li>
<li>Photographs may be uploaded directly to the frame from any device with a web browser.</li>
<li>Integration into other open source projects such as the <a href="https://www.asterisk.org" target="_blank">Digium Asterisk<a> telecommunications system - when someone calls my landline, their details and a photograph appear on the frame.</li>
</ul>

<h1>Videos</h1>

Check out our YouTube channel to see some videos of the digital photo frame in action:

COMING SOON

<h1>Parts list and costs including delivery</h1>

<ul>
<li>1x laptop screen out of an old broken laptop  - £0.00</li>
<li>1x laptop screen controller for your particular laptop screen - £20.75</li>
<li>1x Custom made wooden frame to make it all look nice - £20.00</li>
<li>1x Raspberry Pi Zero W with pre-soldered header - £16.27</li>
<li>1x SanDisk 16GB Micro SD card with SD card adapter - £5.93</li>
<li>1x 10A 5v power supply - £13.84</li>
<li>1x RCWL-0516 microwave radar motion sensor to detect presence of a person to turn on the frame - £3.00</li>
<li>2x tilt switch to detect orientation of the frame - £1.33 each</li>
<li>1x XL6009 Step Up Boost Power Supply DC-DC Adjustable Converter LM2577 voltage regulator - £1.10</li>
<li>1x 25mm tactile switch to act as the turn off button - £</li>
<li>1x 18mm tactile switch to act as the factory reset button - £</li>
<li>1x ? ohm resistor - £</li>
<li>1x Micro USB 5 Pin Male Plug Power Socket Connector with plastic cover - £0.39</li>
<li>1x 5 pin male/female JST connector to connect the RCWL-0516 to the voltage regulator and Raspberry Pi Zero W - £1.83</li>
<li>2x 6 pin male JST connector to provide power from the screen controller to the Raspberry Pi Zero W - £1.88 each</li>
<li>1x 30cm HDMI to Mini HDMI Cable Male to Male - £5.75</li>
<li>1x rubber grommet - £0.05</li>
<li>Assorted lengths of wire ("Good news everyone") - £</li>
</ul>

<b>Total cost of parts: £</b>
  
<h1>Other key software projects incorporated into the design</h1>

<ul>
<li><a href="https://www.raspberrypi.org/software/operating-systems" target="_blank">https://www.raspberrypi.org/software/operating-systems</a></li>
<li><a href="https://savannah.gnu.org/git/?group=screen" target="_blank">https://savannah.gnu.org/git/?group=screen</a></li>
<li><a href="https://www.github.com/CyberShadow/autossh" target="_blank">https://github.com/CyberShadow/autossh</a></li>
<li><a href="https://www.gitlab.com/DarkElvenAngel/initramfs-splash" target="_blank">https://gitlab.com/DarkElvenAngel/initramfs-splash</a></li>
<li><a href="https://www.github.com/jasbur/RaspiWiFi" target="_blank">https://github.com/jasbur/RaspiWiFi</a></li>
<li><a href="" target="_blank"></a></li>
</ul>

<h1>Key server software packages used externally to provide various features and functions</h1>

As well as the core digital photo frame, I have also implemented various server side technologies in order to provide supporting roles to the frames.  For example:

<ul>
<li>In sending frames to parents, friends and relatives, I wanted a way to allow easy remote access to provide support in the case of problems.</li>
<li>I wanted to provide a central cloud based photo storage solution where people can upload their photos instead of storing on local frame storage.</li>
<li>I wanted the owner to be able to provide browser access to both the frames local and remote cloud storage to whomever they choose.</li>
</ul> 

The software projects used to implement these functions are as follows:

<ul>
<li><a href="https://www.ubuntu.com/server" target="_blank">Ubuntu Linux Server</a> - The core server operating system upon which all of the server side software runs.</li>
<li><a href="https://httpd.apache.org" target="_blank">Apache web server</a> - Used to host <a href="https://www.nextcloud.com" target="_blank">Nextcloud</a> as well as provide the means to access the local frame file storage by acting as proxy.</li>
<li><a href="https://www.nextcloud.com" target="_blank">Nextcloud</a> - A web based file storage system which can be self hosted.  This is installed on the server infrastructure to provide the cloud based photo storage.  It is also installed locally on the photo frame to provide the management for local storage.</li>
<li><a href="https://www.letsencrypt.org" target="_blank">Let's Encrypt</a> - A free SSL certificate authority.  SSL certificates to provide secure communication for the <a href="https://www.nextcloud.com" target="_blank">Nextcloud</a> instances were obtained here.</li>
<li><a href="https://www.openssh.com" target="_blank">OpenSSH</a> - Used to provide secure reverse connections between the photo frame and <a href="https://httpd.apache.org" target="_blank">Apache web server</a>.</li>
<li><a href="https://www.asterisk.org" target="_blank">Digium Asterisk</a> - A telecommunications PBX (Private Branch Exchange) system.  I use this in my home to provide telephone services.  I linked it to the photo frame so that the frame now displays caller details and a photograph of the caller. I consider this fun :-p</li>
<li><a href="" target="_blank"></a></li>
</ul>
