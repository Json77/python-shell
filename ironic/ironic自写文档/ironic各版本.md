#ironic版本差异
http://docs.openstack.org/releasenotes/ironic/mitaka.html
##M版本
###Bug Fix
- 使用'agent_ilo'或'iscsi_ilo'的节点在node validate里有了'driver_info/ilo_deploy_iso'这项验证。

- 修复了如果在enabled_drivers选项里有多个入口会引起conductor在启动时进入error状态。

- 之前设置用ipminative驱动的节点的启动设备时，没有考虑启动模式（UEFI或BIOS）。现在修复为，从UEFI转换为legacy BIOS作为改变启动设备的部分要求。

- 修复在改变节点的启动设备时，没有检查启动模式（UEFI或BIOS），导致在一些硬件模组上从UEFI转换为Legacy BIOS错误。

- 在修复模式下，升级一个活动实例的网口mac地址，以前会返回HTTP500错误，已经修复。

- 升级一个活动实例的网口mac地址在非修复模式下，以前会返回HTTP500错误，现在改为返回HTTP400。

- 修复iRMC带外检查中的非法MAC请求。

- iRMC虚拟媒介用远程重新传输的CD/DVD替代默认的CD/DVD。

- 确保节点进入稳定状态时，节点的target_provision_state清除，表明状态转换结束。

- 修复bug，当使用agent驱动和partition镜像时，用户指定的disk_label会被忽略。

- 解决了错误，一些硬件或固件（特别是一些错误的）通过带内ACPI软关机后，不会重新上线。在节点通过IPA ramdisk部署时添加一个新的驱动项，“deploy_forces_oob_reboot”。如果这个项设为true，Ironic会通过带外重新上电这个节点。

- 修复了bug，当实例化客户端时，keystone_authtoken/region_name不会传递给swift。在多区域环境下，需要这个以便客户端可以选择正确的swift的endpoint。

  ​

###安全问题
- 修复了一个关键安全漏洞（CVE-2016-4985）。以前，通过网络连接到ironic-api服务的客户端能够通过keystone验证，取回所有ironic注册节点的信息。如果他们知道或能猜到该节点网卡的mac地址，通过发送一个POST请求，到/v1/drivers/$DRIVER_NAME/vendor_passthru源完成。Ironic的policy.json设置遵照请求，如果来的请求通过密码加密，他们的回复也加密。

  ​


###升级日志
- 升级python-scciclient需要iRMC驱动为0.3.1版本，包含修复bug'#1561852'。
- 增加[glance]glance_cafile设置选项，传递一个可选的CA认证，来验证为glance和ironic的安全https连接提供的SSL认证。

###新特性
- 为基于agent的驱动添加支持partition images（注：L版本及之前，agent驱动只支持whole-disk images）
- 支持传递一个可选的CA认证，使用[glance]glance_cafile设置选项，来验证为glance和ironic的安全https连接提供的SSL认证。
- 在返回帧Opstack-Request-Id开头增加request_id。


## N版本

### Bug Fix

- 包含任意kwargs对象的Ironic请求通过RPC发送会引发oslo_messaging串行失败。在ironic API里表现为500错误，从conductor等待恢复超时。从本版本开始，所有在计划外kwargs里的无序对象被丢弃。错误是否返回给服务由配置项`[DEFAULT]fatal_exception_format_errors`决定。

- 给ipmitool电源驱动reboot添加了一个error检查，即下电失败可以显示。

- 修复pxe_drac驱动`get_bios_config()`出现意外的AttributeError。

- 修复oneview驱动中，周期性检查节点是否被oneview使用时过早结束。

- 修复错误的基础socat命令，其妨碍了控制台的使用。

- 从默认iPXE脚本中，删除了dhcp命令，多余且当规定的NIC不是第一个时会中断部署。

- ​修复ironic API的查询机制查到非法的MAC地址时，会导致节点部署失败。比如一个节点包含一个无线带宽网卡，agent传递一个20字节（正常应该是6字节）的mac地址或GID，作为查询请求的一部分，这个查询原先会失败。现在会忽略非法地址。

  ​

### 安全问题

- 私有ssh密钥现在在用于电源驱动和节点请求时加密。

  ​

### 升级日志

- ​
- ​

### 新特性

- ​







