from fish_util.src.decorator_util import *
import allure


@trace_time
def train_model():
    print("Starting the model training function...")
    # simulate a function execution by pausing the program for 5 seconds
    # time.sleep(1)
    print("Model training completed!")


@trace_args
def add_numbers(x, y):
    return x + y


@trace_exception
def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    result = x / y
    return result


@trace_exception
@trace_validate(
    lambda x: x > 0,
    lambda message: isinstance(message, str),
    lambda level: level >= 0,
)
def divide_and_print(x, message, level=2):
    print(f"x: {x}")
    print(f"message: {message}")
    print(f"level: {level}")


@trace_retry(max_attempts=1, delay=1)
def fetch_data(url):
    print("Fetching the data..")
    # raise timeout error to simulate a server not responding..
    raise TimeoutError("Server is not responding.")


@allure.feature(__file__)
def test():
    print(__file__)
    train_model()
    add_numbers(7, y=5)
    train_model()
    divide(10, 0)
    divide_and_print(-1, "test", level=-3)
    fetch_data("https://example.com/data")  # retry 3 delay 1


if __name__ == "__main__":
    test()
