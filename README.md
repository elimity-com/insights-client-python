# Elimity Insights Python client

This Python module provides a client for connector interactions with an Elimity
Insights server.

## Usage

```python3
from datetime import datetime

from elimity_insights_client import Client, Config, ConnectorLog, Level

if __name__ == "__main__":
    config = Config(url="https://local.elimity.com:8081", token="token")
    client = Client(config)

    timestamp = datetime.now()
    log = ConnectorLog(level=Level.INFO, message="Hello world!", timestamp=timestamp)
    logs = [log]
    client.create_connector_logs(logs)
```

## Installation

```sh
$ pip install git+https://github.com/elimity-com/insights-client-python.git
```

## Compatibility

| Client version | Insights version |
| -------------- | ---------------- |
| 1              | 2.8 - 2.10       |
| 2 - 3          | 2.11 - 3.0       |
| 4              | 3.1 - 3.3        |
| 5 - 6          | ^3.4             |
