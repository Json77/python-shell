#disk-image-create镜像生成流程
#安装：
## 源码安装：

```shell
git clone https://git.openstack.org/openstack/diskimage-builder
git clone https://git.openstack.org/openstack/dib-utils
export PATH=$PATH:$(pwd)/diskimage-builder/bin:$(pwd)/dib-utils/bin
```

## pip安装：

```shell
pip install diskimage-builder
```


#制作流程：
##准备阶段
1. 执行命令开始
2. 创建 _IMAGE_CACHE
3. 加载命令库img-defaults，common-defaults
4. 定义结构：ARCH=amd64
5. 加载element路径
6. 加载命令库common-functions，img-functions
7. 解析命令中包含的element（centos7 baremetal dhcp-all-interfaces grub2）（至少有一个发行版，否则报错）
8. 解决element的依赖包（centos7  -python rpm-distro install-types install-bin redhat-common  -init-system  -run-parts manifests baremetal grub2 base pkg-map cache-url yum source-repositories dhcp-all-interfaces package-installs）
9. 解析镜像类型IMAGE_TYPES，文件系统格式FS_TYPE，非xfs格式需要 _IMAGE_ROOT_FS_UUID，根盘标签 _ROOT_LABEL。
10. 创建build路径，tmpfs_check，检查MemTotal是否大于4G，小于则不用tmpfs，用/tmp
11. 创建base，对每个element下每个目录下每个文件检索，按目录分类归类到TMP_HOOKS_PATH

##执行阶段
1. 开始加载TMP_HOOKS_PATH/root.d，这里也叫Target。包括01-ccache，10-centos7-cloud-image（比较服务器镜像和本地缓存有无差异，包括时间差异，有则curl命令下载，解压到mnt），50-yum-cache（挂载yum到mnt），90-base-dib-run-parts（安装dib-run-parts命令）。
2. 重挂载dev，proc，/dev/pts给临时系统用。
3. Target：TMP_HOOKS_PATH/extra-data.d。包括10-create-pkg-map-dir（获取要安装的包列表），20-manifest-dir，50-store-build-settings，98-source-repositories，99-enable-install-types，99-squash-package-instal，99-yum-repo-conf。（后面的都是准备对应yum源，确定要安装的包）
4. Target：pre-install.d。这个就需要执行chroot到临时系统中执行。包括，00-fix-requiretty，00-usr-local-bin-secure-path，01-dib-python，01-install-bin，01-override-yum-arch，01-set-centos-mirror，01-yum-keepcache，02-package-installs（安装各种需要的工具包，centos官方安装的有os-prober，system-logos，grub2-tools，gettext，redhat-lsb-core）， 03-baseline-tools，04-dib-init-system，15-remove-grub（删除grub2包，安装下载的grub2包），99-package-uninstalls。
5. Target：install.d。需要执行chroot到临时系统中执行。包括00-baseline-environment（安装iscsi-initiator-utils及其依赖），00-up-to-date（yum -y update），01-package-installs(安装dhclient，git，traceroute，efibootmgr，grub2-efi-modules，grub2-efi shim，lsof，grub2，ccache，which，tcpdump)，02-grub-install-spec，10-cloud-init，20-install-init-scripts，50-dhcp-all-interfaces，50-store-build-settings，60-remove-cloud-image-interfaces，80-disable-rfc3041，99-package-uninstalls。
6. Target：post-install.d。在chroot执行。包括00-package-installs，01-delete-grubenv，05-fstab-rootfs-label，06-network-config-nonzeroconf，10-enable-init-scripts，95-package-uninstalls，99-reset-yum-conf。
7. 解除各种挂载，loop2上建对应标签的文件系统，检查文件系统，挂载loop2到临时目录。
8. 切换chroot，执行Target：finalise.d，包括01-clean-old-kernels（安装yum-utils，擦除老kernel），90-selinux-fixfiles-restore，99-cleanup-tmp-grub（删除临时grub）。
9. 执行Target：cleanup.d，包括01-ccache，01-copy-manifests-dir，99-extract-kernel-and-ramdisk（拷贝出vmlinuz和initrd），99-remove-yum-repo-conf，99-tidy-logs。
10. 删除和解挂临时文件，qemu-img命令生成qcow2镜像，退出。


#elements解析
常见elements的编写和使用

## dib-init-system
**作用**：用于运行系统初始化脚本。
**文件**：分为environment，pre，install，post，在不同的安装阶段运行脚本。

##rpm-distro
**作用**：分区。
**文件**：pre主要解决sudo权限，调整yum结构。post阶段05-fstab-rootfs-label修改fstab的label，添加网络设置NOZEROCONF=yes，finalise.d修复selinux的label。

##partitioning-sfdisk
**作用**：分区。
**文件**：通过DIB_PARTITIONING_SFDISK_SCHEMA=字符串来分区，environment里的10-partitioning-sfdisk用来存分区的环境变量，block-device.d里的10-partitioning-sfdisk用来执行sfdisk命令，按字符串格式。

## ironic-agent

**作用**：ironic客户端工具，安装ironic-python-agent。同时安装`dhcp-all-interfaces`，禁止`iptables`服务，禁止`ufw`服务，安装IPA需要的包`qemu-utils` `parted` `hdparm` `util-linux` `genisoimage`，安装`python-dev` 和`gcc`建立源， 安装验证（CA或自签名验证）。注：使用镜像需要至少1.5Gram。

**文件**：

## dhcp-all-interfaces

**作用**：自动检索所有网络接口并设为DHCP。

**说明**：需要多个网络接口用于裸机，在此之前不知道哪个可用，所以在第一次boot时，在每个网口执行一次`dhcpclient`。non-Gentoo分支，在网络服务启用前，调用`/usr/local/sbin/dhcp-all-interfaces.sh`。

Gentoo分支，安装dhcpcd包，在boot时，启动服务，自动从dhcp起所有网口。

**文件**：

## grub2

**作用**：安装grub2 bootloader

**说明**：



# 生成镜像实例

## 创建带账号密码的centos7镜像

### 环境变量：

export DIB_DEV_USER_PWDLESS_SUDO="yes"
export DIB_DEV_USER_USERNAME="user"
export DIB_DEV_USER_PASSWORD="password"

### 部署及用户镜像：

```shell
disk-image-create ironic-agent centos7 -o ironic-deploy
```

```shell
disk-image-create centos7 baremetal dhcp-all-interfaces grub2 -o my-image
```




