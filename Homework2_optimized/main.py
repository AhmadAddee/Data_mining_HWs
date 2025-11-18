import argparse
from frequent_itemsets import Apriori
from association_rules import AssociationRules


def perf_assoc_rules(transactions: list[frozenset], s: int, c: float):
    print(f"Finding frequent itemsets in the corpus: {len(transactions)} transactions, with support threshold of {s}")

    model = Apriori()
    frequent_itemsets = model.get_frequent_count(transactions, s)
    # print_frequent_itemsets(frequent_itemsets)

    print(f"\nGenerating association rules from: {len(frequent_itemsets)} frequent itemsets, with support threshold of {s} and confidence threshold of {c:.2f}")
    transactions_len = len(transactions)
    min_support_fraction = s / transactions_len if transactions_len > 0 else 0.0
    rules_model = AssociationRules(frequent_itemsets, transactions_len, min_support_fraction, c)
    rules = rules_model.generate_rules()

    print_rules(rules)
    return rules


def print_frequent_itemsets(frequent_itemsets):
    for itemset, count in sorted(frequent_itemsets.items(), key=lambda x: (len(x[0]), x[0])):
        items = ", ".join(sorted(itemset))
        print(f"{{ {items} }}: {count}")


def print_rules(rules):
    for r in rules:
        lhs = ", ".join(sorted(map(str, r["lhs"])))
        rhs = ", ".join(sorted(map(str, r["rhs"])))
        sup = r["support"]
        conf = r["confidence"]
        print(f"  {{ {lhs} }} -> {{ {rhs} }} [support={sup:.3f}, conf={conf:.3f}]")


def load_transactions_dataset(dataset_path: str):
    """Read transactions file: one transaction per line, whitespace-separated items."""
    if not dataset_path:
        return [
            frozenset(["A", "C", "D"]),
            frozenset(["B", "C", "E"]),
            frozenset(["A", "B", "C", "E"]),
            frozenset(["B", "E"])
        ]
    transactions = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            items = line.split()
            if items:
                transactions.append(frozenset(items))
    return transactions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Frequent Itemsets and Association Rules in corpus of sales transactions dataset.")
    parser.add_argument("--data-file", "-d", type=str, default=None, help="The path of the dataset of sales transactions.")
    parser.add_argument("--support-threshold", "-s", type=int, default=1000, help="The support of an itemset is the number of transactions containing the itemset.")
    parser.add_argument("--confidence-threshold", "-c", type=float, default=0.5, help="The confidence of a rule is the fraction of transactions containing the rule in all transactions that contain the rule's antecedent.")

    args = parser.parse_args()

    transactions = load_transactions_dataset(args.data_file)
    perf_assoc_rules(transactions, args.support_threshold, args.confidence_threshold)
