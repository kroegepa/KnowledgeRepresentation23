import elreasoner
from py4j.java_gateway import JavaGateway
import time
file_path = "bfo.basic-formal-ontology.2.owl.xml"

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

time_our = 0
time_elk = 0
time_hermit = 0



for concept in conceptNames:
    concept = formatter.format(concept)
    print(concept)
    time_start = time.time()
    subsumer = elreasoner.compute_subsumers(ontology,concept)
    time_end = time.time()
    time_our += time_end - time_start

    class_name = elFactory.getConceptName(concept)

    time_start = time.time()
    subsumers_elk = elk.getSubsumers(class_name)
    time_end = time.time()
    time_elk += time_end - time_start

    time_start = time.time()
    subsumers_hermit = hermit.getSubsumers(class_name)
    time_end = time.time()
    time_hermit += time_end - time_start

    total_our += len(subsumer)
    total_elk += len(subsumers_elk)
    total_hermit += len(subsumers_hermit)

f = open(file_path + "_test_result.txt", "w+")

f.write("our Reasoner found " + str(total_our) + " Concepts in the" + file_path + " Ontology")
f.write("ELK Reasoner found " + str(total_elk) + " Concepts in the" + file_path + " Ontology")
f.write("Hermit Reasoner found " + str(total_hermit) + " Concepts in the" + file_path + " Ontology")
f.write("total time taken for our reasoner in seconds was" + str(time_our))
f.write("total time taken for ELK reasoner in seconds was " + str(time_elk))
f.write("total time taken for our reasoner in seconds was " + str(time_hermit))
f.close()
