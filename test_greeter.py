from greeter import Greeter

def test_greet():
    g = Greeter("Alice")
    assert g.greet() == "Hello, Alice!"
