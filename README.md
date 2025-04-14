# DPLL SAT Solver
14/04/2025

This is a lightweight Python implementation of the DPLL Boolean satisfiability algorithm using an occurrence list. You can use this sat solver on [this website].

[Sat Solving](https://en.wikipedia.org/wiki/SAT_solver)  is the process of determining whether there exists an assignment of **true/false values** to variables that makes a given **Boolean formula** evaluate to **true**.

The **SATISFIABILITY PROBLEM is NP**.

Most Sat-Solvers work with formulae in [**CNF(Conjunctive Normal Form).**](https://en.wikipedia.org/wiki/Conjunctive_normal_form)

The objective of developing sat solvers is to be able to solve increasingly **complex** formulae as **efficiently** as possible. 

Modern SAT Solvers are implementations of the [CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning) algorithm but the DPLL algorithm is much **simpler** to implement which is why it is **better for learning**.

# Implementing DPLL
---
This solver takes CNF formulae in [**DIMACS format.**](https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html#:~:text=The%20DIMACS%20CNF%20format%20is,a%20negation%20of%20a%20variable.)
- I've made a function that accepts `.txt` & `.cnf` files in DIMACS format and that outputs it in a python **list of lists** 
	**DIMACS format:**
	- Follows CNF, conjunction of disjunctions
	- **comments**: lines that start with c are ignored
	- **Problem**: a line starting with p, specifying number of variables; number of clauses
	- **clauses**: each line below is a clause, with space-seperated integers, minus means not, ending with 0
	example:
	```
	p cnf 2 3
	1 0
	1 -1 0
	-1 -2 0
	```
	gives : [1] and [1 or not 1] and [not 1 or not 2]
	in my code it should be return in the form:
	```
	[[1], [1, -1], [-1, -2]]
	```

There are multiple **components** to the actual sat solver and understanding all of them is important when trying to build, fix, or optimise one.

The 3 main ones are probably:
- **Literal deletion**
- **Branching heuristic**
- **Unit Propagation**

A lot of research has been conducted on the topic of [branching heuristics](https://en.wikipedia.org/wiki/Boolean_satisfiability_algorithm_heuristics).

## Unit Propagation
---

## Branching Heuristics
---
