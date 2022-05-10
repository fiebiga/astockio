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

# Services
- **put_record:**- Insert a record into DynamoDB. This replaces the existing record entirely.
- **delete_record:**- Delete a single record from DynamoDB.
- **update_record:**- Update a record in DynamoDB. This operates as an upsert.
- **batch_update_records:**- Update multiple records concurrently via futures concurrent batching
- **does_record_exist:**- Whether or not a record(s) exists matching this partition key and sort key value. More optimized than get_record as it does not return the record iself
- **put_records:**- Insert records in batch using the dynamodb batch writer API.
- **delete_records:**- Delete record(s) based on sort key matching.
- **batch_delete_records:**- Delete records in batch matching the sort key and partition keys of each item.
- **get_record:**- Get (Read) a record from DynamoDB.
- **batch_get_records:**- Get all records matching the partition_key and sort_key of the provided records list.
- **get_records:**- Get multiple records in a single call based on sort key matching.

### Exceptions
| Exception | Description | Retryable? |
| --------- | ------------- | ------------- |
| DynamoDBException | Base for all exceptions thrown from dynamodb | |
| RecordNotFoundException | Exception thrown when no record was found | no |
| TableDoesNotExistException | Exception thrown when the specified table does not exist | no |
| ConditionFailedException | Exception thrown when the conditions defined in the query are not met and the operation was rejected | no |
| RetryableException | Base type for all client retryable exceptions | yes |
| DynamoDBTimeoutException | Exception thrown when the service manually timed out executing batch operations that took too long | yes* |
| ThrottlingException | Exception thrown when DynamoDB is currently throttling requests | no |
| InternalServerError | Exception thrown due to an unspecified internal server error from DynamoDB server | yes |
| ExpressionTooLarge | Exception thrown when the expression built to execute the given query exceeded DynamoDB size requirements | no |

\* Timeouts are inherently retryable, but as timeouts are added for safety for the client, 
it is up to the client to add explicit logic around what to do when a timeout is hit. Therefore, it is not included as a RetryableException automatically

### Example
Insert a record into dynamodb. This example is complete and should run as is (assuming my_table_name exists)
```python
from core.dynamodb import DynamoDB

dynamodb_client = DynamoDB("my_table_name", partition_key="my_partition_key", sort_key="my_sort_key")
dynamodb_client.put_record(
    partition_key="a_pk_value",
    sort_key="a_sk_value",
    item={"foo": 5, "bar": "fdsaf"}
)
```
Query a record from dynamodb. This example is complete and should run as is (assuming my_table_name exists)
```python
from core.dynamodb import DynamoDB

dynamodb_client = DynamoDB("my_table_name", partition_key="my_partition_key", sort_key="my_sort_key")
result = dynamodb_client.get_record(
    partition_key="a_pk_value",
    sort_key="a_sk_value"
)
```
Update (upsert) a record in dynamodb, while APPENDING/INCREMENTING values that can be appended or incremented
```python
from core.dynamodb import DynamoDB, UpdateMode

dynamodb_client = DynamoDB("my_table_name", partition_key="my_partition_key", sort_key="my_sort_key")
dynamodb_client.update_record(
    partition_key="a_pk_value",
    sort_key="a_sk_value",
    item={"foo": 5, "bar": "replacement_bar_value"},    # This will increment "foo" by 5, and replace "bar" with "replacement_bar_value", as strings are not updateable
    update_mode=UpdateMode.update
)
```
Update (upsert) a record in dynamodb, replacing all provided values
```python
from core.dynamodb import DynamoDB, UpdateMode

dynamodb_client = DynamoDB("my_table_name", partition_key="my_partition_key", sort_key="my_sort_key")
dynamodb_client.update_record(
    partition_key="a_pk_value",
    sort_key="a_sk_value",
    item={"foo": 5, "bar": "replacement_bar_value"}, # This will set "foo" to 5, and set "bar" to "replacement_bar_value"
    update_mode=UpdateMode.replace
)
```
## DynamoDB Job Executor <a name="dynamodb-job-executor"></a>
The Job Executor is designed to wrap the futures concurrency utility and retry based on the DynamoDB Exception thrown from the registered function


### Functions
- **register_job:**- Register a job for this executor to execute in the form of a callable function and job kwargs. Returns job id for callback references
- **execute_jobs:**- Execute all pending jobs registered to this executor. Operates as a generator and throws _IncompleteExecutionException_ if not all jobs were able to be completed

### Exceptions
- **IncompleteExecutionException:**- Exception thrown if not all jobs were successfully completed. Contains a list of all failed jobs
  

### Example
The following example executes a batch insert on 100 records to "some_test_table" using the DynamoDBJobExecutor. This sample is complete and should run as is
```python
from core.dynamodb import DynamoDBJobExecutor, DynamoDB, BatchRecordItem
from uuid import uuid4

dynamodb = DynamoDB(table_name="some_test_table")

items = []
for _ in range(0, 100):
    items.append(
        BatchRecordItem(
            partition_key="test",
            sort_key=f"{uuid4()}",
            item={"some": "data"}
        )
    )

executor = DynamoDBJobExecutor()
for i in range(0, len(items), 25):
    job_id = executor.register_job(
        dynamodb._do_put_records,
        dict(
            items=items[i:i - 25]
        )
    )
for _ in executor.execute_jobs():
    pass
```

# AWS Lambda Utilities <a name="aws-lambda-utilities"></a>
AWS Lambda Module contains decorators for handling consumption of different types of lambda events as well as services for invoking lambdas

## Handler Decorators
### DynamoDB Update Event <a name="dynamodb-update-event"></a>
Wraps the signature of a function to integrate with a dynamodb update lambda event and morph signature for convenience

#### Example
```python
from core.awslambda import dynamodb_update_handler, DynamoDbUpdateRecord
from typing import List

@dynamodb_update_handler(partition_key="partition_key", sort_key="sort_key")
def process_updates(records: List[DynamoDbUpdateRecord]):
    for record in records:
        print(f"Processing {record.type} for {record.partition_key} :: {record.sort_key}. Old: {record.old}. New {record.new}")
```

### Kinesis Event <a name="kinesis-event"></a>
Wraps the signature of a function to integrate with a kinesis record lambda event and morph signature for convenience

Automatically unpacks records from base64 encoded form and decompresses it using higher compression algorithms used in KinesisProducerService

If a model class is provided, deserialization into that class is automatically attempted for all incoming records

#### Example
```python
from uuid import UUID
from core.model import CoreBaseModel
from core.awslambda import kinesis_lambda_handler
from typing import List

class MyKinesisEvent(CoreBaseModel):
    my_id: UUID
    my_string: str


@kinesis_lambda_handler(model=MyKinesisEvent, decompress=True)
def process_kinesis_records_with_model(events: List[MyKinesisEvent]):
    for event in events:
        print(event)

@kinesis_lambda_handler(decompress=True)
def process_kinesis_records_no_model(events: List[str]):
    for event in events:
        print(event)
```

### SQS Event <a name="sqs-event"></a>
Wraps the signature of a function to integrate with an SQS Lambda Event and morphs signature for convenience

If a model class is provided, deserialization into that class is automatically attempted for all incoming records

If the event is sourced with core.sqs.SQSService, "string" and "json" body types are supported without a model
#### Example
```python
from uuid import UUID
from core.model import CoreBaseModel
from core.awslambda import sqs_lambda_handler
from typing import List

class MySQSMessage(CoreBaseModel):
    my_id: UUID
    my_string: str


@sqs_lambda_handler(model=MySQSMessage)
def process_sqs_event_with_model(events: List[MySQSMessage]):
    for event in events:
        print(event)

@sqs_lambda_handler()
def process_sqs_records_no_model(events: List[str]):
    for event in events:
        print(event)

```

### API Gateway HTTP Event <a name="api-gateway-http-event"></a>
Wraps the signature of a function to integrate with Http lambda events from AWS Gateway and returns responses to api gateway 
in the format it expects without the function having to create that response structure manually

    Args:
        method (HttpMethod): The Http Method this handler is configured for [Default: HttpMethod.GET]
        decode_base64 (bool): Whether or not to automatically decode an incoming base64encoded message [Default: True]
        body_arg (str): The key value passed to the handler function representing the incoming body [Default: "data"]
        default_response_code (int): The default response code to return on a successful message (Default: 200)
        default_error_response_code (int): The default response code to return on an unmapped error (Default: 500)
        content_type (Optional[str]): The content type header to return with this http response. 
            Defaults to "application/json" for CoreBaseModel and Dict responses and application/octet-stream for byte responses

This decorator also automatically parses path parameters and query parameters into inputs of the function
- Path parameters are represented as **required positional arguments**
- Query string parameters are represented as **optional keyword arguments**
- The request body, if one exists, is passed to the function using the keyword of the configured 'body_arg' parameter

**The returned json body is always minified automatically**

#### Core Exception HTTP Mappings

| Exception | Response Code |
| --------- | ------------- |
| CoreException | 500 |
| ResourceNotFound | 404 |
| ResourceConflict | 401 |
| ActionNotSupported | 405 |
| MalformedData | 400 |
| TimeoutException | 408 |

#### Examples
Example of posted data, no parameters. Returns 200 on success, representing POST /users
```python
from core.awslambda import HttpMethod, http_lambda_handler
from core.model import CoreBaseModel

class User(CoreBaseModel):
    first_name: str
    last_name: str

@http_lambda_handler(method=HttpMethod.POST)
def create_user(data: User):
    my_user_service.create_user(data)
```

Example GET data with path parameter, representing GET /users/:user_id
```python
from core.awslambda import HttpMethod, http_lambda_handler
from core.model import CoreBaseModel

class User(CoreBaseModel):
    first_name: str
    last_name: str

@http_lambda_handler(method=HttpMethod.GET)
def get_user(user_id: str):
    # Get a user
    return User(
        first_name="foo",
        last_name="bar"
    )
```

Example GET data with query parameters. Representing GET /users?first_name=foo&last_name=bar
```python
from core.awslambda import HttpMethod, http_lambda_handler
from core.model import CoreBaseModel
from typing import Optional

class User(CoreBaseModel):
    first_name: str
    last_name: str

@http_lambda_handler(method=HttpMethod.GET)
def get_users(first_name: Optional[str] = None, last_name: Optional[str] = None):
    users = [
        User(first_name="foo", last_name="bar"),
        User(first_name="zoo", last_name="zar")
    ]
    users = filter(
        lambda _user: (_user.first_name == first_name if first_name else True) and (_user.last_name == last_name if last_name else True),
        users
    )
    return list(users)
```

### Custom Events <a name="custom-events"></a>
This lightweight decorator wraps a generic lambda that isn't tied to a specific source, and has a custom event format

#### Example
```python
from core.awslambda import raw_lambda_handler
from core.model import CoreBaseModel
from uuid import UUID
from typing import Optional

class MyCustomLambdaEvent(CoreBaseModel):
    parameter_a: UUID
    parameter_b: Optional[str]

@raw_lambda_handler(model=MyCustomLambdaEvent)
def my_lambda_handler_function(data: MyCustomLambdaEvent):
    # Execute the lambda
    return
```

# SQS Service <a name="sqs-service"></a>

# Kinesis  <a name="kinesis"></a>

## Kinesis Producer  <a name="kinesis-producer"></a>

## Kinesis Consumer  <a name="kinesis-consumer"></a>

# S3 Service  <a name="s3-service"></a>

# Core Exceptions  <a name="core-exceptions"></a>

# Utilities
## Data Flattening  <a name="data-flattening"></a>

## Futures Concurrency Executor  <a name="futures-concurrency-executor"></a>

## Pydantic Model Generation from JSON  <a name="pydantic-model-generation-from-json"></a>
We have a utility designed to parse in json endpoints and generate pydantic dataclasses that fit all observed data points on those endpoints

The utility is meant to run over the largest sample size needed to ensure all exceptions and use cases are covered (e.g.)
some values being null or not present, or exceptional values existing

```
OUTPUT_PACKAGE = "foo.models"

json_parser = JsonToModelParser(root_name="FooModel")

for _ in range(5):
    data = requests.get("https://httpbin.org/json")
    json_parser.parse_dict(data.json())

json_parser.output_models_to_package(OUTPUT_PACKAGE)            # Outputs the observed data to the desired package
json_parser.write_observed_values(}                             # Outputs the observed 'enum' values to a file
```


