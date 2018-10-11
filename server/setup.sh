sudo apt-get install libapache2-mod-wsgi &
sudo apt-get install python-pip libmysqlclient-dev -y &
sudo pip install flask user_agents flask_failsafe flask_cors flask-mysql mysql-python numpy pillow &
sudo service apache2 restart &
