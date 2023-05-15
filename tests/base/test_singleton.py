from uglygpt.base.singleton import AbstractSingleton

class Cls(AbstractSingleton):
    pass

def test_abstract_singleton():
    assert id(Cls()) == id(Cls())