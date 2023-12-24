# PentoNav

This directory contains the raw logs and all the scripts necessary to extract the PentoNav dataset.

| variables                         | easy  | medium| hard  |
|---|----|---|---|
| grouped pieces                    | 12    | 12    | 12    |   
| similar pieces per group          | 3     | 3     | 4     |   
| random pieces                     | 4     | 5     | 6     |   
| shared characteristics per group  | 2     | 3     | 4     |  


## Structure
* `logs/`: the raw logs from slurk
* `images/`: the images of the Pentomino boards for both the instruction giver and receiver. the name is encoded as `{STATE_ID}_{ROLE}.png`
* `Rscripts/`: the R scripts to run the statistical analysis with linear mixed effects models and the dataset
* `plots_tables.ipynb`: plots and tables extracted from the data
* `create_R_dataset.py`: takes as input `recolage.tsv` and creates a `.csv` file used for the analysis in R
* `data_structures.py`: contains data structure used to extract data from the raw logs
* `jsonl2tsv.py`: script to convert `recolage.jsonl`to `recolage.tsv`
* `logs2jsonl.py`: script to convert raw logs to `recolage.jsonl``


## Usage
* convert raw logs to .jsonl: `python logs2jsonl.py -i logs > recolage.jsonl`  
* convert jsonl to .tsv: `python jsonl2tsv.py < recolage.jsonl > recolage.tsv`  
* create a dataset for R: `python create_R_dataset.py recolage.tsv > Rscripts/Rdataset`
