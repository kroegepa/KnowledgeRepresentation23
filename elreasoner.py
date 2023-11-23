from py4j.java_gateway import JavaGateway
from sys import argv

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

#global concept list - this is ugly and there is too many global variables here but we'll run with it now
all_concept_list = set()

#ontology = parser.parseFile("file_path")
#ontology = parser.parseFile("BurgerRest.ttl")
#gateway.convertToBinaryConjunctions(ontology)


# get the TBox axioms
#tbox = ontology.tbox()
#axioms = tbox.getAxioms()


# get all concepts occurring in the ontology
#allConcepts = ontology.getSubConcepts()
elFactory = gateway.getELFactory()

conceptA = elFactory.getConceptName("A")
conceptB = elFactory.getConceptName("B")
conjunctionAB = elFactory.getConjunction(conceptA, conceptB)
role = elFactory.getRole("r")
existential = elFactory.getExistentialRoleRestriction(role,conjunctionAB)
top = elFactory.getTop()
conjunction2 = elFactory.getConjunction(top,existential)

gci = elFactory.getGCI(conjunctionAB,conjunction2)



def remove_quotes(text):
    return text.replace('"', '').replace("'", "")



def compute_subsumers(ontology, class_name):
    gateway = JavaGateway()
    parser = gateway.getOWLParser()
    formatter = gateway.getSimpleDLFormatter()
    elFactory = gateway.getELFactory()
    ontology = parser.parseFile(ontology)
    gateway.convertToBinaryConjunctions(ontology)
    #Add inclusion axioms for equivalence ones
    t_box = []
    for axiom in ontology.tbox().getAxioms():
        if axiom.getClass().getSimpleName() == "EquivalenceAxiom":
            concepts = axiom.getConcepts()
            inclusion_one = elFactory.getGCI(concepts[0],concepts[1])
            inclusion_two = elFactory.getGCI(concepts[1],concepts[0])
            t_box.append(inclusion_one)
            t_box.append(inclusion_two)            
        else:
            t_box.append(axiom)
    for concept in ontology.getSubConcepts():
        all_concept_list.add(concept)
    concept_names = [formatter.format(concept) for concept in ontology.getConceptNames()]
    
    # check if concept exists
    class_name = remove_quotes(class_name)
    if class_name not in concept_names:
        class_name = '"' + class_name + '"'
        if class_name not in concept_names:
            print("The given class is not part of the ontology")
            exit()
    class_name = elFactory.getConceptName(class_name)
    subsumers = []

    individuals = [0]
    concept_list = [[class_name]]
    relation_list = [[]]

    changed = True

    
    while changed:
        changed = False

        for individual in individuals:
            # Apply ⊤-rule: Add ⊤ to any individual
    
            if not any(concept == elFactory.getTop() for concept in concept_list[individual]):
                #print("apply t-rule")
                concept_list[individual].append(elFactory.getTop())
                changed = True

            for concept in concept_list[individual]:
                concept_type = concept.getClass().getSimpleName()
                # ⊑-rule: If d has C assigned and C ⊑ D ∈ T, then also assign D to d
                for axiom in t_box:
                    if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
                        if concept == axiom.lhs() and axiom.rhs() not in concept_list[individual]:
                           # print("Applying ⊑-rule...")
                            concept_list[individual].append(axiom.rhs())
                            changed = True


                # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d
                if concept_type == "ConceptConjunction":
                    conjuncts = concept.getConjuncts()
                    for conj in conjuncts:
                        if conj not in concept_list[individual] and conj in all_concept_list:
                            concept_list[individual].append(conj)
                            changed = True
                #⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d
                for concept_two in concept_list[individual]:
                    new_conjunction_one = elFactory.getConjunction(concept, concept_two)
                    new_conjunction_two = elFactory.getConjunction(concept_two, concept)

                    # Check if the new conjunction already exists for the individual
                    if new_conjunction_one not in concept_list[individual] and new_conjunction_one in all_concept_list:
                        concept_list[individual].append(new_conjunction_one)
                        #print("Applying ⊓-rule 2...")
                        changed = True
                        #print(f"Added {new_conjunction} to concept_list[{index}]")
                    # Check if the new conjunction already exists for the individual
                    if new_conjunction_two not in concept_list[individual] and new_conjunction_two in all_concept_list:
                        concept_list[individual].append(new_conjunction_two)
                        #print("Applying ⊓-rule 2...")
                        changed = True                                    
                            
                #∃-rule 1: If d has ∃r .C assigned...
                if concept_type == "ExistentialRoleRestriction":
                    #print("Applying ∃-rule 1...")
                    found = False
                    for relation in relation_list[individual]:
                        if relation[0] == concept.role() and concept.filler() in concept_list[relation[1]]:
                            found = True
                            break
                    if not found:
                        added_flag = False
                        #Check if individual exists with filler assigned already
                        for indiv in individuals:
                            if concept.filler() in concept_list[indiv] and indiv != individual:
                                relation_list[individual].append((concept.role(),indiv))
                                added_flag = True
                                changed = True
                                break
                                
                        if not added_flag:
                            new_individual = len(individuals)
                            individuals.append(new_individual)
                            concept_list.append([concept.filler()])
                            relation_list[individual].append((concept.role(),new_individual))
                            relation_list.append([])
                            changed = True
            # # ∃-rule 2: If d has an r-successor with C assigned, add ∃r .C to d
            for relation in relation_list[individual]:
                for concept in concept_list[relation[1]]:
                    existential_concept = elFactory.getExistentialRoleRestriction(relation[0],concept)
                    if existential_concept not in concept_list[individual] and existential_concept in all_concept_list:
                        #print("Applying ∃-rule 2...")
                        concept_list[individual].append(existential_concept)
                        changed = True
    
    subsumers = []
    for concept in concept_list[0]:
        if concept.getClass().getSimpleName() == "ConceptName":
            subsumers.append(concept)
        elif concept.getClass().getSimpleName() == "TopConcept$":
            subsumers.append(concept)


    elk = gateway.getELKReasoner()
    print()
    print("I am first testing ELK.")
    elk.setOntology(ontology)
    print()
    print("According to ELK, Margherita has the following subsumers: ")
    subsumersss = elk.getSubsumers(class_name)
    for concept in subsumersss:
        print(" - ",formatter.format(concept))
    print("(",len(subsumersss)," in total)")
    print()
        
    return subsumers



if __name__ == "__main__":
    if len(argv) != 3:
        raise Exception("Please provide the Ontology Filename and relevant class as input")
    file_path = argv[1]
    class_name = argv[2]
    ontology = parser.parseFile(file_path)
    print("Computing subsumers for class:", class_name)
    subsumers = compute_subsumers(file_path, class_name)
    print("Subsumers computed.")
    # Gather results in a list
    # Print one class name per line
    print("Those are the subsumers of the " + str(class_name) + ":")
    for subsumer in subsumers:
        print(formatter.format(subsumer))
    
    
    
    
    
    
    
