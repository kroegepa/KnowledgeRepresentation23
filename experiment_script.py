import elreasoner
from py4j.java_gateway import JavaGateway
file_path = "Skin Physiology Ontology 2.0.owl"

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

elFactory = gateway.getELFactory()

ontology = parser.parseFile(file_path)
gateway.convertToBinaryConjunctions(ontology)
# subsumer = elreasoner.compute_subsumers(ontology,class_name)
# print(subsumer)
conceptNames = ontology.getConceptNames()
# print([formatter.format(concept) for concept in conceptNames])
# elk = gateway.getELKReasoner()
# print()
# print("I am first testing ELK.")
# elk.setOntology(ontology)
# print()
# print("According to ELK, Margherita has the following subsumers: ")
# class_name = elFactory.getConceptName(class_name)
# subsumersss = elk.getSubsumers(class_name)
# for concept in subsumersss:
#     print(" - ",formatter.format(concept))
# print("(",len(subsumersss)," in total)")
# print()
elk = gateway.getELKReasoner()
elk.setOntology(ontology)
hermit = gateway.getHermiTReasoner() # might the upper case T!
hermit.setOntology(ontology)

total_our = 0
total_elk = 0
total_hermit = 0


for concept in conceptNames:
    concept = formatter.format(concept)
    print(concept)
    subsumer = elreasoner.compute_subsumers(ontology,concept)
    class_name = elFactory.getConceptName(concept)

    subsumers_elk = elk.getSubsumers(class_name)
    subsumers_hermit = hermit.getSubsumers(class_name)

    total_our += len(subsumer)
    total_elk += len(subsumers_elk)
    total_hermit += len(subsumers_hermit)
print()
print("our Reasoner found " + str(total_our) + " Concepts in the" + file_path + " Ontology")
print("ELK Reasoner found " + str(total_elk) + " Concepts in the" + file_path + " Ontology")
print("Hermit Reasoner found " + str(total_hermit) + " Concepts in the" + file_path + " Ontology")