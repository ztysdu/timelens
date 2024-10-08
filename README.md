# Project Configuration Guide

This repository contains the `TimeLens` code used in Swift-Eye. For detailed information, you can refer to the original paper: [Time Lens: Event-based Video Frame Interpolation](https://rpg.ifi.uzh.ch/docs/CVPR21_Gehrig.pdf).


## Environment Setup

To set up the environment, please refer to [rpg_timelens](https://github.com/uzh-rpg/rpg_timelens) and the `conda-requirements.txt` available in this repository.

## Model Weights

Download the fine-tuned model weights from [model weights](https://drive.google.com/file/d/1LXarGqhp8h0xevHAfQxi4UgW6ln7kUR2/view?usp=drive_link). After downloading, place the weights inside the `refined_model` directory.

## Code Modification

change the line in  tests/run_attention.py from sys.path.append('absolute path of timelens') to sys.path.append('/Path/to/rpg_timelens')

## Running the Model

To interpolate frames, execute the following:

python tests/run_attention.py

