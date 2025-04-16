def load_dimacs(clauseFile): # this function accepts a problem set in DIMACS format in either a .txt or .cnf file - clauseFile is the a string of the filepath to the problem file
    clauseFile = open(clauseFile, 'r')
    while clauseFile.read(1) == "c":
        clauseFile.readline()
    clauseCount = int(clauseFile.readline().split()[-1])
    clauseList = [""] * clauseCount
  
    for i in range(clauseCount):
        line = clauseFile.readline()
        while line[0] == "c":
            line = clauseFile.readline()
        clauseList[i] = list(map(int,line.split()[:-1]))
    
    return clauseList

def dpll_sat_solve(clauseSet=[], partialAssignment=[]): # the entire solver is here (I should probably refactor it but this works)
    def JWCof4(clauseSet, occurenceList): #heuristic
        scores = {}
        for literal, indices in occurenceList.items():
            for idx in indices:
                clause = clauseSet[idx]
                if clause: 
                    scores[literal] = scores.get(literal, 0) + 4 ** (-len(clause))
        

        combined_scores = {}
        for literal in scores:
            if -literal in combined_scores:
                continue
            combined_scores[literal] = scores.get(literal) + scores.get(-literal, 0)
        
        if combined_scores:
            best = max(combined_scores, key=combined_scores.get)
            
            if combined_scores[best] >= scores.get(-best, 0):
                return best
            return -best
        return next(iter(occurenceList))

    def buildOccurenceList(clauseSet): # function to build the occurence list
        occurenceList = {}
        for i in range(len(clauseSet)):
            for literal in clauseSet[i]:
                occurenceList.setdefault(literal,set()).add(i)
                
        return occurenceList
      
    def dynamicUP(clauseSet, UPstack): #still have to check this for EDGE CASES - function to Unit Propagate the clauseSet - implemented in a convenient way
        units = {next(iter(clause)) for clause in clauseSet if clause and len(clause) == 1}
        # print('units:', units, clauseSet, partialAssignment)

        if not units:
            return clauseSet,[],[]
        if any(-unit in units for unit in units):
            # print('returned 1')
            return False
        UPclauseSet = clauseSet[:]
        newAssignments = units
        
        while units:
            newUnits = set()
            for unit in units:
                # print('units', units)
                indexes = occurenceList.get(unit)
                # print(unit, indexes)
                for index in indexes:
                    UPclauseSet[index] = None
                UPstack.append((unit, indexes))
                occurenceList.__delitem__(unit)
                indexes = occurenceList.get(-unit)
                if indexes:
                    for index in indexes:
                        if UPclauseSet[index]:
                            newClause = UPclauseSet[index] - {-unit}
                            if len(newClause) <= 1:
                                if not newClause:
                                    while UPstack:
                                        key, indexes = UPstack.pop()
                                        occurenceList[key] = indexes
                                    # print('returned 2')
                                    return False
                                newUnit = next(iter(newClause))
                                
                                # newUnits.add(newUnit)
                                if newUnit not in units:
                                    newUnits.add(newUnit)
                                else:
                                    # print('overlap')
                                    OL = index

                            UPclauseSet[index] = newClause
                    UPstack.append((-unit, indexes))
                    occurenceList.__delitem__(-unit)
                 
            newAssignments.update(newUnits)
            units = newUnits
            # print('bottom units:', units)
            
        return UPclauseSet, newAssignments, UPstack

    def inner_ol_l(clauseSet, partialAssignment= []): #this is the main recursive function - ol for occurence list
        UP = dynamicUP(clauseSet, [])
        if not UP:
            return False
        UPclauseSet, addedAssignments, UPstack = UP
        partialAssignment.extend(list(addedAssignments))

        if not occurenceList:
            return partialAssignment
        
        stack = []
        PosClauses = UPclauseSet[:]
        variable = JWCof4(UPclauseSet, occurenceList)
        indexes = occurenceList[variable]
        for index in indexes:
            PosClauses[index] = None
        stack.append((variable, indexes))
        occurenceList.__delitem__(variable)
        indexes = occurenceList.get(-variable)
        if indexes:
            for index in indexes:
                if PosClauses[index]:
                    PosClauses[index] = PosClauses[index] - {-variable}
            stack.append((-variable, indexes))
            occurenceList.__delitem__(-variable)
        

        posBranch = inner_ol_l(PosClauses, partialAssignment + [variable])
        if posBranch:
            return posBranch
        # print('after posBranch')
        while stack:
            key, indexes = stack.pop()
            occurenceList[key] = indexes
            
        # print(occurenceList)
        negClauses = UPclauseSet[:]
        indexes = occurenceList.get(-variable)
        if indexes:
            for index in indexes:
                negClauses[index] = None
            stack.append((-variable, indexes))
            occurenceList.__delitem__(-variable)
        indexes = occurenceList.get(variable)
        if indexes:
            for index in indexes:
                if negClauses[index]:
                    negClauses[index] = negClauses[index] - {variable}
            stack.append((variable, indexes))
            occurenceList.__delitem__(variable)

        # print('backtracked to false')
        negBranch = inner_ol_l(negClauses, partialAssignment + [-variable])
        if negBranch:
            return negBranch
        # print('double backtracked')
        while stack:
            key, indexes = stack.pop()
            occurenceList[key] = indexes
        while UPstack:
            key, indexes = UPstack.pop()
            occurenceList[key] = indexes
        return False
 

    occurenceList = buildOccurenceList(clauseSet)
    clauseSet = [set(clause) for clause in clauseSet]
    return inner_ol_l(clauseSet,[])
