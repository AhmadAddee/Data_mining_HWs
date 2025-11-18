# **ID2222 HT25 Data Mining** - HW2

## Homework 2: Discovery of Frequent Itemsets and Association Rules

### Intro
The problem of discovering association rules between itemsets in a sales transaction database (a set of baskets) includes the following two sub-problems [R. Agrawal and R. Srikant, VLDB '94](https://www.vldb.org/conf/1994/P487.PDF):
1. Finding frequent itemsets with support at least $s$.
2. Generating association rules with confidence at least $c$ from the itemsets found in the first step.

Remind that an association rule is an implication $X \to Y$, where $X$ and $Y$ are itemsets such that $X \cap Y = \phi$. **Support** of rule $X \to Y$ is the number of transactions that contain $X$. **Confidence** of rule $X \to Y$ is the fraction of transactions containing $X \cup Y$ in all transactions that contain $X$.

#### Task

1. Implement the A-Priori Algorithm for finding frequent items with support at least $s$ in a dataset of sales transactions.
    - **support** of an itemset is the number of transactions containing the itemset
2. (Optional) Develop and implement an algorithm for generating association rules between frequent itemsets discovered using the A-Priori algorithm in a dataset of sale transactions. The rules must have the support of at least $s$ and confidence of at least $c$, where $s$ and $c$ are given as input parameters. 

#### Prerequisites
- Python version >= 3.10
- Optional! create a virtual environment `python -m venv venv`, and then activate it.

#### Datasets
- The dataset is provided in the assignment description. It should be downloaded an located under [dataset](dataset).
- In [run_app.bat](run_app.bat) (on Mac/Linux, use [run_app.sh](run_app.sh)), modify `FILE_PATH` to point to the .dat file
you fetched in the previous step.

#### How to run
- You can run the batch script with the default parameters specified there, by double-clicking at the file, or from a CLI
run `run_app.bat`
- To use your own parameters, look at the CLI description by typing `python main.py --help`.
- Another way to run the app is to specify only two (or more) documents to compare. For example,
