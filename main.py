import sys

class Grammar:
    def __init__(self):
        self.productions = {}  # {non_terminal: [list of production strings]}
        self.non_terminals = []  # ordered list of non-terminals
    
    def add_production(self, lhs, rhs_list):
        if lhs not in self.productions:
            self.productions[lhs] = []
            self.non_terminals.append(lhs)
        self.productions[lhs].extend(rhs_list)
    
    def get_productions(self, nt):
        return self.productions.get(nt, [])
    
    def set_productions(self, nt, new_productions):
        self.productions[nt] = new_productions
    
    def get_ordered_non_terminals(self):
        return self.non_terminals
    
    def print_grammar(self):
        for nt in self.non_terminals:
            prods = " | ".join(self.productions[nt])
            print(f"{nt} → {prods}")
    
    def find_leading_nonterminal(self, prod):
        # sort non-terminals by length
        sorted_nts = sorted(self.non_terminals, key=len, reverse=True)
        
        for nonterminal in sorted_nts:
            if prod.startswith(nonterminal):
                # make sure it's not part of a longer identifier
                if len(prod) == len(nonterminal):
                    return (nonterminal, "")
                next_char = prod[len(nonterminal)]
                # check if next char could be part of identifier
                if next_char.isalnum() and next_char != "'" and nonterminal + next_char not in self.non_terminals:
                    # might be part of longer identifier, but check if that identifier exists
                    continue
                return (nonterminal, prod[len(nonterminal):])
        
        # print("The non terminals are: ",  prod)
        return (None, prod)


def starts_with_non_terminal(production, non_terminal):
    if not production.startswith(non_terminal):
        return False
    
    if len(production) == len(non_terminal):
        return True
    
    next_char = production[len(non_terminal)]
    
    # this handles the edge case where "A" should not match "A'" 
    if next_char == "'":
        return False
    
    return True


def substitute_non_terminal(production, non_terminal, replacements):
    if not starts_with_non_terminal(production, non_terminal):
        # if production doesn't start with the non-terminal, return it unchanged
        return [production]
    
    suffix = production[len(non_terminal):]
    
    # create new productions by concatenating each replacement with the suffix
    result = []
    for replacement in replacements:
        if replacement == "empty":
            # if suffix is also empty, result is empty
            if suffix == "":
                result.append("empty")
            else:
                # empty concatenated with suffix is just the suffix
                result.append(suffix)
        else:
            # concatenate replacement with suffix
            result.append(replacement + suffix)
    
    return result


def eliminate_direct_left_recursion(grammar, non_terminal):
    productions = grammar.get_productions(non_terminal)
    
    # separate productions into alpha and beta lists
    alpha = []
    beta = []
    
    for prod in productions:
        if starts_with_non_terminal(prod, non_terminal):
            # direct left recursive production
            suffix = prod[len(non_terminal):]
            alpha.append(suffix)
        else:
            # non left-recursive production
            beta.append(prod)
    
    if not alpha:
        return
    
    # generate new primed non-terminal name by appending "'"
    primed_non_terminal = non_terminal + "'"
    
    # if the primed non-terminal already exists, keep adding primes
    while primed_non_terminal in grammar.non_terminals:
        primed_non_terminal += "'"
    
    # create new beta productions with primed non-terminals
    new_productions = []
    if beta:
        for b in beta:
            if b == "empty":
                new_productions.append(primed_non_terminal)
            else:
                new_productions.append(b + primed_non_terminal)
    else:
        # if all productions were left recursive, just add the primed non-terminal
        new_productions.append(primed_non_terminal)
    
    # create primed non terminal productions
    primed_productions = []
    for a in alpha:
        primed_productions.append(a + primed_non_terminal)
    primed_productions.append("empty")
    
    # update grammar with new productions for both original and primed non-terminals
    grammar.set_productions(non_terminal, new_productions)
    
    # add primed non terminal to ordered list immediately after original and find index
    nt_index = grammar.non_terminals.index(non_terminal)
    
    # add the primed non terminal's productions
    grammar.productions[primed_non_terminal] = primed_productions
    
    # insert the primed non-terminal right after the original in the list
    grammar.non_terminals.insert(nt_index + 1, primed_non_terminal)


def eliminate_indirect_left_recursion(grammar):
    original_non_terminals = grammar.get_ordered_non_terminals()[:]
    n = len(original_non_terminals)
    
    for i in range(n):
        Ai = original_non_terminals[i]
        
        current_non_terminals = grammar.get_ordered_non_terminals()
        current_i = current_non_terminals.index(Ai)
        
        # for all non teminals that come before Ai in current ordering
        for j in range(current_i):
            Aj = current_non_terminals[j]
            
            # get all productions of Ai
            Ai_productions = grammar.get_productions(Ai)
            
            # get all productions of Aj
            Aj_productions = grammar.get_productions(Aj)
            
            # for each production of Ai, check if it starts with Aj
            new_productions = []
            for prod in Ai_productions:
                # if production starts with Aj, get all productions of Aj
                if starts_with_non_terminal(prod, Aj):
                    # substitute Aj with its productions, creating new productions with suffixes
                    substituted = substitute_non_terminal(prod, Aj, Aj_productions)
                    # replace old production with new substituted productions
                    new_productions.extend(substituted)
                else:
                    # keep the production unchanged
                    new_productions.append(prod)
            
            # update Ai with the new productions
            grammar.set_productions(Ai, new_productions)
        
        # after inner loop completes, call eliminate_direct_left_recursion for Ai
        # tthis caused a lot of problems when I did not have this since you can create direct left recursion after eliminating indirect left recursion
        eliminate_direct_left_recursion(grammar, Ai)
    
    current_non_terminals = grammar.get_ordered_non_terminals()
    
    # find all primed non-terminals
    for i in range(n, len(current_non_terminals)):
        Ai = current_non_terminals[i]
        
        # apply substitutions for all non-terminals that come before this primed non-terminal
        for j in range(i):
            Aj = current_non_terminals[j]
            
            # get all productions of Ai
            Ai_productions = grammar.get_productions(Ai)
            
            # get all productions of Aj
            Aj_productions = grammar.get_productions(Aj)
            
            # for each production of Ai, check if it starts with Aj
            new_productions = []
            for prod in Ai_productions:
                # if production starts with Aj, substitute
                if starts_with_non_terminal(prod, Aj):
                    substituted = substitute_non_terminal(prod, Aj, Aj_productions)
                    new_productions.extend(substituted)
                else:
                    new_productions.append(prod)
            
            # update Ai with the new productions
            grammar.set_productions(Ai, new_productions)
        
        # eliminate direct left recursion for this primed non-terminal
        eliminate_direct_left_recursion(grammar, Ai)
        
        # update the list in case new primed non-terminals were added
        current_non_terminals = grammar.get_ordered_non_terminals()
    
    return grammar


def format_grammar(grammar):
    lines = []
    
    # iterate through ordered non-terminals
    for non_terminal in grammar.get_ordered_non_terminals():
        # get productions for this non-terminal
        productions = grammar.get_productions(non_terminal)
        
        # join alternative productions with | separator
        productions_str = " | ".join(productions)
        
        # format each line as "NonTerminal → productions"
        line = f"{non_terminal} → {productions_str}"
        lines.append(line)
    
    # return formatted string with one production rule per line
    return "\n".join(lines)


def parse_grammar(grammar_text):
    
    grammar = Grammar()
    lines = grammar_text.strip().split('\n')
    line_number = 0
    
    for line in lines:
        line_number += 1
        original_line = line
        line = line.strip()
        
        # skip empty lines
        if not line:
            continue
        
        # skip comment lines
        if line.startswith('#'):
            continue
        
        # handel both arrow formats
        arrow = None
        if '→' in line:
            arrow = '→'
        elif '->' in line:
            arrow = '->'
        
        # split on arrow
        parts = line.split(arrow)
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        # print(lhs)
        # print(rhs)
        
        # split alternatives by |
        alternatives = []
        for alt in rhs.split('|'):
            alternatives.append(alt.strip())
        
        validated_alternatives = []
        for i, alt in enumerate(alternatives):
            # if the alternative contains spaces, remove it
            if ' ' in alt:
                alt = ''.join(alt.split())
            validated_alternatives.append(alt)
        
        # convert "ε" to "empty"
        alternatives = []
        for alt in validated_alternatives:
            if alt in ('ε', 'empty'):
                alternatives.append('empty')
            else:
                alternatives.append(alt)
        
        grammar.add_production(lhs, alternatives)
    
    return grammar


def main():
    # Take in input from a file or string (aka, python3 main_old.py < sample_inputs/input1.txt > actual_outputs/output1.txt)
    
    input_text = sys.stdin.read()
    try:
        grammar = parse_grammar(input_text)
        # print(grammar)
    except ValueError as e:
        print(e)
        return
    eliminated_grammar = eliminate_indirect_left_recursion(grammar)
    output = format_grammar(eliminated_grammar)
    print(output)


if __name__ == "__main__":
    main()