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

This module also provides a client for other API interactions with Elimity Insights. The snippet below shows how to
authenticate with an API token and list sources at an Elimity Insights server. You can generate a token identifier and
secret by visiting the 'API tokens' page in Elimity Insights and clicking the 'CREATE API TOKEN' button.

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
