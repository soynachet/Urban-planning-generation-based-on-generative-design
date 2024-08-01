```mermaid
classDiagram
    direction TB
    class GeometryInputs {
        dataset
        plot_outline
    }

    class UserInterfaceInputs {
        clustering_parameters
        clustering_weights
        optimization_weights
    }

    class OpossumInputs {
        plot_subdivision_parameters
        building_allocation_parameters
    }

    class DatasetClustering {
        park_polylines_clean
        plot_polylines_clean
        building_solids_clean
        geometry_dictionary
        -> compute_clustering_values
    }

    class PlotSubdivision {
        -> subplots
    }

    class BuildingAllocation {
        houses_in_subplots
        -> compute_optimization_values
    }

    class Utility {
        functions
    }

    class Optimization {
        normalize_values
        -> compute_penalization_value
    }

    class Opossum {
        RBFOpt
    }

    GeometryInputs --> DatasetClustering : input
    GeometryInputs --> PlotSubdivision : input
    GeometryInputs --> BuildingAllocation : input

    UserInterfaceInputs --> DatasetClustering : input
    UserInterfaceInputs --> PlotSubdivision : input
    UserInterfaceInputs --> BuildingAllocation : input
    UserInterfaceInputs --> Optimization : input

    OpossumInputs --> PlotSubdivision : input
    OpossumInputs --> BuildingAllocation : input

    DatasetClustering --> Optimization : uses

    Utility --> DatasetClustering : uses
    Utility --> PlotSubdivision : uses
    Utility --> BuildingAllocation : uses
    Utility --> Optimization : uses

    PlotSubdivision --> BuildingAllocation : uses

    BuildingAllocation --> DatasetClustering : uses
    BuildingAllocation --> Optimization : uses

    Optimization --> Opossum : uses

    Opossum --> OpossumInputs : uses

    style GeometryInputs fill:#ADD8E6,stroke:#000000,stroke-width:2px,color:#000000
    style UserInterfaceInputs fill:#ADD8E6,stroke:#000000,stroke-width:2px,color:#000000
    style OpossumInputs fill:#ADD8E6,stroke:#000000,stroke-width:2px,color:#000000
    style DatasetClustering fill:#FFBBFF,stroke:#000000,stroke-width:2px,color:#000000
    style PlotSubdivision fill:#FFBBFF,stroke:#000000,stroke-width:2px,color:#000000
    style BuildingAllocation fill:#FFBBFF,stroke:#000000,stroke-width:2px,color:#000000
    style Utility fill:#FFBBFF,stroke:#000000,stroke-width:2px,color:#000000
    style Optimization fill:#90EE90,stroke:#000000,stroke-width:2px,color:#000000
    style Opossum fill:#90EE90,stroke:#000000,stroke-width:2px,color:#000000
