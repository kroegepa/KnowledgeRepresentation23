from py4j.java_gateway import JavaGateway
from sys import argv

# connect to the java gateway of dl4python
gateway = JavaGateway()
print(gateway)
# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()
print(parser)
# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()
print(formatter)
print("Loading the ontology...")

# load an ontology from a file
#ontology = parser.parseFile("Burger.rdf")
ontology = parser.parseFile("BurgerRest.ttl")
print("Loaded the ontology!")

# IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
# Ontologies in OWL can however have conjunctions over an arbitrary number of concpets.
# The following command changes all conjunctions so that they have at most two conjuncts
print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)
print(gateway.convertToBinaryConjunctions(ontology))
print("---------------------------------------------------------------------------------------------------")


# get the TBox axioms
tbox = ontology.tbox()
axioms = tbox.getAxioms()


print("These are the axioms in the TBox:")
for axiom in axioms:
    print(formatter.format(axiom))


# get all concepts occurring in the ontology
allConcepts = ontology.getSubConcepts()

print()
print("There are ",len(allConcepts), " concepts occurring in the ontology")
print("These are the concepts occurring in the ontology:")
print([formatter.format(x) for x in allConcepts])

conceptNames = ontology.getConceptNames()
print(type(conceptNames))
print("----------------------------------------------------------------------------------------------------")
print()
print("There are ", len(conceptNames), " concept names occurring in the ontology")
print("These are the concept names: ")
print([formatter.format(x) for x in conceptNames])


# access the type of axioms:
foundGCI = False
foundEquivalenceAxiom = False
print()
print("Looking for axiom types in EL")
for axiom in axioms:
    axiomType = axiom.getClass().getSimpleName() 
    #print(axiomType)
    if(not(foundGCI)
       and axiomType == "GeneralConceptInclusion"):
        print("I found a general concept inclusion:")
        print(formatter.format(axiom))
        print("The left hand side of the axiom is: ", formatter.format(axiom.lhs()))
        print("The right hand side of the axiom is: ", formatter.format(axiom.rhs()))
        print()
        foundGCI = True

    elif(not(foundEquivalenceAxiom)
         and axiomType == "EquivalenceAxiom"):
        print("I found an equivalence axiom:")
        print(formatter.format(axiom))
        print("The concepts made equivalent are: ")
        for concept in axiom.getConcepts():
            print(" - "+formatter.format(concept))
        print()
        foundEquivalenceAxiom = True

# accessing the relevant types of concepts:
foundConceptName=False
foundTop=False
foundExistential=False
foundConjunction=False
foundConceptTypes = set()

print()
print("Looking for concept types in EL")
for concept in allConcepts:
    conceptType = concept.getClass().getSimpleName()
    if(not(conceptType in foundConceptTypes)): 
        print(conceptType)
        foundConceptTypes.add(conceptType)
    if(not(foundConceptName) and conceptType == "ConceptName"):
        print("I found a concept name: "+formatter.format(concept))
        print()
        foundConceptName = True
    elif(not(foundTop) and conceptType == "TopConcept$"):
        print("I found the top concept: "+formatter.format(concept))
        print()
        foundTop = True
    elif(not(foundExistential) and conceptType == "ExistentialRoleRestriction"):
        print("I found an existential role restriction: "+formatter.format(concept))
        print("The role is: "+formatter.format(concept.role()))
        print("The filler is: "+formatter.format(concept.filler()))
        print()
        foundExistential = True
    elif(not(foundConjunction) and conceptType == "ConceptConjunction"):
        print("I found a conjunction: "+formatter.format(concept))
        print("The conjuncts are: ")
        for conjunct in concept.getConjuncts():
            print(" - "+formatter.format(conjunct))
        print()
        foundConjunction=True


# Creating EL concepts and axioms

elFactory = gateway.getELFactory()

conceptA = elFactory.getConceptName("A")
conceptB = elFactory.getConceptName("B")
conjunctionAB = elFactory.getConjunction(conceptA, conceptB)
role = elFactory.getRole("r")
existential = elFactory.getExistentialRoleRestriction(role,conjunctionAB)
top = elFactory.getTop()
conjunction2 = elFactory.getConjunction(top,existential)

gci = elFactory.getGCI(conjunctionAB,conjunction2)

print()
print()
print("I made the following GCI:")
print(formatter.format(gci))
print()
print()
print("EL REASONER TEST")

# Apply all rules for the EL reasoner
def apply_rules(individuals, concept_list, relation_list):
    changed = False

    # Apply ⊤-rule: Add ⊤ to any individual
    for index, concepts in enumerate(concept_list):
        if not all(elFactory.getTop() in c for c in concepts):
            concept_list[index].append(elFactory.getTop())
            changed = True

    # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            if isinstance(c, elFactory.ConceptConjunction):
                conjuncts = c.getConjuncts()
                for conj in conjuncts:
                    if conj not in concept_list[index]:
                        concept_list[index].append(conj)
                        changed = True

    # ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d
    for index, concepts in enumerate(concept_list):
        for i, c1 in enumerate(concepts):
            for j, c2 in enumerate(concepts):
                if i != j and elFactory.getConjunction(c1, c2) not in concept_list[index]:
                    concept_list[index].append(elFactory.getConjunction(c1, c2))
                    changed = True

    # ∃-rule 1: If d has ∃r .C assigned...
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            if isinstance(c, elFactory.ExistentialRoleRestriction):
                role = c.role()
                filler = c.filler()
                for i, relation in enumerate(relation_list):
                    if role in relation:
                        for j, concept in enumerate(concept_list):
                            if filler in concept and elFactory.getExistentialRoleRestriction(role, filler) not in concept_list[j]:
                                concept_list[j].append(elFactory.getExistentialRoleRestriction(role, filler))
                                changed = True
                        if filler not in concept_list[i]:
                            concept_list[i].append(filler)
                            changed = True

    # ∃-rule 2: If d has an r-successor with C assigned, add ∃r .C to d
    for index, relation in enumerate(relation_list):
        for r in relation:
            for i, concept in enumerate(concept_list):
                if r in concept:
                    for j, concept2 in enumerate(concept_list):
                        if isinstance(concept2, elFactory.ConceptName) and elFactory.getExistentialRoleRestriction(r, concept2) not in concept_list[i]:
                            concept_list[i].append(elFactory.getExistentialRoleRestriction(r, concept2))
                            changed = True

    # ⊑-rule: If d has C assigned and C ⊑ D ∈ T, then also assign D to d
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            for axiom in ontology.tbox().getAxioms():
                if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
                    if c == axiom.lhs() and axiom.rhs() not in concept_list[index]:
                        concept_list[index].append(axiom.rhs())
                        changed = True

    return changed








def check_entailment(file_path, class_name):

    gateway = JavaGateway()
    parser = gateway.getOWLParser()
    formatter = gateway.getSimpleDLFormatter()

    ontology = parser.parseFile("BurgerRest.ttl")
    gateway.convertToBinaryConjunctions(ontology)

    tbox = ontology.tbox()
    axioms = tbox.getAxioms()

    all_concepts = ontology.getSubConcepts()
    concept_names = ontology.getConceptNames()
    conceptNamesFormatted = [formatter.format(x) for x in conceptNames]
    # Initialization of individuals, concepts, and relations
    individuals = [0]
    #concept_list = [[conceptNamesFormatted[class_name]]]
    concept_list = []
    for i in conceptNamesFormatted:
        concept_list.append(i)
    #concept_list = [[] for _ in range(len(conceptNamesFormatted))]
    print(concept_list)
    relation_list = [[]]

    changed = True

    while changed:
        changed = False

        # Loop through individuals' interpretations
        for index, individual in enumerate(individuals):
            # Apply rules to the current individual
            result = apply_rules(individuals, concept_list, relation_list)
            if result:
                changed = True  # If any change occurred, set changed to True
    for concept in concept_list[0]:
            if concept.getClass.getSimpleName() == "ConceptName":
                print(formatter.format(concept))












# if conceptNamesFormatted["D0"] in concept_list[0]:  # Assuming D0 is the desired class and d0 is the initial element
#     print("Entailment holds: O |= C0 ⊑ D0")
# else:
#     print("Entailment does not hold: O !|= C0 ⊑ D0")
        






if __name__ == "__main__":
    if len(argv) != 3:
        raise Exception("Please give the Ontology Filename and relevant class as input")
    file_path = argv[1]
    class_name = argv[2]
    check_entailment(file_path, class_name)
    print(check_entailment(file_path, class_name))
    
    
    
    
    
    
    
