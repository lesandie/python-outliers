from loadmonth import LoadMonth
from functions import *

def test_node_creation():
    name = "Jose"
    matric = "1234"
    year = 2

    node = Node(name, matric, year)

    if node.name == name and node.matric == matric and node.year == year:
        assert True
    else:
        assert False

def test_list_creation():
    linked_list = LinkedList()

    if linked_list.get_root() == None:
        assert True
    else:
        assert False      