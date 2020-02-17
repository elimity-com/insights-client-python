import logging

from client import Client, Config, AttributeType, Type, DomainGraph, Entity, Relationship
from util import random_string

config = Config('admin', 'admin', 'https://local.elimity.com:8081/api')

graph = DomainGraph(
    entities=[Entity(True, [], 'id0', 'userA', 'user'), Entity(True, [], 'id1', 'roleA', 'user')],
    relationships=[Relationship([], 'id0', 'user', 'id1', 'role')]
)

try:
    c = Client(config, disable_ssl_check=True)
    c.create_attribute_type(AttributeType('user', random_string(5), Type.STRING, 'some description'))
    c.reload_domain_graph(graph)
except Exception as exception:
    logging.error(exception)
else:
    logging.info('import finished successfully')
