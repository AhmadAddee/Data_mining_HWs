from pathlib import Path
import hashlib
from find_similar_items import Shingling, CompareSets, CompareSignatures, MinHashing
from doc_processor import read_zipped_docs

path = "./dataset"
sample_text = "This is a sample document for testing shingling."
expected_shingles = {"This ", "his i", "is is", "s is ", " is a", "is a ", "s a s", " a sa", "a sam", " samp", "sampl",
                     "ample", "mple ", "ple d", "le do", "e doc", " docu", "docum", "ocume", "cumen", "ument", "ment ",
                     "ent f", "nt fo", "t for", " for ", "for t", "or te", "r tes", " test", "testi", "estin", "sting",
                     "ting ", "ing s", "ng sh", "g shi", " shin", "shing", "hingl", "ingli", "nglin", "gling", "ling."}
signature = [2186258, 87698587, 89240749, 7471309, 54234297, 263421532, 163268404, 24506622, 5156157, 60050740, 9891126,
              54354879, 499226685, 103721781, 89045834, 6564099, 370887024, 41868788, 6066040, 8348912, 36600821,
              51950986, 245031457, 99971994, 56673962, 75203094, 58835906, 7274510, 22845985, 105225574, 15029773,
              5099486, 92982790, 83496205, 323829749, 7831546, 15896576, 63424546, 45644416, 17934593, 98774811, 6787450,
              49933077, 24653782, 206383502, 227310338, 21667214, 57970811, 12153131, 35736551, 70681130, 2612487,
              14337933, 43937875, 22751523, 99198889, 139610187, 38486451, 22545323, 72522636, 131924804, 16608685,
              69233332, 429984979, 109166342, 38149306, 125002047, 10351108, 60943624, 17005183, 89499533, 66796175,
              1721189, 117451606, 7440159, 325762842, 105365458, 6502708, 65750241, 38435497, 244326732, 2298821,
              180742090, 16447857, 279034471, 76522784, 57956169, 4413649, 38477726, 15996326, 81949364, 62934023,
              218183803, 116678254, 67108899, 129341692, 24503841, 60152750, 60423089, 96949510]

def test_char_shingling():
    shingling = Shingling(k=5)
    shingles = shingling.shingles(sample_text, use_hashing=False)
    assert shingles == sorted(expected_shingles), "Shingling test failed."

def test_hashed_shingles():
    hashed_shingling = Shingling(k=5)
    shingles_hashed = hashed_shingling.shingles(sample_text)
    assert shingles_hashed == sorted(
        set([int(hashlib.md5(shingle.encode("utf-8")).hexdigest(), 16) % (2**32)
             for shingle in expected_shingles])), "Hashed shingling test failed."

def test_jaccard_similarity():
    shingles = Shingling(k=10)
    docs = read_zipped_docs(Path(path), "twenty+newsgroups.zip", 2)
    shingled_dos = []
    for doc in docs:
        text = doc.read_text()
        shingled_dos.append(shingles.shingles(text))

    assert CompareSets.jaccard(shingled_dos[0], shingled_dos[0]) == 1, "Jaccard similarity test failed."
    assert CompareSets.jaccard(shingled_dos[0], shingled_dos[1]) < 1, "Jaccard similarity test failed."

def test_min_hashing():
    shingles = Shingling(k=5)
    min_hash = MinHashing(100)
    docs = read_zipped_docs(Path(path), "twenty+newsgroups.zip", 2)
    min_signatures = [
        min_hash.get_signature(shingles.shingles(sample_text)),
        min_hash.get_signature(shingles.shingles(sample_text)),
        min_hash.get_signature(shingles.shingles(docs[0].read_text())),
        min_hash.get_signature(shingles.shingles(docs[1].read_text())),
    ]

    assert min_signatures[0] == min_signatures[1] == signature, "Min-Hashing test failed."
    assert min_signatures[2] != min_signatures[3], "Min-Hashing test failed."

    # Testing CompareSignatures
    assert CompareSignatures.estimate(min_signatures[1], signature) == 1
    assert CompareSignatures.estimate(min_signatures[1], min_signatures[3]) != 1

