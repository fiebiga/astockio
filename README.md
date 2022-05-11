# Description

A personal POC to implement a basic stock exchange architecture. Tooling wise, the following tools were used
* Kafka: Event driven asynchronous processing and messaging
* FastAPI/Guvicorn: Web API
* Redis: Caching and Zset for sorted items
* MongoDB: General data persistence*

*This is now being converted to MariaDB. Upon further analysis of the use cases, stronger ACID reliability is preferred over the 
data flexibility and distributed scability that NoSQL offers. That said, if MySQL is good enough for Facebook, it's good enough for a stock exchange

The primarily role of this project will be to see how well asyncio driven python processes, which excel large numbers of small I/O operations,
are able to process millions of I/O bound transactions in a short amount of time in a humble docker compose deployment

It also just sounded like a neat thing to slap together. **There will be no sensitive data used by this application**

- [Architecture Diagram](#architecture)
- [Roadmap](#roadmap)
- [Services](#services)
  - [Orders](#orders)
  - [Order Exchange](#order-exchange)
  - [Order Fulfillment](#order-fulfillment)
  - [Users](#users)
  - [Users Stock Ledger](#users-stock-ledger)
  - [Users Accounts](#users-accounts)
  - [Users Orders](#users-orders)
- [Getting Started](#getting-started)

# Architecture Diagram <a name="architecture"></a>
![Architecture Diagram](docs/stock_exchange_diagram.png?raw=true "Stock Exchange ~~Flow~~")

# Roadmap <a name="roadmap"></a>
1. Convert MongoDB to MariaDB
2. Implement User Ledger and Account Service
3. Implement User Order Service
4. Exclusion of user ability to have simultaneous buy and sell orders for the same stock
5. Implement Proper Exchange of stocks and account balances in Order Fulfillment Service
6. Order Lifecycle introspection and record logging
7. Implement ability for a user to request "all or nothing" batch transactions instead of streamed fulfillment
8. Nginx proxy in front of all uvicorn hosted localhost web servers
9. Front End UI for basic order/user account balance

# Getting Started <a name="getting-started"></a>
In order to get started with the provided configuration, docker must be installed, as well as docker-compose. Beyond that,
all one needs is to execute the following command

```shell
docker-compose up
```

From then on you may access [The Fast API Documentation](http://localhost:8000/docs), available on localhost, to get started
