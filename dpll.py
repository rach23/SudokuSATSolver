import random
from copy import deepcopy
from itertools import chain
from typing import List, Tuple

class DPLL:
    def __init__(self, clauses, variable_selection_method='random', verbose=0):
        self.variables_set = set(map(str, (map(abs, chain.from_iterable(clauses)))))  # extracts unique variable from DIMACS format
        # converts into internal format where each literal looks like (var_name, True)
        self.clauses = [[(str(abs(l)), l > 0) for l in c] for c in clauses]
        self.variable_selection_method = variable_selection_method
        self.verbose = verbose

    @staticmethod
    def neg(literal):
        return (literal[0], not literal[1])

    def select_random_variable(self, partial_assignment: List[Tuple]):
        if self.verbose:
            print('inside variable selection partial_assignment', partial_assignment)
        already_split = set([v[0] for v in partial_assignment])
        if self.verbose:
            print('already_split', already_split)
        return random.choice(list(self.variables_set - already_split))

    def clause_simplication(self, clauses, literal: tuple):
        new_clauses = deepcopy(clauses)
        if self.verbose:
            print('before simplication', new_clauses)
        # delete clauses containing true literals
        new_clauses = [c for c in new_clauses if literal not in c]
        if self.verbose:
            print('simplified true literals', new_clauses)
        # shorten clauses containing false literals
        new_clauses = [[el for el in c if el != self.neg(literal)] for c in new_clauses]
        if self.verbose:
            print('shortened false literals', new_clauses)

        return new_clauses

    def backtrack(self, clauses, partial_assignment: List[Tuple], split_literal: tuple):
        # copying the list of tuples
        partial_assignment = partial_assignment[:]

        if self.verbose:
            print("\nBacktrack with partial_assignment", partial_assignment, 'and split_literal', split_literal)
        if split_literal != tuple():
            clauses = self.clause_simplication(clauses, split_literal)
            partial_assignment.append(split_literal)

        # An empty set of clauses is (trivially) true (conjunction: all of these have to be true)
        if len(clauses) == 0:
            if self.verbose:
                print('Empty set of clauses')
            return True, partial_assignment

        # An empty clause is (trivially) false (disjunction: at least one of these must be true)
        if any([len(c) == 0 for c in clauses]):
            if self.verbose:
                print("Empty clause")
            return False, None

        try:
            if self.variable_selection_method == 'random':
                split_variable = self.select_random_variable(partial_assignment)
        except:
            print('Can not split anymore')
            return False, None
        split_literal = (split_variable, False)
        sat, assignments = self.backtrack(clauses, partial_assignment, split_literal)
        if not sat:
            if self.verbose:
                print(f"partial_assignment {partial_assignment} didn't work with split_literal {split_literal}. Try with negation")
            sat, assignments = self.backtrack(clauses, partial_assignment, self.neg(split_literal))

        return sat, assignments
