import pytest

from mandos.model.pubchem_support._nav_fns import Filter, Flatmap
from mandos.model.pubchem_support._nav import JsonNavigator


class TestNav:
    def test(self):
        nav = JsonNavigator.create(dict(a=dict(b=1)))
        assert (nav / "a" >> "b").contents == [1]

    def test_filter(self):
        nav = JsonNavigator.create([dict(a="x", b="y"), dict(a="123", b="456")])
        a = nav / Filter.key_equals("b", "y") // "a" // Flatmap.require_only()
        assert a.contents == ["x"]

    def test_mod(self):
        nav = JsonNavigator.create([dict(a="x", b="y"), dict(a="123", b="456")])
        assert len((nav % "a").contents) == 1
        assert dict((nav % "a").contents[0]) == {
            "x": dict(a="x", b="y", _landmark=""),
            "123": dict(a="123", b="456", _landmark=""),
        }


if __name__ == "__main__":
    pytest.main()
