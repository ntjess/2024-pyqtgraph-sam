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

### Topic Overview

Image annotation is the bedrock of computer vision machine learning tasks. Unfortunately, it is also time-consuming and soul-sucking. However, a small amount of automation can go a long way in reducing the time and effort required to label images. This tutorial "teaches a man to fish" with groundwork in each major area of the image labeling process: displaying data, handling user input, adding automation, and saving the results. Toward this end, the following objectives are covered
- **Computer Vision**: Basic image handling (loading, resizing, pytorch/numpy manipulation), morphological operations (erosion/dilation, contour detection), CV models (Ultraltyics FastSAM usage)
- **Interactive plotting**: Basic PyQtGraph window setup, forms of data representation (image, scatterplot, axis scaling), hooking into user input
- **Qt for Python**: Qt events, signals and slots
- **General data science practices**: Data visualization, python ecosystem integration, and general programming practices

### Who Should Attend?
Minimal prerequisite experience is required to attend this tutorial, as it is geared primarily toward novice-to-intermediate Python data scientists. The table below provides a rough outline of who would benefit most from the material based on their skill level in each given topic:

<table>
<thead>
  <tr>
    <th></th>
    <th></th>
    <th style="text-align: center" colspan="3"><b>Topics Covered</b></th>
  </tr>
</thead>
<tbody>
  <tr>
    <td></td>
    <td></td>
    <td>Computer vision</td>
    <td>Interactive plotting</td>
    <td>Qt for Python</td>
  </tr>
  <tr>
    <td rowspan="3"><b>Tutorial Depth</b></td>
    <td>Novice</td>
    <td>✅</td>
    <td>✅</td>
    <td>✅</td>
  </tr>
  <tr>
    <td>Intermediate</td>
    <td>✅</td>
    <td>✅</td>
    <td>-</td>
  </tr>
  <tr>
    <td>Expert</td>
    <td>-</td>
    <td>-</td>
    <td>-</td>
  </tr>
</tbody>
</table>


### Outline

- Overview [10 minutes]
    - Give a brief overview of annotation as a concept and its usefulness
    - Get everyone setup with tutorial materials
<div style="text-align:center">
<img src="./slides/media/types-of-annotation.jpg" width="50%"/>
</div>

- Creating a basic image viewer [40 minutes]
    - Introduction to PyQtGraph, Qt, and GUI anatomy
    - Gathering independent examples of `ImageItem`, `PlotWidget`, and `ParameterTree` into a coherent application

<div style="text-align:center">
<img src="./slides/media/window-loading-image.jpg" width="50%"/>
</div>

- [10 minute break]

- Segment the current image using `FastSAM` & add configurations [50 minutes]

<div style="text-align:center">
<img src="./slides/media/fast-sam.jpg" width="50%"/>
</div>

- [10 minute break]

- Enable user-selectable region building [50 minutes]

<div style="text-align:center">
<video controls src="./slides/media/region-builder.mp4" width="50%"/>
</div>

- [10 minute break]

- Persist user edits [50 minutes]
  - Undo / redo region edits
  - Save prediction mask and edits to disk
  - Load prediction mask and edits from disk

- Enable manual edits using a brush [20 minutes]

- Future work: incorporate image processing algorithms, metadata like labels, QA, etc. [10 minutes]

<div style="text-align:center">
<img src="./slides/media/s3a-window.jpg" width="50%"/>
</div>


- Conclusion [10 minutes]

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