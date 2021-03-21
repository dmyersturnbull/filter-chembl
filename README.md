# Mandos

[![Version status](https://img.shields.io/pypi/status/mandos)](https://pypi.org/project/mandos)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python version compatibility](https://img.shields.io/pypi/pyversions/mandos)](https://pypi.org/project/mandos)
[![Version on Docker Hub](https://img.shields.io/docker/v/dmyersturnbull/mandos?color=green&label=Docker%20Hub)](https://hub.docker.com/repository/docker/dmyersturnbull/mandos)
[![Version on GitHub](https://img.shields.io/github/v/release/dmyersturnbull/mandos?include_prereleases&label=GitHub)](https://github.com/dmyersturnbull/mandos/releases)
[![Version on PyPi](https://img.shields.io/pypi/v/mandos)](https://pypi.org/project/mandos)
[![Version on Conda-Forge](https://img.shields.io/conda/vn/conda-forge/mandos?label=Conda-Forge)](https://anaconda.org/conda-forge/mandos)  
[![Documentation status](https://readthedocs.org/projects/mandos-chem/badge)](https://mandos-chem.readthedocs.io/en/stable)
[![Build (GitHub Actions)](https://img.shields.io/github/workflow/status/dmyersturnbull/mandos/Build%20&%20test?label=Build%20&%20test)](https://github.com/dmyersturnbull/mandos/actions)
[![Test coverage (coveralls)](https://coveralls.io/repos/github/dmyersturnbull/mandos/badge.svg?branch=main&service=github)](https://coveralls.io/github/dmyersturnbull/mandos?branch=main)
[![Maintainability (Code Climate)](https://api.codeclimate.com/v1/badges/aa7c12d45ad794e45e55/maintainability)](https://codeclimate.com/github/dmyersturnbull/mandos/maintainability)
[![CodeFactor](https://www.codefactor.io/repository/github/dmyersturnbull/mandos/badge)](https://www.codefactor.io/repository/github/dmyersturnbull/mandos)
[![Code Quality (Scrutinizer)](https://scrutinizer-ci.com/g/dmyersturnbull/mandos/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/dmyersturnbull/mandos/?branch=main)  
[![Created with Tyrannosaurus](https://img.shields.io/badge/Created_with-Tyrannosaurus-0000ff.svg)](https://github.com/dmyersturnbull/mandos)

**Fetch knowledge on chemical compounds from public databases, squeezing it all into a consistent form.**

Mandos extracts ~30 annotation types from ~15 databases.
Types include mechanisms of action (MoAs), binding activity, disease indications, classifications, clinical trials,
pathways involved, legal statuses, physical properties, and co-occurring literature terms.
Output is formatted in consistent CSV files, mainly for consumption by algorithms.
All knowledge is a semantic triple, such as `alprazolam inactive at BK receptor`, plus additional data
specific to each type (e.g. EC50 or clinical phase).
It’s also happy to fetch annotations for compounds that are structurally similar to yours.

### 🎨 Example

You can use Mandos as a Python API or command-line tool.
To search just the mechanism of action for alprazolam:

```bash
echo "VREFGVBLTWBCJP-UHFFFAOYSA-N" > compounds.txt
mandos chembl:mechanism compounds.txt
```

The following info is perhaps enough to get started.
A lot of processing is done behind-the-scenes;
**[see the docs 📚](https://mandos-chem.readthedocs.io/en/latest/)** for more.

**Input:** compounds.txt is a line-by-line list of
[InChI Keys](https://en.wikipedia.org/wiki/International_Chemical_Identifier#InChIKey)
Pass type-specific command-line options like `--taxa vertebrata`,
or run multiple searches with `mandos meta:all compounds.txt --config searches.toml`.
(See: [example config file](https://github.com/dmyersturnbull/mandos/blob/main/mandos/resources/ags_example.toml))
`mandos <type> --help` will show and briefly explain the options.

**Output:** One CSV file per annotation type – 10 columns shared between all files, plus type-specific columns.
The consistent columns are: _record_id_, _inchikey_, _compound_id_, _compound_name_,
_predicate_, _object_id_, _object_name_, _search_key_, _search_class_, and _data_source_.
Additional columns include EC50, original name, species, clinical phase, etc.
You could concatenate the files for something like the following.
(_Columns were dropped and renamed for display._)

```
comp. ID  comp. name  predicate name                 object ID       object name
--------- ----------  -----------------------------  ------------- ------------------------------
CHEMBL661 alprazolam  positive allosteric modulator  CHEMBL2093872 GABA-A receptor; anion channel
CHEMBL661 alprazolam  activity at                    CHEMBL2096986 Cholecystokinin receptor
CHEMBL661 alprazolam  phase-3 trial for              D012559       Schizophrenia
CHEMBL661 alprazolam  phase-4 trial for              D016584       Panic Disorder
CHEMBL661 alprazolam  has ATC L3 code                N05B          anxiolytics
CHEMBL661 alprazolam  has ATC L4 code                N05BA         Benzodiazepine derivatives
PC218     alprazolam  has GHS symbol                 H302          Harmful if swallowed
PC218     alprazolam  has acute effect               -             behavioral: euphoria
PC218     alprazolam  DDI with                       PC65016       amprenavir
PC218     alprazolam  therapeutic for                D001008       Anxiety Disorders
PC218     alprazolam  enriched for term              -             anxiolytic
PC218     alprazolam  co-occurs with drug            PC134664      Benzodiazepine
PC218     alprazolam  co-occurs with gene            1.14.14.1     Monoamine Oxidase
PC218     alprazolam  co-occurs with disease         D016584       Panic Disorder
PC218     alprazolam  interacts with gene            -             CYP3A4
PC218     alprazolam  positive allosteric modulator  GABRA1        GABA(A) Receptor
PC218     alprazolam  inactive at                    KCNMB4        BK Channel
PC218     alprazolam  active at                      AR            androgen receptor
PC218     alprazolam  is of class                    CHEBI:22720   benzodiazepine
PC218     alprazolam  has DEA schedule               4             Schedule IV
.         .             .                              .             .
.         .             .                              .             .
.         .             .                              .             .
```

### 🍁 Contributing

Mandos is licensed under the [Apache License, version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
[New issues](https://github.com/dmyersturnbull/mandos/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/mandos/blob/master/CONTRIBUTING.md).  
Generated with [Tyrannosaurus](https://github.com/dmyersturnbull/tyrannosaurus).
