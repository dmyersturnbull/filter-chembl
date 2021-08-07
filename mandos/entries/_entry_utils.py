from typing import Set, Sequence

from mandos.model.settings import MANDOS_SETTINGS
from mandos.model.apis.chembl_support.chembl_activity import DataValidityComment
from mandos.model.apis.chembl_support.chembl_targets import TargetType
from mandos.model.apis.pubchem_support.pubchem_models import ClinicalTrialsGovUtils
from mandos.model.taxonomy import Taxonomy
from mandos.model.taxonomy_caches import TaxonomyFactories


class EntryUtils:
    """ """

    @staticmethod
    def split(st: str) -> Set[str]:
        return {s.strip() for s in st.split(",")}

    @staticmethod
    def get_taxa(taxa: str) -> Sequence[Taxonomy]:
        factory = TaxonomyFactories.from_uniprot(MANDOS_SETTINGS.taxonomy_cache_path)
        return [factory.load(str(taxon).strip()) for taxon in taxa.split(",")]

    @staticmethod
    def get_trial_statuses(st: str) -> Set[str]:
        return ClinicalTrialsGovUtils.resolve_statuses(st)

    @staticmethod
    def get_target_types(st: str) -> Set[str]:
        return {s.name for s in TargetType.resolve(st)}

    @staticmethod
    def get_flags(st: str) -> Set[str]:
        return {s.name for s in DataValidityComment.resolve(st)}


__all__ = ["EntryUtils"]
