---
title: 'DE-Sim: An Object-Oriented Discrete-Event Simulator in Python'
tags:
  - Python
  - dynamics
  - modeling
  - simulation
  - discrete-event simulation
  - object-oriented simulation
  - parallel discrete-event simulation
authors:
  - name: Arthur P. Goldberg
    orcid: 0000-0003-2772-1484
    affiliation: "1"
  - name: Jonathan R. Karr
    orcid: 0000-0002-2605-5080
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Department of Genetics and Genomic Sciences, and Icahn Institute for Genomics and Multiscale Biology, Icahn School of Medicine at Mount Sinai, New York, NY, 10029, USA
   index: 1
date: 20 July 2020
bibliography: paper.bib
---

# Summary

Discrete-event simulation (DES) is a simulation method that analyzes systems whose events occur at discrete instants in time.
Events and their simulation times are dynamically determined.
Many fields employ models that use DES, including biochemical modeling, computer network performance analysis, war gaming, modeling of infectious disease transmission, and others [@banks2005discrete].

The construction of a DES model can be simplified and accelerated by using a DES simulator that implements the generic features needed by all DES models, such as executing events in increasing simulation time order.
Model construction can be further enhanced, and models can be made more comprehensible and reusable, by structuring models as object-oriented programs.
This approach, known as *object-oriented discrete-event simulation* (OO DES), requires that modelers represent entities in the system being modeled as objects in a model, and represent interactions between entities as event messages exchanged between objects.
OO DES was invented in the 1960s by the SIMULA language [@dahl1966simula; @nygaard1978development] and continues with modern languages such as SystemC [@mueller2001simulation; @ieee2012ieee] and SIMUL8 [@concannon2003dynamic].

`DE-Sim` is a Python package that supports OO DES simulations written in Python.

# Research purpose

Since existing open source Python simulators do not support an object-oriented, message-passing interface researchers who want to build OO DES models in Python need an OO DES Python package like DE-Sim.
For example, we have used DE-Sim to create a research tool--a multi-algorithmic simulator of models that comprehensively represent the biochemical dynamics inside individual biological cells [@goldberg2020wc_sim].

Another benefit of implementing models in the object-oriented, message-passing framework supported by DE-Sim is that parallel DES simulation can reduce the runtimes of their simulations, which are often inconveniently long.
The OO DES framework makes parallel simulation feasible because 1) objects that they do not share memory references can be distributed on multiple processors, and 2) a parallel DES simulator interfaces with simulation objects via operations that exchange event message between objects [@Jefferson1985; @Barnes2013; @Carothers2000].
Examples of research models that may be accelerated by parallel simulation include epidemic outbreak phenomena [@perumalla2012discrete] and comprehensive models of the biochemistry of human cells [@goldberg2016toward].

# DE-Sim features

Simulation applications that run on DE-Sim are structured as OO programs.
Simulation objects are specified as subclasses of DE-Sim's built-in `ApplicationSimulationObject`.
Each simulation object instance has these state variables required by the simulator and used by the application:
  `name`: the text name of a simulation object; each simulation object must be given a unique text name when it's created
  `time`: the current simulation time

Simulation events are scheduled and executed by simulation object instances. Two event scheduling methods are provided by the DE-Sim simulation object:
  `send\_event(delay, recieving\_object, event\_message)`: schedule an event to occur `delay` time units in the future; `event\_message` contains the data needed to execute the event; the event will be executed by simulation object `recieving\_object` which will receive `event\_message`.
  `send\_event\_absolute(event\_time, receiving\_object, event\_message)`: schedule an event to occur at absolute simulation time `event\_time`; the remaining arguments have the same meaning as in `send\_event\_absolute`

# DE-Sim implementation

# Example

# Acknowledgements

# References