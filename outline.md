# SciPy 2024 Tutorial Submission: Image Labeling Tool from Scratch using PyQtGraph an FastSAM

Contributors:

- Nathan Jessurun

## Short Description

Image annotation is an essential part of computer vision and machine learning workflows,
but is an incredibly time-consuming & manual task. Several tools provide automated
assistance, but they are often complex, difficult to customize, or hidden behind a
paywall. This tutorial empowers attendees to build their own image labeling tool from
scratch using PyQtGraph for visuals and FastSAM for automated labeling. Along the way,
they will learn the basics of real-time data visualization, Qt Python GUI development, and
image annotation -- skills that broadly apply beyond the walls of this tutorial.

## Long Description

### Overview

Image annotation is the bedrock of computer vision machine learning tasks. Unfortunately,
it is also time-consuming, soul-sucking,

<!-- Example from different tutorial-->
Dask is a flexible tool for parallelizing Python code on a single machine or across a cluster.

We can think of dask at a high and a low level:

- High level collections: Dask provides high-level Array, Bag, and DataFrame collections that mimic and build upon NumPy arrays, Python lists, and Pandas DataFrames, but operate in parallel on large datasets that may not fit into memory.

- Low Level schedulers: Dask provides dynamic task schedulers that execute task graphs in parallel. These schedulers power the high-level collections mentioned above but can also power custom, user-defined workloads to expose potential parallelism in procedural code.

Different users operate at different levels but it is useful to understand both. This tutorial will cover both the high-level use of `dask.array` and `dask.dataframe` and the low-level use of dask graphs and schedulers. Attendees will come away:

- Able to use `dask.delayed` to parallelize existing code
- Understanding the differences between the dask schedulers, and when to use one over another
- Able to use the `distributed` futures interface to distribute work over a cluster
- With a firm understanding of the different dask collections (`dask.array` and `dask.dataframe`) and how and when to use them

### Outline

- Overview [10 minutes]

    - Give a brief overview of what dask is
    - Get everyone setup with tutorial materials

- Parallelizing general code using Dask Delayed [40 minutes]

    - Introduce the `dask.delayed` interface. Participants will learn how to use dask to parallelize existing code by decorating functions.
    - Motivating example: Parallelizing an ETL workflow

- [10 minute break]

- Scheduling and futures [50 minutes]

    - Discuss the different schedulers. Briefly enumerate why you might use one over another.
    - Dive into using the distributed scheduler futures interface.
    - Motivating example: Repeat of the ETL workflow above, this time using the distributed futures interface

- [10 minute break]

- Parallel arrays using Dask Array [50 minutes]

    - Introduce dask collections by starting with dask array. Discuss how dask collections mirror their single-threaded counterparts (e.g. dask array mirrors numpy). Many examples of converting numpy code to dask
    - Motivating example: Ocean temperature data

- [10 minute break]

- Parallel DataFrames using Dask DataFrame [50 minutes]

    - Introduction to dask dataframe. Participants will work through several examples demonstrating common tasks and pitfalls, with brief discussions of performance tips.
    - Motivating example: NYC taxi data

- If Extra Time…

    - Discuss debugging and profiling strategies
    - Discuss advanced features of the distributed scheduler

- Conclusion [10 minutes]
    - Recap on what we learned
    - Provide references for where to go from here.

### Comments

This tutorial is based on the author's experience giving similar tutorials in the past. The materials will (likely) be modified and updated versions based on the following repositories:

- [https://github.com/dask/dask-tutorial/tree/scipy-2017](https://github.com/dask/dask-tutorial/tree/scipy-2017)
- [https://github.com/jcrist/dask-tutorial-pydata-seattle-2017](https://github.com/jcrist/dask-tutorial-pydata-seattle-2017)

The tutorial is presented as a set of notebooks, with materials and multiple exercises provided in each notebook. The latter part of the tutorial will make use of a distributed environment provided via an easy web interface (just a single blue button that drops them into a jupyter notebook) that the students can connect to experiment with using dask on a cluster. This allows experiencing real world workloads without requiring the students do any extensive setup beforehand. The earlier part of the tutorial will be done on the student's laptop to ensure the students have dask/distributed setup properly locally for any further experimenting/learning after the tutorial.

## Setup Instructions

If using conda:

    $ conda install -c conda-forge dask distributed numpy pandas jupyter

If using pip

    $ pip install dask distributed numpy pandas jupyter