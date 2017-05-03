#inspector配置

针对M版本
http://docs.openstack.org/developer/ironic-inspector/mitaka/index.html
http://docs.openstack.org/developer/ironic-inspector/mitaka/install.html

1. 取openstack-mitaka的yum源，安装openstack-ironic-inspector-3.2.2-1.el7.noarch
   python-ironic-inspector-client-1.6.0-1.el7.noarch包

2. 修改/etc/ironic-inspector/inspector.conf
   ```
   [DEFAULT]
   [cors]
   [cors.subdomain]
   [database]
   connection = mysql+pymysql://ironic_inspector:IRONIC_INSPECTOR_PASSWORD@192.168.2.40/ironic_inspector?charset=utf8
   [discoverd]
   [discovery]
   [firewall]
   dnsmasq_interface = br-data1
   [ironic]
   os_auth_url = http://192.168.2.40:5000
   os_username = ironic-inspector
   os_password = IRONIC_INSPECTOR_PASSWORD
   os_tenant_name = services
   identity_uri = http://192.168.2.40:35357
   [keystone_authtoken]
   [processing]
   add_ports = all
   keep_ports = all
   [swift]
   ```

3. 修改/etc/ironic-inspector/dnsmasq.conf
```
port=0
bind-interfaces
enable-tftp
tftp-root=/tftpboot
interface=eth0
dhcp-range=192.168.2.100,192.168.2.200
dhcp-boot=pxelinux.0
dhcp-sequential-ip
```

4. 修改/tftpboot/pxelinux.cfg/default
   ```shell
   default introspect
   label introspect
   kernel ironic-deploy.kernel
   append initrd=ironic-deploy.initramfs ipa-inspection-callback-url=http://192.168.2.40:5050/v1/continue ipa-inspection-collectors=default,logs systemd.journald.forward_to_console=yes
   ipappend 3
   ```


5. 镜像ironic-deploy.kernel和ironic-deploy.initramfs放到/tftpboot目录
6. 更新配置文件

```
ironic-inspector-dbsync --config-file /etc/ironic-inspector/inspector.conf upgrade
```

7. 创建inspector用户
   ```language
   openstack user create --password IRONIC_INSPECTOR_PASSWORD --email ironic_inspector@example.com ironic-inspector
   openstack role add --project services --user ironic-inspector admin
   openstack service create --name ironic-inspector --description "Ironic baremetal inpector service" baremetal-introspection
   openstack endpoint create --region RegionOne --publicurl http://192.168.2.40:5050 --internalurl http://192.168.2.40:5050 --adminurl http://192.168.2.40:5050 baremetal-introspection
   ```

8. 创建inspector数据库
```
mysql -u root -p
mysql> CREATE DATABASE ironic_inspector CHARACTER SET utf8;
mysql> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'localhost' IDENTIFIED BY 'IRONIC_INSPECTOR_PASSWORD';
mysql> GRANT ALL PRIVILEGES ON ironic_inspector.* TO 'ironic_inspector'@'%' IDENTIFIED BY 'IRONIC_INSPECTOR_PASSWORD';
```

9. 重启所有ironic服务
10. 创建ironic节点
```shell
#!/bin/bash
NODE_UUID=$(ironic node-create -d pxe_ipmitool | awk '/^\| uuid / {print $4}')
ironic node-update $NODE_UUID add driver_info/ipmi_username=USERID driver_info/ipmi_password=PASSW0RD driver_info/ipmi_address=192.168.2.27
DEPLOY_VMLINUZ_UUID=$(glance image-list | awk '/deploy-vmlinuz/ {print $2}')
DEPLOY_INITRD_UUID=$(glance image-list | awk '/deploy-initrd/ {print $2}')
IMG=$(glance image-list | awk '/ my-image / {print $2}')
KERNEL=$(glance image-list | awk '/my-kernel/ {print $2}')
RAMDISK=$(glance image-list | awk '/ my-image.initrd / {print $2}')
NIC_UUID=$(neutron net-list | awk '/ sharednet1 / {print $2}')
ironic node-update $NODE_UUID add driver_info/deploy_kernel=$DEPLOY_VMLINUZ_UUID driver_info/deploy_ramdisk=$DEPLOY_INITRD_UUID
ironic node-update $NODE_UUID add instance_info/image_source=$IMG instance_info/kernel=$KERNEL instance_info/ramdisk=$RAMDISK instance_info/root_gb=100
ironic node-update $NODE_UUID add properties/capabilities="boot_option:local"
exit 1
ironic node-update $NODE_UUID add properties/cpus=40 properties/memory_mb=262144 properties/local_gb=500 properties/cpu_arch=x86_64
ironic port-create -n $NODE_UUID -a 08:94:ef:25:21:6c
```

11.  改变节点为manageable
    ```language
    ironic node-set-provision-state ＜UUID＞ manage
    ```

12.  起一个节点，观察状态
```
openstack baremetal introspection start [--wait] [--new-ipmi-password=PWD ][--new-ipmi-username=USER]] UUID [UUID ...] 
 openstack baremetal introspection status UUID
```

13.  等待inspector状态为true后，provide使其available
    ```
    ironic node-set-provision-state ＜UUID＞ provide 
    ```