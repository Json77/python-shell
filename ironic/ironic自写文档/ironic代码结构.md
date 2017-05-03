# ironic代码结构

```
ironic-stable-liberty:.
│  babel.cfg
│  CONTRIBUTING.rst
│  driver-requirements.txt
│  LICENSE
│  MANIFEST.in
│  openstack-common.conf
│  README.rst
│  RELEASE-NOTES
│  requirements.txt
│  setup.cfg      #pbr的配置文件
│  setup.py 
│  test-requirements.txt
│  tox.ini        #tox配置文件
│  vagrant.yaml
│  Vagrantfile
├─doc   #文档       
├─etc  #相关配置文件 
├─ironic
│  │  
│  ├─api        #api,使用peach框架
│  │  │  acl.py
│  │  │  app.py     #API入口
│  │  │  app.wsgi
│  │  │  config.py
│  │  │  expose.py
│  │  │  hooks.py
│  │  │  __init__.py
│  │  │  
│  │  ├─controllers   #控制器
│  │  │  │  base.py
│  │  │  │  link.py
│  │  │  │  root.py   #API总控制器
│  │  │  │  __init__.py
│  │  │  │  
│  │  │  └─v1      #v1 版本API
│  │  └─middleware
│  ├─cmd            # 服务入口
│  │      api.py
│  │      conductor.py
│  │      dbsync.py
│  │      __init__.py
│  ├─common  常用方法
│  ├─conductor  
│  │      manager.py  
│  │      rpcapi.py
│  │      task_manager.py
│  │      utils.py
│  │      __init__.py
│  ├─db    #数据库相关，包括sqlalchemy、alembic
│  ├─dhcp  #neutron dhcp api
│  │      base.py
│  │      neutron.py
│  │      none.py
│  │      __init__.py
│  ├─drivers    #驱动相关
│  │  │  agent.py    #agent_* 驱动
│  │  │  base.py
│  │  │  drac.py     #drac驱动
│  │  │  fake.py
│  │  │  ilo.py      #ilo驱动，惠普的
│  │  │  irmc.py     #irmc
│  │  │  pxe.py      #pxe_* 驱动
│  │  │  raid_config_schema.json
│  │  │  utils.py
│  │  │  __init__.py
│  │  └─modules     #驱动的具体方法
│  ├─locale      #翻译
│  ├─nova        #nova相关，这里包括与Nova computer冲突的临时解决办法
│  ├─objects     #基本对象的方法，包括conducotr、node、port、field、chassis
│  ├─openstack  #openstack相关的，这里包含处理镜像的方法的帮助函数
│  └─tests    #测试相关
├─releasenotes   #发布历史
└─tools     #相关工具
```



## ironic

### api



### conductor

#### manage.py

```python
class ConductorManager(base_manager.BaseConductorManager):
     def __init__(self, host, topic):
     def create_node(self, context, node_obj):
     def update_node(self, context, node_obj):
     def update_node(self, context, node_obj):
     def change_node_power_state(self, context, node_id, new_state):
     def vendor_passthru(self, context, node_id, driver_method,http_method, info):
        '''供应商定制node操作，需要uuid，在validate里'''
     def driver_vendor_passthru(self, context, driver_name, driver_method, http_method, info):
     	'''供应商定制底层操作，不需要uuid，随机选一个用了供应商驱动的conductor'''
     def get_node_vendor_passthru_methods(self, context, node_id):
     def get_driver_vendor_passthru_methods(self, context, driver_name):
     def do_node_deploy(self, context, node_id, rebuild=False,configdrive=None):
        '''
        部署节点，validate同步，实际部署工作异步。有同步锁定
        验证镜像类型，是否wholedisk。
        '''
        
     
```