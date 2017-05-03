1.yum源配置：

[swift_tmp]

name=yu_tmp

baseurl=http://10.43.177.198/centos/7/cloud/x86_64/openstack-mitaka/

enabled=1

gpgcheck=0

2.安装rpm包:

yum install openstack-swift

yum install openstack-swift-account

yum install openstack-swift-container

yum install openstack-swift-object

yum install openstack-swift-proxy

3.执行：pre_install.sh

\#!/bin/bash

GROUP='root'

USER='swift'

function pre_install

{

    sudo mkdir -p /srv

    sudo truncate -s 1GB /srv/swift-disk-1

    sudo truncate -s 1GB /srv/swift-disk-2

    sudo truncate -s 1GB /srv/swift-disk-3

    echo "create loop device successful!"

    sudo mkfs.xfs -f /srv/swift-disk-1

    sudo mkfs.xfs -f /srv/swift-disk-2

    sudo mkfs.xfs -f /srv/swift-disk-3

    sudo mkdir -p /srv/node/sdb

    sudo mkdir -p /srv/node/sdc

    sudo mkdir -p /srv/node/sdd

    sudo mount  /srv/swift-disk-1 /srv/node/sdb

    echo "mount swift-disk-1 to /srv/node/sdb"

    sudo mount  /srv/swift-disk-2 /srv/node/sdc

    echo "mount swift-disk-2 to /srv/node/sdc"

    sudo mount  /srv/swift-disk-3 /srv/node/sdd

    echo "mount swift-disk-3 to /srv/node/sdd"

    sudo mkdir -p /var/cache/swift

    sudo chown -R ${GROUP}:${USER} /var/cache/swift

    sudo mkdir -p /var/log/swift

    sudo chown -R ${GROUP}:${USER} /var/log/swift

    sudo chmod -R g+w /var/log/swift

   

    cd /etc/swift

    rm -f *.builder *.ring.gz backups/*.builder backups/*.ring.gz

    swift-ring-builder object.builder create 10 3 1

    swift-ring-builder object.builder add r1z1-127.0.0.1:6200/sdb 1

    swift-ring-builder object.builder add r1z2-127.0.0.1:6200/sdc 1

    swift-ring-builder object.builder add r1z2-127.0.0.1:6200/sdd 1

    swift-ring-builder object.builder rebalance

    swift-ring-builder container.builder create 10 3 1

    swift-ring-builder container.builder add r1z1-127.0.0.1:6201/sdb 1

    swift-ring-builder container.builder add r1z2-127.0.0.1:6201/sdc 1

    swift-ring-builder container.builder add r1z2-127.0.0.1:6201/sdd 1

    swift-ring-builder container.builder rebalance

    swift-ring-builder account.builder create 10 3 1

    swift-ring-builder account.builder add r1z1-127.0.0.1:6202/sdb 1

    swift-ring-builder account.builder add r1z2-127.0.0.1:6202/sdc 1

    swift-ring-builder account.builder add r1z2-127.0.0.1:6202/sdd 1

    swift-ring-builder account.builder rebalance

}

pre_install

echo "pre_install successful!"

\#4.拷贝rsyncd.conf到/etc/

[root@2c510cg swift(keystone_admin)]# cat rsyncd.conf

uid = swift

gid = swift

log file = /var/log/rsyncd.log

pid file = /var/run/rsyncd.pid

address = 127.0.0.1

[account]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/account.lock

[container]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/container.lock

[object]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/object.lock

重启rsyncd服务

sudo systemctl enable rsyncd.service

sudo systemctl start rsyncd.service

5.创建用户：

source /root/keystonerc_admin

openstack user create --password swift swift

openstack role add --project services --user swift admin

openstack service create --name swift --description "OpenStack Object Storage" object-store

openstack endpoint create --region RegionOne object-store --publicurl [http://10.43.203.133:8080/v1/AUTH_%\(tenant_id\)s](javascript:void(0);) --internalurl[http://10.43.203.133:8080/v1/AUTH_%\(tenant_id\)s](javascript:void(0);) --adminurl [http://10.43.203.133:8080/v1](javascript:void(0);) 

6.修改/etc/swift/proxy-server.conf

admin_tenant_name = services

admin_user = swift

admin_password = swift

auth_host = 127.0.0.1

7.修改配置文件权限，重启服务

chown -R root:swift /etc/swift

systemctl restart openstack-swift-account.service

systemctl restart openstack-swift-container.service

systemctl restart openstack-swift-object.service    

systemctl restart openstack-swift-proxy.service