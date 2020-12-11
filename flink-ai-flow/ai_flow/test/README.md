#Run test_sqlalchemy_store.py
TestSqlAlchemyStoreMySQL is used to run tests against a MySQL database. Run the test command with the environment variables set, 
e.g:
```shell
MYSQL_TEST_USERNAME=your_username MYSQL_TEST_PASSWORD=your_password <your-test-command>.
```

You may optionally specify MySQL host via MYSQL_TEST_HOST (default is 100.69.96.145) and specify MySQL port via MYSQL_TEST_PORT (default is 3306).

#Environment variables
```text
# Username of MySQL database.
MYSQL_TEST_USERNAME=[mysql_username]
# Password of MySQL database.
MYSQL_TEST_PASSWORD=[mysql_password]
# Host of MySQL database, default value is 100.69.96.145.
MYSQL_TEST_HOST=[mysql_host]
# Port of MySQL database, default value is 3306.
MYSQL_TEST_PORT=[mysql_port]
```