# Automatic 3D T-Shirt Fitting

This project demonstrates a process for automatically fitting a 3D T-shirt model onto various 3D human body models using Python, `trimesh`, and `pyrender`. The core idea is to standardize the human model, estimate its shoulder width, resize the T-shirt model based on this estimation, position it appropriately, and then visualize the result.

## Overview

The workflow involves the following steps:

1.  **Load Models:** Load a 3D human body model (supports `.glb`, `.obj`, etc., via `trimesh`) and a template 3D T-shirt model.
2.  **Standardize Human Model:** Process the human model to have a consistent size and orientation. This involves centering, potentially rotating, and scaling it to predefined target dimensions using functions in `methods.py`. The standardization logic attempts to account for different initial model orientations.
3.  **Estimate Shoulder Width:** Calculate an approximate shoulder width for the *standardized* human model by analyzing vertices near the top of the mesh.
4.  **Resize T-shirt:** Scale the T-shirt model based on the estimated shoulder width of the human model, applying some heuristic multipliers to achieve a reasonable fit. The T-shirt is also standardized (rotated/scaled) to fit the target dimensions derived from the shoulder width.
5.  **Position T-shirt:** Apply a simple translation to position the resized T-shirt onto the standardized human model's torso area.
6.  **Visualize:** Use `pyrender` to display the standardized human model with the fitted T-shirt in an interactive viewer.

## Features

*   Loads various 3D model formats supported by `trimesh`.
*   Standardizes human body models to consistent dimensions and orientation.
*   Estimates shoulder width from mesh vertices.
*   Resizes a T-shirt model dynamically based on the target human model.
*   Provides a visual representation of the fitting using `pyrender`.

## Prerequisites

*   Python 3.6+
*   Required Python packages:
    *   `trimesh`: For loading and manipulating 3D meshes. Often requires dependencies like `numpy`, `scipy`, `rtree`, etc. Installing with `pip install trimesh[easy]` or `trimesh[all]` can be helpful.
    *   `pyrender`: For rendering and visualizing the 3D scene. Requires OpenGL compatible drivers.
    *   `numpy`: For numerical operations.
    *   `scipy`: Used here specifically for rotation conversions (`scipy.spatial.transform`).
    *   `Pillow` (PIL Fork): Image processing library (imported in `main.py`, though not directly used in the provided `cloth_mesh` logic, it might be needed by dependencies or other parts).
    *   `pygltflib`: For GLTF file interactions (imported in `main.py`, potentially used by `pyrender` or `trimesh` implicitly for `.glb` files).

## Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install trimesh[easy] pyrender numpy scipy Pillow pygltflib
    # Or install individually:
    # pip install trimesh numpy scipy Pillow pygltflib
    # pip install pyrender
    ```
    *Note: `pyrender` installation can sometimes be tricky depending on your OS and graphics setup. Refer to the official `pyrender` documentation if you encounter issues.*

4.  **Prepare Model Files:** Ensure you have the necessary 3D model files (`.glb`, `.obj`) organized in a structure similar to what's expected by `main.py`, typically within a `files` directory:
    ```
    .
    ├── main.py
    ├── methods.py
    └── files/
        ├── Female/
        │   ├── female_body_base.glb
        │   └── female_body.glb
        ├── Male/
        │   ├── male_body-1.glb
        │   ├── male_body-2.glb
        │   ├── Local-Generated-1.obj
        │   └── Local-Generated-2.obj
        └── T-shirt Sample/
            └── static_tshirt.glb
    ```
    *Adjust the paths in `main.py` if your structure differs.*

## Usage

1.  Make sure your model files are correctly placed and the paths in `main.py` point to them.
2.  Navigate to the project directory in your terminal.
3.  Activate your virtual environment (if you created one).
4.  Run the main script:
    ```bash
    python main.py
    ```

The script will sequentially process each human model listed in the `l` list within `main.py`. For each model, it will:
*   Load the human and T-shirt models.
*   Perform the standardization and fitting process.
*   Print the calculated target T-shirt width (`d` after heuristic scaling).
*   Open a `pyrender` interactive viewer window showing the human model wearing the fitted T-shirt.
*   Close the viewer window to proceed to the next model in the list.

## Code Explanation

### `methods.py`

This file contains utility functions for processing the 3D meshes.

*   **`get_model_orientation_and_extents(mesh_or_scene)`:**
    *   Takes a `trimesh.Trimesh` or `trimesh.Scene` object.
    *   If it's a Scene, concatenates all geometries into a single mesh.
    *   Calculates the axis-aligned bounding box extents (dimensions).
    *   Calculates the principal inertia transform, which helps determine the natural orientation of the mesh based on mass distribution.
    *   Returns a dictionary containing the extents, the rotation matrix from the principal inertia transform, and the Euler angles (in degrees) corresponding to that rotation.
*   **`load_and_standardize_model2(filepath, target_dims=(...), angle=0.0)`:**
    *   Takes a mesh object (or Scene), target dimensions (X, Y, Z), and an optional initial rotation angle (around X-axis).
    *   If it's a Scene, concatenates geometries.
    *   Applies the initial X-axis rotation.
    *   Translates the mesh so its centroid is at the origin (0, 0, 0).
    *   Calculates the current dimensions based on the bounding box.
    *   Determines the scaling factors needed to reach the `target_dims`.
    *   Applies the scaling transformation.
    *   Returns the transformed (standardized) mesh.
*   **`estimate_shoulder_distance(mesh, z_threshold_ratio=0.85)`:**
    *   Takes a standardized `trimesh.Trimesh` object.
    *   Determines a Z-height threshold (defaulting to 85% of the total height from the bottom).
    *   Selects vertices above this threshold (approximating the upper body/shoulder region).
    *   Calculates the difference between the maximum and minimum X-coordinates among these upper vertices.
    *   Returns this difference as the estimated shoulder width.
*   **`get_standerd_mesh(body)`:**
    *   Takes a raw human body mesh or scene.
    *   Combines geometries if it's a scene.
    *   Uses `get_model_orientation_and_extents` to check the principal Y-axis Euler angle (`flag`).
    *   Applies `load_and_standardize_model2` with *different* target dimensions and initial rotations based on the `flag`. This seems to be a heuristic approach to handle models that might be oriented differently (e.g., facing sideways vs. forward in their principal axes).
        *   If `flag < 0`, uses target `(0.8, 0.28, 1.8)` and rotates 90 degrees around X.
        *   If `flag >= 0`, uses target `(1.5, 0.28, 1.8)` and no initial rotation.
    *   Returns the standardized human mesh.

### `main.py`

This script orchestrates the loading, processing, and visualization.

*   **Model Loading:** Loads several predefined human body models and the T-shirt model using `trimesh.load`.
*   **`cloth_mesh(mesh)` Function:**
    *   Takes a raw human body mesh/scene as input.
    *   Loads the T-shirt model (`static_tshirt.glb`) and combines its geometries if necessary.
    *   Calls `m.get_standerd_mesh` to get the standardized version of the input human model.
    *   Calls `m.estimate_shoulder_distance` on the standardized human model.
    *   Applies a heuristic scaling factor (`2.7` or `3.6`) to the estimated shoulder distance (`d`) to determine the target width for the T-shirt. The choice depends on whether the raw shoulder estimate is above or below 0.4.
    *   Calls `m.load_and_standardize_model2` to resize and orient the T-shirt using the calculated target width (`d`), a fixed depth (`0.45`), a fixed height (`0.85`), and a fixed 90-degree rotation around the X-axis.
    *   Applies a *fixed translation* (`[0.0, 0, 0.240]`) to the standardized T-shirt to position it roughly on the human model's torso.
    *   Creates a `pyrender.Scene`.
    *   Adds the standardized human mesh and the transformed T-shirt mesh to the scene.
    *   Launches the `pyrender.Viewer` to display the scene.
*   **Main Execution Loop:**
    *   Defines a list `l` containing some of the loaded human models.
    *   Iterates through this list, calling `cloth_mesh` for each model.

## Potential Improvements & Future Work

*   **More Robust Positioning:** The current fixed translation `[0.0, 0, 0.240]` for the T-shirt is very basic. A better approach might involve aligning centroids or using bounding box information for more accurate initial placement.
*   **Refined Standardization:** The `get_standerd_mesh` function uses a heuristic based on one Euler angle. A more robust method might involve aligning models based on specific anatomical landmarks if available, or using more sophisticated orientation analysis.
*   **Improved Shoulder/Body Measurement:** The `estimate_shoulder_distance` is approximate. More accurate body measurements could lead to better T-shirt scaling. This might involve identifying specific landmarks or using more complex shape analysis.
*   **Realistic Fitting:** This implementation performs rigid scaling and positioning. True clothing fitting requires non-rigid deformation (simulation) to make the cloth conform realistically to the body shape. Libraries like ARCSim, PyFlex, or custom physics simulations could be explored.
*   **Parameterization:** Hardcoded values (target dimensions, scaling factors, translation offsets, threshold ratios) could be exposed as parameters or configuration options.
*   **User Interface:** A simple GUI could allow users to load arbitrary models and adjust parameters.
*   **Error Handling:** Add checks for file loading errors or cases where `estimate_shoulder_distance` might fail (e.g., very flat meshes).
*   **Support for Different Garments:** Extend the logic to handle different types of clothing with varying scaling and positioning requirements.


