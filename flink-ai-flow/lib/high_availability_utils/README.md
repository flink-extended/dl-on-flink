# high_availability_utils

The `high_availability_utils` provides the tools that helps to build the high availability service.

## wal
The wal module provides the WAL(Write Ahead Log) function.

**Notice:
Before import the `DbWAL`, you need to invoke the function `set_ha_db_base` to specific the `declarative_base()`.   
**

For example:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from high_availability_utils.wal.db_init import set_ha_db_base

Base = declarative_base()
set_ha_db_base(Base)
from high_availability_utils.wal.db_wal import DbWAL
from high_availability_utils.wal.wal import TransactionMessage

engine = create_engine('sqlite:///high_availability_utils.db')
DbSession = sessionmaker(bind=engine)
session = DbSession()
wal = DbWAL(session=session)
transaction_id = wal.begin_transaction(transaction_message=TransactionMessage(name='a'), server_id='1')
wal.end_transaction(transaction_id=transaction_id)
```