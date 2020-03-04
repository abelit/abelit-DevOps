This tool provides montoring of remote SQL databases and does not need to be installed on the database
server[s]. A better place is on the zabbix server or on a zabbix proxy.

# what is a host?
A host in zabbix can be a computer but also a router, switch, SAN and in this case, a database cluster. A host
in zabbix is a thing that has a collection of items. For Oracle create a host for the physical database, for
SQLServer create a host for an Instance, for Postgres create a host for the cluster, for cockroach create a host
for the cluster. 
An Oracle database can have multiple Instances and multiple databases. They are collected in a single host.
A SQLServer instance has multiple databases and in an always on configuration can be active on several machines.
That instance s handled by a single host.
A Postgres cluster is very similar to a SQLServer instance.
A cockroach cluster can have many nodes. That cluster is handled by a single host.

# setup
To do that, create a simple OS user that has the ability to use cron, zabbix_sender and is able to connect
to the server or proxy port, as wel as a creating a connection to the remote database[s]. For example create user zbxdb.

logon as zbxdb
use pyenv to manage a local python version for zbxdb

curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

pyenv install 3.6.5

git clone https://github.com/ikzelf/zbxdb.git

pip install -r zbxdb/requirements.txt

cp -rp zbxdb/etc $HOME/
cp -p zbxdb/logging.json.example  $HOME/etc/

in your etc directory are some sample monitoring configs. The naming convention for the configs is
zbxdb.{hostname_in_zabbix}.cfg
Replace the samples with your own configuration files.

Add these entries into .bash_profile of the home directoy of the user that will run zbxdb:
  - export ZBXDB_HOME=$HOME
  - export ZBXDB_OUT=$ZBXDB_HOME/zbxora_out  ## make sure this reflects the out_dir parameter in the monitoring cfg files.
  - export PATH=$PATH:$HOME/zbxdb/bin

source .bash_profile

Load the template (zbxdb_template_v3.xml or zbxdb_template_v4.xml) and link it to hostname in zabbix that
represents the database that you want to monitor. That hostname should be in the hostname parameter in your monitoring .cfg file of this database.

make sure that zabbix_sender is available
create the directory for log, collecting the metrics and workspace for zbxdb_sender
- mkdir $ZBXDB_OUT
- mkdir $ZBXDB_HOME/log
- mkdir $HOME/zbxdb_sender

add into the crontab:
<br>
`* * * * * $HOME/zbxdb/bin/zbxdb_starter > /dev/null 2>&1`
<br>
`* * * * * $HOME/zbxdb/bin/zbxdb_sender  > /dev/null 2>&1`
<br>or:<br>
`* * * * * export ZBXDB_OUT={out_dir_from_zbxdb.py's};$HOME/zbxdb/bin/zbxdb_sender.py  > /dev/null 2>&1`

Now, zbxdb_starter will check $ZBXDB_HOME/etc/ for files starting with 'zbxdb.' and ending with '.cfg'
that are writeable. If such a file is found and the corresponding zbxdb.py process is not running, it
will start that process.

zbxdb_sender will check $ZBXDB_OUT/ and move the contents to $HOME/zxbdb_sender/in/. Next it will send
the files to zabbix and keep a few days of history in $HOME/zbxdb_sender/archive/

- If anything fails, first check the log/ directory.
- zbxdb.py can be run from the commandline to debug the cfg files.
- if you see data coming into $ZBXDB_OUT/ the collection could be OK (errors are reported on stdout)
- if zbxdb_sender/archive/ remains empty, zbxdb_sender is not picking up your metrics.  Check the log.

# Note

```bash
cd /opt
mkdir oracle
cd oracle
wget https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
unzip instantclient-basic-linux.x64-19.6.0.0.0dbru.zip 


echo /opt/oracle/instantclient_19_6 > /etc/ld.so.conf.d/oracle-instantclient.conf
ldconfig  

yum install glibc
yum install libnsl
yum install zabbix-sender


[zbxdb@zabbix_server ~]$ cat .bashrc 
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
PATH="$HOME/.local/bin:$HOME/bin:$PATH"
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
export ORACLE_HOME=/opt/oracle/instantclient_19_6
export TNS_ADMIN=$ORACLE_HOME/network/admin
export NLS_LANG="SIMPLIFIED CHINESE_CHINA.ZHS16GBK"
#export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_6:$LD_LIBRARY_PATH

export ZBXDB_HOME=$HOME
export ZBXDB_OUT=$ZBXDB_HOME/zbxdb_out
export PATH=$PATH:$HOME/zbxdb/bin



[zbxdb@zabbix_server ~]$ cat etc/zbxdb.odb.cfg 
[zbxdb]
db_url = //10.10.10.20:1521/garland.org
username = cistats
password = 
db_type = oracle
db_driver = cx_Oracle
instance_type = rdbms
role = normal
out_dir = $HOME/zbxdb_out
# hostname 填写zabbix Web前端主机配置的名字
hostname = P-Garland-DB-Monitor
checks_dir = etc/zbxdb_checks
site_checks = sap,ebs
password_enc = Y2lzdGF0cw==


[zbxdb@zabbix_server ~]$ crontab -l
* * * * * $HOME/zbxdb/bin/zbxdb_starter > /dev/null 2>&1
* * * * * $HOME/zbxdb/bin/zbxdb_sender.py $ZBXDB_OUT > /dev/null 2>&1

```