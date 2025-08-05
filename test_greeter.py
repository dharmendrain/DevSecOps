#TEST
from greeter import Greeter

def test_greet():
    g = Greeter("Prajapati")
    assert g.greet() == "Hello, Dharmendra!"
