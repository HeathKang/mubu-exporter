# Overview
[MUBU](https://mubu.com) export all contents to pdf with one click!
# Usage
1. install requirements in your virtaulenv of course:
    ```
    pip install -r requirements.txt
    ```
2. install [edge drivers](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) for selenium, see [selenium doc](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) for details
3. replace `run.py` `DRIVER_PATH` to your `edge_drivce` location;
3. run script:
    ```
    python run.py
    ```
4. enter your username, password within **30** seconds to store your jwt-token in local `cookies.pkl`.
5. waiting for complete.

# TODO
1. remove selenium to simplify whole process, find another way to get `jwt-token`;
2. support folders creation for clear documents stucture.

