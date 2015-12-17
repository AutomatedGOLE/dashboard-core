# AutoGOLE Dashboard Core #

## Install instructions ##

**Debian Jessie**

### Install dependencies ###
```
apt-get install mariadb-server python-pip python-mysqldb
mysql_secure_installation
pip install paramiko
pip install python-daemon
mkdir /var/run/dashboard/
```
**Note: The dashboard needs write access to the directory created above.**

**Note: MySQL instead of MariaDB should also work.**

### Set-up database ###

**Note: Replace username and password as intended.**

```
CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'monitor_pass';

create database dashboard;
use dashboard;
create table peerswith (nsa1 varchar(255), nsa2 varchar(255));
create table nopeers (nsa varchar(255));
create table unknownpeers (nsa varchar(255), unknown varchar(255));
create table peerswithmismatches (nsa1 varchar(255), nsa2 varchar(255));
create table isalias (src_domain varchar(255), src_port varchar(255), dst_domain varchar(255), dst_port varchar(255));
create table isaliasmatch (src_domain varchar(255), src_port varchar(255), dst_domain varchar(255), dst_port varchar(255));
create table isaliasvlans (src_domain varchar(255), src_port varchar(255), src_vlans varchar(255), dst_domain varchar(255), dst_port varchar(255), dst_vlans varchar(255));
create table cp_connectivity (nsa varchar(255), result int);
create table notref (nsa varchar(255));
create table unknowntopologies (topology varchar(255) PRIMARY KEY);
create table nsastopologies (nsa varchar(255), topology varchar(255), status int);
create table topologynsa (topology varchar(255), nsa varchar(255), status int);
create table switchports (topology varchar(255), service varchar(255), port varchar(255));
create table switch (topology varchar(255), service varchar(255), labelswapping varchar(255), labeltype varchar(255), switchtype varchar(255), encoding varchar(255));
create table peersroles (nsa varchar(255), role varchar(255));
create table dp_connectivity (topology varchar(255), result int);
GRANT ALL PRIVILEGES ON dashboard.* To 'monitor'@'localhost' IDENTIFIED BY 'monitor_pass';
```

### Start Dashboard Core ###

python $PWD/core.py start