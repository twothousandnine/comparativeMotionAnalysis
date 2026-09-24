# Comparative Motion Analysis: MediaPipe and MoCa

This repository contains the processed data and analysis code for *Comparative Feasibility Evaluation of Marker-Based and Markerless Computer-Vision Pose Estimation for Quantitative Human Motion Analysis: An Initial Methods Comparison.*

The study compares two motion-analysis pipelines applied to the same smartphone videos:

- **MediaPipe (MP):** a markerless pose-estimation pipeline using MediaPipe Pose and Face Landmarker.
- **Mobile Motion Capture (MoCa):** a marker-based pipeline that tracks 10 mm adhesive markers using OpenCV color thresholding.

It is a feasibility and methods comparison, not a clinical validation study.

## What is included

The repository contains processed, de-identified pose time series, face-detection outputs, and scripts used to generate the reported analyses.

```text
data/raw/       Per-system full-body trial time series (180 CSV files)
data/aligned/   Frame-matched and cropped paired trials (90 CSV files)
data/face/      Static face-landmark detection results (12 CSV files)
```

Filenames are parsed by the scripts, so they should not be renamed:

```text
data/raw/     <SYSTEM>.<MOTION>.<SUBJECT>.<CAMERA>.<RUN><SPEED>.csv
data/aligned/          <MOTION>.<SUBJECT>.<CAMERA>.<RUN><SPEED>.csv
data/face/    <SYSTEM>.<SUBJECT>.all.csv
```

`SYSTEM` is `MEDIAPIPE` or `MOCA`. Full-body data include five motions, three participants, three trials per condition, and fast/slow speeds. Face data include six participants photographed at rotations from 0° to 180°.

Raw video, still images, and landmark-extraction code are not included because they cannot be shared under the governing IRB protocol (University of Arizona HSPP, IRB 2107032177).

## Analysis overview

For full-body trials, each system tracks three points that define a joint or body angle. The scripts filter coordinates, calculate angle displacement, then derive velocity and a roughness measure. Paired trials in `data/aligned/` are matched frame by frame and are the input to the figures and tables.

The main analyses cover:

- range of motion;
- Pearson correlation between systems;
- Bland–Altman agreement;
- motion roughness; and
- face-landmark detection by head rotation.

The distributed files already include angle, velocity, and roughness values. The `compute_*` scripts are only needed when regenerating those values after a parameter change; they overwrite `data/raw/` in place.

## Setup

The project uses Python 3.12 and [Poetry](https://python-poetry.org/). Dependencies are pinned in `pyproject.toml` and `poetry.lock`.

```bash
poetry install
```

## Reproduce the analyses

Run scripts from the repository root:

```bash
poetry run python -m src.fig4_Pearson
poetry run python -m src.fig5_BlandAltman
poetry run python -m src.fig6_FaceDetection
poetry run python -m src.table3_rangeOfMotion
poetry run python -m src.table4_roughness
```

Generated figures are written to `figures/`; aggregated range-of-motion data are written to `data/aggregate/`. Some plotting scripts open a display window. To save figures without displaying them, set `MPLBACKEND=Agg`.

For direct use of an aligned trial:

```python
import pandas as pd

trial = pd.read_csv("data/aligned/BicepC.Subject1.Cam1.R1Fast.csv")
correlation = trial["mp_angles"].corr(trial["moca_angles"], method="pearson")
```

## Scope and limitations

The study compares agreement between two systems; it does not establish measurement accuracy because no external reference standard, such as optical motion capture, goniometry, or IMUs, was used.

Data were collected from nine healthy adults aged 18–30 in a single controlled setting with fixed cameras and standardized lighting. The results therefore describe performance under these conditions and should not be generalized directly to clinical, in-home, or more diverse settings. Both systems use single-camera, two-dimensional measurements, so they cannot recover out-of-plane movement.

## Citation

> De Anda L, Rohrer K, Garcia J, Jonas B, Michael B, Slepian RC, Patterson H, Slepian MJ. *Comparative Feasibility Evaluation of Marker-Based and Markerless Computer-Vision Pose Estimation for Quantitative Human Motion Analysis: An Initial Methods Comparison.*

Related work on the MoCa pipeline:

> Rohrer K, De Anda L, Grubb C, Hansen Z, Rodriguez J, St Pierre G, et al. Around-body versus on-body motion sensing: a comparison of efficacy across a range of body movements and scales. *Bioengineering.* 2024;11:1163. doi:10.3390/bioengineering11111163

> Vincent AC, Furman H, Slepian RC, Ammann KR, Di Maria C, Chien JH, et al. Smart phone-based motion capture and analysis: importance of operating envelope definition and application to clinical use. *Applied Sciences.* 2022;12:6173. doi:10.3390/app12126173

## Data availability, ethics, and license

The anonymized processed data and analysis code are available in this repository: <https://github.com/twothousandnine/comparativeMotionAnalysis>. The data contain no participant-identifying information. Raw video and still images are not available because of IRB restrictions.

The study was reviewed and approved by the University of Arizona Human Subjects Protection Program (IRB 2107032177), and all participants provided written informed consent.

All rights reserved; see [LICENSE](LICENSE). You may download, run, and reproduce the analyses to review or verify the associated study. Other uses, including research reuse, publication, redistribution, or incorporation into software or models, require written permission from the authors. Contact the corresponding author, Marvin J. Slepian, University of Arizona.

Questions, corrections, and reproduction reports are welcome through GitHub issues.
