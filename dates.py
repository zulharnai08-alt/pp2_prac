def fibonacci(limit): 
    a, b = 0, 1
    while a <= limit:
        yield a
        # take the variables one at a time
        a, b = b, a + b


if __name__ == "__main__":
    print("Fibonacci sequence up to 100:")

    for number in fibonacci(100):
        print(number)
