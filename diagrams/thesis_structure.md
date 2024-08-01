```mermaid

flowchart LR
    %% Chapters
    C1(Chapter 1<br>Introduction)
    C2(Chapter 2<br>Preliminaries)
    C3(Chapter 3<br>A methodology<br>for urban planning<br>generation)
    C4(Chapter 4<br>Rhino Plug-in)
    C5(Chapter 5<br>Case study <br>in Vienna)
    C6(Chapter 6<br>Case study <br>in Málaga)
    C7(Chapter 7<br>Conclusions<br> and Future Work)
    C8(Chapter 8<br>Appendix)

    %% Subsections for Chapter 2
    C21(AEC)
    C22(Literature Review)
    C23(Market Analysis)

    %% Subsections for Chapter 3
    C31(Parametric model)
    C32(Objectives<br>based on<br>geometrical<br>datasets)
    C33(Optimization)

    %% Subsections for Chapter 4
    C41(Plug-in description)
    C42(User Experience)

    %% Subsections for Chapter 5
    C51(Urban planning generation)
    C52(Evaluation of results)

    %% Subsections for Chapter 6
    C61(Urban planning generation)
    C62(Evaluation of results)

    %% Subsections for Chapter 8
    C81(GitHub repository)
    C82(Further<br>Ideas)

    %% Styling
    style C1 fill:#FFB1AF,stroke:#333,stroke-width:2px,color:black
    style C2 fill:#FFB1AF,stroke:#333,stroke-width:2px,color:black
    style C3 fill:#ff6661,stroke:#333,stroke-width:2px,color:black
    style C4 fill:#ff6661,stroke:#333,stroke-width:2px,color:black
    style C5 fill:#ff6661,stroke:#333,stroke-width:2px,color:black
    style C6 fill:#ff6661,stroke:#333,stroke-width:2px,color:black
    style C7 fill:#FFB1AF,stroke:#333,stroke-width:2px,color:black
    style C8 fill:#FFB1AF,stroke:#333,stroke-width:2px,color:black
    style C21 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C22 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C23 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C31 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C32 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C33 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C41 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C42 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C51 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C52 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C61 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C62 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C81 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black
    style C82 fill:#D3D3D3,stroke:#333,stroke-width:2px,color:black

    %% Connections
    C1 --> C2
    C2 --> C3
    C2 --> C21
    C2 --> C22
    C2 --> C23
    C3 --> C31
    C3 --> C32
    C3 --> C33
    C3 --> C4
    C4 --> C41
    C4 --> C42
    C4 --> C5
    C5 --> C51
    C5 --> C52
    C4 --> C6
    C6 --> C61
    C6 --> C62
    C5 --> C7
    C6 --> C7

    C4 --> C81
    C8 --> C81
    C1 --> C82
    C8 --> C82
