# Linux环境采用pxe自动安装windows

>  以win7旗舰版64位为例

## 1. 准备dhcp服务器

安装dhcp

```shell
yum install -y dhcp
```

配置dhcp

```
ddns-update-style ad-hoc;^M
option space PXE;^M
option PXE.mtftp-ip               code 1 = ip-address;  ^M
option PXE.mtftp-cport            code 2 = unsigned integer 16;^M
option PXE.mtftp-sport            code 3 = unsigned integer 16;^M
option PXE.mtftp-tmout            code 4 = unsigned integer 8;^M
option PXE.mtftp-delay            code 5 = unsigned integer 8;^M
option PXE.discovery-control      code 6 = unsigned integer 8;^M
option PXE.discovery-mcast-addr   code 7 = ip-address;^M
^M
class "pxeclients" {^M
match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";^M
option vendor-class-identifier "PXEClient";^M
vendor-option-space PXE;^M
option PXE.mtftp-ip 0.0.0.0;^M
filename "/pxelinux.0";^M
next-server 192.168.1.1;
}^M
^M
ddns-update-style interim;^M
ignore client-updates;^M
default-lease-time 86400;^M
max-lease-time 604800;^M
shared-network 0 {^M
subnet 192.168.1.0 netmask 255.255.255.0 {^M
option routers 192.168.1.1;^M
option subnet-mask 255.255.255.0;^M
range 192.168.1.100 192.168.1.200;^M
^M
}^M
^M
}^M
```

重启网络和dhcp服务

## 2. 准备tftp服务器

准备tftp服务器，引导裸机下载memdisk和pe小系统。

安装服务器：

```shell
yum install tftp-server.x86_64 xinetd.x86_64
```

建立目录：

```shell
mkdir /tftpboot
mkdir /tftpboot/pxelinux.cfg/
```

创建default文件：

```
default win7
prompt   10  
timeout  300 
ONTIMEOUT win7
MENU TITLE PXE Menu
label win7
        MENU LABEL Windwos7
        kernel memdisk 
        initrd windows/winpe_amd64.iso
        append iso raw 
        MENU end
```

## 3. 制作winPE镜像

### windows环境：

下载安装Windows Automated Installation Kit。

以管理员权限运行**Windows Start** -> **All Programs** -> **Microsoft Windows AIK** -> **Deployment Tools Command Prompt**

在E盘创建目录E:\winPE_amd64并将必要的文件复制进去。

```
copy "C:\Program Files\Windows AIK\Tools\PETools\amd64\winpe.wim" E:\winpe_amd64\ISO\Sources\Boot.wim
copy "C:\Program Files\Windows AIK\Tools\amd64\Imagex.exe" E:\winpe_amd64\ISO\
```

下面用DISM工具挂载并修改镜像：

```
# mount
Dism /Mount-Wim /WimFile:E:\winPE_amd64\ISO\sources\boot.wim /index:1 /MountDir:E:\winPE_amd64\mount

# 加入驱动（第三方驱动复制到drivers目录，执行命令安装）
dism /image:E:\winPE_amd64\mount /add-driver /driver:E:\winPE_amd64\drivers /recurse /forceunsigned

# 查看驱动
dism /image:E:\winPE_amd64\mount /get-drivers /format:table > C:\Users\10200024\Desktop\wim-table.txt

# 改启动脚本（startnet.cmd文件在mount后的system32目录中）
startnet.cmd
wpeinit
net use z: \\192.168.1.1\install\x64
z:
setup.exe

# 删除ISO\BOOT\bootfix.bin（可以去掉启动时选择是否从光盘启动的交互）

# 提交更改
Dism /unmount-Wim /MountDir:E:\winPE_amd64\mount /Commit
（umount失败，删除文件后，dism /cleanup-wim）

# 重新制作pe.iso
oscdimg -n -bE:\winpe_amd64\etfsboot.com E:\winpe_amd64\ISO E:\winpe_amd64\winpe_amd64.iso

# 日志
C:\Windows\Logs\DISM
```

### linux环境：

安装：

wimtools-1.9.2-1.el7.nux.x86_64
libwim15-1.9.2-1.el7.nux.x86_64工具包

按dsim一样的方式操作。

完成后：

将镜像中的memdisk拷贝到/tftpboot

将做成的pe拷贝到/tftpboot/windows

## 4. 准备samba服务器

```shell
yum install samba samba-common samba-winbind 
```

修改服务器配置，修改后一段时间自动加载，或重启smb服务加载

```shell
vi /etc/samba/smb.conf
[global]
        workgroup = PXESERVER
        server string = Samba Server Version %v
        log file = /var/log/samba/log.%m
        max log size = 50
        idmap config * : backend = tdb
        cups options = raw
        netbios name = pxe
        map to guest = bad user
        dns proxy = no
        public = yes
        ## For multiple installations the same time - not lock kernel
        kernel oplocks = no
        nt acl support = no
        security = user
        guest account = nobody
[install]
        comment = Windows 7 Image 
        path = /windows
        read only = no
        browseable = yes
        public = yes
        printable = no
        guest ok = yes
        oplocks = no
        level2 oplocks = no
        locking = no
```

建立/windows路径给用户存放镜像。

```shell
systemctl enable smb
systemctl start smb
```

## 5. 准备安装镜像

在/windows下建立目录win7x64，将镜像文件mount到该目录

```shell
mkdir -p /windows/win7x64
mount /home/win7x64.iso /windows/win7x64
chmod -R 0755 /windows
chown -R nobody:nobody /windows
```

## 6. windows自动配置安装

在windows下同样使用Windows Automated Installation Kit工具生成windows自动安装的xml文件。生成后也可以直接修改xml文件（linux下即这么操作）。完成之后，命名为Autounattend.xml放在samba目录下mount出来的大镜像里。即/windows/win7x64/sources目录。

这里给一个示例xml文件。

```xml
<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
    <settings pass="windowsPE">
        <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <ImageInstall>
                <OSImage>
                    <InstallFrom>
                        <MetaData wcm:action="add">
                            <Key>/IMAGE/NAME</Key>
                            <Value>Windows 7 ULTIMATE</Value>
                        </MetaData>
                    </InstallFrom>
                    <InstallTo>
                        <DiskID>0</DiskID>
                        <PartitionID>1</PartitionID>
                    </InstallTo>
                </OSImage>
            </ImageInstall>
            <UserData>
                <ProductKey>
                    <Key>FJ82H-XT6CR-J8D7P-XQJJ2-GPDD4</Key>
                    <WillShowUI>Never</WillShowUI>
                </ProductKey>
                <AcceptEula>true</AcceptEula>
            </UserData>
            <DiskConfiguration>
                <WillShowUI>Never</WillShowUI>
                <Disk wcm:action="add">
                    <CreatePartitions>
                        <CreatePartition wcm:action="add">
                            <Order>1</Order>
                            <Size>100000</Size>
                            <Type>Primary</Type>
                        </CreatePartition>
                    </CreatePartitions>
                    <ModifyPartitions>
                        <ModifyPartition wcm:action="add">
                            <Active>true</Active>
                            <Extend>false</Extend>
                            <Format>NTFS</Format>
                            <Letter>C</Letter>
                                                        <Order>1</Order>
                            <PartitionID>1</PartitionID>
                        </ModifyPartition>
                    </ModifyPartitions>
                    <DiskID>0</DiskID>
                    <WillWipeDisk>true</WillWipeDisk>
                </Disk>
            </DiskConfiguration>
        </component>
        <component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <SetupUILanguage>
                <WillShowUI>Never</WillShowUI>
                <UILanguage>en-US</UILanguage>
            </SetupUILanguage>
            <UILanguage>en-US</UILanguage>
        </component>
        <component name="Microsoft-Windows-PnpCustomizationsWinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <DriverPaths>
                <PathAndCredentials wcm:action="add" wcm:keyValue="1">
                    <Path>z:\realtek81xx</Path>
                </PathAndCredentials>
            </DriverPaths>
        </component>
    </settings>
    <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <ComputerName>vagrant-win7</ComputerName>
            <TimeZone>Pacific Standard Time</TimeZone>
        </component>
        <component name="Microsoft-Windows-TCPIP" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <Interfaces>
                <Interface wcm:action="add">
                    <Ipv4Settings>
                        <DhcpEnabled>false</DhcpEnabled>
                        <Metric>20</Metric>
                        <RouterDiscoveryEnabled>false</RouterDiscoveryEnabled>
                    </Ipv4Settings>
                    <Identifier>20-12-00-00-00-10</Identifier>
                    <UnicastIpAddresses>
                        <IpAddress wcm:action="add" wcm:keyValue="1">192.168.5.161/24</IpAddress>
                    </UnicastIpAddresses>
                </Interface>
            </Interfaces>
        </component>
        <component name="Networking-MPSSVC-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <DomainProfile_EnableFirewall>false</DomainProfile_EnableFirewall>
            <PrivateProfile_EnableFirewall>false</PrivateProfile_EnableFirewall>
            <PublicProfile_EnableFirewall>false</PublicProfile_EnableFirewall>
        </component>
    </settings>
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <Display>
                <ColorDepth>32</ColorDepth>
                <DPI>96</DPI>
                <HorizontalResolution>1024</HorizontalResolution>
                <RefreshRate>60</RefreshRate>
                <VerticalResolution>768</VerticalResolution>
            </Display>
            <AutoLogon>
                <Enabled>true</Enabled>
                <Username>Administrator</Username>
            </AutoLogon>
            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <NetworkLocation>Work</NetworkLocation>
                <ProtectYourPC>3</ProtectYourPC>
            </OOBE>
            <FirstLogonCommands>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Prepare to copy Logs&quot; &gt; c:\log.txt</CommandLine>
                    <Order>1</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Mounting samba...&quot; &gt;&gt; c:\log.txt</CommandLine>
                    <Order>2</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                     </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <Order>3</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                    <CommandLine>cmd /c net use p: \\192.168.1.1\install</CommandLine>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Mount done&quot; &gt;&gt; c:\log.txt</CommandLine>
                    <Order>4</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Wait a while for connectivity ...&quot; &gt;&gt; c:\log.txt</CommandLine>
                    <Order>5</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c ping 127.0.0.1 -n 5 -w 1000</CommandLine>
                    <Order>6</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Start copy logs files from %WINDIR\Panther%&quot; &gt;&gt; c:\log.txt</CommandLine>
                    <Order>7</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c copy %WINDIR%\Panther\*.log p:\</CommandLine>
                    <Order>8</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
                <SynchronousCommand wcm:action="add">
                    <CommandLine>cmd /c echo &quot;%TIME% Copy Done&quot; &gt;&gt; c:\log.txt</CommandLine>
                    <Order>9</Order>
                    <RequiresUserInput>false</RequiresUserInput>
                </SynchronousCommand>
            </FirstLogonCommands>
        </component>
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <UserAccounts>
                <LocalAccounts>
                <LocalAccount wcm:action="add">
                        <Name>Administrator</Name>
                        <Group>Administrators</Group>
                    </LocalAccount>
                </LocalAccounts>
            </UserAccounts>
        </component>
    </settings>
    <settings pass="offlineServicing">
        <component name="Microsoft-Windows-LUA-Settings" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <EnableLUA>false</EnableLUA>
        </component>
    </settings>
    <cpi:offlineImage cpi:source="wim://10.43.112.155/home/windows/x64/sources/install.wim#Windows 7 ULTIMATE" xmlns:cpi="urn:schemas-microsoft-com:cpi" />
</unattend>
```

xml文件里还做了挂载samba，并向samba目录中写入日志文件的操作。这个文件解决了所有的windows配置项的交互，相当于linux anaconda安装的ks文件。

## 7.windows安装进度

采用上面的xml文件中执行命令写入samba的日志文件，可以分析得到windows安装完成的记录，由于windows安装会多次重启（至少2次），无法像anaconda一样用rsyslog返回日志。



至此，windows自动pxe安装结束。