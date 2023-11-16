from py4j.java_gateway import JavaGateway
from sys import argv
def ELReasoner(Filename, Class):
    # connect to the java gateway of dl4python
    gateway = JavaGateway()

    # get a parser from OWL files to DL ontologies
    parser = gateway.getOWLParser()

    # get a formatter to print in nice DL format
    formatter = gateway.getSimpleDLFormatter()

    print("Loading the ontology...")

    # load an ontology from a file
    ontology = parser.parseFile(Filename)

    print("Loaded the ontology!")

    # IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
    # Ontologies in OWL can however have conjunctions over an arbitrary number of concpets.
    # The following command changes all conjunctions so that they have at most two conjuncts
    print("Converting to binary conjunctions")
    gateway.convertToBinaryConjunctions(ontology)



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

    print()
    print("There are ", len(conceptNames), " concept names occurring in the ontology")
    print("These are the concept names: ")
    print(conceptNames)
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

    conceptNamesFormatted = [formatter.format(x) for x in conceptNames]
    if Class not in conceptNamesFormatted:
        raise Exception("Please input a valid class name")
    classIndex = conceptNamesFormatted.index(Class)
    #EL Reasoner
    for Name in conceptNamesFormatted:
        #find out if you should exclude the class of its own
        ClassConcept = elFactory.getConceptName(Class)
        SubsumeeConcept = elFactory.getConceptName(Name)
        gci = elFactory.getGCI(ClassConcept,SubsumeeConcept)
        print(formatter.format(gci))

        SubsumeeList = []
        Individuals = [0]
        ConceptList = [[conceptNames[classIndex]]]
        RelationList = [[]]
        IndividualCounter = 1
        changed = True
        #Apply all rules
        #Give out all concepts assigned to first individual that are a conceptName
        while changed:
            changed = False
            for index,individual in enumerate(Individuals):
                for concept in ConceptList[index]:
                    

                    
                if changed:
                    break

        for concept in ConceptList[0]:
            if concept.getClass.getSimpleName() == "ConceptName":
                print(formatter.format(concept))




if __name__ == "__main__" :
    if len(argv) != 3:
        raise Exception("Please give the Ontology Filename and relevant class as input")
    FilePath = argv[1]
    Class = argv[2]            
    ELReasoner(FilePath, Class)