# DPLL SAT Solver
14/04/2025

This is a lightweight Python implementation of the DPLL Boolean satisfiability algorithm using an occurrence list. You can use this sat solver on [this website].

# Table of Contents
- [Introduction](#introduction)
- [Implementing DPLL](#implementing-dpll)
  - [Input Format](#input-format)
    - [DIMACS Format Explained](#dimacs-format-explained)
  - [Implementation Components](#implementation-components)
- [Unit Propagation](#unit-propagation)
- [Branching Heuristics](#branching-heuristics)
  - [What is a Branching Heuristic?](#what-is-a-branching-heuristic)
  - [The Heuristics I Tested](#the-heuristics-i-tested)
  - [Benchmarking](#benchmarking)
- [Literal Deletion](#literal-deletion)
  - [Occurrence List](#occurrence-list)
 
# Introduction
[Sat Solving](https://en.wikipedia.org/wiki/SAT_solver)  is the process of determining whether there exists an assignment of **true/false values** to variables that makes a given **Boolean formula** evaluate to **true**.

The **SATISFIABILITY PROBLEM is NP**.

Most Sat-Solvers work with formulae in [**CNF(Conjunctive Normal Form).**](https://en.wikipedia.org/wiki/Conjunctive_normal_form)

The objective of developing sat solvers is to be able to solve increasingly **complex** formulae as **efficiently** as possible. And maybe solving P=NP?

Modern SAT Solvers are implementations of the [CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning) algorithm but the DPLL algorithm is much **simpler** to implement which is why it is **better for learning**.

I spent a bit too much time building this solver as coursework for Durham University's COMP 1051(Computational Thinking) Module.

# Implementing DPLL
## Input Format

This solver handles CNF (Conjunctive Normal Form) formulae in [**DIMACS format**](https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html), which is the standard format for representing SAT problems.

### DIMACS Format Explained

DIMACS is a plain text format where:

- **Comments**: Lines starting with `c` are comments and ignored by the parser
- **Problem Line**: A line starting with `p cnf [variables] [clauses]` specifies the number of variables and clauses
- **Clauses**: Each subsequent line represents a clause with space-separated integers:
    - Positive integers represent variables
    - Negative integers represent negated variables
    - Each clause ends with `0` (as a delimiter)

For example, this DIMACS file:
```
c This is a simple example
p cnf 2 3
1 0
1 -1 0
-1 -2 0
```

Represents the CNF formula: **(1) ∧ (1 ∨ ¬1) ∧ (¬1 ∨ ¬2)**

My parser converts this into a Python list of lists:
```python
[[1], [1, -1], [-1, -2]]
```

### Implementation Components

There are multiple **components** to the actual sat solver and understanding all of them is important when trying to build, fix, or optimise one.

The 4 main ones are probably (in order of Algorithmic Implementation):
- **Unit Propagation**
- **Branching heuristic**
- **Literal deletion**
- **Recursive backtracking**

*This particular solver does not implement Pure Literal Elimination as It made performance **worse** when I did but **PLE** is part of the typical DPLL algorithm.*

A lot of research has been conducted on the topic of [branching heuristics](https://en.wikipedia.org/wiki/Boolean_satisfiability_algorithm_heuristics).

## Unit Propagation
When a **clause contains only one literal**, that literal **must** be true for the formula to be satisfiable. 
- Unit propagation identifies these single-literal clauses and assigns their variables accordingly, **simplifying the formula and reducing the search space.**

Pseudo Code (this is just one way to do it):
```
def unitPropagation(clauseSet):
	identify all unit clauses
	set all of the literals in these clauses to true

	while the set of new units isn't empty
		remove all satisfied clauses from the clause set
		remove opposite literals form each clause
		identify all unit clauses
		set all of the literals in these clauses to true

	return the modified clauseSet along with the new assignments
```

**Improving log:**
- [x]  Right now I'm applying the unit clauses i find iteratively - there must be a way to add unit clause to the clause set dynamically 
	- made the unit propagation update dynamically saved ~ 1 millisecond on 8 queens

## Branching Heuristics
Credit to  [aima-python](https://github.com/aimacode/aima-python/blob/master/improving_sat_algorithms.ipynb) for making this amazing resource (with way more than just branching heuristics) - there **definitely is** some interesting stuff here. 

I spent way too much time researching, implementing, and testing these heuristics so I made this section to spare you some time if you don't want to the same, although I would encourage diving even deeper into this topic. (it's low-key the funnest part)

### What is a Branching Heuristic ?

**After** exhausting unit propagation and pure literal elimination (not in my solver) , the algorithm must **select an unassigned variable and try different truth values**. The **efficiency** of a SAT solver largely **depends on which variable is chosen** at each decision point. Various sophisticated heuristics have been developed to make these selections intelligently, making this a **critical component of modern SAT solvers.**

### The heuristics I tested

Heuristics can be either **Static**(a score/priority is assigned to each variable once at the beginning of the computation) or **Dynamic**(computed or updated at many or every decision level). The trade-off is **overhead vs decision quality.**

All of my implementations are **Dynamic**: the heuristic's formula is **applied** to the clause set at **each decision level**. (this is the simple way to do dynamic heuristics)

**Note:** *Implementations written for clause set as **list of sets**.*

1. **First Lit:** No heuristic == 0 overhead - always conveniently picks a value that is assignable (I call it first literal)
	- no overhead 
	- slow af
```python
def firstLit(clauseSet):
	return next(iter(clauseSet[0]))
```

2. **MOMS**(Maximum Occurrence in Minimum-size clauses)
	- it's in the name
	- finds the length of the shortest clause
	- chooses the variable that appears the most in clauses of that length
	- on any input of substantial size, i've found that MOMS is considerably quicker (than first-lit) unless most clauses are of the same length; MOMs is quite slow for aim or 8 queens, that is because if most clauses are of the shortest length, MOMS doesn't reduce the choice by much :( **moms is bad for clause sets with consistent lengths**

```python
def MOMS(clauseSet):
    min_length = min(len(clause) for clause in clauseSet)
    shortestClauses = [clause for clause in clauseSet if len(clause) == min_length]
    
    scores = {}
    for clause in shortestClauses:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1

    return max(scores, key=scores.get)
```

3. **MOMSf**
	- same concept as mums but **with a function**
		- we choose the variable maximising the expression, k is a parameter:
			$[f(x) + f(-x)] * 2^k + f(x) * f(-x)$
		- Returns x if f(x) >= f(-x) otherwise -x
	 
	 DeepSeeks guidelines for **choice of k**:

| `k`Value | Best For                                                            | Example Use Cases                |
| -------- | ------------------------------------------------------------------- | -------------------------------- |
| `k=0`    | Problems where balanced polarity is critical                        | Crafted instances with symmetry  |
| `k=1`    | General-purpose balance                                             | Mixed industrial/random problems |
| `k=2`    | Default for most implementations (strong emphasis on short clauses) | SAT competitions, random k-SAT   |
| `k=3`    | Highly constrained problems with many short clauses                 | Hard combinatorial problems      |
- An adaptive strategy for k: **increase k every 1000 decisions** 
- It looks like MOMSf has the same issues as MOMS (slow for clause sets with constant or very consistent clause length) but is faster by ~30% on the jnh instances where MOMS was already quick (much quicker on some, considerably quicker on a lot, and a bit slower on a few) - this stuff is hard to compare

```Python
def MOMSf(clauseSet, k=3):

    min_length = 9999
    shortestClauses = []
    for clause in clauseSet:
        clause_len = len(clause)
        if clause_len < min_length:
            min_length = clause_len
            shortestClauses = [clause]
        elif clause_len == min_length:
            shortestClauses.append(clause) 
    
    scores = {}
    for clause in shortestClauses:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1
    
    def bCaseGet(literal):
        return scores.get(literal, 0)
    

    def score(literal):
        return (scores.get(literal) + scores.get(-literal, 0)) * 2**k + scores.get(literal) * scores.get(-literal, 0)
            
    bestliteral = max(scores, key= score)
    
    return max([bestliteral, -bestliteral], key=bCaseGet)
```

Some more variations MOMSfrom [aima-python](https://github.com/aimacode/aima-python/blob/master/improving_sat_algorithms.ipynb) + some experimentation

```python
def MOMSPosit(clauseSet):
    min_length = min(len(clause) for clause in clauseSet)
    shortestClauses = [clause for clause in clauseSet if len(clause) == min_length]
    
    scores = {}
    for clause in shortestClauses:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1

    sum = {}
    for literal in scores:
        sum[literal] = scores.get(literal) + scores.get(-literal, 0)
    
    best = max(sum, key=sum.get)
    if scores[best] >= scores.get(-best, 0):
        return best
    return - best

def MOMSMOD(clauseSet): # twist on MOMS posit (simplified)
    min_length = min(len(clause) for clause in clauseSet)
    shortestClauses = [clause for clause in clauseSet if len(clause) == min_length]
    
    scores = {}
    for clause in shortestClauses:
        for literal in clause:
            literal = abs(literal)
            scores[literal] = scores.get(literal, 0) + 1
    
    return max(scores, key=scores.get)

def MOMSZM(clauseSet):
    min_length = min(len(clause) for clause in clauseSet)
    shortestClauses = [clause for clause in clauseSet if len(clause) == min_length]
    
    scores = {}
    for clause in shortestClauses:
        for literal in clause:
            if literal < 0:
                scores[literal] = scores.get(literal, 0) + 1
    
    if not scores:
        return next(iter(clauseSet[0]))

    return max(scores, key=scores.get)

```

3. **Jeroslow-Wang**
	- idea: shorter clauses are more critical to satisfy because they have fewer options for satisfaction
	- works by assigning a score to each literal based on the lengths of the clauses it appears in. 
	- for each literal compute J(l) = \sum{l in clause c} 2^{-|c|}
	- return the literal maximising J
	![[Screenshot 2025-03-18 at 15.03.38.png]]
```Python
def JW(clauseSet):
    scores = {}
    for clause in clauseSet:
        power = pow(2, -len(clause))
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + power
            
    return max(scores, key= scores.get)
```

3. **Jeroslow-Wang Combined** (this is the one I ended up chosing): 
	- works the same as the previous JW but evaluates the sum for both the positive and negative occurrences of a variable
	- returns the the TRUE or FALSE assignment the maximises the function 
	- this is probably my best for now, it cannot solve aim but it is what it is, fastest 8queens and second fastest JNH
```Python
def JWCof4(clauseSet):
    scores = {}
    for clause in clauseSet:
        power =  pow(4, -len(clause))
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + power
    
    sum = {}
    for literal in scores:
        if -literal in sum:
            continue
        sum[literal] = scores.get(literal) + scores.get(-literal, 0)
        
    best = max(sum, key= sum.get)
    if sum[best] >= sum.get(-best, 0):
        return best
    return -best
```

4. **RNDM**
	- randomly picked
	- no scoring
	- it's slow and struggles with big clause sets
```Python
def RNDM(clauseSet):
    return next(iter(random.choice(clauseSet)))
```


5. **DLIS** (Dynamic Largest Individual Sum)
	- Choose the variable and value that satisfies the maximum number of unsat clauses
	- we only consider the literal - we don't combine the literal and its opposite
	- This is similar to my implementation of MOMS apart from the fact that we literal occurrences for the whole clause set rather than a subset clauses with the shortest length
	- **much worse** than MOMSf for false clause sets, it's only quicker than MOMSf at some stuff, slower at most - not an improvement
```python
def DLIS(clauseSet): 
    
    scores = {}
    for clause in clauseSet:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1
            
    return max(scores, key= scores.get)
```

6. **DLCS** (Dynamic largest combined sum)
	- same as above but tracks the frequency of a literal and it's negation
	- return the most frequent assignment of the most frequent literal
```python
def DLCS(clauseSet):
    
    scores = {}
    for clause in clauseSet:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1

    sum = {}
    for literal in scores:
        if -literal in sum:
            continue
        sum[literal] = scores.get(literal) + scores.get(-literal, 0)
        
    return max(sum, key= sum.get)


def DLCSAlt(clauseSet):
    
    scores = {}
    for clause in clauseSet:
        for literal in clause:
            if literal < 0:
                scores[-literal] = scores.get(-literal, 0) + 1
            scores[literal] = scores.get(literal, 0) + 1

    mostFrequent = max(scores, key= scores.get)
    
    if scores[mostFrequent] - scores.get(-mostFrequent, 0) > scores.get(-mostFrequent, 0):
        return mostFrequent
    return -mostFrequent
```



### Benchmarking

This is benchmark I created to give me an idea of overall performance on a variety of problem sets. I would've probably chosen another heuristic then JWC(of4) if it hadn't been for this benchmark.

These tests were ran on a previous version of the solver when I was still iterating through the clause set instead of using an occurence list. That doesn't change the relative performance of these heuristics. 
Testing all of these heuristics on my new solver requires them to be re-written to make use of the occurence list - which I haven't done as I had already decided on a heuristic.

Hardware & Software:
- M1 Macbook Pro
- MacOS 15
- 8gb ram
- VScode
- python 3.11.9

|            | JNH    | 8queens (500 runs) | Aim     | Total Time(s) |
| ---------- | ------ | ------------------ | ------- | ------------- |
| firstLit   | 24.224 | 0.00212            | 0.204   | 25.49         |
| RNDM       | 33.192 | 0.00417            | 230.875 | 270.88        |
| MOMS       | 1.228  | 0.01144            | 0.674   | 7.63          |
| MOMSf(k=3) | 0.698  | 0.01039            | 0.361   | 6.26          |
| MOMSPosit  | 0.748  | 0.01116            | 0.282   | 6.61          |
| MOMSMod    | 0.815  | 0.00151            | 0.455   | 2.03          |
| MOMSZM     | 1.270  | 0.01174            | 1.072   | 8.21          |
| DLIS       | 11.236 | 0.00941            | 1.513   | 17.45         |
| DLCSAlt    | 5.818  | 0.00901            | 1.963   | 12.29         |
| DLCS       | 6.860  | 0.00099            | 3.138   | 10.50         |
| Hamza      | 3.896  | 0.00301            | 0.425   | 5.83          |
| JW         | 1.964  | 0.01181            | 1.053   | 8.92          |
| JWC        | 1.111  | 0.00100            | 0.295   | 1.91          |
| JWC(of4)   | 0.913  | 0.00100            | 0.306   | 1.72          |

Occurence List Solver with JWCof4: 

| 0.819 | 0.00131 | 0.211 | 1.69 |
| ----- | ------- | ----- | ---- |


## Literal Deletion
This is the process of modifying the clause set **during unit propagation** and **after deciding** on a literal to branch on. By implementing literal deletion you significantly reduce the size of the problem set with each new literal assignment unit you reach either a contradiction or an empty problem set meaning that you've solved it. (the current assignment is a satisfying assignment)

With each new literal you do 2 things: 
- delete all the clauses that contain the literal (as they are satisfied)
- delete all the negative instances of that literal from the clauses that contain it

The **most obvious way** to do this is to go through the whole clause set **iteratively** with every new literal with something like this:
```
for each clause in the clause set:
	if the clause contains the new literal:
		delete the clause from the clause set
	else if the clause contains the negation of the new literal:
		deleter the negation of the literal from the clause
	else:
		do noting
```

Doing it this way is **simple** but **time consuming** for big clause-sets

That's when my good friend Oje told me about Occurence Lists which I read learned more about on [this repo](https://github.com/necavit/li-sat-solver).

### Occurence List

Instead of iterating through the entire clause set each time you make modifications, the idea is to keep a dictionary that stores the location of literals instead of having to iterate through the clauseSet on every recursive call.

The O list is initialised using this builder function:
```python
def buildOccurenceList(clauseSet):
	occurenceList = {}
	for i in range(len(clauseSet)):
		for literal in clauseSet[i]:
			occurenceList.setdefault(literal,set()).add(i)
			
return occurenceList
```

###### **Handling Modifications:**
The issue now is how we **handle modifications to the clause set**, while:
- minimising overhead
- not messing up recursion (doing stuff we can't undo)

The clause set's length **never changes**:
clauses can be:
- NONE = SAT
- set() = unsat
- [literals] = yet to be satisfied 
- this also means that our base cases have to change:
	- **sat**: if occurence dictionnary is empty 
	- **unsat**: if there is an empty clause 
The solver makes modifications to a new copy of the clause set every time:
- new clauses are only created if they need to be modified

A **Stack** is created to keep track of changes to the occurrence list, like this:
```python

change_stack = []

def remove_literal_from_clause(clause, literal, occurrence_list):
    if literal in clause:
        clause.discard(literal
        
        # Save the change to allow backtracking
        change_stack.append((literal, clause.copy()))  
        
        # Update the occurrence list
        occurrence_list[literal].remove(clause)

def backtrack(occurrence_list):
    while change_stack:
        literal, original_clause = change_stack.pop()
        occurrence_list[literal].append(original_clause) 
```


