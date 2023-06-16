## Webshop selenium testing 
### run
This is a selenium testing project for a webshop. The project is written in Python3 and selenium 4 using Py-Test as a testing framework.

Program runs py calling "pytest [-v] [--GUI] util.py tests/"

-v(optional) for calling each test case

--GUI for running the tests in GUI mode, opening browser window

it also requires a data folder with shipping.csv, personal_info.csv, search.csv tables for data provided tests.
<br> -- search.csv: is to be composed like so, first cell in each row is a query, the rest non empty cells are items that to be found by query. If empty NO items should be found by search.
<br> -- personal_info.csv: is to be composed like so, first row contains categories of user data that can be changed, for rest rows, non empty cells representing data to be changed.
<br> -- shipping.csv: is a list of possible shipping to be checked, also second parametr is an address of a branch.

### install
pip3 install -r requirements.txt
requires python3.8 or higher
also requires a mozilla installed for selenium webdriver

### structure
<br>utils.py - contains helpers

<br>Account.py - contains all profile related tests and helper logic, such as login

<br>Bucket.py - contains all purchase, shopping cart etc logic and tests

<br>Search.py - contains serach test logic
