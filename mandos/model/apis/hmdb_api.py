import abc
import gzip
from pathlib import Path
from dataclasses import dataclass
from typing import Union, Sequence

import defusedxml.ElementTree as Xml
import orjson
from pocketutils.tools.common_tools import CommonTools

from mandos.model.settings import QUERY_EXECUTORS, MANDOS_SETTINGS
from pocketutils.core.dot_dict import NestedDotDict
from pocketutils.core.query_utils import QueryExecutor

from mandos.model import Api


def _is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@dataclass(frozen=True, repr=True, order=True)
class HmdbProperty:
    name: str
    source: str
    value: Union[None, str, int, float, bool]
    experimental: bool


class HmdbApi(Api, metaclass=abc.ABCMeta):
    def fetch(self, hmdb_id: str) -> NestedDotDict:
        raise NotImplementedError()

    def fetch_properties(self, hmdb_id: str) -> Sequence[HmdbProperty]:
        raise NotImplementedError()

    def fetch_tissues(self, hmdb_id: str) -> Sequence[HmdbProperty]:
        raise NotImplementedError()


class JsonBackedHmdbApi(HmdbApi, metaclass=abc.ABCMeta):
    def fetch_properties(self, hmdb_id: str) -> Sequence[HmdbProperty]:
        data = self.fetch(hmdb_id)
        pred = data.sub("metabolite.predicted_properties.property")
        exp = data.sub("metabolite.experimental_properties.property")
        items = [self._prop(x, True) for x in exp]
        items += [self._prop(x, False) for x in pred]
        return items

    def fetch_tissues(self, hmdb_id: str) -> Sequence[str]:
        data = self.fetch(hmdb_id)
        tissues = data.get_list_as("metabolite.biological_properties.tissue_locations.tissue", str)
        return [] if tissues is None else tissues

    def _prop(self, x: NestedDotDict, experimental: bool):
        value = x.req_as("value", str)
        if value.isdigit():
            value = int(value)
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif CommonTools.is_probable_null(value):
            value = None
        elif _is_float(value):
            value = float(value)
        return HmdbProperty(
            name=x["kind"], value=value, source=x["source"], experimental=experimental
        )


class QueryingHmdbApi(JsonBackedHmdbApi):
    def __init__(self, query: QueryExecutor = QUERY_EXECUTORS.hmdb):
        self._query = query

    def fetch(self, hmdb_id: str) -> NestedDotDict:
        # e.g. https://hmdb.ca/metabolites/HMDB0001925.xml
        url = f"https://hmdb.ca/metabolites/{hmdb_id}.xml"
        data = self._query(url)
        data = self._to_json(data)
        return NestedDotDict(data)

    def _to_json(self, xml):
        response = {}
        for child in list(xml):
            if len(list(child)) > 0:
                response[child.tag] = self._to_json(child)
            else:
                response[child.tag] = child.text or ""
        return response


class CachingHmdbApi(JsonBackedHmdbApi):
    def __init__(self, query: QueryingHmdbApi):
        self._query = query

    def fetch(self, hmdb_id: str) -> NestedDotDict:
        path = self.path(hmdb_id)
        if not path.exists():
            return self._read_json(path)
        else:
            data = self._query.fetch(hmdb_id)
            self._write_json(data, path)
            return data

    def path(self, hmdb_id: str):
        return (MANDOS_SETTINGS.hmdb_cache_path / hmdb_id).with_suffix(".json.gz")

    def _write_json(self, data: NestedDotDict, path: Path) -> None:
        path.write_bytes(gzip.compress(data.to_json()))

    def _read_json(self, path: Path) -> NestedDotDict:
        deflated = gzip.decompress(path.read_bytes())
        read = orjson.loads(deflated)
        return NestedDotDict(read)


__all__ = ["HmdbApi", "QueryingHmdbApi", "HmdbProperty"]