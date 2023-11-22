from py4j.java_gateway import JavaGateway
from sys import argv

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()


ontology = parser.parseFile("BurgerRest.ttl")
gateway.convertToBinaryConjunctions(ontology)


# get the TBox axioms
tbox = ontology.tbox()
axioms = tbox.getAxioms()


# get all concepts occurring in the ontology
allConcepts = ontology.getSubConcepts()
elFactory = gateway.getELFactory()

conceptA = elFactory.getConceptName("A")
conceptB = elFactory.getConceptName("B")
conjunctionAB = elFactory.getConjunction(conceptA, conceptB)
role = elFactory.getRole("r")
existential = elFactory.getExistentialRoleRestriction(role,conjunctionAB)
top = elFactory.getTop()
conjunction2 = elFactory.getConjunction(top,existential)

gci = elFactory.getGCI(conjunctionAB,conjunction2)


# Apply all rules for the EL reasoner
def apply_rules(individuals, concept_list, relation_list):
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
            for axiom in ontology.tbox().getAxioms():
                if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
                    if c == axiom.lhs() and axiom.rhs() not in concept_list[index]:
                        concept_list[index].append(axiom.rhs())
                        changed = True

    return changed



def compute_subsumers(ontology, class_name):
    gateway = JavaGateway()
    parser = gateway.getOWLParser()
    formatter = gateway.getSimpleDLFormatter()

    ontology = parser.parseFile(ontology)
    gateway.convertToBinaryConjunctions(ontology)

    concept_names = ontology.getConceptNames()

    concept_key_map = {str(concept): concept for concept in concept_names}

    subsumers = []

    individuals = [0]
    concept_list = [[concept_key_map[class_name]]] if class_name in concept_key_map else []
    relation_list = [[]]

    changed = True

    while changed:
        changed = False

        for index, individual in enumerate(individuals):
            result = apply_rules(individuals, concept_list, relation_list)
            if result:
                changed = True
        concept_list = sum(concept_list,[])
        for concept in concept_list:
            k=formatter.format(concept)
            if k.isalnum():
                subsumers.append(k)

        return subsumers



if __name__ == "__main__":
    if len(argv) != 3:
        raise Exception("Please provide the Ontology Filename and relevant class as input")
    file_path = argv[1]
    class_name = argv[2]
    print("Computing subsumers for class:", class_name)
    subsumers = compute_subsumers(file_path, class_name)
    print("Subsumers computed.")
    # Gather results in a list
    results = [subsumer for subsumer in subsumers]

    # Print one class name per line
    print("Those are the subsumers of the " + str(class_name) + ":")
    for result in results:
        print(result)
    
    
    
    
    
    
    
