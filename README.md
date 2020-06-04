# Elimity Insights Python client

This Python module provides a client for connector interactions with an Elimity
Insights server.

## Usage

```python
from datetime import datetime

from elimity_insights_client import Client, Config, ConnectorLog, Level

if __name__ == "__main__":
    config = Config(base_path="https://local.elimity.com:8081/api", token="token")
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
| 1              | ^2.8             |