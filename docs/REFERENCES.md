# Academic References

Citations for the mathematical foundations used by glyph-animator.
Proof documents reference these via key (e.g. "see ABOP" or "per AS64 Table 25.4").

| Key | Citation | Used In |
|---|---|---|
| ABOP | Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants*, Springer, 1990 | L-systems, phyllotaxis (proofs 08, 09, 11) |
| AS64 | Abramowitz & Stegun, *Handbook of Mathematical Functions*, NBS/NIST, 1964, Table 25.4 | Gauss quadrature nodes/weights (proof 02) |
| BEZIER | Bézier, *Numerical Control: Mathematics and Applications*, Wiley, 1972 | Cubic bezier curves (proof 01) |
| DECASTELJAU | De Casteljau, *Formes à pôles*, Citroën, 1959 | Subdivision algorithm (proof 03) |
| KUHN | Kuhn, *The Hungarian Method for the Assignment Problem*, Naval Research Logistics, 1955 | Contour matching (proof 05) |
| STEINHAUS | Steinhaus, *Three-Distance Theorem*, Bull. Acad. Polon. Sci., 1957 | Golden angle optimality (proof 08) |
| VERLET | Verlet, *Computer Experiments on Classical Fluids*, Physical Review 159, 1967 | Petal physics (proof 13) |
| VOGEL | Vogel, *A Better Way to Construct the Sunflower Head*, Mathematical Biosciences 44, 1979 | Phyllotaxis spiral (proof 08) |

## Additional References

- **Sederberg & Parry**, *Free-Form Deformation of Solid Geometric Models*, SIGGRAPH 1986 — context for shape morphing approaches
- **Kuhn & Munkres**, Hungarian algorithm O(n³) implementation — used for contour matching (k ≤ 5, so brute-force sufficient)
- **Jonker & Volgenant**, *A Shortest Augmenting Path Algorithm for Dense and Sparse Linear Assignment Problems*, Computing 38, 1987 — O(n²) LAP variant, relevant if flower count exceeds 200
- **Lindenmayer**, *Mathematical Models for Cellular Interactions in Development*, Journal of Theoretical Biology, 1968 — original L-system formalism
