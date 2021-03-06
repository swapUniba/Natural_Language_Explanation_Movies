from Mapper import *
from Builder import *
import sys


# Funzione che prende in input la proprieta e ritorna il rispettivo punteggio IDF preso dal file
# di mapping degli IDF di ogni proprieta precedentemente creato
def calcola_IDF(prop):
    IDF = ''
    with open("list_idf_prop_movies", 'r') as f:    # scorre il file riga per riga
        for line in f:
            line = line.rstrip().split('\t')
            if prop == line[0]:                     # quando trova la proprieta restituisce il rispettivo IDF
                IDF = line[1]
                IDF = float(IDF)
                break
    return IDF


# Funzione che prende in input il grafo costruito, le proprieta in comune e i due dizionari di film piaciuti e
# raccomandati  ed effettua il ranking delle proprieta in comune in ordine di
# influenza attraverso il calcolo di un punteggio (in ordine decrescente)
def ranking_proprieta(G, proprieta_comuni, item_piaciuti, item_raccom, idf):
    alfa = 0.5
    beta = 0.5
    score_prop = {}

    if idf:
        for prop in proprieta_comuni:               # per ogni proprieta in comune, calcolo il numero di archi entranti
            if prop in G.nodes():                   # ed uscenti e li uso nella formula, insieme al rispettivo IDF
                num_in_edges = G.in_degree(prop)    # per calcolare il punteggio
                num_out_edges = G.out_degree(prop)
                score_prop[prop] = ((alfa * num_in_edges / len(item_piaciuti)) + (beta * num_out_edges / len(item_raccom))) * calcola_IDF(prop)

        sorted_values = sorted(score_prop.values())  # ordino la lista di punteggi in ordine decrescente in modo da
        sorted_values.reverse()                      # avere per prime le proprieta con più rilevanza
        sorted_prop = {}
        for i in sorted_values:
            for k in score_prop.keys():
                if score_prop[k] == i:
                    sorted_prop[k] = score_prop[k]
                    break
    else:
        for prop in proprieta_comuni:               # per ogni proprieta in comune, calcolo il numero di archi entranti
            if prop in G.nodes():                   # ed uscenti e li uso nella formula, insieme al rispettivo IDF
                num_in_edges = G.in_degree(prop)    # per calcolare il punteggio
                num_out_edges = G.out_degree(prop)
                score_prop[prop] = ((alfa * num_in_edges / len(item_piaciuti)) + (beta * num_out_edges / len(item_raccom))) * 1

        sorted_values = sorted(score_prop.values())  # ordino la lista di punteggi in ordine decrescente in modo da
        sorted_values.reverse()                      # avere per prime le proprieta con più rilevanza
        sorted_prop = {}
        for i in sorted_values:
            for k in score_prop.keys():
                sorted_prop[k] = i

    print("Le proprieta sono state rankate e ordinate con successo!\n")

    return sorted_prop


# Funzione che prende in input le proprieta rankate e ordinate per punteggio e il numero di proprieta da considerare
# per la spiegazione e ritorna solo quelle che devono essere considerate
def proprieta_da_considerare(prop_rankate, numero_prop_considerate):
    prop_considerate = {}
    for prop, score in prop_rankate.items():
        prop_considerate[prop] = score
        if len(prop_considerate) == numero_prop_considerate:
            break

    return prop_considerate


# Funzione che stampa in ordine di punteggio le proprieta
def stampa_proprieta(proprieta):
    print("\nEcco le proprieta in comune dei film in ordine decrescente per influenza:\n")
    for key, value in proprieta.items():
        print(value, "\t", key)
    print("\n")


# Funzione che prende in input il grafo creato, le proprieta rankate da considerare, i due dizionari dei film piaciuti
# e raccomandati e inizializza la struttura dati che sara data in input alla funzione che genera la spiegazione
# partendo da questi dati
def inizializzaNewPreGenArchitecture(G, score_IDF, profile, recommendation):
    NewPreGenArchitecture = []
    profile_prov = get_property_movies(profile)                       # prendo le proprieta dei film piaciuti
    recommendations_prov = get_property_movies(recommendation)        # prendo le proprieta dei film raccomandati
    profile = []
    recommendations = []
    for line in profile_prov:
        profile.append(line[0])

    for line in recommendations_prov:
        recommendations.append(line[0])

    for proprieta, score in score_IDF.items():                        # per ogni proprieta in comune considerata
        prop = proprieta
        opposite_nodes = estraiNodiOpposti_item_prop(G, prop)         # estraggo i nodi opposti alla proprieta (film)
        profile_nodes = []
        recomm_nodes = []
        for current in opposite_nodes:
            if current in profile and current not in profile_nodes:       # se il film piaciuto non e stato gia inserito
                profile_nodes.append(current)                                 # lo inserisco
            elif current in recommendations and current not in recomm_nodes:
                recomm_nodes.append(current)                                  # faccio lo stesso per i film raccomandati

        if len(profile_nodes) != 0 and len(recomm_nodes) != 0:     # aggiungo alla struttura dati creata gli item
            NewPreGenArchitecture.append(str(recomm_nodes) + "\t" + prop + "\t" + str(profile_nodes))

    return NewPreGenArchitecture


# Funzione che prende in input il grafo creato e una proprieta ed estrae i nodi opposti alla proprieta
def estraiNodiOpposti_item_prop(G, item):
    lista_item_prop = []
    map_prop = {}
    archi_item_user_prop_in = G.in_edges(item)                        # calcola archi entranti nella proprieta
    for archi_itemURI_user_prop_in in archi_item_user_prop_in:
        nodo_prop_in = archi_itemURI_user_prop_in[0]                  # prende il nodo opposto
        map_prop[nodo_prop_in] = ""

    archi_item_user_prop_out = G.out_edges(item)                      # calcola archi uscenti dalla proprieta
    for archi_itemURI_user_prop_out in archi_item_user_prop_out:
        nodo_prop_out = archi_itemURI_user_prop_out[1]                # prende il nodo opposto
        map_prop[nodo_prop_out] = ""

    for prop, n in map_prop.items():
        lista_item_prop.append(prop)

    return lista_item_prop


def cmd_ranker(profilo, racc, idf):
    if "[" not in sys.argv[2] or "]" not in sys.argv[2] or " " in sys.argv[2] or "[" not in sys.argv[3] or "]" not in sys.argv[3] or " " in sys.argv[3] or (sys.argv[4] != "True" and sys.argv[4] != "False"):
        print("\nI dati inseriti non sono corretti!\nAssicurarsi di aver inserito gli id tra parentesi quadre e senza lasciare spazi.")
        print("\nAssicurarsi di aver scelto True o False per il ranking con o senza IDF.")
    else:
        if idf == "True":
            idf = True
        elif idf == "False":
            idf = False
        profile, numero_film1 = mapping_profilo(profilo)
        recommendation, numero_film2 = mapping_profilo(racc)
        G, common_properties, numero_proprieta = costruisci_grafo(profile, recommendation)
        print("\nEsecuzione componente Ranker...\n")
        ranked_prop = ranking_proprieta(G, common_properties, profile, recommendation, idf)
        stampa_proprieta(ranked_prop)


if __name__ == "__main__":
    globals()[sys.argv[1]](sys.argv[2][1:-1].split(','), sys.argv[3][1:-1].split(','), sys.argv[4])
