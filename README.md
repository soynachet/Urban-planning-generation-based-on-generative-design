Automated Urban Planning — Generative Design (Rhino/Grasshopper)

An open-source plugin for generative urban planning that integrates parametric modeling with Rhino/Grasshopper, context analysis through clustering, subdivision and typology allocation, and fitness-based optimization using a unified penalty formulation.

The project aims to generate regulation-aware, traceable urban layouts that balance density, greenery, and zoning requirements within a transparent and controllable workflow.



Key Features

End-to-end reproducible workflow from clustering to optimization.

Unified fitness formulation with quadratic penalty scaling and outlier capping.

Modular architecture that allows replacing clustering, allocation, or fitness modules independently.

Real-world validation through urban-scale case studies.

Rhino/Grasshopper integration with Opossum (RBFOpt) for optimization.

Python scripts for data handling, normalization, and metric evaluation.



Requirements

Rhino 7 or 8 with Grasshopper

Opossum plugin for optimization

Python 3.9 or later

Recommended Python packages: NumPy, Pandas, Scikit-learn




Installation

1. Clone or download this repository.


2. Install Opossum in Grasshopper.


3. Open the Grasshopper definitions provided in the “rhino” folder.


4. Optionally, set up a Python environment and install the required libraries listed above.





Quick Start

1. Load the site context including plot boundaries, buildings, and green areas.


2. Run the clustering module to define target values and admissible parameter ranges.


3. Adjust the weights for density, green area, building count, heights, and other metrics.


4. Launch Opossum to optimize the configuration.


5. Evaluate and select the best-performing solutions.





Fitness Parameters

Spatial metrics include plot count, green area ratio, and compactness.
Volumetric metrics include total volume, mean height, and density.
Morphological metrics include building count and footprint size.
Locational metrics measure distance to centroid or perimeter.

Constraint penalties are computed as normalized deviations with quadratic scaling, rewarding feasible solutions and penalizing violations.


---

Recommended Practices

Begin with balanced weights and adjust based on performance feedback.

Maintain consistent evaluation budgets to ensure comparability.

Tune subdivision depth and density targets according to site type.

Reuse and adapt Grasshopper components for efficiency.



---

Data and Outputs

Inputs can include geometric files such as GeoJSON, DXF, or 3DM, and configuration files in CSV or JSON format.
Outputs consist of optimized Rhino geometries and corresponding logs of fitness values and constraints.


---

Authors

Ignacio Pérez-Martínez
María Martínez-Rojas
José Manuel Soto-Hidalgo

