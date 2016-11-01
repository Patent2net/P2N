     _____      _             _     ___    _   _      _           _____   ___    _   _ 
    |  __ \    | |           | |   |__ \  | \ | |    | |      /  |  __ \ |__ \  | \ | | \
    | |__) |_ _| |_ ___ _ __ | |_     ) | |  \| | ___| |_    /   | |__) |   ) | |  \| |  \
    |  ___/ _` | __/ _ \ '_ \| __|   / /  | . ` |/ _ \ __|   |   |  ___/   / /  | . ` |   |
    | |  | (_| | ||  __/ | | | |_   / /_  | |\  |  __/ |_     \  | |      / /_  | |\  |  /
    |_|   \__,_|\__\___|_| |_|\__| |____| |_| \_|\___|\__|     \ |_|     |____| |_| \_| /       

About
-----

Patent2Net is elaborated and maintained (on a free base) by a small international team of professors and researchers.  
Patent2Net is a "free" package, dedicated to :

* Augment the use of patent information in academic, nano and small firms, developing countries (all those without pay mode access)
* learn, study and practice how to collect, treat and communicate "textual bibliographic information", and automation process
* provide statistical analysis and representations of a set of patents.

Patent2Net is an "open source" package and contributions are welcome.  
Patent2Net is available "as it is".  
First step : Train how to search patent information using interface
-------------------------------------------------------------------

Test your queries at EPO with [Advanced Search](http://worldwide.espacenet.com/advancedSearch?locale=en_EP "Advanced Search"). Practice and use the available help :
http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=index
more especially :

* [Full-text search](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=&lt;fulltext&gt;&lt;/fulltext&gt;)

* [Boolean operators](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=booleans)

* [Truncation](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=truncation)

* [Smart search - field identifiers](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=fieldidentifier)

* [Limitations](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=limitations)

* [Date formats and Ranges](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=dateformats)

* [Kind Codes](http://worldwide.espacenet.com/help?locale=en_EP&method=handleHelpTopic&topic=kindcodes)

* [Respect the Fair use Charter for the EPO's online patent information products](http://www.epo.org/searching/free/fair-use.html)

Install Patent2Net package on Windows
-------------------------------------

To run as python script need to install python and some libraries (see InstallP2NLinux.txt):

* Install python 2.7 x86  from https://www.python.org/
* Update the "path" to python My Computer > Properties > Advanced System Settings > Environment Variables > Reboot
* Install pip http://www.pip-installer.org/en/latest/installing.html
* Install requests library : in "C:\Python27\Scripts" open a command windows and run "pip install requests"
* Install networkx library : finding the good way to install in http://networkx.github.io/documentation/latest/install.html
* Install epo-ops client from gsong on github : https://github.com/55minutes/python-epo-ops-client

Download Patent2Net from https://github.com/Patent2net/Patent2Net unpack where you want on your disk
Use the current version as above

setup.py is provided also to compile binaries for your windows operating system. Use it with the command python setup.py py2exe to produce binaries in the dist directory.

To run as a an exe file (windows) : need to install the "full package", updating can be done only copying the "Patent2Net" files. Operate as a "Command window"


Install Patent2Net on Linux (Need to fix this)
---------------------------

If you're using Ubuntu or Debian distributions, make sure to have PIP installed:

    sudo apt-get install python-pip build-essential python-dev libjpeg-dev libxml2-dev libfreetype6-dev libpng-dev

Then, run the requirements.txt file to install all dependencies:

    sudo pip install -r Development/requirements.txt

To use the current Development version, you can make a symbolic link to your desired folder:

    ln -sd Development Patent2Net


Use Patent2Net
--------------

1. Edit the file OpsGatherPatentsV2.py and adapt in line 31 the path to you epo accreditation couple: just put in an ASCII file key, password on the same line.
The authenticated credits are obtained from OPS, registering and following instructions.

See the wiki : http://patent2netv2.vlab4u.info/dokuwiki/doku.php


#### Todo List V 2.0 (Beta) 30/10/2016:
