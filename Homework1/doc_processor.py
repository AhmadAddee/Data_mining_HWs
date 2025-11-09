import os
from zipfile import ZipFile
import tarfile
import itertools
from os.path import join
from pathlib import Path

def read_zipped_docs(path: Path, zip_file_name: str, num_of_docs: int) -> list[Path]:
    docs = []

    with ZipFile(path/zip_file_name, "r") as zipped_data:
        tar_file = zipped_data.namelist()[3]
        zipped_data.extractall(path, [tar_file])

    tari_tari = tarfile.open(path/tar_file, "r:gz")
    tari_tari.extractall(path)
    tari_tari.close()
    folder_name = path/tar_file.split(".")[0]
    for root, _dirs, files in itertools.islice(os.walk(folder_name), 1, None):
        for filename in files:
            docs.append(Path(join(root, filename)))
            if len(docs) >= num_of_docs:
                return docs

    return docs

def get_text_dict(doc_list:list[Path] = None) -> dict[str, str]:
    if doc_list is None:
        return {
            "doc1": "Locality-sensitive hashing is used for near-duplicate detection in large corpora.",
            "doc2": "Locality sensitive hashing helps find near duplicates in very large text collections.",
            "doc3": "Minhash signatures provide efficient similarity estimation for sets of shingles.",
            "doc4": "Graph algorithms are a different topic and not directly about shingling or minhash.",
            "doc5": "This sentence is unrelated to the others and should have low similarity.",
            "doc6": "This sentence is unrelated to others and should have low similarity.",
            "doc7": "This sentence is unrelated to others and should have low similarity.",
        }
    doc_dict = {f"doc{doc.name}": doc.read_text() for doc in doc_list}
    return doc_dict