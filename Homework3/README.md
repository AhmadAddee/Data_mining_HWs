# **ID2222 HT25 Data Mining** - HW3

## Homework 3: Mining Data Streams

The paper chosen for this homework is L. De Stefani, A. Epasto, M. Riondato, and E. Upfal, [TRIÈST: Counting Local and Global Triangles in Fully-Dynamic Streams with Fixed Memory Size](https://www.kdd.org/kdd2016/papers/files/rfp0465-de-stefaniA.pdf), KDD'16. It presents the streaming graph processing method and corresponding algorithm that make use of the stream mining algorithm of the reservoir sampling.

#### Task
Study and implement the streaming graph processing algorithm described in the paper mentioned above. The following two steps must be performed:
1. First, implement the reservoir sampling algorithm used in the graph algorithm presented in the paper selected.
2. Second, implement the streaming graph algorithm presented in the paper that uses the algorithm implemented in the first step.

The implementation should be tested with publicly available graph datasets (see [Datasets](#datasets)).

Questions to be answered:
1. What were the challenges you faced when implementing the algorithm?
2. Can the algorithm be easily parallelized? If yes, how? If not, why? Explain.
3. Does the algorithm work for unbounded graph streams? Explain.
4. Does the algorithm support edge deletions? If not, what modification would it need? Explain.

#### Prerequisites
- Python version >= 3.10
- Optional! create a virtual environment `python -m venv venv`, and then activate it.
- Install required Python packages, `pip install -r requirements.txt`

#### Datasets
- From [Stanford Large Network Dataset Collection](https://snap.stanford.edu/data/), go to [Note Dame web graph](https://snap.stanford.edu/data/web-NotreDame.html) and download the gzip-file. Locate the file under [dataset](dataset).
- In [run_app.bat](run_app.bat) (on Mac/Linux, use [run_app.sh](run_app.sh)), modify `FILE_PATH` to point to the zip file
you fetched in the previous step.

#### How to run
- You can run the batch script with the default parameters specified there, by double-clicking at the file, or from a CLI
run `run_app.bat`
- To use your own parameters, look at the CLI description by typing `python main.py --help`.
