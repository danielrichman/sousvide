- Instlal postgresql-9.6 python3-psycopg2
- echo dtoverlay=w1-gpio >> /boot/config.txt
- (echo w1-gpio; echo w1-therm) >> /etc/modules
- sudo -u postgres psql postgres -c 'create database sousvide'
- adduser sousvide

