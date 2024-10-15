import time

def print_separator():
    print("\n" + "=" * 50 + "\n")

def print_slowly(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()
