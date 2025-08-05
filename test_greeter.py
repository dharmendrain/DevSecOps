#TEST
from greeter import Greeter

def test_greet():
    g = Greeter("Dharmendra")
    assert g.greet() == "Hello, Dharmendra!"
