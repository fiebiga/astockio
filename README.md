# Description

A personal POC to implement a basic stock exchange architecture. Tooling wise, the following tools were used
* Kafka: Event driven asynchronous processing and messaging
* FastAPI/Guvicorn: Web API Development
* Redis: Caching and Zset for sorted items
* MongoDB: General data persistence

The primarily role of this project will be to see how well asyncio driven python processes, which excel large numbers of small I/O operations,
are able to process millions of I/O bound transactions in a short amount of time in a humble docker compose deployment

It also just sounded like a neat thing to slap together. **There will be no sensitive data used by this application**

- [Architecture Diagram](#architecture)
- [Services](#services)
  - [Orders](#orders)
  - [Order Exchange](#order-exchange)
  - [Order Fulfillment](#order-fulfillment)
  - [Users](#users)
  - [Users Stock Ledger](#users-stock-ledger)
  - [Users Accounts](#users-accounts)
  - [Users Orders](#users-orders)
- [Getting Started](#getting-started)

# DynamoDB <a name="architecture"></a>
![Architecture Diagram](docs/stock_exchange_diagram.png?raw=true "Stock Exchange ~~Flow~~")

