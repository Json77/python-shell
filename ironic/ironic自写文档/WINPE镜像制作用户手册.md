# WINPE镜像制作用户手册

## 1.环境准备
win7环境：
1. 一台windows 7机器。
2. 在https://www.microsoft.com/zh-CN/download/details.aspx?id=5753下载AIK，并按说明安装。
3. 管理员权限。
win8环境：
1. https://technet.microsoft.com/zh-cn/library/hh825212.aspx下载ADK，按说明继续。
2. 管理员权限。

## 2. 使用命令行工具拷贝必要的文件

win7环境以管理员权限运行**Windows Start** -> **All Programs** -> **Microsoft Windows AIK** -> **Deployment Tools Command Prompt**

在E盘创建目录E:\winPE_amd64并将必要的文件复制进去。（这里假设AIK安装在C盘，其他盘同理，如果要制作32位系统的winpe，只需将文中所有的`amd64`改为`x86`，另外，windows默认不区分大小写）

```powershell
copy "C:\Program Files\Windows AIK\Tools\PETools\amd64\winpe.wim" E:\winpe_amd64\ISO\Sources\Boot.wim
copy "C:\Program Files\Windows AIK\Tools\amd64\Imagex.exe" E:\winpe_amd64\ISO\
```

win8环境以管理员权限运行**Windows Start** -> **All Programs** -> **Windows Kits** -> **Windows ADK** -> **Deployment Tools Command Prompt**

在E盘创建目录E:\winpe并将必要的文件复制进去。（这里默认运行时就在安装目录下，如果要制作32位系统的winpe，只需将文中所有的`amd64`改为`x86`，另外，windows默认不区分大小写）

```powershell
copype amd64 e:\winpe_5x64或copype x86 e:\winpe_5x86
```

## 3. 挂载和修改镜像

下面用DISM工具挂载并修改镜像，DISM工具随AIK工具一起安装：

```powershell
# mount
Dism /Mount-Wim /WimFile:E:\winPE_amd64\ISO\sources\boot.wim /index:1 /MountDir:E:\winPE_amd64\mount

# 加入驱动（第三方驱动复制到drivers目录，执行命令安装。也可以指定drivers的目录）
dism /image:E:\winPE_amd64\mount /add-driver /driver:E:\winPE_amd64\drivers /recurse /forceunsigned

# 添加程序包
Dism /Image:E:\winpe5\mount /Add-Package /PackagePath:"C:\Program Files (x86)\Windows Kits\8.1\Assessment and Deployment Kit\Windows Preinstallation Environment\amd64\WinPE_OCs\WinPE-WinReCfg.cab"

# 添加相应的语言包。
Dism /Image:E:\winpe5\mount /Add-Package /PackagePath:"C:\Program Files (x86)\Windows Kits\8.1\Assessment and Deployment Kit\Windows Preinstallation Environment\amd64\WinPE_OCs\en-us\WinPE-WinReCfg_en-us.cab"

# 查看驱动
dism /image:E:\winPE_amd64\mount /get-drivers /format:table > E:\winPE_amd64\wim-table.txt

#删除驱动，删除驱动后文件并没有删除
Dism /Image:E:\winPE_amd64\mount /Remove-Driver /Driver:OEM1.inf /Driver:OEM2.inf

## 改启动脚本（startnet.cmd文件在mount后的system32目录中，即E:\winPE_amd64\mount\system32\startnet.cmd）
#wpeinit
#net use z: \\192.168.1.1\install\x64  #这里的ip填提供samba服务的节点ip，后面的目录根据samba共享镜像目录填写
#z:
#setup.exe
## 这一部分在linux下会使用wimtool工具在脚本中配置，可以略过。

# 删除ISO\BOOT\bootfix.bin（可以去掉启动时选择是否从光盘启动的交互，同样会使用wimtool工具由脚本配，略过。）

# 提交更改
Dism /unmount-Wim /MountDir:E:\winPE_amd64\mount /Commit
#如果umount失败，删除文件后，执行dism /cleanup-wim。commit参数是必须的，表示保存更改。/commit是提交修改，/discard放弃

# 重新制作pe.iso
win7的pe3.0
oscdimg -n -bE:\winpe_amd64\etfsboot.com E:\winpe_amd64\ISO E:\winpe_amd64\winpe_amd64.iso
windows_server_2012的pe5.0
oscdimg -n -bE:\winpe5\fwfiles\etfsboot.com E:\winpe5\media E:\winpe5\winpe_amd64.iso

# 日志
C:\Windows\Logs\DISM
```

## 4. 制作完成

完成后，将生成的winpe镜像拷贝到作ironic安装的计算节点所在的控制节点，作为部署镜像加入glance中。

