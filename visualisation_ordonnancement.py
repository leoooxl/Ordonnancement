from random import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class Processus:
    def __init__(self, nom, temps_exec, arrivee, d_blocage={}, prio=0):
        assert isinstance(d_blocage, dict)
        self.nom = nom
        self.temps_exec = temps_exec
        self.arrivee = arrivee
        self.d_blocage = d_blocage
        self.temps_exec_original = temps_exec  # Store the original execution time


    def __str__(self):
        return f'Nom : {self.nom}\nDuree : {self.temps_exec} ms\nArrivée : {self.arrivee}'


def PAPS(L_processus):
    L_processus.sort(key=lambda p: p.arrivee)
    temps_courant = 0
    planification = []

    for processus in L_processus:
        if temps_courant < processus.arrivee:
            temps_courant = processus.arrivee
        planification.append((processus, temps_courant, processus.temps_exec))
        temps_courant += processus.temps_exec

    return planification

def SJF(L_processus):
    L_processus.sort(key=lambda p: (p.arrivee, p.temps_exec))
    temps_courant = 0
    planification = []
    file_attente = []

    while L_processus or file_attente:
        while L_processus and L_processus[0].arrivee <= temps_courant:
            file_attente.append(L_processus.pop(0))

        if file_attente:
            file_attente.sort(key=lambda p: p.temps_exec)
            processus = file_attente.pop(0)
            planification.append((processus, temps_courant, processus.temps_exec))
            temps_courant += processus.temps_exec
        else:
            temps_courant = L_processus[0].arrivee if L_processus else temps_courant + 1

    return planification


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def afficher_planification(planification):
    # Extraction des noms uniques des processus
    processus_uniques = sorted(set(p.nom for p, _, _ in planification))

    # Limiter la hauteur pour éviter que le graphique dépasse du cadre
    nb_processus = len(processus_uniques)
    fig_height = min(10, 1 + 0.8 * nb_processus)  # Ajuste la hauteur automatiquement (max 10)

    # Configuration de la figure
    fig, ax = plt.subplots(figsize=(15, fig_height))

    # Palette de couleurs vives et contrastées
    colors = plt.cm.rainbow(np.linspace(0, 1, len(processus_uniques)))  # Utilisation de la palette rainbow
    color_dict = dict(zip(processus_uniques, colors))

    # Position verticale des processus (axe Y)
    y_positions = {p: i for i, p in enumerate(processus_uniques)}

    # Ajout des rectangles représentant les processus
    for processus, debut, duree in planification:
        y = y_positions[processus.nom]
        ax.add_patch(patches.Rectangle((debut, y), duree, 0.6,
                                       facecolor=color_dict[processus.nom],
                                       edgecolor='black',
                                       linewidth=1,
                                       alpha=0.9))

        # Ajouter du texte au centre des rectangles si la durée est suffisamment grande (> 20ms)
        if duree > 20:
            ax.text(debut + duree / 2, y + 0.3, f'{processus.nom}\n{duree}ms',
                    ha='center', va='center', fontsize=10, fontweight='bold', color='black')

    # Configuration des axes
    ax.set_ylim(-0.5, nb_processus + 0.5)  # Ajustement automatique de la hauteur
    ax.set_xlim(0, max(debut + duree for _, debut, duree in planification) + 10)  # Ajout d'un espace à droite
    ax.set_yticks(range(nb_processus))
    ax.set_yticklabels(processus_uniques, fontsize=12, fontweight='bold')
    ax.set_xlabel('Temps (ms)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Processus', fontsize=14, fontweight='bold')
    ax.set_title('Planification des Processus', fontsize=16, fontweight='bold', color="darkblue")

    # Ajout d'une grille légère pour l'axe X
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    # Suppression des bordures inutiles et personnalisation des axes
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # Ajout d'une légende avec les couleurs des processus
    legend_elements = [patches.Patch(facecolor=color, edgecolor='black', label=nom)
                       for nom, color in color_dict.items()]
    ax.legend(handles=legend_elements, loc='upper right', title='Processus', frameon=True)

    # Ajustement de la mise en page pour éviter les chevauchements et ajouter une marge en haut
    plt.subplots_adjust(top=0.9)  # Ajuste la marge en haut

    # Ajustement de la mise en page pour éviter les chevauchements
    plt.tight_layout(rect=[0, 0, 1, 0.9])  # Ajuste la mise en page

    # Affichage du graphique
    plt.show()



def RoundRobin(L_processus, quantum):
    temps_courant = 0
    planification = []
    file_attente = []
    L_processus_copy = [Processus(p.nom, p.temps_exec, p.arrivee) for p in L_processus]

    while L_processus_copy or file_attente:
        while L_processus_copy and L_processus_copy[0].arrivee <= temps_courant:
            file_attente.append(L_processus_copy.pop(0))

        if file_attente:
            processus = file_attente.pop(0)
            temps_exec = min(processus.temps_exec, quantum)

            # Regrouper les exécutions consécutives du même processus
            if planification and planification[-1][0].nom == processus.nom:
                _, debut, duree = planification.pop()
                planification.append((processus, debut, duree + temps_exec))
            else:
                planification.append((processus, temps_courant, temps_exec))

            temps_courant += temps_exec
            processus.temps_exec -= temps_exec

            if processus.temps_exec > 0:
                file_attente.append(processus)
        else:
            temps_courant = L_processus_copy[0].arrivee if L_processus_copy else temps_courant + 1

    return planification


if __name__ == "__main__":
    L_processus = [
        Processus("P1", 200, 0),
        Processus("P2", 100, 50),
        Processus("P3", 300, 20),
        Processus("P4", 150, 70),
        Processus('P5',300,35)
    ]

    user_inp = int(input('Quel algorithme souhaitez-vous simuler ?\n1-PAPS \n2-Round Robin \n3-SJF\n'))
    if user_inp == 1:
        planification = PAPS(L_processus)
    elif user_inp == 2:
        quantum = int(input('Quelle taille de quantum souhaitez-vous utiliser ? '))*10
        planification = RoundRobin(L_processus, quantum)
    elif user_inp == 3:
        planification = SJF(L_processus)

    # Afficher la planification
    for processus, temps_debut, duree in planification:
        print(f'Temps de début: {temps_debut} ms, Durée: {duree} ms\n{processus}\n')

    # Afficher le graphique de planification
    afficher_planification(planification)

