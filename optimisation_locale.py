import plotly.graph_objects as go
import os
import sys

list_time_x = []
list_time_y = []

output_files_path = sys.argv[1]

list_file = os.listdir(f"{output_files_path}/hashcat_result/")

limite_seconde_algo = 3600*3

def create_set(filename):
    with open(f"{output_files_path}/hashcat_result/{filename}", "r") as f:
            all_lines = f.readlines()

    list_mdp = []
    compteur_seconde = 0
    for k in range(len(all_lines)):
        if ":" in all_lines[k] and " " not in all_lines[k].split(":")[1] and all_lines[k].split(":")[1] != "\n":
           list_mdp.append(all_lines[k].split(":")[1])
        if "STATUS" in all_lines[k]:
            compteur_seconde +=1
    return list_mdp, compteur_seconde


ensemble_objets = {}
for filename in list_file:
    try:
        list_mdp, compteur_seconde = create_set(filename)
        if len(set(list_mdp)) != 0:

            if " " not in filename:
                filename2 = f"brute-force {filename} characters"

            else:
                filename2 = filename

            ensemble_objets[filename2] = {"ensemble":set(list_mdp), "poids":compteur_seconde}
    except:
        pass

def get_best_element(sous_ensemble_objets, total_mdp):
    vitesse_sous_ensemble_objets = []
    for name in [*sous_ensemble_objets]:
        vitesse_sous_ensemble_objets.append(len(sous_ensemble_objets[name]["ensemble"])/sous_ensemble_objets[name]["poids"])

    if [*sous_ensemble_objets]!= []:
        vitesse_sous_ensemble_objets_trie, sous_ensemble_objets_trie,  = zip(*sorted(zip(vitesse_sous_ensemble_objets, [*sous_ensemble_objets]), reverse=True))
    else:
        return None
    return sous_ensemble_objets_trie[0]


def create_sous_ensemble_objets(name_set_retenu, sous_ensemble_objets, total_mdp):
    for name in [*sous_ensemble_objets]:
        sous_ensemble_objets[name]["ensemble"] = sous_ensemble_objets[name]["ensemble"] - total_mdp
    return sous_ensemble_objets


def solver_local_optimisation(sous_ensemble_objets):
    fig = go.Figure()
    total_seconde = 0
    liste_ordre = []
    total_mdp = set()

    while total_seconde < limite_seconde_algo:
        meilleur_element = get_best_element(sous_ensemble_objets, total_mdp)
        print("meilleur element", meilleur_element)


        if meilleur_element == None or len(total_mdp | sous_ensemble_objets[meilleur_element]["ensemble"]) == len(total_mdp):
            break

        liste_ordre.append(meilleur_element)

        fig.add_trace(go.Scatter(
            x=[total_seconde, total_seconde+sous_ensemble_objets[meilleur_element]["poids"]], 
            y=[len(total_mdp), len(total_mdp | sous_ensemble_objets[meilleur_element]["ensemble"])],
            mode='markers+lines',
            name=meilleur_element)
        )

        fig.update_layout(showlegend=True)

        total_mdp = total_mdp | sous_ensemble_objets[meilleur_element]["ensemble"]

        total_seconde += sous_ensemble_objets[meilleur_element]["poids"]

        sous_ensemble_objets = create_sous_ensemble_objets(meilleur_element, sous_ensemble_objets, total_mdp)

        
    fig.update_layout(
        title={
            'text': 'Optimal password cracking sequence',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Time (s)",
        yaxis_title="Number of recovered passwords",
        )

    fig.show()

    fig.write_image(f"{output_files_path}/result.png")

    return liste_ordre


liste_ordre = solver_local_optimisation(ensemble_objets)

print(liste_ordre)

with open(f"{output_files_path}/cracking_sequence.txt", "w") as f:
    for k in liste_ordre:
        f.write(k+"\n")
