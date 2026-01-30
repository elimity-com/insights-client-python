# Elimity Insights Python client

This Python module provides a client for connector interactions with an Elimity
Insights server.

## Usage

### Importing data to custom sources

The following snippet shows how to authenticate as a custom source and create a connector log at an Elimity Insights
server. You can generate a source identifier and token by visiting the custom source's detail page in Elimity Insights
and clicking the 'GENERATE CREDENTIALS' button, which can be found under the 'SETTINGS' tab.

```python3
from datetime import datetime

from elimity_insights_client import Client, Config, ConnectorLog, Level

if __name__ == "__main__":
    config = Config(id=1, url="https://local.elimity.com:8081", token="token")
    client = Client(config)

    timestamp = datetime.now()
    log = ConnectorLog(level=Level.INFO, message="Hello world!", timestamp=timestamp)
    logs = [log]
    client.create_connector_logs(logs)
```

### Other API interactions

This module also provides a client for other API interactions with Elimity Insights. The snippets below show how to
execute queries and list sources respectively. Both use an API token for authentication. You can generate a token
identifier and secret by visiting the 'API tokens' page in Elimity Insights and clicking the 'CREATE API TOKEN' button.

#### Executing queries

The following example performs the query "find all users for which isShareByEmailGuestUser is true" on source with identifier `1` without specific attributes, ordering or grouping.

```python3
from elimity_insights_client.api import Config, query
from elimity_insights_client.api.expression import AttributeBooleanExpression
from elimity_insights_client.query import AnyExpression, DirectLinkGroupByQuery, DirectLinkQuery, LinkGroupByQuery, Ordering, Query

if __name__ == "__main__":
    config = Config(token_id="1", token_secret="my-secret-value", url="https://example.elimity.com", verify_ssl=True)
    condition = AttributeBooleanExpression("isShareByEmailGuestUser", "u")
    direct_link_group_by_queries: list[DirectLinkGroupByQuery] = []
    direct_link_queries: list[DirectLinkQuery] = []
    include: list[AnyExpression] = []
    link_group_by_queries: list[LinkGroupByQuery] = []
    link_queries: list[Query] = []
    orderings: list[Ordering] = []
    q = Query(
        "u", condition, direct_link_group_by_queries, direct_link_queries, "user", include, 10, link_group_by_queries,
        link_queries, 0, orderings, 1
    )
    queries = [q]
    pages = query(config, queries)
    print(pages)
```

#### Listing sources

```python3
from elimity_insights_client.api import Config, sources

if __name__ == "__main__":
    config = Config(token_id="1", token_secret="my-secret-value", url="https://example.elimity.com", verify_ssl=True)
    my_sources = sources(config)
    print(my_sources)
```

## Installation

```sh
$ pip install elimity-insights-client
```

## Compatibility

| Client version | Insights version |
| -------------- | ---------------- |
| 1              | 2.8 - 2.10       |
| 2 - 3          | 2.11 - 3.0       |
| 4              | 3.1 - 3.3        |
| 5 - 6          | 3.4 - 3.5        |
| 7              | 3.6 - 3.7        |
| 8              | 3.8 - 3.15       |
| 9              | ^3.16            |
