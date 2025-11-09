# **ID2222 HT25 Data Mining** - HW1

## Homework 1: Finding Similar Items: Textually Similar Documents 

#### Task

1. A class Shingling that constructs k–shingles of a given length k (e.g., 10) from a given document, computes a hash value for each unique shingle and represents the document in the form of an ordered set of its hashed k-shingles.
2. A class CompareSets computes the Jaccard similarity of two sets of integers – two sets of hashed shingles.
3. A class MinHashing that builds a minHash signature (in the form of a vector or a set) of a given length n from a given set of integers (a set of hashed shingles).
4. A class CompareSignatures estimates the similarity of two integer vectors – minhash signatures – as a fraction of components in which they agree.
5. (Optional task for an extra 2 bonus points) A class LSH that implements the LSH technique: given a collection of minhash signatures (integer vectors) and a similarity threshold t, the LSH class (using banding and hashing) finds candidate pairs of signatures agreeing on at least a fraction t of their components.

#### Prerequisites
- Python version >= 3.10
- Optional! create a virtual environment `python -m venv venv`, and then activate it.
- Install required Python packages, `pip install -r requirements.txt`

#### Datasets
- From [the UC Irvine Machine Learning Repository](https://archive.ics.uci.edu/dataset/113/20+newsgroups), download the
the **_Twenty Newsgroups_** dataset (only the zip file, no need to unzip it). Locate the file under [dataset](dataset).
- In [run_app.bat](run_app.bat) (on Mac/Linux, use [run_app.sh](run_app.sh)), modify `FILE_PATH` to point to the zip file
you fetched in the previous step.

#### How to run
- You can run the batch script with the default parameters specified there, by double-clicking at the file, or from a CLI
run `python run_app.bat`
- To use your own parameters, look at the CLI description by typing `python main.py --help`.
- Another way to run the app is to specify only two (or more) documents to compare. For example,
`python main.py --docs <document1.txt> <document2.txt>` 
