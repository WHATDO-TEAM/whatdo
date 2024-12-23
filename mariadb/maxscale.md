### maxscale 서버
```
sudo apt update
sudo apt -y install net-tools
sudo apt -y install build-essential
sudo apt -y install wget
```

### SELinux 설치
```
sudo apt update
sudo apt install selinux-basics selinux-policy-default auditd

sudo selinux-activate
sudo reboot

sestatus
```


### DNS 설정
```
sudo vi /etc/hosts

10.178.0.3 galera1
10.178.15.231 galera2 
10.178.15.232 galera3
```

### Ubuntu에서 MaxScale 및 MariaDB 클라이언트 설치하기
```
sudo apt-get install software-properties-common
sudo wget -O - https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash

sudo apt-get update
sudo apt-get install maxscale

sudo apt-get install mariadb-client
```

### Mariadb (node)1번서버

```
CREATE USER 'maxscale'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON mysql.user TO 'maxscale'@'%';
GRANT SELECT ON mysql.db TO 'maxscale'@'%';
GRANT SELECT ON mysql.tables_priv TO 'maxscale'@'%';
GRANT SELECT ON mysql.columns_priv TO 'maxscale'@'%';
GRANT SELECT ON mysql.procs_priv TO 'maxscale'@'%';
GRANT SELECT ON mysql.proxies_priv TO 'maxscale'@'%';
GRANT SELECT ON mysql.roles_mapping TO 'maxscale'@'%';
GRANT SHOW DATABASES ON *.* TO 'maxscale'@'%';
FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON wemeet.* TO 'maxscale'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;


SELECT User, Host FROM mysql.user;
```

### Maxscale서버(Maxscale설정)
```
sudo vi /etc/maxscale.cnf


[server1]
type=server
address=10.178.15.226
port=3306
protocol=MariaDBBackend

[server2]
type=server
address=10.178.15.229
port=3306
protocol=MariaDBBackend

[server3]
type=server
address=10.178.15.230
port=3306
protocol=MariaDBBackend


# [MariaDB-Monitor 주석]
[Galera-Monitor]
type=monitor
module=galeramon
servers=server1,server2,server3
user=maxscale
password=password
monitor_interval=2000ms


# [Read-Only-Service], [Read-Write-Service] 삭제 혹은 주석 처리 후 입력
[Splitter-Service]
type=service
router=readwritesplit
servers=server1,server2,server3
user=maxscale
password=password

# [Read-Only-Listener], [Read-Write-Listener] 삭제 혹은 주석 처리 후 입력
[Splitter-Listener]
type=listener
service=Splitter-Service
protocol=MariaDBClient
port=3306
```

###  MaxScale 서비스 실행 및 확인
```
sudo systemctl start maxscale
```

### maxscale과 cluster 들의 상태 확인
```
maxctrl list servers
maxctrl list services
maxctrl list listeners

maxctrl show server server1
maxctrl show server server2
maxctrl show server server3
```

### port 설정
```
sudo apt install firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports

sudo systemctl restart mariadb
```