# Given frequent itemsets (k -> {tuple: support}), produce all rules X -> Y where
# X ∪ Y = I, X ∩ Y = ∅, and confidence >= min_conf.

import itertools

def generate_rules(frequent_itemsets, min_conf):
    support_map = {}
    for k, d in frequent_itemsets.items():
        for tup, cnt in d.items():
            support_map[frozenset(tup)] = cnt
    rules = [] 
    for k, d in frequent_itemsets.items():
        if k < 2: 
            continue
        for item_tup, sup in d.items():
            I = set(item_tup) 
            for r in range(1, len(I)):  
                for lhs in itertools.combinations(I, r): 
                    lhs_set = frozenset(lhs)
                    rhs_set = frozenset(I - lhs_set) 
                    lhs_support = support_map.get(lhs_set, 0)
                    if lhs_support == 0:
                        continue
                    confidence = sup / lhs_support
                    if confidence >= min_conf:
                        rules.append({
                            'lhs': tuple(sorted(lhs_set)),
                            'rhs': tuple(sorted(rhs_set)),
                            'support': sup,
                            'confidence': confidence
                        })
    # sort by confidence desc then support desc
    rules.sort(key=lambda x: (-x['confidence'], -x['support']))
    return rules
