# NYU DevOps2022 Suppliers

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![codecov](https://codecov.io/gh/NYU-DevOp2022/suppliers/branch/master/graph/badge.svg?token=1BIJLFSVOR)](https://codecov.io/gh/NYU-DevOp2022/suppliers)[![CI Build](https://github.com/NYU-DevOp2022/suppliers/actions/workflows/main.yml/badge.svg)](https://github.com/NYU-DevOp2022/suppliers/actions/workflows/main.yml)

###  Project description
The purpose of this project is to develop a suppliers system for an eCommerce web site backend as a collection RESTful services for a client by adopting DevOps methodology. 




## Contents
### Model description
## Supplier
|  Column  |  Type  |
| :----------: | :---------: |
| id | Integer |
| name | String |
| avaliable | Boolean |
| address | String |
| rating | Float |

## Item
|  Column  |  Type  |
| :----------: | :---------: |
| id | Integer |
| name | String |

## Supplier_Item
|  Column  |  Type  |
| :----------: | :---------: |
| supplier_id | Integer |
| item_id | Integer |

### URLS
| RESTful APIS |  URL | Short description | Return |
| :----------: | :---------: | :---------: | :---------: |
| `GET` | `/` | Get index | general information |
| `POST` | `/suppliers` | Create a new supplier | Supplier Object |
| `PUT` | `/suppliers/<int:supplier_id>` |  Update a Supplier based on the body that is posted | Supplier Object |
| `GET` | `/suppliers` | List all the suppliers | List of Supplier Objects |
| `GET` | `/suppliers/rating/<float:rating>` | List the suppliers based on their ratings | List of Supplier Objects filtered by their ratings |
| `GET` | `/suppliers/rating/<float:rating>` | List all the suppliers sorted by their rating | List of sorted Supplier Objects |
| `GET` | `/suppliers/<int:supplier_id>` | Find a supplier based on his id | Supplier Objects |
| `DELETE` | `/suppliers/<int:supplier_id>` | Delete a supplier based on his id | HTTP_204_NO_CONTENT |
| `POST` | `/items` | Create a new item  | Item object |
| `DELETE` | `/items` | Delete an item based on its id | HTTP_204_NO_CONTENT |
| `GET` | `/items` | List all the items  | List of item objects |
| `POST` | `/suppliers/<int:supplier_id>/items` | Add an item to a supplier  | Item id and supplier id |
| `POST` | `/suppliers/<int:supplier_id>/items` | Add an item to a supplier  | Item id and supplier id |
| `GET` | `/suppliers/<int:supplier_id>/items` | List all items of a supplier  | List of item objects |
| `DELETE` | `/suppliers/<int:supplier_id>/items` | Delete an item of a supplier based on an item id  | HTTP_204_NO_CONTENT |





### Project files

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
├── status.py              - HTTP status constants
├── error_handlers.py.     - HTTP error handling code
└── utils                  - utility package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── factories.py    - generate test cases
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
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

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
