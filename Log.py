import os
from pathlib import Path

def main():
    print("NEW EVENT BEING LOGGED")
    gen_file()

def gen_file():
    print("New log file being generated")
    print("DATE TIME ID")
    try:
        with open("test.txt", "a") as file:
            file.write("SAMPLE DATA\n")
        print(f"File  created successfully")
        return True
    except PermissionError:
        print(f"Error: Permission denied to create ")
    except FileNotFoundError:
        print(f"Error: Invalid directory path '")
        return False
    except IOError as e:
        print(f"Error creating file : {e}")
        return False
    except Exception as e:
        print(f"Unexpected error creating : {e}")
        return False

if __name__ == "__main__":
    main()