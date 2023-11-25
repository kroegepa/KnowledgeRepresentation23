
import pandas as pd
from scipy.stats import f_oneway
import matplotlib.pyplot as plt
import seaborn as sns
# Create DataFrame with provided data
data = {
    'Reasoner': ['Custo EL', 'ELK', 'HermiT', 'Custo EL', 'ELK', 'HermiT', 'Custo EL', 'ELK', 'HermiT', 'Custo EL', 'ELK', 'HermiT'],
    'Ontology': ['BurgerOnt', 'BurgerOnt', 'BurgerOnt', 'PizzaOnt', 'PizzaOnt', 'PizzaOnt', 'Bfo.basicOnto', 'Bfo.basicOnto', 'Bfo.basicOnto', 'animoOnto', 'animoOnto', 'animoOnto'],
    'Concepts_Found': [348, 464, 466, 600, 813, 895, 186, 186, 186, 156, 210, 211],
    'Reasoning_Timing': [135.755, 0.037, 0.012, 1904.150, 0.0341, 0.142, 7.037, 0.008, 0.004, 149.304, 0.0126, 0.007]
}

# Creating a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)
# ANOVA for Concepts Found
anova_concepts = f_oneway(
    df[df['Reasoner'] == 'Custo EL']['Concepts_Found'],
    df[df['Reasoner'] == 'ELK']['Concepts_Found'],
    df[df['Reasoner'] == 'HermiT']['Concepts_Found']
)
print(df[df['Reasoner'] == 'Custo EL']['Concepts_Found'],
    df[df['Reasoner'] == 'ELK']['Concepts_Found'],
    df[df['Reasoner'] == 'HermiT']['Concepts_Found'])
# ANOVA for Reasoning Timing
anova_timing = f_oneway(
    df[df['Reasoner'] == 'Custo EL']['Reasoning_Timing'],
    df[df['Reasoner'] == 'ELK']['Reasoning_Timing'],
    df[df['Reasoner'] == 'HermiT']['Reasoning_Timing']
)

print("ANOVA for Concepts Found:", anova_concepts)
print("ANOVA for Reasoning Timing:", anova_timing)

# Box plot
plt.figure(figsize=(10, 6))
sns.barplot(x='Ontology', y='Concepts_Found', hue='Reasoner', data=df)
plt.xlabel('Ontologies')
plt.ylabel('Concepts Found')
plt.title('Number of Concepts Found by Reasoners for Different Ontologies')
plt.legend(title='Reasoner', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Data
ontologies = ['Bfo.basicOnto', 'BurgerOnt', 'animoOnto', 'PizzaOnto']
reasoning_timing_El = [7.037, 135.755, 149.304, 1904.150]
reasoning_timing_ELK = [0.008, 0.037, 0.0126, 0.0341]
reasoning_timing_HermiT = [0.004, 0.012, 0.007, 0.142]

# Create line plots for each reasoning method
plt.figure(figsize=(8, 5))

plt.plot(ontologies, reasoning_timing_El, marker='o', label='Custom EL')
plt.plot(ontologies, reasoning_timing_ELK, marker='o', label='ELK')
plt.plot(ontologies, reasoning_timing_HermiT, marker='o', label='HermiT')

plt.xlabel('Ontologies')
plt.ylabel('Reasoning Timing')
plt.title('Reasoning Timing for Different Ontologies by Method')
plt.legend()
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()

# Show plot
plt.show()