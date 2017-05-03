# Ironic Python Agent
## 概述
控制裸机节点，检查，安装，清除，部署镜像。
IPA分布运行在各个节点中，在内存盘启动时运行。

## 驱动
- 前缀是pxe\_或iscsi\_的，把根硬盘驱动作为iSCSI共享盘暴露，回传给ironic conductor。conductor mount这个共享盘，拷贝image进去，发信号给IPA进行安装后操作，比如启动bootloader支持本地启动。
- 前缀是agent\_的，conductor准备一个swift临时image的URL。IPA处理整个部署进程：从URL下载image，发到目标机，执行安装后操作。

选用时基于环境，iscsi驱动对conductor负荷高，agent驱动要求全镜像适配节点内存。制作镜像可以使用CoreOS工具或disk-image-builder。

###IPMITool
- agent_ipmitool
- pxe_ipmitool

#####使能驱动
两种驱动控制ipmi，需要安装ipmitool utility，使能驱动，在 /etc/ironic/ironic.conf 中，添加 pxe_ipmitool或/和agent_ipmitool 到 enabled_drivers。
#####注册节点
添加节点到driver_info，ipmi_address，ipmi_username，ipmi_password，ipmi_port默认623，然后ironic node-create/ironic node-update。
#####高级设置
1.8.12版后的ipmitool可以使用桥接函数，单桥或双桥。
需要在driver_info中添加ipmi_bridging，ipmi_local_address，ipmi_local_address，ipmi_target_address，ipmi_target_channel。
可以修改ipmi协议版本：ipmi_protocol_version。
###DRAC
在 /etc/ironic/ironic.conf 中，添加 pxe_drac 到 enabled_drivers，安装 python-dracclient 包。
###AMT
amt驱动，扩展ironic，通过桌面远程控制电源。pxe_amt，agent_amt。
###SNMP
###iLo driver
###SeaMicro driver
###iRMC
###VirtualBox drivers
###Cisco UCS driver
###Wake-On-Lan driver
###iBoot driver
###CIMC driver
###OneView driver
###XenServer ssh  driver

### 要求
在部署的内存盘上安装和配置IPA。

## agent驱动使用代理下载

###使能代理
1. 设置代理服务器，缓存内容，提升最大缓存容量。可以通过HTTP下载上传，镜像保存在非加密cache。
2. 设置[glance]swift\_temp\_url\_cache\_enabled为True，使用缓存的镜像，查询到URL的镜像变化才生成新的。
3. 设置[glance]swift\_temp\_url\_expected\_download\_start\_delay选项为适合硬件的值，从部署请求到开始下镜像的延迟。估计一下从IPA的ramdisk启动到开始下载的时间。保证URL的有效性。
4. [glance]swift\_temp\_url\_duration，镜像缓存的有效时间，设为1200则20分钟后缓存一个新的镜像。此值大于等于[glance]swift\_temp\_url\_expected\_download\_start\_delay。
5. image\_http\_proxy, image\_https\_proxy, image\_no\_proxy添加到driver\_info，使用不同的代理。

##高级设置

###带外和带内电源控制
部署完ironic会重启机器进入新的镜像系统。默认电源操作由带内完成，即ironic-conductor让IPA的ramdisk自己关机。

部分硬件默认接口不支持，需要Ironic直接让控制器关机并再打开。必须升级节点的driver_info，设置deploy\_forces\_oob\_reboot参数为True，比如：
`ironic node-update <UUID or name> add driver_info/deploy_forces_oob_reboot=True`

##工作流程

###集成Ironic
###兼容部署驱动（agent,pxe）
###发现
agent通过发送硬件配置文件到Ironic vendor\_passthru查找终端，/v1/drivers/{driver}/vendor\_passthru/lookup，决定自己的节点UUID。

###心跳
查找到节点，每N秒通过：
/v1/nodes/{node\_ident}/vendor\_passthru/heartbeat
心跳，设置在Ironic conductor的agent项里，值乘以0.3和0.6之间，以消除连接抖动。

###查询
执行硬件查询，发送到 Ironic inspector。修改镜像中的默认PXE/iPXE设置或IPA选项设置 ipa-inspection-callback-url为完整的终端或 Ironic inspector。
`ipa-inspection-callback-url=http://IP:5050/v1/continue`
确保DHCP环境设为boot IPA。

##硬件详情
使用硬件管理，在发现时发送到 Ironic，以及在查询时发给Inspector。

硬件详情的格式基于使用的硬件管理，详情是一个json目录，至少包含：
**cpu**
模组名，主频，数量，架构，旗标
**memory**
大小，物理大小(物理大小包含内核的内存，稍大，也是nova flavor可以设置节点的，inspector用的)
**bmc\_address**
**disk**
name, model, size (in bytes), rotational (boolean), wwn, serial, vendor, wwn\_with\_extension, wwn\_vendor\_extension
**interfaces**
name, mac\_address, ipv4\_address, lldp, vendor, product,(collect_lldp设为true，lldp即用LLDP的TLV填充)
**system_vendor**
SMBIOS, dmidecode: product\_name, serial\_number and manufacturer.
**boot**
current_boot_mode, pxe_interface

##创建镜像
###CoreOS
在docker里安装创建带文件系统镜像，IPA文件系统镜像运行在systemdnspawn容器内。
###diskimage-builder
采用安装包和配置服务方式创建镜像。
###tinyipa
采用Linux核心最小系统，耗资源小，常用于CI和虚机。
###iso镜像
IPA ramdisk可以打包为iso
`./iso-image-create -o /path/to/output.iso -i /path/to/ipa.initrd -k /path/to/ipa.kernel`
###IPA标志
- --standalone，关闭发现和心跳。
- --debug，开启调试日志

##硬件管理
###硬件管理概述
支持不同硬件平面，任意硬件行为都可以用自己的硬件管理覆盖。
###硬件管理执行方法
修改硬件调用按优先级分发。
如果对应的硬件管理没有这个名字，产生IncompatibleHardwareMethodError，IPA继续下一个硬件管理。任意硬件管理响应了调用被认为是成功的。
如果所有硬件管理都没有响应这个调用，产生HardwareManagerMethodNotFound。
###IPA搭载硬件管理
IPA搭载了GenericHardwareManager，提供基础清除和部署的调用，兼容其他管理。
###自定义硬件管理
支持定制，如把BIOS flashing utility和BIOS 文件做在用户ramdisk里。
用户需要定义子类hardware.HardwareManager或hardware.GenericHardwareManager，仅需一个evaluate\_hardware\_support()调用，返回数字给hardware.HardwareSupport。其指定了先执行哪一个硬件管理。
要执行的调用在list_hardware_info()。
###用户硬件管理和清除
用户定制硬件管理可用在清除时添加额外的步骤。节点删除或从manageable到available时，都会触发clean，如果是用agent\_\*驱动，ironic查询IPA获得清除步骤，IPA调用get_clean_steps()从所有硬件管理获取清除步骤。
用户硬件管理在get_clean_steps()函数里写步骤，创建函数对应每个清除步骤，包含参数node和port。
IPA执行hardware.dispatch_to_managers()，如果有硬件管理里有对应的key，执行。
###版本
###优先级
 执行evaluate_hardware_support()获得每个硬件管理的整数优先级。



