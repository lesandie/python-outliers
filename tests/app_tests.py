from loadmonth import LoadMonth
from functions import *

def test_loadmonth_creation():
    name = "Mar.22"
    month = LoadMonth(name)
    if month.name == name:
        assert True
    else:
        assert False
