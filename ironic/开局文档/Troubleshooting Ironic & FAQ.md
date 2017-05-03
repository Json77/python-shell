# Troubleshooting Ironic & FAQ

## ironic安装问题

### 常用检查步骤

1. 查看rpm包是否安装
2. 查看ironic各个服务状态
3. ironic配置文件
4. 数据库情况

### 典型问题

1、

Q：安装完成后，ironic-condcutor服务起不来，查看服务状态或`/var/log/ironic/ironic-conductor.log`有如下提示： 

```shell
DriverLoadError: Driver, hardware type or interface NeutronNetwork could not be loaded. Reason: The following [neutron] group configuration options are missing: cleaning_network, provisioning_network.
```

A：原因是ironic配置了默认网络接口为neutron，这种方式支持vlan部署，但是需要配置cleaning_network和provisioning_network。在`/etc/ironic/ironc.conf`里配置后即可解决。

2、

Q：ironic命令行执行超时：

```shell
Timed out waiting for a reply to message ID fc238981371a47fd82cd08f1211a3cdb (HTTP 500)
```

A：ironic配置文件中的数据库地址，rabbitmq地址配的有问题，可能是不匹配。检查配置项和数据库，修改完成后，需要执行数据库同步的命令：

```shell
ironic-dbsync --config-file $IRONIC_CONF create_schema #如果已经存在则upgrade
```

## 注册问题

### 常用检查步骤

1. 命令行注册需要检查环境变量export IRONIC_API_VERSION="1.20"；
2. 注册完成之后节点应该是enroll状态；
3. vlan环境下ironic未发现前应该没有port信息。

## 发现问题

### 常用检查步骤

1. 检查用于inspect的端口的vlan设置。
2. 检查inspect服务状态。
3. 如果是下载镜像前，分析网络问题，查看配置中的端口，见tftp和dhcp问题。
4. 如果是下载镜像后，分析配置问题，查看default文件中的返回api。有没有创建port，和更新资源信息。
5. 检查lldp信息，查看交换机端口的lldp配置。

## 无可用节点问题

### 常用检查步骤

这种情况一般是能够在nova的`/var/log/nova/nova-conductor.log`中看到如下日志：

```shell
NoValidHost: No valid host was found. There are not enough hosts available.
```

这代表nova scheduler不能找到一个适合实例的裸机资源，可能是nova instance申请的资源和ironic node的发现的裸机资源不匹配。

1. 搜索是否有可用的ironic节点（只有处于available，非maintenance，且未绑定instance的节点可用）

   ```shell
   ironic node-list --provision-state available --maintenance false --associated false
   ```

   如果是有manageable状态的节点，且已经进行过inspect（可以查看裸机资源信息和port信息），则通过provide置为available。

   ```shell
   ironic node-set-provision-state <IRONIC NODE> provide
   ```

   如果有maintenance状态的节点，且检查过ipmi的状态，则可以去除maintenance状态。

   ```shell
   ironic node-set-maintenance <IRONIC NODE> off
   ```

   检查ironic认证信息

   ```shell
   ironic node-validate baremetal-0 | grep -E '(power|management)\W*False'
   #可用的节点不该返回任何信息。
   ```

2. 确保nova instance使用flavor申请的资源，至少能够找到一个匹配的ironic裸机节点。

   ```shell
   #比较下两个命令的输出结果，必须完全一致
   ironic node-show <IRONIC NODE> --fields properties
   openstack flavor show <FLAVOR NAME>
   ```

3. 在部署前检查hypervisor

   ```shell
   nova hypervisor show <IRONIC NODE>
   ```

   比对可用的资源和已经使用的资源信息。

4. 检查当前使用的是哪一个nova scheduler

   ```shell
   Filter ComputeCapabilitiesFilter returned 0 hosts
   ```

   是否是使用的裸机filter。

5. 以上都无效时，分阶段查询各服务日志。首先是scheduling阶段，查询`/var/log/nova/nova-schedule.log`，spawning阶段，node没有绑定ironic节点前，先检查`/var/log/nova/nova-conductor.log`，如果已经绑定了ironic节点，检查`/var/log/ironic/ironic-conductor.log`。查找具体的错误打印，必要时开启对应服务的DEBUG。

### 典型问题

1、

Q：在nova scheduling阶段失败，`/var/log/nova/nova-conductor.log`里有如下打印：

```shell
AttributeError: 'NoneType' object has no attribute 'support_requests'
```

A：出现这种情况，一般是选择了错误的nova过滤器，检查控制节点nova配置中的以下选项：

```shell
[DEFAULT]
nova_and_ironic_host_manager_enabled=True
scheduler_use_baremetal_filters=True
baremetal_scheduler_default_filters=RetryFilter,AvailabilityZoneFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ExactRamFilter,ExactDiskFilter,ExactCoreFilter
```

2、

Q：在nova scheduling阶段失败，`/var/log/nova/nova-scheduler.log`里有如下打印：

```shell
Filter results: ['RetryFilter: (start: 1, end: 1)', 'AvailabilityZoneFilter: (start: 1, end: 1)', 'ComputeFilter: (start: 1, end: 1)', 'ComputeCapabilitiesFilter: (start: 1, end: 1)', 'ImagePropertiesFilter: (start: 1, end: 1)', 'ExactRamFilter: (start: 1, end: 0)']
```

A：即资源过滤器没有通过，一般是flavor中的信息和ironic的node节点信息没有精确匹配，根据不同过滤器，如果是ExactRamFilter就是内存大小填的不对（注意单位）。注意：inspect发现的硬盘大小只有1块盘，有多块盘的情况不要把所有盘的硬盘大小算上。

3、

Q：在nova scheduling阶段失败，`/var/log/nova/nova-conductor.log`里有如下打印：

```shell
Binding failed for port cc64691c-4c4a-4b8f-be62-63d81a3a2d0a, please check neutron logs for more information
```

A：这种情况一般是前一次部署失败后，nova instance已经被删除，但是ironic port绑定的neutron port信息没有被删除。查看port信息中的internal_info字段（需要环境变量export IRONIC_API_VERSION=1.20），如果有这个字段信息，需要删除port，重新创建或发现。否则此port就是已经被占用的状态，无法进行下一次部署。

## tftp和dhcp问题

### 常用检查步骤

#### dhcp获取不到ip

1. 查看dhcp服务有没有起，neutron-dhcp-agent；
2. 查看opts文件是否正确配置；
3. 根据tecs需要，ovs网口要放到网桥里；
4. 查看用于裸机部署的网络落到了哪个节点的dhcp-agent上；
5. 查看裸机端口的vlan有没有正确配置为当前网络的vlan；
6. 用tcpdump -i 网口 抓包分析，是否能获取到。

#### tftp获取不到（已经获取到了dhcp提供的ip）

1. 另选一个节点，`tftp $ip `然后用get命令获取文件。
2. 查看`xinetd.service`的服务状态，有没有`remove tftp`，如果有，修改`/etc/xinetd.d/tftp`配置，修改/tftpboot目录下的map-file等文件。
3. 修改default的文件。
4. tftp的网口要配合适网段的ip。网桥上的口不要配ip。
5. 查看裸机端口的vlan有没有正确配置为当前网络的vlan。
6. 查看获取不到的文件和目录的用户和用户权限。

## 组网问题

### 常用检查步骤

1. 检查各部分端口的vlan配置。
2. 检查部署的各个阶段裸机连接交换机端口的vlan配置。开始处于inspect网络的vlan，开始部署后（ironic节点进入deploying状态后）处于provision网络的阶段。active之后，处于租户网络的vlan。
3. 检查neutron插件在`/etc/neutron/neutron-server.log`中的日志打印。

## 部署问题

### 常用检查步骤

1. 分阶段查看不同的日志，scheduling阶段按前面章节《无可用节点问题》定位；
2. nova spawning状态但是ironic没有deploying，查看nova conductor的日志查看超时等问题；
3. ironic进入deploying阶段，查看准备阶段的ironic conductor日志。
4. ironic进入wait-call-back阶段，主要查看dhcp和tftp能不能下载到镜像，完成后小系统网卡能否获得ip。
5. 最后检查部署完成后的裸机端口vlan。

### 典型问题

1、

Q：nova spawning但是ironic没有deploying，查nova conductor日志有如下打印：

```shell
 Request to http://192.168.200.190:9696/v2.0/ports.json timed out
```

A：这种情况一般是修改了neutron的配置文件后没有重启neutron服务，或者网络原因，导致json文件发生变化，向neutron发送的请求超时。一般重启neutron的相关服务即可解决。

## 清除问题

### 常用检查步骤

1. 查看ironic node状态
2. 查看ironic port信息（注意要先export IRONIC_API_VERSION="1.20"）
3. 查看nova instance状态
4. 查看neutron port信息
5. 查看配置文件中的clean设置（后期），查看各个日志

### 典型问题

1、

Q：ironic节点为error状态，无法部署完成，日志中有：

```shell
The requested action "active" can not be performed on node "783e906c-4690-4efa-a332-a1304fc4e80e" while it is in state "error".
```

A：这种情况一般是由于在ironic部署完成前，手动删除了neutron port，导致的问题。一般情况下，部署中的裸机，有一个node，绑定了一个nova instance，在provision网和tenant网各有一个neutron port。部署完成后，会保留在tenant网络的neutron port，不需要额外操作。如果手动删除了任意neutron port，就会导致各种问题。

2、

Q：由于网络问题，导致ironic和nova的连接中断，nova节点可以删除，但ironic节点没有失败。出现以下问题：

```shell
# ironic node-list
+------------------------------------------------------------------------------------------------------+
| UUID              | Name | Instance UUID         | Power State | Provisioning State | Maintenance |
+------------------------------------------------------------------------------------------------------+
| $UUID             | None | $Instance_UUID        | power on    | wait call-back     | False       |
+------------------------------------------------------------------------------------------------------+
# nova list
+----+------+--------+------------+-------------+----------+
| ID | Name | Status | Task State | Power State | Networks |
+----+------+--------+------------+-------------+----------+
+----+------+--------+------------+-------------+----------+
```

A：网络问题导致的连接中断，nova就不会触发ironic的delete操作，这种情况下，ironic的清除就需要自己完成。状态机的切换可以通过`ironic node-set-provision-state $UUID deleted`触发ironic的删除流程，但是ironic port和问题1一样，需要重新创建。

