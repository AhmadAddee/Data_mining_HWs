# **ID2222 HT25 Data Mining** - HW4

## Homework 4: Graph Spectra

The paper [On Spectral Clustering: Analysis and an algorithm](https://ai.stanford.edu/~ang/papers/nips01-spectral.pdf) by Andrew Y. Ng, Michael I. Jordan, and Yair Weiss, describes the spectral graph clustering algorithm studied and implemented in this HW.

#### Task
Study and implement the spectral graph clustering algorithm described in the paper above. The two sample graphs are to be analyzed using the implementation of the K-eigenvector algorithm:
1. A real graph [example1.dat](dataset/example1.dat) -- This data set was prepared by Ron Burt. He dug out the 1966 data collected by Coleman, Katz, and Menzel on medical innovation. They collected data from physicians in four towns in Illinois: Peoria, Bloomington, Quincy, and Galesburg.
2. A synthetic graph [example2.dat](dataset/example2.dat)

#### Prerequisites
- Python version >= 3.10
- Optional! create a virtual environment `python -m venv venv`, and then activate it.
- Install required Python packages, `pip install -r requirements.txt`

#### Datasets
- Download the files mentioned in [Task](#task), and locate the file under [dataset](dataset).
- In [run_app.bat](run_app.bat) (on Mac/Linux, use [run_app.sh](run_app.sh)), modify `FILE_PATH` to point to the zip file
you fetched in the previous step.

#### How to run
- You can run the batch script with the default parameters specified there, by double-clicking at the file, or from a CLI
run `run_app.bat`
- To use your own parameters, look at the CLI description by typing `python main.py --help`.
