# pytest
import pytest

# custom imports
from item import Item_methods

# init classes
item = Item_methods()

def test_item_methods_get_sheen_and_killstreaker():
    assert item.get_sheen_and_killstreaker("(killstreaker: hypno-beam, sheen: villainous violet)") == {"killstreaker" : "hypno-beam", "sheen": "villainous violet"}
    assert item.get_sheen_and_killstreaker("(killstreaker: incinerator, sheen: villainous violet)") == {"killstreaker" : "incinerator", "sheen": "villainous violet"}

    assert item.get_sheen_and_killstreaker("(killstreaker: balls12312, sheen: villainous violet)") == None

def test_item_methods_get_sheen():
    assert item.get_sheen("(sheen: mean green)") == "mean green"
    assert item.get_sheen("(sheen: villainous violet)") == "villainous violet"

    assert item.get_sheen("(sheen: villainous violet)") == "villainous violet"