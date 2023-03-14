---
title: 'NEMSEER: A Python package for downloading and handling historical National Electricity Market forecast data produced by the Australian Energy Market Operator'
tags:
  - Python
  - NEM
  - National Electricity Market
  - Forecast
  - PASA
  - Pre dispatch
authors:
  - name: Abhijith Prakash
    orcid: 0000-0002-2945-4757
    affiliation: "1, 3"
    corresponding: true
  - name: Anna Bruce
    orcid: 0000-0003-1820-4039
    affiliation: "2, 3"
  - name: Iain MacGill
    orcid: 0000-0002-9587-6835
    affiliation: "1, 3"
affiliations:
 - name: School of Electrical Engineering and Telecommunications, University of New South Wales, Australia
   index: 1
 - name: School of Photovoltaics and Renewable Energy Engineering, University of New South Wales, Australia
   index: 2
 - name: Collaboration on Energy and Environmental Markets (CEEM), University of New South Wales, Australia
   index: 3
date: 14 March 2023
bibliography: paper.bib
---

# Summary

In electrical power systems and their associated market frameworks, actions close to or during real-time (i.e. the time of power delivery) may be critical to ensuring that:

1. Supply and demand are balanced, and that the power system is operated within its technical envelope.
2. Market participants can maximise revenues from their generating and/or demand-side resources.

To some degree, *real-time* actions and their outcomes are dependent on decisions made *ahead-of-time*, e.g. starting a gas turbine, charging a battery energy storage system and maintaining a greater level of spare capacity in reserve during periods of system stress. Given physical and financial uncertainties, no ahead-of-time decision is perfect; instead, they are made in light of the best available information, which includes demand, generation and market price forecasts [@maysPrivateRiskSocial2022].

Though the Australian National Electricity Market (NEM) lacks the ahead-of-time market platforms that are present in many restructured electricity industries in Europe and North America [@cramtonElectricityMarketDesign2017; @roquesEvolutionEuropeanModel2021], market participants provide resource and market offer information to the Australian Energy Market Operator (AEMO), which uses this submitted data alongside demand and renewable energy generation forecasts to run several centralised ahead-of-time processes [@australianenergymarketoperatorPredispatchOperatingProcedure2021; @australianenergymarketoperatorPreDispatch; @australianenergymarketoperatorReliabilityStandardImplementation2020]. These processes produce ahead-of-time information, or ["forecasts"](https://github.com/UNSW-CEEM/NEMSEER#user-content-fn-1-046877d6fabd7950d214da5f5dbc27c4), that market participants can use to inform their operational decision-making (i.e. how they participate in the central dispatch process that is used to clear the gross-pool energy markets in each region of the NEM), and that AEMO can use as a trigger to undertake emergency actions during potential risk periods [@australianenergymarketcommissionReserveServicesNational2021].

`NEMSEER` is a Python 3 package that facilitates the access and analysis of *historical* ahead-of-time operational information from AEMO-run processes. Specifically, it enables users to download

# Statement of need

Whilst AEMO publicly releases data from five of its operational ahead-of-time processes, significant effort is required to obtain and process this data for analysis. Firstly, a user must be familiar with how AEMO's data repositories are organised. Secondly, a user must have knowledge of what type of data each ahead-of-time process generates (i.e. the range of tables and columns available), and of each process' lookahead horizon (i.e. for a given time at which the process is *run*, what are the *forecasted* periods?). Finally, a user must download and unzip CSV files before being able to handle tables of interest using data analysis tools.

`NEMSEER` solves these issues by:

1. Providing learning resources and references (via the README and a [glossary](https://nemseer.readthedocs.io/en/latest/glossary.html) in the documentation) that unpack what each ahead-of-time process is and what data they offer.
2. Making it easier to download and handle this data. `NEMSEER` can inform the user of the date range of available data, which data tables are available and even generate the appropriate range of run times for a set forecasted times that a user is interested in. Once a user queries a subset of data, `NEMSEER` will download, unzip and process the CSV files into `pandas` or `xarray` data structures.


# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Nicholas Gorman, Declan Heim and Dylan McConnell.

`NEMSEER` was developed as a part of research supported by an Australian Government Research Training Program Scholarship.

# References
