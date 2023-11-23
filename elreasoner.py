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

# Apply all rules for the EL reasoner
def apply_rules(individuals, concept_list, relation_list, t_box):
    changed = False

    # Apply ⊤-rule: Add ⊤ to any individual
    print("Applying ⊤-rule...")
    for index, concepts in enumerate(concept_list):
        if not any(concept == elFactory.getTop() for concept in concepts):
            concept_list[index].append(elFactory.getTop())
            changed = True

    # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d
    print("Applying ⊓-rule 1...")
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            axiom_type = c.getClass().getSimpleName()
            if axiom_type == "ConceptConjunction":
                conjuncts = c.getConjuncts()
                for conj in conjuncts:
                    if conj not in concept_list[index]:
                        concept_list[index].append(conj)
                        changed = True

    
    #⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d
    print("Applying ⊓-rule 2...")

    for index, concepts in enumerate(concept_list):
        existing_concepts = set(concepts)  # Store existing concepts for the individual

        for i, c1 in enumerate(existing_concepts):
            for j, c2 in enumerate(existing_concepts):
                if i != j:
                    new_conjunction = elFactory.getConjunction(c1, c2)
                    # Check if the new conjunction already exists for the individual
                    if new_conjunction not in existing_concepts:
                        concept_list[index].append(new_conjunction)
                        changed = True
                        #print(f"Added {new_conjunction} to concept_list[{index}]")
                                    
                    
    #∃-rule 1: If d has ∃r .C assigned...
    print("Applying ∃-rule 1...")
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            #if isinstance(c, elFactory.ExistentialRoleRestriction):
            if c is not None and hasattr(c, '__class__') and hasattr(c.__class__, '__name__') and c.__class__.__name__ == 'ExistentialRoleRestriction':    
                role = c.role()
                filler = c.filler()
                #print(f"Role: {role}, Filler: {filler}")
                for i, relation in enumerate(relation_list):
                    if role in relation:
                        #print(f"Role {role} found in relation: {relation}")
                        for j, concept in enumerate(concept_list):
                            if filler in concept and elFactory.getExistentialRoleRestriction(role, filler) not in concept_list[j]:
                                concept_list[j].append(elFactory.getExistentialRoleRestriction(role, filler))
                                changed = True
                                print(f"Added {elFactory.getExistentialRoleRestriction(role, filler)} to concept_list[{j}]")
                        if filler not in concept_list[i]:
                            concept_list[i].append(filler)
                            changed = True
                            #print(f"Added {filler} to concept_list[{i}]")

    # # ∃-rule 2: If d has an r-successor with C assigned, add ∃r .C to d
    print("Applying ∃-rule 2...")
    for index, relation in enumerate(relation_list):
        for r in relation:
            for i, concept in enumerate(concept_list):
                if r in concept:
                    for j, concept2 in enumerate(concept_list):
                        if isinstance(concept2, elFactory.ConceptName) and elFactory.getExistentialRoleRestriction(r, concept2) not in concept_list[i]:
                            concept_list[i].append(elFactory.getExistentialRoleRestriction(r, concept2))
                            changed = True

    # ⊑-rule: If d has C assigned and C ⊑ D ∈ T, then also assign D to d
    print("Applying ⊑-rule...")
    for index, concepts in enumerate(concept_list):
        for c in concepts:
            for axiom in t_box:
                if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
                    if c == axiom.lhs() and axiom.rhs() not in concept_list[index]:
                        concept_list[index].append(axiom.rhs())
                        changed = True

    return changed



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
    concept_names = ontology.getConceptNames()

    concept_key_map = {remove_quotes(str(concept)):concept for concept in concept_names}

    subsumers = []

    individuals = [0]
    concept_list = [[concept_key_map[class_name]]] if class_name in concept_key_map else []
    relation_list = [[]]

    changed = True

    
    while changed:
        changed = False

        for index, individual in enumerate(individuals):
            # Apply ⊤-rule: Add ⊤ to any individual
    
            if not any(concept == elFactory.getTop() for concept in concept_list[index]):
                print("apply t-rule")
                concept_list[index].append(elFactory.getTop())
                changed = True

            for concept in concept_list[index]:
                concept_type = concept.getClass().getSimpleName()
                # ⊑-rule: If d has C assigned and C ⊑ D ∈ T, then also assign D to d
                print("Applying ⊑-rule...")
                for axiom in t_box:
                    if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
                        if concept == axiom.lhs() and axiom.rhs() not in concept_list[index]:
                            concept_list[index].append(axiom.rhs())
                            changed = True


                # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d
                if concept_type == "ConceptConjunction":
                    conjuncts = concept.getConjuncts()
                    for conj in conjuncts:
                        if conj not in concept_list[index] and conj in all_concept_list:
                            concept_list[index].append(conj)
                            changed = True
                #⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d
                for concept_two in concept_list[index]:
                    new_conjunction_one = elFactory.getConjunction(concept, concept_two)
                    new_conjunction_two = elFactory.getConjunction(concept_two, concept)

                    # Check if the new conjunction already exists for the individual
                    if new_conjunction_one not in concept_list[index] and new_conjunction_one in all_concept_list:
                        concept_list[index].append(new_conjunction_one)
                        print("Applying ⊓-rule 2...")
                        changed = True
                        #print(f"Added {new_conjunction} to concept_list[{index}]")
                    # Check if the new conjunction already exists for the individual
                    if new_conjunction_two not in concept_list[index] and new_conjunction_two in all_concept_list:
                        concept_list[index].append(new_conjunction_two)
                        print("Applying ⊓-rule 2...")
                        changed = True                                    
                            
                #∃-rule 1: If d has ∃r .C assigned...
                if concept_type == "ExistentialRoleRestriction":
                    print("Applying ∃-rule 1...")
                    found = False
                    for relation in relation_list[index]:
                        if relation[0] == concept.role() and concept.filler() in concept_list[relation[1]]:
                            found = True
                            break
                    if not found:
                        added_flag = False
                        #Check if individual exists with filler assigned already
                        for indiv in individuals:
                            if concept.filler() in concept_list[indiv] and indiv != individual:
                                relation_list[index].append((concept.role(),indiv))
                                added_flag = True
                                break
                        if not added_flag:
                            new_individual = len(individuals)
                            individuals.append(new_individual)
                            concept_list.append([concept.filler()])
                            relation_list[index].append((concept.role(),new_individual))
                            relation_list.append([])
            # # ∃-rule 2: If d has an r-successor with C assigned, add ∃r .C to d
            for relation in relation_list[individual]:
                for concept in concept_list[relation[1]]:
                    existential_concept = elFactory.getExistentialRoleRestriction(relation[0],concept)
                    if existential_concept not in concept_list[individual] and existential_concept in all_concept_list:
                        print("Applying ∃-rule 2...")
                        concept_list[individual].append(existential_concept)
    
    subsumers = []
    for concept in concept_list[0]:
        if concept.getClass().getSimpleName() == "ConceptName":
            subsumers.append(concept)
        elif concept.getClass().getSimpleName() == "TopConcept$":
            subsumers.append(concept)

    print(concept_list[0])
    print()
    print(subsumers)

    
    elk = gateway.getELKReasoner()
    print(class_name)
    print()
    print("I am first testing ELK.")
    elk.setOntology(ontology)
    print()
    print("According to ELK, Margherita has the following subsumers: ")
    test = elFactory.getConceptName(class_name)

    print(test)
    subsumersss = elk.getSubsumers(test)
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
    
    
    
    
    
    
    
