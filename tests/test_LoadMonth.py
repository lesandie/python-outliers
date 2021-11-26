from app.loadmonth import LoadMonth

def test_loadmonth_creation():
    name = "Mar.22"
    month = LoadMonth(name)
    if month.name == name:
        assert True
    else:
        assert False

