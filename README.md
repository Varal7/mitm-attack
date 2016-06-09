#The Hacking Xperience
## A Man-In-The-Middle attack by Victor Quach (Varal7) && Alexis Thual

###Description of our hack :
We chose to implement a man-in-the-middle attack so as to acquire users’ logins and passwords on various websites, assuming that the users we are to hack are students web-browsing from the Ecole polytechnique’s network and use casual settings - the ones prescribed by the Binet Réseau.

###Design of implementation :
We first chose to set a wifi router so as to actually be able to be between the user and the page he or she wants to fetch. This router acts as DHCP server and mainly does one thing: it uses the IP address of a DNS server which we control, in a way that makes it transparent for the user.

This DNS server most of the time asks the usual DNS server of Ecole polytechnique’s network for answers. However, on some « useful » adresses, it gives the IP of our Raspberry Pi. This allows to use this pirate DNS server so as to redirect the proxy server - which the user casually refers to as « kuzh.polytechnique.fr » in his or her settings - to our own proxy server.

This proxy server - implemented by SQUID - mainly forwards all requests to the real proxy server (kuzh), but modifies the HTML pages on-the-go. To do so, it acts as a ICAP client for our own ICAP server.

This ICAP server allows to add portions of Javascript code to downloaded pages so as to change the behavior of the page : when the submit button of a specific HTML form is clicked, all data is sent through a simple Javascript POST request to a PHP page which we own and which stores into a text file the input written by the hacked user. This request does not interfere with the submitting of the form, which eventually leads the user to being connected to his or her account without noticing our hacking process.

###Files used are the following :

####On the router:
Config file for the DHCP server: ```/etc/config/dhcp```

Config file for DNS resolution: ```/etc/hosts```

####On the Raspberry Pi:
DNS server: ```/srv/dns.py```

ICAP server: ```/srv/respmod_icap.py```

SQUID config file: ```/etc/squid3/squid.conf```

Init.d files to use these servers as services: ```/etc/init.d/dns.sh``` and ```icap.sh```

####On our VPS:
PHP file for treating POST requests: ```traitement.php```

