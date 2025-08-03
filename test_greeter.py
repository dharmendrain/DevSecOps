class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

# Create an instance of the class
g = Greeter("Alice")

# Call the greet method
g.greet()
