# NYU DevOps2022 Suppliers

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![codecov](https://codecov.io/gh/NYU-DevOp2022/suppliers/branch/master/graph/badge.svg?token=1BIJLFSVOR)](https://codecov.io/gh/NYU-DevOp2022/suppliers)

Supplier team repository for DevOps & Agile Methodologies 2022 summer

##  Project description
Here, as a Supplier team for an eCommerce site development project, implementing microservices which allows lifecycle operations on a collection of suppliers. The microservice is RESTful service.

## Features

This microservice has the main features for the lifetime cycle operations of suppliers as follows.

#### Get a supplier
You can get the current information of a supplier. The operation is as follows.
```bash
GET /suppliers/{supllier_id}
```

#### List all suppliers
You can get a list of all suppliers. The operation is as follows.
```bash
GET /suppliers
```
#### Create a supplier
You can create a new supplier. The operation is as follows
```bash
POST /suppliers/{supplier_id}
```
#### Update a supplier
You can update the information of a supplier. The operation is as follows
```bash
PUT /suppliers/{supllier_id}
```

#### Delete a supplier
You can delete a supplier. The operation is as follows.
```bash
DELETE /suppliers/{supllier_id}
```

We also implement some other features, error messages, and also test cases. The microservice is developed based on the test driven development.

<<<<<<< HEAD
## USAGE

#### Run the service
To run the service, use the `bash` terminal and use `honcho start` (Press Ctrl+C to exit):

```bash
honcho start
```
<!---
#### Make some REST calls
With the service running, open a second `bash` terminal and issue the following `curl` commands:

Create a supplier:

```bash
curl -i -X POST http://localhost:8000/suppliers/12
```

Read a supplier:

```bash
curl -i -X GET http://localhost:8000/suppliers/12
```
--->

#### Run the test suite
Run the tests in a `bash` terminal using the following command:

```bash
nosetests
```

### Manually Running the server
```
 git clone https://github.com/NYU-DevOps2022/suppliers.git
 cd suppliers
 make run
```

### Manually Running The Tests
To run the TDD tests please run the following commands:
```
 git clone https://github.com/NYU-DevOps2022/suppliers.git
 cd suppliers
 nosetests
```

### Running Pylint: (Current Score 10/10)
To run the pylint score please run the following commands:
```
 git clone https://github.com/NYU-DevOps2022/suppliers.git
 cd suppliers/service
 pylint model.py
 pylint route.py
```

## License

Copyright (c) Zelin Gong, Zhihao Shu, Dongzhe Fan, Keigo Ando, and Junzhou Liu. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** 