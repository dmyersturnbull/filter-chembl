"""
Command-line interface for mandos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Mapping, Any, TypeVar

# noinspection PyProtectedMember
import pandas as pd
from typeddfs import TypedDf

from mandos.entry._arg_utils import Arg

from mandos.analysis.io_defns import (
    EnrichmentDf,
    SimilarityDfLongForm,
    PhiPsiSimilarityDfLongForm,
    PsiProjectedDf,
)

# noinspection PyProtectedMember
from mandos.analysis._plot_utils import (
    MandosPlotStyling,
    MandosPlotUtils,
    PredicateObjectStyleDf,
    CompoundStyleDf,
    PhiPsiStyleDf,
    VIZ_RESOURCES,
)
from mandos.analysis.plots import (
    TauPlotter,
    ProjectionPlotter,
    CorrPlotter,
    ScorePlotter,
    CatPlotType,
    RelPlotType,
    PlotOptions,
)
from mandos.entry._common_args import CommonArgs

# noinspection PyProtectedMember
from mandos.entry.calc_commands import Aa
from mandos.model.utils.resources import MandosResources
from mandos.model.utils.setup import MANDOS_SETUP
from mandos.entry._arg_utils import Opt
from mandos.model.settings import MANDOS_SETTINGS

DEF_SUFFIX = MANDOS_SETTINGS.default_table_suffix


T = TypeVar("T", bound=TypedDf)
V = TypeVar("V", bound=TypedDf)


class Pa:

    stylesheet: str = Opt.val(
        rf"""
        The name of a standard matplotlib style or a path to a .mplstyle file.

        See https://matplotlib.org/stable/tutorials/introductory/customizing.html.
        [default: matplotlib default]
        """,
        show_default=False,
    )

    size: str = Opt.val(
        rf"""
        The width and height of a single figure.

        In the format "<width> x <height>' (e.g. "8.5 in x 11 in") or "<width>" (without height).
        If present, use simple expression with units or built-in, "registered" names.

        Example formats: "8.5 in", "8.5 in x 11 in", "2 cm + 5 in", "pnas.1-col x pnas.full-page".

        Registered widths: {", ".join(VIZ_RESOURCES.dims["heights"])}

        Registered heights: {", ".join(VIZ_RESOURCES.dims["widths"])}

        [default: matplotlib style default]
        """,
        show_default=False,
    )

    ci = Opt.val(
        f"""
        The upper side of the confidence interval, as a percentage.
        """,
        default=95.0,
    )

    out_fig_file: Optional[Path] = Opt.out_file(
        r"""
        Path to an output PDF or other figure file.

        PDF (.pdf) is recommended, but .svg, .png, and others are supported.

        [default: <input-dir>/<auto-generated-filename>.pdf]
        """
    )

    out_fig_dir: Optional[Path] = Opt.out_file(
        r"""
        Path to an output directory for figures.

        [default: <input-dir>]
        """
    )

    in_projection: Optional[Path] = Opt.in_file(
        rf"""
        Path to data from ``:calc:project`` or a similar command.
        """
    )

    cat_plot_kind: str = (
        Opt.val(
            r"""
            The type of categorical-to-numerical plot.

            Can be: 'bar', 'fold', 'box', 'violin', 'strip', or 'swarm'.
            The type of plot: bar, box, violin, or swarm.
            'fold' plots an opaque bar plot for the score over a transparent one for the total.
            It is intended for integer scores representing simple counts.
            Bar (and box) plots include confidence/error bars.
            """,
            default="violin",
        ),
    )

    rel_plot_kind = Opt.val(
        r"""
        The type of x--y relationship plot.

        Either 'scatter', 'line', 'regression:logistic', or 'regression:<order>.
        'regression:1' plots a linear regression line, 'regression:2' plots a quadratic,
        and so on. ('regression:linear', 'regression:quartic', etc., are also accepted.)
        Line and regression plots include confidence/error bands (see --ci and --boot).
        """,
        default="scatter",
    )

    group = Opt.flag(
        """
        Combine the colors (with --color) into plots.

        Applies only if --color is set and there is more than 1 category / color value.

        For strip and swarm plots, ignores the category, plotting all points together in
        single scatter plots. (Otherwise, slightly separates the colors along the x-axis.)
        For bar, box, and violin plots, places the bars immediately adjacent.
        For violin plots with exactly 2 colors, splits each violin into a half-violin per color.
        """
    )

    bandwidth = Opt.val(
        r"""
        Bandwidth as a float.

        Defaults to using Scott's algorithm.
        Only applies to violin plots.
        """
    )

    cut = Opt.val(
        r"""
        Distance, in units of bandwidth size, to extend the density past extreme points.

        Only applies to violin plots.
        """,
        default=2,
    )

    in_compound_style: Optional[Path] = Opt.in_file(
        r"""
        Path to a table mapping compounds to colors and markers.

        If this is set, ``--colors`` and ``--markers`` will refer to columns in this file.
        Otherwise, they will refer to columns in the input.
        Should contain a column called "inchikey", along with 0 or more additional columns.
        See ``--colors`` and ``--markers`` for info on the formatting.
        """
    )

    in_pair_viz: Optional[Path] = Opt.in_file(
        r"""
        Path to a table mapping predicate/object pairs to colors and markers.

        NOTE: This is currently not supported when using predicate/object pair intersection.

        If this is set, ``--colors`` and ``--markers`` will refer to columns in this file.
        Otherwise, they will refer to columns in the input.
        Should contain columns "key", "predicate", and "object", along with 0 or more additional columns.
        The "key" refers to the search key specified in ``:search``.
        Any null (empty-string) value will be taken to mean any/all.
        (The main use is to easily collapse over all predicates.)
        See ``--colors`` and ``--markers`` for info on the formatting.
        """
    )

    in_psi_viz: Optional[Path] = Opt.in_file(
        r"""
        Path to a table mapping each psi variable name (search key) to a color and marker.

        If this is set, ``--colors`` and ``--markers`` will refer to columns in this file.
        Otherwise, they will refer to columns in the input.
        Should contain a "psi" column, along with 0 or more additional columns.
        See ``--colors`` and ``--markers`` for info on the formatting.
        """
    )

    colors: Optional[str] = Opt.val(
        rf"""
        A column that defines the 'group' and color.

        Each group is assigned a different color.
        If not specified, will use one color unless the plot requires more.

        See also: ``--palette``.
        """,
    )

    palette: Optional[str] = Opt.val(
        rf"""
        The name of a color palette.

        If not set, chooses a palette depending on the data type:

        - a vibrant palette for strings with a max of 26 unique items

        - a palette from white to black for numbers of the same sign (excluding NaN and 0)

        - a palette from blue to white to red for negative and positive numbers

        Choices: {", ".join(MandosPlotStyling.list_named_palettes())}.
        Some are only available for some data types.
        """
    )

    markers: Optional[Path] = Opt.val(
        rf"""
        The column to use for markers.

        If not specified, Mandos will use one marker shape, unless the plot requires more.
        If required, a semi-arbitrary column will be chosen.

        If the values are matplotlib-recognized (e.g. ``:`` or ``o``), mandos uses those.
        Otherwise, markers are chosen from the available set and mapped to the distinct values.
        """,
    )

    @classmethod
    def to_dir(cls, in_path: Path, out_path: Optional[Path]) -> Path:
        if out_path is None:
            out_path = in_path
        return out_path

    @classmethod
    def to_file(cls, in_path: Path, out_path: Optional[Path], default_filename: str) -> Path:
        if out_path is None:
            out_path = in_path / default_filename
        return out_path

    @classmethod
    def add_styling(cls, data: T, viz: Optional[TypedDf]) -> T:
        if viz is None:
            return data
        viz = pd.merge(data, viz, on=viz.get_typing().required_names)
        return CompoundStyleDf.convert(viz)

    @classmethod
    def read_rel_kind(cls, kind: str) -> Tuple[RelPlotType, Mapping[str, Any]]:
        type_ = RelPlotType.or_none(kind)
        if type_ is not None:
            return type_, {}
        type_, order = kind.split(":")
        if order == "logistic":
            return type_, dict(logistic=True)
        order = cls.get_arity(order)
        if order is None:
            raise ValueError(f"Unknown kind {kind}")
        return type_, dict(order=order)

    @classmethod
    def get_arity(cls, order: str):
        try:
            order = int(order)
        except ValueError:
            return None
        arities = [
            "nullary",
            "unary",
            "binary",
            "ternary",
            "quaternary",
            "quinary",
            "senary",
            "septenary",
            "octonary",
            "novenary",
            "denary",
            "undenary",
            "duodenary",
        ]
        arities = dict(enumerate(arities))
        arities.update(dict(enumerate(range(0, len(arities)))))
        return arities[order]


class PlotCommands:
    @staticmethod
    def plot_enrichment(
        path: Path = Aa.in_scores_table,
        kind: str = Pa.cat_plot_kind,
        group: bool = Pa.group,
        ci: float = Pa.ci,
        boot: int = Aa.boot,
        seed: int = Aa.seed,
        bandwidth: float = Pa.bandwidth,
        cut: int = Pa.cut,
        viz: Optional[Path] = Pa.in_pair_viz,
        colors: Optional[str] = Pa.colors,
        palette: Optional[str] = Pa.palette,
        size: Optional[str] = Pa.size,
        stylesheet: Optional[str] = Pa.stylesheet,
        to: Optional[Path] = Pa.out_fig_dir,
        log: Optional[Path] = CommonArgs.log,
        stderr: bool = CommonArgs.stderr,
    ) -> None:
        r"""
        Plot correlation to scores.

        Visualizes the correlation between predicate/object pairs and user-supplied scores.
        Will output one figure (file) per scoring function.
        Will plot over a grid, one row per key/source pair and column per predicate/object pair.
        """
        kind = CatPlotType.of(kind)
        MANDOS_SETUP(log, stderr)
        to = Pa.to_dir(path, to)
        df = EnrichmentDf.read_file(path)
        viz = None if viz is None else PredicateObjectStyleDf.read_file(viz)
        df = Pa.add_styling(df, viz)
        palette = MandosPlotStyling.choose_palette(df, colors, palette)
        extra = dict(bandwith=bandwidth, cut=cut) if kind is CatPlotType.violin else {}
        rc = PlotOptions(
            size=size,
            stylesheet=stylesheet,
            rc={},
            hue=colors,
            palette=palette,
            extra=extra,
        )
        plotter = ScorePlotter(
            rc=rc,
            kind=kind,
            group=group,
            ci=ci,
            seed=seed,
            boot=boot,
        )
        for score_name in df["score_name"].unique():
            fig = plotter.plot(df)
            MandosPlotUtils.save(fig, to / f"{score_name}-{kind}-plot.pdf")

    @staticmethod
    def plot_phi_psi(
        path: Path = Aa.in_matrix_long_form,
        kind: str = Pa.rel_plot_kind,
        ci: float = Pa.ci,
        boot: int = Aa.boot,
        seed: int = Aa.seed,
        viz: Optional[Path] = Pa.in_psi_viz,
        colors: Optional[str] = Pa.colors,
        palette: Optional[str] = Pa.palette,
        markers: Optional[str] = Pa.markers,
        size: Optional[str] = Pa.size,
        stylesheet: Optional[str] = Pa.stylesheet,
        to: Optional[Path] = Pa.out_fig_file,
        log: Optional[Path] = CommonArgs.log,
        stderr: bool = CommonArgs.stderr,
    ) -> None:
        r"""
        Plot line plots of phi against psi.

        Plots scatter plots of (phi, psi) values, sorted by phi values.
        All plots are log/log (all similarity values should be scaled from 0 to 1).

        For each unique phi matrix and psi matrix, flattens the matrices and plots
        the flattened (n choose 2 - n) pairs of each jointly, phi mapped to the y-axis
        and psi mapped to the x-axis.

        Will show values for all psi variables together.
        If --colors is not set, will choose a palette.
        """
        MANDOS_SETUP(log, stderr)
        to = Pa.to_file(path, to, f"phi-psi-{kind}-plot.pdf")
        df = PhiPsiSimilarityDfLongForm.read_file(path)
        viz = None if viz is None else PhiPsiStyleDf.read_file(viz)
        df = Pa.add_styling(df, viz)
        palette = MandosPlotStyling.choose_palette(df, colors, palette)
        kind, extra = Pa.read_rel_kind(kind)
        rc = PlotOptions(
            size=size,
            stylesheet=stylesheet,
            rc={},
            hue=colors,
            palette=palette,
            extra=extra,
        )
        plotter = CorrPlotter(
            rc=rc,
            kind=kind,
            ci=ci,
            boot=boot,
            seed=seed,
        )
        fig = plotter.plot(df)
        MandosPlotUtils.save(fig, to)

    @staticmethod
    def plot_tau(
        path: Path = Arg.in_file(
            rf"""
            Output file from ``:calc:tau``.
            """
        ),
        kind: str = Pa.cat_plot_kind,
        group: bool = Pa.group,
        ci: float = Pa.ci,
        boot: int = Aa.boot,
        seed: int = Aa.seed,
        bandwidth: float = Pa.bandwidth,
        cut: int = Pa.cut,
        viz: Optional[Path] = Pa.in_psi_viz,
        colors: Optional[str] = Pa.colors,
        markers: Optional[str] = Pa.markers,
        palette: Optional[str] = Pa.palette,
        size: Optional[str] = Pa.size,
        stylesheet: Optional[str] = Pa.stylesheet,
        to: Optional[Path] = Pa.out_fig_file,
        log: Optional[Path] = CommonArgs.log,
        stderr: bool = CommonArgs.stderr,
    ) -> None:
        r"""
        Plot violin plots or similar from tau values.

        The input data should be generated by ``:calc:phi-vs-psi.tau``.

        Will plot each (phi, psi) pair over a grid, one row per phi and one column per psi
        (unless ``--split`` is set).
        """
        kind = CatPlotType.of(kind)
        MANDOS_SETUP(log, stderr)
        to = Pa.to_file(path, to, f"tau-{kind}-plot.pdf")
        df: SimilarityDfLongForm = SimilarityDfLongForm.read_file(path)
        viz = None if viz is None else PhiPsiStyleDf.read_file(viz)
        df = Pa.add_styling(df, viz)
        palette = MandosPlotStyling.choose_palette(df, colors, palette)
        extra = dict(bandwith=bandwidth, cut=cut) if kind is CatPlotType.violin else {}
        rc = PlotOptions(
            size=size,
            stylesheet=stylesheet,
            rc={},
            hue=colors,
            palette=palette,
            extra=extra,
        )
        plotter = TauPlotter(
            rc=rc,
            kind=kind,
            group=group,
            ci=ci,
            boot=boot,
            seed=seed,
        )
        fig = plotter.plot(df)
        MandosPlotUtils.save(fig, to)

    @staticmethod
    def plot_heatmap(
        path: Path = Aa.in_matrix_long_form,
        size: Optional[str] = Pa.size,
        stylesheet: Optional[str] = Pa.stylesheet,
        to: Optional[Path] = Pa.out_fig_file,
        log: Optional[Path] = CommonArgs.log,
        stderr: bool = CommonArgs.stderr,
    ) -> None:
        r"""
        Plot a heatmap of correlation between compounds.

        Will output one figure / file per correlation definition ('key' column).
        """
        MANDOS_SETUP(log, stderr)
        to = Pa.to_dir(path, to)
        df = PsiProjectedDf.read_file(path)
        rc = PlotOptions(
            size=size,
            stylesheet=stylesheet,
            rc={},
            hue=None,
            palette=None,
            extra={},
        )
        fig = ProjectionPlotter(rc).plot(df)
        MandosPlotUtils.save(fig, to)

    @staticmethod
    def plot_projection(
        path: Path = Pa.in_projection,
        viz: Optional[Path] = Pa.in_compound_style,
        colors: Optional[str] = Pa.colors,
        markers: Optional[str] = Pa.markers,
        palette: Optional[str] = Pa.palette,
        size: Optional[str] = Pa.size,
        stylesheet: Optional[str] = Pa.stylesheet,
        to: Optional[Path] = Pa.out_fig_file,
        log: Optional[Path] = CommonArgs.log,
        stderr: bool = CommonArgs.stderr,
    ) -> None:
        r"""
        Plot UMAP, etc. of compounds from psi matrices.

        Will plot the psi variables over a grid.
        """
        MANDOS_SETUP(log, stderr)
        to = Pa.to_dir(path, to)
        df = PsiProjectedDf.read_file(path)
        viz = None if viz is None else CompoundStyleDf.read_file(viz)
        df = Pa.add_styling(df, viz)
        palette = MandosPlotStyling.choose_palette(df, colors, palette)
        rc = PlotOptions(
            size=size,
            stylesheet=stylesheet,
            rc={},
            hue=colors,
            palette=palette,
            extra={},
        )
        fig = ProjectionPlotter(rc).plot(df)
        MandosPlotUtils.save(fig, to)


__all__ = ["PlotCommands"]
