## 修改清单

> 在_custom_action里增加我们需要的url，并添加对应的方法。方法中通过rpc调用。

`/usr/lib/python2.7/site-packages/ironic/api/controllers/v1/node.py`

```python
class NodesController(rest.RestController):
    _custom_actions = {
        'detail': ['GET'],
        'validate': ['GET'],
        'progress': ['GET'],
    }
    
    @expose.expose(wtypes.text, types.uuid_or_name, types.uuid)
    def progress(self, node=None, node_uuid=None):
        """Get the install progress using the node's UUID or name

        :param node: UUID or name of a node.
        :param node_uuid: UUID of a node.
        """
        if node is not None:
            # We're invoking this interface using positional notation, or
            # explicitly using 'node'.  Try and determine which one.
            if (not api_utils.allow_node_logical_names() and
                    not uuidutils.is_uuid_like(node)):
                raise exception.NotAcceptable()

        rpc_node = api_utils.get_rpc_node(node_uuid or node)
        topic = pecan.request.rpcapi.get_topic_for(rpc_node)
        return pecan.request.rpcapi.progress_interfaces(
            pecan.request.context, rpc_node.uuid, topic)
```



> 这里接收api发过来的信号，调用对应的方法。

`/usr/lib/python2.7/site-packages/ironic/conductor/rpcapi.py`

```python
class ConductorAPI(object):
    
        def progress_interfaces(self, context, node_id, topic=None):
        cctxt = self.client.prepare(topic=topic or self.topic, version='1.5')
        return cctxt.call(context, 'progress_interfaces',
                          node_id=node_id)
```



> manager.py是通过rpc调用的实现代码。

`/usr/lib/python2.7/site-packages/ironic/conductor/manager.py`



```python
class ConductorManager(base_manager.BaseConductorManager):
    
    @messaging.expected_exceptions(exception.NodeLocked)
    def progress_interfaces(self, context, node_id):
        """Validate the `core` and `standardized` interfaces for drivers.

        :param context: request context.
        :param node_id: node id or uuid.
        :returns: a dictionary containing the results of each
                  interface validation.

        """
        LOG.debug('RPC progress_interfaces called for node %s.',
                  node_id)
        ret_dict = {'progress': '10%'}
        return ret_dict
```



