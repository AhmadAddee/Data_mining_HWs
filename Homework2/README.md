# **ID2222 HT25 Data Mining** - HW2

## Homework 2: Frequent Itemsets and Association Rules (A-Priori)

#### Task

1. A-Priori miner that finds all frequent itemsets with support ≥ s (absolute).
2. Candidate generation using join + prune from L(k−1) to form Ck.
3. Single-pass candidate counting per level k to produce Lk.
4. CLI that accepts either absolute `--min_support` or percent `--min_support_percent` and prints all results.
5. (Optional task for an extra bonus) Association-rule generation that produces rules X → Y with confidence ≥ c from the frequent itemsets.

#### Prerequisites

- Python version >= 3.10  
- Optional! create a virtual environment `python -m venv venv`, and then activate it.  

#### Datasets

- Use the market-basket dataset `T10I4D100K.dat`. Each line is a transaction; items are whitespace-separated.  
- Place the file anywhere; pass its path via `--path` (e.g., `Dataset/T10I4D100K.dat`).
- You can also use any other transaction dataset from the web, as long as items in each transaction are separated by whitespace (one transaction per line).

#### How to run

- Using Makefile (edit the path in `Makefile`, keep quotes if it has spaces), then run:
  - `make run`

- To use your own parameters, look at the CLI description by typing:
  - `python apriori.py --help`

- Example runs:
  - Percent support (recommended):
    - `python apriori.py --path "C:\...\T10I4D100K.dat" --min_support_percent 1.0 --min_conf 0.6`
  - Absolute support:
    - `python apriori.py --path "C:\...\T10I4D100K.dat" --min_support 1000 --min_conf 0.6`