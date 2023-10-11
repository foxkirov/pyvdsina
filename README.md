# pyvdsina
VDSina.ru api wrapper

Base example:
```python
from pyvdsina import Api

api = Api(api_token='api_token')
server = api.create_server(datacenter='ru', server_plan=105, template=36)
```
datacenter - Datacenter class or country code of datacenter ( ru, nl)

server_plan - ServerPlan class or server plan id

template - ServerTemplate or sever template id

delete server:
```python
api.delete_server(server)
```