#!/bin/env python
from dnf import PredicateFormula


if __name__ == '__main__':
    with open('./test_data.txt', 'r') as f:
        test_data = [line.rstrip('\n') for line in f.readlines()]
    
    print(test_data, sep='', end='\n\n')
    for data in test_data[:-1]:
        pfml = PredicateFormula(origin=data)
        pfml.parse()
        print(pfml.pdnf)
    # print(pfml.to_postfix_exp())
    # pfml.parse()
    # pfml.truth_table_print()
    # print(pfml.postfix_exp)
    # for data in test_data:
    #     print('\n', '-' * 70)
    #     print(data)
    #     pfml = PredicateFormula(origin=data)
    #     pfml.parse()
    #     pfml.truth_table_print()
    #     print(pfml.sigma)
    #     print(pfml.pdnf)
    