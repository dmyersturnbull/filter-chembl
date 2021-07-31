from __future__ import annotations

import abc
import dataclasses
import typing
from typing import Generic, Sequence, TypeVar

from mandos import logger
from mandos.model import CompoundNotFoundError, MiscUtils, ReflectionUtils
from mandos.model.hits import AbstractHit, HitFrame
from mandos.model.hit_utils import HitUtils

H = TypeVar("H", bound=AbstractHit, covariant=True)


class SearchError(Exception):
    """
    Wrapper for any exception raised in ``find`` except for ``CompoundNotFoundError``.
    """

    def __init__(
        self,
        *args,
        inchikey: str = None,
        search_key: str = None,
        search_class: str = None,
        **kwargs,
    ):
        super().__init__(*args, *kwargs)
        self.inchikey = inchikey
        self.search_key = search_key
        self.search_class = search_class


class Search(Generic[H], metaclass=abc.ABCMeta):
    """
    Something to search and how to do it.
    """

    def __init__(self, key: str):
        self.key = key

    @property
    def search_class(self) -> str:
        return self.__class__.__name__

    @property
    def search_name(self) -> str:
        return self.__class__.__name__.lower().replace("search", "")

    @property
    def data_source(self) -> str:
        """
        Where the data originally came from; e.g. ``the Human Metabolome Database (HMDB)``"
        """
        raise NotImplementedError()

    def get_params(self) -> typing.Mapping[str, typing.Any]:
        """
        Returns the *parameters* of this ``Search`` their values.
        Parameters are attributes that do not begin with an underscore.
        """
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}

    def find_to_df(self, inchikeys: Sequence[str]) -> HitFrame:
        """
        Calls :py:meth:`find_all` and returns a :py:class:`HitFrame` DataFrame subclass.
        Writes a logging ERROR for each compound that was not found.

        Args:
            inchikeys: A list of InChI key strings
        """
        hits = self.find_all(inchikeys)
        return HitUtils.hits_to_df(hits)

    def find_all(self, inchikeys: Sequence[str]) -> Sequence[H]:
        """
        Loops over every compound and calls ``find``.
        Comes with better logging.
        Writes a logging ERROR for each compound that was not found.

        Args:
            inchikeys: A list of InChI key strings

        Returns:
            The list of :py:class:`mandos.model.hits.AbstractHit`
        """
        lst = []
        # set just in case we never iterate
        i = 0
        for i, compound in enumerate(inchikeys):
            try:
                x = self.find(compound)
            except CompoundNotFoundError:
                logger.info(f"NOT FOUND: {compound}. Skipping.")
                continue
            except Exception:
                raise SearchError(
                    f"Failed {self.key} [{self.search_class}] on compound {compound}",
                    compound=compound,
                    search_key=self.key,
                    search_class=self.search_class,
                )
            lst.extend(x)
            logger.debug(f"Found {len(x)} {self.search_name} annotations for {compound}")
            if i % 10 == 9:
                logger.notice(
                    f"Found {len(lst)} {self.search_name} annotations for {i+1} of {len(inchikeys)} compounds"
                )
        logger.notice(
            f"Found {len(lst)} {self.search_name} annotations for {i+1} of {len(inchikeys)} compounds"
        )
        return lst

    def find(self, inchikey: str) -> Sequence[H]:
        """
        To override.
        Finds the annotations for a single compound.

        Args:
            inchikey: An InChI Key

        Returns:
            A list of annotations

        Raises:
            CompoundNotFoundError
        """
        raise NotImplementedError()

    @classmethod
    def hit_fields(cls) -> Sequence[str]:
        """
        Gets the fields in the Hit type parameter.
        """
        # Okay, there's a lot of magic going on here
        # We need to access the _parameter_ H on cls -- raw `H` doesn't work
        # get_args and __orig_bases__ do this for us
        # then dataclasses.fields gives us the dataclass fields
        # there's also actual_h.__annotations__, but that doesn't include ClassVar and InitVar
        # (not that we're using those)
        # If this magic is too magical, we can make this an abstract method
        # But that would be a lot of excess code and it might be less modular
        x = cls.get_h()
        return [f.name for f in dataclasses.fields(x) if f.name != "search_class"]

    @classmethod
    def get_h(cls):
        """
        Returns the underlying hit TypeVar, ``H``.
        """
        return ReflectionUtils.get_generic_arg(cls, AbstractHit)

    def _create_hit(
        self,
        c_origin: str,
        c_matched: str,
        c_id: str,
        c_name: str,
        predicate: str,
        object_id: str,
        object_name: str,
        **kwargs,
    ) -> H:
        # ignore statement -- we've removed it for now
        entry = dict(
            record_id=None,
            search_key=self.key,
            search_class=self.search_class,
            data_source=self.data_source,
            run_date=MiscUtils.utc(),
            cache_date=None,
            value=1,
            compound_id=c_id,
            origin_inchikey=c_origin,
            matched_inchikey=c_matched,
            compound_name=c_name,
            predicate=predicate,
            object_id=object_id,
            object_name=object_name,
        )
        clazz = self.__class__.get_h()
        # noinspection PyArgumentList
        return clazz(**entry, **kwargs)

    def __repr__(self) -> str:
        return ", ".join([k + "=" + str(v) for k, v in self.get_params().items()])

    def __str__(self) -> str:
        return repr(self)

    def __eq__(self, other: Search) -> bool:
        """
        Returns True iff all of the parameters match, thereby excluding attributes with underscores.
        Multiversal equality.

        Raises:
            TypeError: If ``other`` is not a :py:class:`Search`
        """
        if not isinstance(other, Search):
            raise TypeError(f"{type(other)} not comparable")
        return repr(self) == repr(other)


__all__ = ["Search", "HitFrame"]
