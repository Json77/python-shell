# ironic镜像部署代码流程：

主要是由nova api，触发node provision状态变化，ironic检测到状态改变，在conductor manager里管理。根据驱动名找到不同驱动模块，进行部署。

跟镜像有关的从：
Z:\home\zs\ironicsc\ironic\ironic\conductor\manager.py开始
```python
def do_node_deploy(task, conductor_id, configdrive=None):
    ##开始节点部署，先有异常处理，然后进入prepare阶段
```

###perpare阶段
Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\iscsi_deploy.py
```python
def prepare(self, task):
    task.driver.boot.prepare_ramdisk(task, deploy_opts)
    ##这里判断provision状态，处理电源关机，网络，IPA设置，然后做上面的task。
```

Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\pxe.py
```python
class PXEBoot(base.BootInterface):
    def prepare_ramdisk(self, task, ramdisk_params):
        ##这里设置了dhcp，加载了配置文件里[pxe]里的配置项，主要有tftpboot路径，镜像缓存路径等
        pxe_info = _get_deploy_image_info(node)
        if node.provision_state == states.DEPLOYING:
            pxe_info.update(_get_instance_image_info(node, task.context))
        ##更新ironic，conf里的pxe设置，这两个method生成了node和镜像的绝对路径的对应关系的list，注，是四个镜像，deploy_kernel，deploy_initrd，user_kernel，user_initrd。根据label=kernel，initrd匹配。这里需要考虑，多个不同系统时，镜像重名的问题，做假镜像的难点。
        _cache_ramdisk_kernel(task.context, node, pxe_info)
        ##这个method用来缓存上面建立了关系的镜像到master_images（路径是配置项决定的）。
```

（这一段是对上面三个method的解释）            
Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\pxe.py
```python
def _get_deploy_image_info(node):
    ##获取部署镜像信息
def _get_instance_image_info(node, ctx):
    ##获取用户镜像信息
##生成了镜像list，在pxe_info里
def _cache_ramdisk_kernel(ctx, node, pxe_info):
    deploy_utils.fetch_images(ctx, TFTPImageCache(), list(pxe_info.values()),
                          CONF.force_raw_images)
##把kernel和initrd拷到master_images
```

（这一段是具体的缓存拷贝函数）
Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\deploy_utils.py
```python
def fetch_images(ctx, cache, images_info, force_raw=True):
    image_cache.clean_up_caches(ctx, cache.master_dir, images_info)
    for href, path in images_info:
        cache.fetch_image(href, path, ctx=ctx, force_raw=force_raw)
```
Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\image_cache.py
    def fetch_image(self, href, dest_path, ctx=None, force_raw=True):
    def _download_image(self, href, master_path, dest_path, ctx=None,force_raw=True):

> 注意：缓存部分有老镜像的清除处理！这个之前部署的时候，如果出错，master_images和node_uuid这两个文件夹没删掉，会导致部署到以前的镜像问题。

最后是prepare的异常处理

###deploy阶段
Z:\home\zs\ironicsc\ironic\ironic\drivers\modules\iscsi_deploy.py
```python
def deploy(self, task):
    cache_instance_image(task.context, node)
    #缓存用户镜像，deploy的代码简单，缓存镜像，检查镜像大小，重启，返回部署等待状态。

def cache_instance_image(ctx, node):
    #建立node和用户镜像绝对路径的关系，获取镜像。
    deploy_utils.fetch_images(ctx, InstanceImageCache(), [(uuid, image_path)],
                            CONF.force_raw_images)
```

调用的也是上面的拷贝函数，见上面的缓存拷贝函数。这里的缓存路径在设置文件里默认为#instance_master_path=/var/lib/ironic/master_images。
