### 1. ubuntu20.04로 서버 만들기
```
sudo apt-get install software-properties-common
sudo apt-key adv --fetch-keys 'https://mariadb.org/mariadb_release_signing_key.asc'
sudo add-apt-repository 'deb [arch=amd64,arm64,ppc64el] https://mirrors.aliyun.com/mariadb/repo/10.5/ubuntu focal main'
```

```
sudo apt-get update
sudo apt-get install mariadb-server mariadb-client
```

```
sudo systemctl status mariadb
```


```
sudo apt-get install ntp
sudo systemctl start ntp
sudo systemctl enable ntp
```


```
sudo mysql_secure_installation
sudo apt-get install mariadb-server-10.5 galera-4 mariadb-plugin-connect
sudo apt-get install rsync
```



### galera cluster 설정
```
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
#bind addres 127.0.0.1 주석처리 해주기

#private ip를 썼었다.
[mysqld]
bind-address=0.0.0.0
default_storage_engine=InnoDB
binlog_format=row
innodb_autoinc_lock_mode=2
innodb_flush_log_at_trx_commit=0
wsrep_on=ON
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_cluster_name="my_galera_cluster"
wsrep_cluster_address="gcomm://10.178.0.3,10.178.15.231,10.178.15.232"
wsrep_node_name="Node3"
wsrep_node_address="10.178.15.232"
wsrep_sst_method=rsync
```


### 방화벽 설정
```
sudo ufw enable

sudo ufw allow 3306/tcp
sudo ufw allow 4567/tcp
sudo ufw allow 4568/tcp
sudo ufw allow 4444/tcp
sudo ufw reload

sudo ufw status verbose
```

### 연결되었는지 확인
```
#1번서버#
sudo galera_new_cluster


SHOW STATUS LIKE 'wsrep_%';
```