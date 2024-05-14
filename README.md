- project
  - test
    - test_log_util.py
  - util
    - log_util.py
tree --charset=ascii -P "*.py" -I ".*" --noreport --dirsfirst utils | sed -e 's/^/  - /'
tree --charset=ascii -P "*.py" -I ".*" --noreport --dirsfirst . | sed -e 's/^/  - /'
- .
- __pycache__
- log
- __init__.py
- log_util.py


- log_util.py
- __init__.py
- log
  - t1.py
  - t2.py


find . -type f -name '*.py' | awk -F/ '{printf "%s%s\n", (NF==2)?"- ":"  - ", $NF}'


- internal_var.py
  - conftest.py
    - test_log_util.py
    - test_case1.py
    - __init__.py
    - test_hello.py
    - test_decorator_util.py
  - __init__.py
  - decorator_util.py
    - log_util.py
    - __init__.py
    - t1.py
    - t2.py
  - content_format.py
  - logging_util.py
  - main.py
  - common_op.py

- fish_util
  - test
    - tree
      - tree3.py
    - test_log_util.py
    - test_case1.py
    - test_hello.py
    - test_decorator_util.py
    - __init__.py
  - src
    - decorator
      - t1.py
      - t2.py
    - log_util.py
    - __init__.py
  - main.py


  - fish_util222
    - internal_var.py
    - conftest.py
    - test_log_util.py
    - test_case1.py
    - __init__.py
    - test_hello.py
    - test_decorator_util.py
    - __init__.py
    - decorator_util.py
    - log_util.py
    - __init__.py
    - t1.py
    - t2.py
    - content_format.py
    - logging_util.py
    - main.py
    - common_op.py
