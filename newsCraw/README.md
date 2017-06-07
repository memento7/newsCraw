# newsCraw
memento crawler

# Installation
```
apt-get update
apt-get install python3 python3-pip python-dev -y
apt-get install build-essential libssl-dev libffi-dev libicu-dev -y
apt-get install software-properties-common git -y

// for polyglot
git clone https://github.com/aboSamoor/polyglot.git
cd polyglot
pip3 install -r requirements.txt
python3 setup.py install

// for jdk installation
add-apt-repository ppa:openjdk-r/ppa -y
apt-get update
apt-get install openjdk-8-jdk -y

git clone https://github.com/memento7/newsCraw.git
cd newsCraw/newsCraw
pip3 install -r requirements.txt
python3 install_nltk_data.py

// run!
```

# Usage
```
scrapy crawl newsCraw -a entity=entity -a date_start=date_start -a date_end=date_end -a id=id
```
date format: "yyyy.mm.dd"