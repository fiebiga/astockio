#!/bin/bash

if [[ $1 == "exchange" ]]
then
  python exchange/async.py
fi

if [[ $1 == "order_fulfillment" ]]
then
  python order_fulfillment/async.py
fi

if [[ $1 == "orders" ]]
then
  #python orders/async.py
  uvicorn orders.web:app --host "0.0.0.0" --port 9000
fi
