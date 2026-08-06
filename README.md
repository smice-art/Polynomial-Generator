<p align="center">
  <img src="images/addon.jpg" alt="K-Noid Generator width="100%">
</p>

# Polynomial Generator
Polynomial Art Studio

# Info ⚠️
Please excuse me regarding the correct mathematical terms; I am unfortunately not a mathematician, so they are sometimes certainly not correct.

# Screen Shot
![Banner Image](images/screen.jpg)

# Instruction - Documentation

1 THE CORE GEOMETRY
* Pattern: Selects the mathematical formula (S2 = Sheet 2, F1/F4 = Original).
* Degree (N-Roots): CRITICAL! Must align with the pattern.
   ** Set to 3 for all S2 (Sheet 2) patterns.
   ** Set to 6 for F4 (Orbital Ring).
   ** Set to 8 for F1 (Original 5-Fold).
  * Coefficients (C8/C5 R & I): Custom number injections to mutate shapes.

ONLY active for F1 and F4. 
You must make massive changes (e.g., 200 or -500) to see effects.

2 THE TRACKING ENGINE 
These sliders stop lines from becoming jagged or crossing over ("jumps").
* Max Jump: Global speed limit for line travel between points.
   ** High (8.0 - 10.0): For wide, sweeping loops (like F4).
   ** Low (0.5 - 0.8): For tight, disconnected masks (like S2_R1_1).
* Points (t1): Resolution of the line. Increase to 600-800 if jumps persist.
* Dual-Zone Stabilizer: Safety net when high Max Jump ruins the center.
   * Inner Zone: Size of the "safe zone" around the origin (1.0 - 2.0).
   * Strictness: Multiplier for jumps inside the zone (e.g., 0.2 reduces jump limit to 20% in the center).

3 3D FORM & VISUALS 
* Layers (t2): Number of stacked rings creating depth.
* Z-Spread: Distance between layers on the Z-axis.
* Thickness: Physical thickness of the curve bevel.
* Spline Type:
   ** Poly: Jagged, straight lines (fastest, good for debugging).
   ** NURBS: Extremely smooth, pulls like a rubber band. (Best for florals).
   ** Bezier: Perfectly smooth, exact coordinates. (Best for Sheet 2 geometric shapes).

## Views
| Image | Preview |
| :--- | :--- |
| <img src="images/P00.jpg" width="250"> | <img src="images/P02.jpg" width="250"> |
| <img src="images/P09.jpg" width="250"> | <img src="images/P03.jpg" width="250"> |
| <img src="images/P06.jpg" width="250"> | <img src="images/P07.jpg" width="250"> |
| <img src="images/P12.jpg" width="250"> | <img src="images/P14.jpg" width="250"> |
| <img src="images/P15.jpg" width="250"> | <img src="images/P16.jpg" width="250"> |
| <img src="images/P18.jpg" width="250"> | <img src="images/P17.jpg" width="250"> |
| <img src="images/P05.jpg" width="250"> | <img src="images/P10.jpg" width="250"> |

## Release Notes

### v1.0.0 (august 6, 2026)
- **Publishing**: First public upload of the Add-on.

### Blender
![Blender](https://img.shields.io/badge/Blender-4.3%2B-orange)
![Blender](https://img.shields.io/badge/Blender-4.58-greenorange)
![Blender](https://img.shields.io/badge/Blender-5.0-orange)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
