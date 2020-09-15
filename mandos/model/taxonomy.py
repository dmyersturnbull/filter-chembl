from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import total_ordering
from typing import List, Mapping, Optional, Sequence, Set, Union

import pandas as pd

logger = logging.getLogger(__package__)


@total_ordering
@dataclass()
class Taxon:
    """"""

    # we can't use frozen=True because we have both parents and children
    # instead, just use properties
    __id: int
    __name: str
    __parent: Optional[Taxon]
    __children: Set[Taxon]

    @property
    def id(self) -> int:
        """

        Returns:

        """
        return self.__id

    @property
    def name(self) -> str:
        """

        Returns:

        """
        return self.__name

    @property
    def parent(self) -> Taxon:
        """

        Returns:

        """
        return self.__parent

    @property
    def children(self) -> Set[Taxon]:
        """

        Returns:

        """
        return set(self.__children)

    @property
    def ancestors(self) -> Sequence[Taxon]:
        """

        Returns:

        """
        return self._ancestors([])

    @property
    def descendents(self) -> Sequence[Taxon]:
        """

        Returns:

        """
        return self._descendents([])

    def _ancestors(self, values: List[Taxon]) -> List[Taxon]:
        values.append(self.parent)
        values += self._ancestors(values)
        return values

    def _descendents(self, values: List[Taxon]) -> List[Taxon]:
        values += self.children
        values += self._descendents(values)
        return values

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id


@dataclass(order=True)
class _Taxon(Taxon):
    """
    An internal, modifiable taxon for building the tree.
    """

    def set_name(self, name: str):
        self.__name = name

    def set_parent(self, parent: _Taxon):
        self.__parent = parent

    def add_child(self, child: _Taxon):
        self.__children.add(child)

    def __hash__(self):
        return hash(self.id)


class Taxonomy:
    """
    A taxonomic tree of organisms from UniProt.
    Elements in the tree can be looked up by name or ID using ``__getitem__`` and ``get``.
    """

    def __init__(self, by_id: Mapping[int, Taxon], by_name: Mapping[str, Taxon]):
        """

        Args:
            by_id:
            by_name:
        """
        self._by_id = by_id
        self._by_name = by_name

    @classmethod
    def from_list(cls, taxa: Sequence[_Taxon]) -> Taxonomy:
        return Taxonomy({x.id: x for x in taxa}, {x.name: x for x in taxa})

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> Taxonomy:
        """
        Reads from a DataFrame from a CSV file provided by a UniProt download.
        Strips any entries with missing or empty-string scientific names.

        Args:
            df: A dataframe with columns (at least) "Taxon", "Scientific name", and "Parent" (case-insensitive)

        Returns:
            The corresponding taxonomic tree
        """
        df.columns = [c.lower() for c in df.columns]
        df = df[["taxon", "scientific name", "parent"]]
        df.columns = ["id", "name", "parent"]
        tax = Taxonomy({}, {})
        # just build up a tree, sticking the elements in by_id
        tax._by_id = {}
        for row in df.itertuples():
            child = tax._by_id.setdefault(row.id, _Taxon(row.id, row.name, None, set()))
            parent = tax._by_id.setdefault(row.parent, _Taxon(row.parent, "", None, set()))
            child.set_name(row.name)
            child.set_parent(parent)
            # noinspection PyProtectedMember
            parent.add_child(child)
        bad = [t for t in tax._by_id.values() if t.name == ""]
        if len(bad) > 0:
            logger.error(f"Removing taxa with missing or empty names: {bad}.")
        # completely remove the taxa with missing names
        tax._by_id = {k: v for k, v in tax._by_id.items() if v.name != ""}
        # fix classes
        for v in tax._by_id.values():
            v.__class__ = Taxon
        # build the name dict
        # use lowercase and trim for lookup (but not value)
        tax._by_name = {t.name.strip().lower(): t for t in tax._by_id.values()}
        return tax

    @property
    def taxa(self) -> Sequence[Taxon]:
        """

        Returns:

        """
        return list(self._by_id.values())

    @property
    def roots(self) -> Sequence[Taxon]:
        """

        Returns:

        """
        return [k for k in self.taxa if k.parent is None]

    @property
    def leaves(self) -> Sequence[Taxon]:
        """

        Returns:

        """
        return [k for k in self.taxa if len(k.children) == 0]

    def under(self, item: Union[int, str]) -> Taxonomy:
        """

        Args:
            item:

        Returns:

        """
        item = self[item]
        descendents = item.descendents
        return Taxonomy({d.id: d for d in descendents}, {d.name: d for d in descendents})

    def get(self, item: Union[int, str]) -> Optional[_Taxon]:
        """
        Corresponds to ``dict.get``.

        Args:
            item: The scientific name or UniProt ID

        Returns:
            The taxon, or None if it was not found
        """
        if isinstance(item, int):
            return self._by_id.get(item)
        elif isinstance(item, str):
            return self._by_name.get(item.strip().lower())
        else:
            raise TypeError(f"Type {type(item)} of {item} not applicable")

    def __getitem__(self, item: Union[int, str]) -> _Taxon:
        """
        Corresponds to ``dict[_]``.

        Args:
            item: The scientific name or UniProt ID

        Returns:
            The taxon

        Raises:
            KeyError: If the taxon was not found
        """
        got = self.get(item)
        if got is None:
            raise KeyError(f"{item} not found in {self}")
        return got

    def __contains__(self, item):
        """

        Args:
            item:

        Returns:

        """
        return self.get(item) is not None

    def __len__(self) -> int:
        """

        Returns:

        """
        return len(self._by_id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self._by_id)} @ {hex(id(self))})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({len(self._by_id)} @ {hex(id(self))})"
