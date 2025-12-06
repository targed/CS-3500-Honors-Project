# 3500 Honors project: Eliminate indirect left recursion

[Link to honors project document](https://docs.google.com/document/d/1rMwrLvwK7GiYRUbVzbxiDjO22aaG6pWuHFUStAzKxMw/edit?tab=t.0#heading=h.j1a9zp1uoctc)


## Eliminate direct left recursion algoritim/pseudocode

Transform: $A \to A\alpha \mid \beta$
Into:
1.  $A \to \beta A'$
2.  $A' \to \alpha A' \mid \epsilon$

*   $\beta$: The Base Case
*   $\alpha$: The Recursive Part

## Eliminate indirect left recursion algoritim/pseudocode


1.  **Outer Loop ($i$ from 1 to $n$):** Pick the current Non-Terminal $A_i$.
2.  **Inner Loop ($j$ from 1 to $i-1$):** Look at all previous Non-Terminals.
  *   **Substitution:** If $A_i$ has a rule starting with $A_j$ (e.g., $A_i \to A_j \gamma$), replace $A_j$ with its body.
3.  **Clean Up:** After the inner loop, $A_i$ might now have **Direct Left Recursion** (because of the substitutions). Run the **EDLR** (Eliminate Direct Left Recursion)


## Test/run the program

You may need to make the bash scripts executable first using `chmod +x ./run.sh` and `chmod +x ./test.sh`

To test or run the program, you can either use 

the `./run.sh` script which just runs the python scrip and can be used like this `./run.sh < sample_inputs/input$i.txt > actual_outputs/output$i.txt` where you replace $i with the number of the input/output file
you can then compare the output with the expected output using `diff -w actual_outputs/output$i.txt sample_outputs/output$i.txt`

or `./test.sh` automatically does that for you
if you would like to add mor test inputs, you can either replace the already existing ones or add another sample input and sample output for that test
PS you will have to update the bounds of the `./test.sh` script if you add more since currently it loops over a fixed number

## Input

you specify the input grammar you want in `/sample_inputs/input*.txt. It can be either with spaces or without and it can either be with -> or → 

for example:

this works:
```
S -> a A | S c
A -> A B b | A d | empty
B -> A d | S c
```

but so does this:
```
S → aA | Sc
A → ABb | Ad | empty
B → Ad | Sc
```