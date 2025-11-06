# **ID2222 HT25 Data Mining** - HW1

## Homework 1: Finding Similar Items: Textually Similar Documents 

#### Task
You are to implement the stages of finding textually similar documents based on Jarrard similarity using the **_shingling_**, **_min-hashing_**, and **_locality-sensitive hashing (LSH)_** techniques and corresponding algorithms. The implementation can be done using big data processing framework, such as Apache Spark or Apache Flink, or no frameworks, e.g., in Java, Python, etc. To test and evaluate your implementation, write a program that uses your implementation to find similar documents in a corpus of 5-10 or more documents, such as web pages or emails.

The stages should be implemented asa a collection of classes, modules, functions, or procedures, depending on the framework and the language of your choice. Below, we describe sample classes implementing different stages of finding textually similar documents. You do not have to develop the exact same classes and data types described below. Feel free to use data structures that suit you best.


1. A class Shingling that constructs k–shingles of a given length k (e.g., 10) from a given document, computes a hash value for each unique shingle and represents the document in the form of an ordered set of its hashed k-shingles.
2. A class CompareSets computes the Jaccard similarity of two sets of integers – two sets of hashed shingles.
3. A class MinHashing that builds a minHash signature (in the form of a vector or a set) of a given length n from a given set of integers (a set of hashed shingles).
4. A class CompareSignatures estimates the similarity of two integer vectors – minhash signatures – as a fraction of components in which they agree.
5. (Optional task for an extra 2 bonus points) A class LSH that implements the LSH technique: given a collection of minhash signatures (integer vectors) and a similarity threshold t, the LSH class (using banding and hashing) finds candidate pairs of signatures agreeing on at least a fraction t of their components.

To test and evaluate your implementation's scalability (the execution time versus the size of the input dataset), write a program that uses your classes to find similar documents in a corpus of 5-10 documents. Choose a similarity threshold s (e.g., 0,8) that states that two documents are similar if the Jaccard similarity of their shingle sets is at least s.

#### Datasets
- For documents, see the datasets in [the UC Irvine Machine Learning Repository](https://archive.ics.uci.edu/) or find other documents such as web pages or emails.
- To find more datasets, follow [this link](https://github.com/awesomedata/awesome-public-datasets)

#### Readings
* [Lecture "Finding Similar Items"](../../Lectures/L2/)
* [Chapter 3 Finding Similar Items](../../Course_book.pdf) in **_Mining of Massive Datasets_**



[back](../)
