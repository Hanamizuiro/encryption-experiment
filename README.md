<div align="center">

# Kodak-Based Benchmarking of Numerical Solvers for Matrix Image Decryption

**A numerical-analysis study of noisy block-based image decryption using the 24-image Kodak benchmark**

| Dataset                        | Block Size | Solvers                                       | Deliverables                                     |
| ------------------------------ | ---------- | --------------------------------------------- | ------------------------------------------------ |
| Kodak lossless 24-image subset | 8 x 8      | Gaussian Elimination, LU, Gauss-Seidel, GMRES | Notebook artifacts, LaTeX paper, figures, tables |

</div>

## Overview

This repository studies image decryption as a numerical linear algebra problem rather than a pure cryptography exercise. Each Kodak image is resized to 128 x 128, partitioned into 8 x 8 blocks, encrypted with matrix-based transforms, corrupted with additive Gaussian noise, and then reconstructed with four solvers.

The core question is: which numerical methods remain accurate, stable, and efficient when corruption is introduced into the encrypted image representation?

> [!IMPORTANT]
> This project evaluates numerical solver behavior in a matrix-based image encryption workflow. It does not claim modern cryptographic security guarantees.

