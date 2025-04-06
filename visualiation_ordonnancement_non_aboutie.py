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
        self.temps_exec_original = temps_exec  # Stocker le temps d'exécution original
        self.etat = 'Prêt'  # L'état initial du processus
        self.temps_fin = None #Ajouter un temps de fin pour chaque processus

    def __str__(self):
        return f'Nom : {self.nom}\nDuree : {self.temps_exec} ms\nArrivée : {self.arrivee}\nEtat : {self.etat}'



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


def RoundRobin(L_processus, quantum, taux_interruption=0.1):
    temps_courant = 0
    planification = []
    interruptions = []
    file_attente = []
    L_processus_copy = [Processus(p.nom, p.temps_exec, p.arrivee) for p in L_processus]

    while L_processus_copy or file_attente:
        # Ajouter les processus arrivés à la file d'attente
        while L_processus_copy and L_processus_copy[0].arrivee <= temps_courant:
            processus = L_processus_copy.pop(0)
            file_attente.append(processus)
            planification.append((processus, temps_courant, processus.arrivee - temps_courant, 'Prêt'))
            temps_courant = processus.arrivee

        if file_attente:
            processus = file_attente.pop(0)
            temps_exec = min(processus.temps_exec, quantum)

            planification.append((processus, temps_courant, temps_exec, 'Exécution'))
            temps_courant += temps_exec
            processus.temps_exec -= temps_exec

            if random() < taux_interruption:
                processus.etat = 'Bloqué'
                interruptions.append((processus.nom, temps_courant - temps_exec, temps_exec))

                planification.append((processus, temps_courant - temps_exec, temps_exec, 'Bloqué'))

                if processus.temps_exec > 0:
                    processus.etat = 'Prêt'
                    file_attente.append(processus)
                    planification.append((processus, temps_courant, 0, 'Prêt'))
                continue


            if processus.temps_exec > 0:
                processus.etat = 'Prêt'
                file_attente.append(processus)
                planification.append((processus, temps_courant, 0, 'Prêt'))
            else:
                processus.etat = 'Terminé'
                processus.temps_fin = temps_courant # Enregistre le temps de fin
                planification.append((processus, temps_courant, 0, 'Terminé'))

        else:
            temps_courant += 1

    return planification, interruptions


def afficher_planification(planification, interruptions):
    processus_uniques = sorted(set(p.nom for p, _, _, _ in planification))

    couleurs_etats = {
        'Prêt': 'lightgray',
        'Exécution': 'green',
        'Bloqué': 'red',
        'Terminé': 'blue'
    }

    nb_processus = len(processus_uniques)
    fig_height = min(10, 1 + 0.8 * nb_processus)

    fig, ax = plt.subplots(figsize=(15, fig_height))

    y_positions = {p: i for i, p in enumerate(processus_uniques)}

    for processus, debut, duree, etat in planification:
        y = y_positions[processus.nom]
        couleur = couleurs_etats.get(etat, 'white')

        ax.add_patch(patches.Rectangle((debut, y), duree, 0.6,
                                       facecolor=couleur,
                                       edgecolor='black',
                                       linewidth=1,
                                       alpha=0.9))

        if duree > 20:
            ax.text(debut + duree / 2, y + 0.3, f'{processus.nom}\n{duree}ms\n{etat}',
                    ha='center', va='center', fontsize=10, fontweight='bold', color='black')

    for nom, temps_debut, duree in interruptions:
        y = y_positions[nom]
        ax.add_patch(patches.Rectangle((temps_debut, y), duree, 0.6,
                                       facecolor='purple', edgecolor='black',
                                       linewidth=1, alpha=0.6, linestyle='--'))

    ax.set_ylim(-0.5, nb_processus + 0.5)
    ax.set_xlim(0, max(max(debut + duree for processus, debut, duree, etat in planification),
                       max((p.temps_fin if p.temps_fin else 0) for p in [proc for proc,_,_,_ in planification])) + 10)
    ax.set_yticks(range(nb_processus))
    ax.set_yticklabels(processus_uniques, fontsize=12, fontweight='bold')
    ax.set_xlabel('Temps (ms)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Processus', fontsize=14, fontweight='bold')
    ax.set_title('Planification des Processus', fontsize=16, fontweight='bold', color="darkblue")

    ax.grid(axis='x', linestyle='--', alpha=0.5)

    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    legend_elements = [patches.Patch(facecolor=couleurs_etats[etat], edgecolor='black', label=etat)
                       for etat in couleurs_etats]
    ax.legend(handles=legend_elements, loc='upper right', title='État du Processus', frameon=True)

    plt.subplots_adjust(top=0.9)
    plt.tight_layout(rect=[0, 0, 1, 0.9])

    plt.show()

if __name__ == "__main__":
    L_processus = [
        Processus("P1", 200, 0),
        Processus("P2", 100, 50),
        Processus("P3", 300, 20),
        Processus("P4", 150, 70)
    ]

    user_inp = int(input('Quel algorithme souhaitez-vous simuler ?\n1-PAPS \n2-Round Robin \n3-SJF\n'))
    if user_inp == 2:
        quantum = int(input('Quelle taille de quantum souhaitez-vous utiliser ? '))*10
        taux_interruption = float(input('Quel taux d\'interruption souhaitez-vous utiliser ? (entre 0 et 1) '))
        planification, interruptions = RoundRobin(L_processus, quantum, taux_interruption)

        for processus, temps_debut, duree, etat in planification:
            print(f'Temps de début: {temps_debut} ms, Durée: {duree} ms, État: {etat}\n{processus}\n')

        afficher_planification(planification, interruptions)
