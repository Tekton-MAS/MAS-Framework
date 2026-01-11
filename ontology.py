# =============================================================================
# [tietokoneohjelma] Holonic Enterprise MAS – TektonAI
# 
# Tekijä:          Toni Miettinen
# Oppilaitos:      Metropolia Ammattikorkeakoulu, Helsinki, Suomi
# Vuosi:           2026
# Versio:          1.0
# Lisenssi:        MIT License
# Saatavuus:       https://github.com/Tekton-MAS/Lotka-Volterra
# Viittaus:        Miettinen T. (2026). Moniagenttinen tekoälyarkkitehtuuri 
#                  pienyrityksen sähkö- ja automaatiojärjestelmien hallintaan.
#                  Insinöörityö, Metropolia AMK.
#
# Kuvaus: Ontologia holoniselle moniagenttijärjestelmälle (MAS). Tiedosto 
#         määrittelee holonit, resurssiholonit, tilaus­holonit sekä niiden
#         ominaisuuksia varten käytettävät relaatiot. Ontologia toimii
#         MAS-arkkitehtuurin semanttisen mallin perustana.
# =============================================================================

from owlready2 import get_ontology, Thing, ObjectProperty

# Luodaan virtuaalinen ontologia muistiin
onto = get_ontology("http://tekton.fi/holonic/2025#")

with onto:
    class Holon(Thing): pass
    class ResourceHolon(Holon): pass
    class OrderHolon(Holon): pass

    class hasCapability(ObjectProperty):
        domain = [ResourceHolon]
        range = [str]

CAPABILITIES = ["Milling", "Turning", "Drilling", "Grinding"]