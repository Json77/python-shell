# 自动化脚本搭建ironic测试环境

> 本测试基于tecs3.0版本，ZXTECS_V03.16.11_I774，操作系统版本Mimosa-V02.16.11-dev206。
>
> 安装和配置在计算节点和控制节点分别进行。
>
> 当前ironic_init下载路径：git clone git@gitlab.zte.com.cn:10192224/ironic_init.git

## 控制节点

>  下载ironic init工具文件夹，并添加keystone认证

### 1. 安装ironic client工具包

在ironic_init文件夹下执行：

```shell
rpm -ivh rpms/python-ironicclient*
```

安装ironic命令工具包。

### 2. 控制节点配置

修改配置文件`vi conf/computer.conf`为当前环境的值。

例如：

```shell
IRONIC_NODE_IP=10.43.200.165       #安装ironic的计算节点的控制面ip
CONTROLLER_IP=10.43.200.166        #控制该计算节点的控制节点ip
IRONIC_DB_PASSWORD=IRONIC_DBPASSWORD    #ironic数据库密码，用户名默认为ironic
IRONIC_PASSWORD=ironic					#openstack ironic用户密码，用户名默认为ironic
MARIADB_PORT=29998						#mariadb的端口号
TFTP_ROOT_PATH=/tftpboot				#计算节点上tftp的根目录
PXELINUX0=/usr/share/syslinux/pxelinux.0    #pxe安装取pxelinux.0的路径
INSTALL_SHARE_PATH=/home/install_share  #nfs取ks文件的路径
LINUX_INSTALL_PATH=/linuxinstall		#nfs挂载iso的目录
DEPLOY_BRIDGE=br-data1					#填写给neutron使用的ovs网桥
DEPLOY_INTERFACE=eno16777728			#加入ovs网桥的网口（这两个是给neutron用的，安装TECS的时候选择）
ISO_MOUNT_DIR_NUM=10					#一次同时可挂载的系统种类
PHYS_NET=physnet1						#采用的物理网络类型
```

root权限执行`./controller.sh`

该脚本根据上述配置文件配置ironic，nova和neutron，上面的配置值都要有，否则报错退出。

### 3. 配置neutron部署网络和子网

1. 如本例中，执行

```shell
#!/bin/bash
TENANT_ID=`openstack project list | awk '/admin/ {print $2}'`
NETWORK_CIDR=192.168.3.0/24
SUBNET_NAME=my_dhcp_test
GATEWAY_IP=192.168.3.1
START_IP=192.168.3.100
END_IP=192.168.3.150

neutron net-create --tenant-id $TENANT_ID deploynet1 --shared --provider:network_type flat --provider:physical_network physnet1
neutron subnet-create deploynet1 $NETWORK_CIDR --name $SUBNET_NAME \
--ip-version=4 --gateway=$GATEWAY_IP --allocation-pool \
start=$START_IP,end=$END_IP --enable-dhcp
```

2. 查看`neutron port-list `看到分配的部署网的ip，将这个ip填到计算节点`/etc/ironic/ironic.conf`中的`my_ip`中，并将计算节点用于连接裸机的网口配置为该ip，完成后重启计算节点ironic的两个服务。

3. 在控制节点修改网络绑定的`neutron-dhcp-agent`比如通过计算节点的dhcp部署裸机就把上面创建的部署网绑定到计算节点的neutron-dhcp-agent。（开始会随机分配一个）

   neutron dhcp绑定到具体的节点

   - neutron agent-list查看所有的agent信息，这里只关注agent_type是DHCP agent的；
   - neutron dhcp-agent-list-hosting-net $NET_ID 查看net绑定到哪个agent了;
   - neutron dhcp-agent-network-remove DHCP_AGENT NETWORK删除已经绑定的agent；
   - neutron dhcp-agent-network-add DHCP_AGENT NETWORK 重新绑定agent

### 4. 创建flavor

根据裸机信息创建flavor，如本例：

```shell
#!/bin/bash
TENANT_ID=`openstack project list | awk '/admin/ {print $2}'`
RAM_MB=108667
CPU=48
DISK_GB=200
ARCH=x86_64

nova quota-update --cores $CPU $TENANT_ID
nova quota-update --ram $RAM_MB $TENANT_ID

nova flavor-create my-baremetal-flavor 20 $RAM_MB $DISK_GB $CPU
nova flavor-key my-baremetal-flavor set cpu_arch=$ARCH
nova flavor-key my-baremetal-flavor set capabilities:boot_option="local"
nova flavor-key my-baremetal-flavor set hw:compute_type=ironic
```

注意修改quota额度上限，脚本的前两行。

### 5. 添加部署镜像

添加部署镜像，采用pxe安装时需要三个镜像：

```shell
glance image-create --name deploy-vmlinuz --visibility public --disk-format aki --container-format aki < ironic-deploy.kernel
glance image-create --name deploy-initrd --visibility public --disk-format ari --container-format ari < ironic-deploy.initramfs
glance image-create --name my-centos --tag centos --visibility public --disk-format iso --container-format bare < CentOS-7-x86_64-Minimal-1611.iso
```

## 计算节点

> 下载ironic init工具文件夹

### 1. 安装ironic rpm包

在ironic_init文件夹下执行：

```shell
rpm -ivh rpms/*
```

安装所有包。

### 2. 计算节点配置

修改配置文件`vi conf/computer.conf`为当前环境的值：

例如：

```shell
IRONIC_NODE_IP=10.43.200.165       #安装ironic的计算节点的控制面ip
CONTROLLER_IP=10.43.200.166        #控制该计算节点的控制节点ip
IRONIC_DB_PASSWORD=IRONIC_DBPASSWORD    #ironic数据库密码，用户名默认为ironic
IRONIC_PASSWORD=ironic					#openstack ironic用户密码，用户名默认为ironic
MARIADB_PORT=29998						#mariadb的端口号
TFTP_ROOT_PATH=/tftpboot				#计算节点上tftp的根目录
PXELINUX0=/usr/share/syslinux/pxelinux.0    #pxe安装取pxelinux.0的路径
INSTALL_SHARE_PATH=/home/install_share  #nfs取ks文件的路径
LINUX_INSTALL_PATH=/linuxinstall		#nfs挂载iso的目录
DEPLOY_BRIDGE=br-data1					#填写给neutron使用的ovs网桥
DEPLOY_INTERFACE=eno16777728			#加入ovs网桥的网口（这两个是给neutron用的，安装TECS的时候选择）
ISO_MOUNT_DIR_NUM=10					#一次同时可挂载的系统种类
PHYS_NET=physnet1						#采用的物理网络类型
```

root权限执行`./computer.sh`

该脚本根据上述配置文件配置ironic，nova和neutron，上面的配置值都要有，否则报错退出。

看到打印`Configure success`并没有错误输出即表示配置成功。

### 3. 根据控制节点neutron分配的部署网ip设置自己的ip

见控制节点3.2

## 正式部署

### 1. 创建节点

如本例：

```shell
#!/bin/bash
NODE_UUID=$(ironic node-create -d pxe_ztetool | awk '/^\| uuid / {print $4}')

ironic node-update $NODE_UUID add driver_info/ipmi_username=root driver_info/ipmi_password=ossdbg1 driver_info/ipmi_address=10.43.200.161

DEPLOY_VMLINUZ_UUID=$(glance image-list | awk '/deploy-vmlinuz/ {if($4=="deploy-vmlinuz"){print $2}}')
DEPLOY_INITRD_UUID=$(glance image-list | awk '/deploy-initrd/ {if($4=="deploy-initrd"){print $2}}')
IMG=$(glance image-list | awk '/ my-centos / {print $2}')
KERNEL=$(glance image-list | awk '/ deploy-vmlinuz/ {print $2}')
RAMDISK=$(glance image-list | awk '/ deploy-initrd/ {print $2}')
NIC_UUID=$(neutron net-list | awk '/ deploynet1 / {print $2}')

ironic node-update $NODE_UUID add driver_info/deploy_kernel=$DEPLOY_VMLINUZ_UUID driver_info/deploy_ramdisk=$DEPLOY_INITRD_UUID
ironic node-update $NODE_UUID add properties/cpus=48 properties/memory_mb=108667 properties/local_gb=200 properties/cpu_arch=x86_64
ironic port-create -n $NODE_UUID -a 98:40:bb:81:37:5b

ironic node-update $NODE_UUID add properties/capabilities="boot_option:local"
```

### 2. nova boot

如本例：

```shell
#!/bin/bash
flavorID=20
NIC_UUID=$(neutron net-list | awk '/ deploynet1 / {print $2}')
nova boot --flavor $flavorID --image my-centos --nic net-id=$NIC_UUID instance_partion_deploy
```