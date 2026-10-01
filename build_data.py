# -*- coding: utf-8 -*-
"""
Script to download royalty-free mushroom images from Wikimedia Commons,
optimize them locally, and generate mushrooms.js for MemoChampi.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image
import io

HEADERS = {
    'User-Agent': 'MemoChampiQuiz/1.0 (https://github.com/chouteau/memochampi; contact@chouteau.fr)'
}

MUSHROOM_DEFINITIONS = [
    {
        "id": "cepe_de_bordeaux",
        "wiki_title": "Boletus_edulis",
        "name": "Cèpe de Bordeaux",
        "latin": "Boletus edulis",
        "family": "Boletaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Roi des champignons des bois, très recherché.",
        "habitat": "Forêts de feuillus (chênes, hêtres, châtaigniers) et de conifères (épicéas, pins).",
        "season": "Fin de l'été à fin de l'automne (août à novembre).",
        "cap": "Brun chamois à noisette, gras au toucher, marge souvent plus claire bordée d'un liseré blanc.",
        "underside": "Tubes blancs dans la jeunesse, devenant jaune verdâtre puis vert olive à maturité.",
        "stem": "Pied robuste, ventru puis cylindrique, orné d'un fin réseau de veines blanches dans sa partie supérieure.",
        "confusion": "Bolet de fiel (Tylopilus felleus, très amer), Bolet de Satan (Rubroboletus satanas, toxique).",
        "funFact": "Son nom vient du gascon 'cep' qui signifie 'tronc de vigne' en raison de son pied charnu."
    },
    {
        "id": "cepe_tete_de_negre",
        "wiki_title": "Boletus_aereus",
        "name": "Cèpe tête-de-nègre",
        "latin": "Boletus aereus",
        "family": "Boletaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Considéré comme l'un des plus savoureux des cèpes.",
        "habitat": "Bois chauds de feuillus, surtout sous chênes et châtaigniers.",
        "season": "Début de l'été à fin de l'automne (juin à novembre, thermophile).",
        "cap": "Chapeau très sombre, brun bistre à presque noir, surface feutrée.",
        "underside": "Tubes blancs serrés puis jaune-verdâtre avec l'âge.",
        "stem": "Pied brun cannelle ou ocre avec réseau fin, chair blanche très ferme.",
        "confusion": "Autres cèpes comestibles (Cèpe de Bordeaux, Cèpe d'été).",
        "funFact": "On le surnomme aussi Bolet bronzé. Il préfère le soleil et les climats méditerranéens ou tempérés chauds."
    },
    {
        "id": "cepe_d_ete",
        "wiki_title": "Boletus_reticulatus",
        "name": "Cèpe d'été (Bolet réticulé)",
        "latin": "Boletus reticulatus",
        "family": "Boletaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Chair parfumée et douce, pousse tôt en saison.",
        "habitat": "Forêts thermophiles de feuillus (chênes, hêtres, châtaigniers).",
        "season": "Mai à octobre (dès les premières chaleurs printanières).",
        "cap": "Brun clair à café au lait, cuticule mate et veloutée pouvant se craqueler en période sèche.",
        "underside": "Tubes blancs puis vert olive.",
        "stem": "Pied ocre clair entièrement couvert d'un réseau blanchâtre en relief très marqué.",
        "confusion": "Bolet de fiel (Tylopilus felleus, tubes rosâtres et réseau sombre).",
        "funFact": "Il fait son apparition dès les beaux jours de mai/juin après les orages d'été."
    },
    {
        "id": "bolet_bai",
        "wiki_title": "Imleria_badia",
        "name": "Bolet bai",
        "latin": "Imleria badia",
        "family": "Boletaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Excellente alternative au cèpe.",
        "habitat": "Bois de conifères (pins, épicéas) et parfois de feuillus, sols acides.",
        "season": "Août à novembre.",
        "cap": "Brun bai à marron brillant, cuticule un peu visqueuse par temps humide.",
        "underside": "Pores jaunâtres qui bleuissent rapidement à la pression des doigts.",
        "stem": "Pied cylindrique brun clair, sans réseau marqué.",
        "confusion": "Bolet à pied rouge (comestible bien cuit), Bolet de fiel.",
        "funFact": "Sa chair bleuit légèrement à la coupe puis blanchit à nouveau. Il a une odeur fruitée agréable."
    },
    {
        "id": "girolle",
        "wiki_title": "Cantharellus_cibarius",
        "name": "Girolle (Chanterelle commune)",
        "latin": "Cantharellus cibarius",
        "family": "Cantharellaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "L'un des champignons les plus célèbres et les plus recherchés en gastronomie.",
        "habitat": "Sous feuillus et conifères, sur sols moussus et aérés.",
        "season": "Mai à novembre, particulièrement après les pluies d'été.",
        "cap": "Jaune d'or à jaune orangé, en entonnoir aux bords ondulés.",
        "underside": "Plis fourchus et décurrents (ce ne sont pas des lames vraies !).",
        "stem": "Pied jaune plein, continu avec le chapeau.",
        "confusion": "Fausse-girolle (Hygrophoropsis aurantiaca, comestible médiocre), Clitocybe de l'olivier (Omphalotus olearius, TOXIQUE).",
        "funFact": "La girolle dégage une délicieuse odeur caractéristique d'abricot ou de mirabelle et n'est presque jamais véreuse."
    },
    {
        "id": "trompette_de_la_mort",
        "wiki_title": "Craterellus_cornucopioides",
        "name": "Trompette de la mort (Cratèrelle)",
        "latin": "Craterellus cornucopioides",
        "family": "Cantharellaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Parfum intense, se prête admirablement au séchage.",
        "habitat": "Forêts denses de hêtres, chênes et noisetiers, sur sols calcaires ou argileux.",
        "season": "Automne (septembre à décembre, souvent vers la Toussaint).",
        "cap": "En entonnoir évasé, creux jusqu'à la base, noir fuligineux à gris cendré.",
        "underside": "Hyménium lisse ou légèrement ridé, sans vraies lames ni plis profonds.",
        "stem": "Pied creux prolongeant naturellement l'entonnoir.",
        "confusion": "Chanterelle cendrée (Craterellus cinereus, également comestible).",
        "funFact": "Malgré son nom lugubre lié à sa couleur noire et sa poussée à la Toussaint, elle est délicieuse et inoffensive !"
    },
    {
        "id": "chanterelle_en_tube",
        "wiki_title": "Craterellus_tubaeformis",
        "name": "Chanterelle en tube",
        "latin": "Craterellus tubaeformis",
        "family": "Cantharellaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Pousse en troupes souvent très abondantes en fin de saison.",
        "habitat": "Forêts humides de conifères et de feuillus, au milieu de la mousse.",
        "season": "Automne tardif jusqu'aux premières gelées (octobre à janvier).",
        "cap": "Brun jaune à grisâtre, ombiliqué et percé au centre.",
        "underside": "Plis jaunâtres ou gris-jaune, fourchus et décurrents.",
        "stem": "Pied jaune vif à orangé, creux et aplati avec sillon.",
        "confusion": "Chanterelle jaunissante (Craterellus lutescens, également délicieuse).",
        "funFact": "Elle résiste bien aux petits frimas d'automne et permet de belles récoltes tardives."
    },
    {
        "id": "morille_commune",
        "wiki_title": "Morchella_esculenta",
        "name": "Morille commune (ronde)",
        "latin": "Morchella esculenta",
        "family": "Morchellaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible (bien cuit)",
        "warning": "⚠️ TOXIQUE CRUE : Contient des hémolysines, doit être impérativement cuite au moins 20 minutes ou séchée !",
        "habitat": "Terrains calcaires, frênaies, sous ormes, vergers abandonnés, lisières.",
        "season": "Printemps (mars à mai).",
        "cap": "Alvéolé comme une éponge, rond à ovoïde, blond à brun ocre.",
        "underside": "Alvéoles profondes et sinueuses tapissant le chapeau.",
        "stem": "Pied creux blanchâtre à jaunâtre, entièrement continu avec le chapeau.",
        "confusion": "Gyromitre fausse-morille (Gyromitra esculenta, MORTEL ! Chapeau cérébriforme en circonvolutions de cerveau).",
        "funFact": "C'est l'un des premiers champignons nobles à apparaître au sortir de l'hiver."
    },
    {
        "id": "morille_conique",
        "wiki_title": "Morchella_elata",
        "name": "Morille conique",
        "latin": "Morchella elata",
        "family": "Morchellaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible (bien cuit)",
        "warning": "⚠️ TOXIQUE CRUE : Cuisson prolongée ou dessiccation indispensable.",
        "habitat": "Forêts de montagne, épicéas, sapins, et zones de brûlis récentes.",
        "season": "Printemps (mars à juin selon l'altitude).",
        "cap": "Conique et pointu, alvéoles allongées disposées en rangées longitudinales régulières, brun sombre à noirâtre.",
        "underside": "Intérieur entièrement creux d'un seul tenant.",
        "stem": "Pied blanc crème, creux, granuleux.",
        "confusion": "Morillon (Mitrophora semilibera), Verpe de Bohême, Gyromitre (MORTEL).",
        "funFact": "Elle apprécie particulièrement les résineux montagnards et les paillages d'écorces récents."
    },
    {
        "id": "coulemelle",
        "wiki_title": "Macrolepiota_procera",
        "name": "Coulemelle (Lépiote élevée)",
        "latin": "Macrolepiota procera",
        "family": "Agaricaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Seul le chapeau se consomme (le pied est trop fibreux). Attention : ne jamais ramasser de petites lépiotes (< 10 cm) !",
        "habitat": "Clairières, prés, lisières de bois, bordures de chemins ensoleillés.",
        "season": "Juillet à novembre.",
        "cap": "Immense parasol (jusqu'à 30-40 cm), beige garni d'écailles concentriques brunes.",
        "underside": "Lames blanches très serrées, libres.",
        "stem": "Très haut pied chiné comme une peau de serpent, muni d'un anneau épais double et coulissant.",
        "confusion": "Petites lépiotes mortelles (Lepiota helveola, Lepiota brunneoincarnata) : ne ramasser que les spécimens de plus de 15 cm !",
        "funFact": "On l'appelle aussi 'nez de chat' au stade jeune (bouton de culotte) ou 'parasol' en anglais."
    },
    {
        "id": "pied_de_mouton",
        "wiki_title": "Hydnum_repandum",
        "name": "Pied-de-mouton",
        "latin": "Hydnum repandum",
        "family": "Hydnaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Retirer les aiguillons des vieux spécimens pour atténuer une légère amertume.",
        "habitat": "Sous feuillus et conifères, formant souvent des 'ronds de sorcières'.",
        "season": "Août à décembre (résiste bien aux premières gelées).",
        "cap": "Blanc crème à chamois orangé pâle, bosselé et charnu.",
        "underside": "Aiguillons mous et fragiles (pas de lamelles ni de pores !), facilement détachables.",
        "stem": "Pied épais, excentré, blanc crème.",
        "confusion": "Hydne roussissant (Hydnum rufescens, plus petit et orangé, également bon).",
        "funFact": "C'est l'un des champignons les plus faciles à reconnaître grâce à ses petits aiguillons sous le chapeau."
    },
    {
        "id": "oronge",
        "wiki_title": "Amanita_caesarea",
        "name": "Oronge (Amanite des Césars)",
        "latin": "Amanita caesarea",
        "family": "Amanitaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "L'un des plus illustres champignons de l'Antiquité romaine. Attention aux confusions !",
        "habitat": "Bois de chênes et châtaigniers du Midi et des régions chaudes tempérées.",
        "season": "Août à novembre (espèce thermophile méditerranéenne).",
        "cap": "Orange vif à rouge flamboyant, lisse et brillant, marge striée.",
        "underside": "Lames jaune d'or éclatant (caractère distinctif crucial face aux autres amanites !).",
        "stem": "Pied jaune d'or avec anneau jaune en jupe et grande volve blanche en sac à la base.",
        "confusion": "Amanite tue-mouches (Amanita muscaria, TOXIQUE : lames blanches et volve floconneuse, chapeau à verrues blanches).",
        "funFact": "Les empereurs romains en étaient si friands qu'ils la réservaient à leur table sous le nom de 'Cibus deorum' (nourriture des dieux)."
    },
    {
        "id": "amanite_rougissante",
        "wiki_title": "Amanita_rubescens",
        "name": "Amanite rougissante (Golmotte)",
        "latin": "Amanita rubescens",
        "family": "Amanitaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Bon comestible (bien cuit)",
        "warning": "⚠️ TOXIQUE CRUE : Contient des hémolysines thermolabiles détruites par une cuisson complète à cœur (70°C).",
        "habitat": "Très commune dans tous types de forêts (feuillus et résineux).",
        "season": "Mai à novembre.",
        "cap": "Brun rosé à ocre rougeâtre, parsemé de plaques floconneuses grisâtres.",
        "underside": "Lames blanches se tachant de rouge vineux aux blessures.",
        "stem": "Pied bulbeux rougissant avec anneau pendant strié sur le dessus.",
        "confusion": "Amanite panthère (Amanita pantherina, TRÈS TOXIQUE : chair immuable restant blanche, volve circoncise nette).",
        "funFact": "Sa chair rougit lentement à la cassure ou aux morsures de limaces, ce qui permet de la distinguer à coup sûr."
    },
    {
        "id": "lactaire_delicieux",
        "wiki_title": "Lactarius_deliciosus",
        "name": "Lactaire délicieux",
        "latin": "Lactarius deliciosus",
        "family": "Russulaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Bon comestible",
        "warning": "Recherché en cuisine provençale et espagnole (poêlé à l'ail et persil).",
        "habitat": "Exclusivement sous les pins, sur sols sablonneux ou calcaires.",
        "season": "Août à novembre.",
        "cap": "Orangé avec zones concentriques plus foncées, verdissant avec l'âge.",
        "underside": "Lames serrées orange carotte, exsudant un lait orange vif à la blessure.",
        "stem": "Pied court et trapu, orange orné de petites fossettes (scrobicules).",
        "confusion": "Lactaire sanguin (Lactarius sanguifluus, excellent), Lactaire à toison (Lactarius torminosus, toxique à lait blanc).",
        "funFact": "Son lait orange vif est immuable à l'air libre et colore l'urine en rouge sans aucun danger."
    },
    {
        "id": "lactaire_sanguin",
        "wiki_title": "Lactarius_sanguifluus",
        "name": "Lactaire sanguin",
        "latin": "Lactarius sanguifluus",
        "family": "Russulaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Très prisé en Catalogne sous le nom de 'rovelló'.",
        "habitat": "Pins et garrigues méditerranéennes sur terrain calcaire.",
        "season": "Septembre à décembre.",
        "cap": "Ocre orangé terne avec reflets purpurins ou verdâtres.",
        "underside": "Lames pourpre violacé, exsudant un lait couleur sang de bœuf ou lie-de-vin.",
        "stem": "Pied creux teinté de pourpre vineux.",
        "confusion": "Lactaire délicieux (lait carotte), Lactaires toxiques à lait blanc.",
        "funFact": "Son latex rouge sang sombre est unique parmi les lactaires et confère une saveur remarquable."
    },
    {
        "id": "russule_charbonniere",
        "wiki_title": "Russula_cyanoxantha",
        "name": "Russule charbonnière",
        "latin": "Russula cyanoxantha",
        "family": "Russulaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Remarquable par ses lames flexibles comme du lard (lames 'lardacées').",
        "habitat": "Bois de feuillus (hêtres, chênes) et mixtes.",
        "season": "Juin à novembre.",
        "cap": "Mélange subtil de violet, ardoise, pourpre et vert olive.",
        "underside": "Lames blanches très souples et grasses au toucher, ne cassant pas sous le doigt.",
        "stem": "Pied blanc et cassant comme de la craie, typique du genre Russule.",
        "confusion": "Autres russules (Russule émétique à goût piquant très brûlant), Amanite phalloïde (qui a un anneau et une volve !).",
        "funFact": "Elle se reconnaît au 'test du pouce' : frottez ses lames, elles ploient sans se rompre contrairement aux autres russules !"
    },
    {
        "id": "russule_verdoyante",
        "wiki_title": "Russula_virescens",
        "name": "Russule verdoyante (Palomet)",
        "latin": "Russula virescens",
        "family": "Russulaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "L'une des meilleures russules au goût délicat de noisette.",
        "habitat": "Forêts claires de feuillus (chênes, hêtres, châtaigniers).",
        "season": "Juin à octobre.",
        "cap": "Vert-de-gris à vert olive, cuticule sèche craquelée en multiples îlots ou croûtes polygonales.",
        "underside": "Lames blanches à crème, fragiles et cassantes.",
        "stem": "Pied blanc pur, ferme puis friable.",
        "confusion": "Amanite phalloïde (MORTELLE : chapeau lisse, anneau, volve, lames libres) !",
        "funFact": "Sa surface ressemble à de la faïence émaillée craquelée. Les connaisseurs la dégustent même crue."
    },
    {
        "id": "pleurote_en_huitre",
        "wiki_title": "Pleurotus_ostreatus",
        "name": "Pleurote en huître",
        "latin": "Pleurotus ostreatus",
        "family": "Pleurotaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Bon comestible",
        "warning": "Pousse en touffes étagées sur le bois mort ou affaibli.",
        "habitat": "Troncs d'arbres feuillus (peupliers, hêtres, saules, chênes).",
        "season": "Automne et hiver (d'octobre à mars, résiste au froid).",
        "cap": "Gris ardoise à brun bleuté en forme de coquille d'huître ou d'éventail.",
        "underside": "Lames blanchâtres décurrentes le long du pied.",
        "stem": "Pied court et excentré, latéral, souvent soudé aux autres.",
        "confusion": "Pleurote de l'olivier (Omphalotus olearius, toxique qui brille dans le noir).",
        "funFact": "C'est un champignon carnivore : son mycélium est capable de paralyser et digérer des nématodes (petits vers) pour puiser de l'azote !"
    },
    {
        "id": "agaric_champetre",
        "wiki_title": "Agaricus_campestris",
        "name": "Rosé des prés (Agaric champêtre)",
        "latin": "Agaricus campestris",
        "family": "Agaricaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Bon comestible",
        "warning": "Ne jamais cueillir un agaric dont la base jaunit immédiatement à la rayure !",
        "habitat": "Pâtures, pelouses, prairies amendées par les chevaux et vaches.",
        "season": "Mai à novembre après les pluies.",
        "cap": "Blanc à beige clair soyeux, hémisphérique puis étalé.",
        "underside": "Lames d'abord rose vif puis brun chocolat à maturité (JAMAIS blanches à maturité !).",
        "stem": "Pied blanc avec un petit anneau fugace, sans volve.",
        "confusion": "Amanites blanches mortelles (Amanita verna, virosa : lames TOUJOURS blanches et présence d'une volve sac), Agaric jaunissant (toxique).",
        "funFact": "C'est l'ancêtre sauvage du célèbre 'champignon de Paris' de nos étals."
    },
    {
        "id": "coprin_chevelu",
        "wiki_title": "Coprinus_comatus",
        "name": "Coprin chevelu",
        "latin": "Coprinus comatus",
        "family": "Agaricaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible (jeune)",
        "warning": "À cuisiner dans les quelques heures suivant la cueillette avant qu'il ne se déliquesce !",
        "habitat": "Pelouses, jardins, décombres, prairies fraîches et chemins.",
        "season": "Avril à novembre.",
        "cap": "Cylindrique blanc en forme de fuseau, couvert de mèches blanches écailleuses évoquant une perruque.",
        "underside": "Lames blanches puis rosées, virant au noir d'encre en liquéfaction.",
        "stem": "Pied blanc élancé, creux, muni d'un anneau mobile étroit.",
        "confusion": "Coprin noir d'encre (Coprinopsis atramentaria, toxique avec de l'alcool).",
        "funFact": "Ce champignon pratique l'autodissolution (déliquescence) : son chapeau fond en un liquide noir semblable à de l'encre de Chine pour disséminer ses spores."
    },
    {
        "id": "pied_bleu",
        "wiki_title": "Lepista_nuda",
        "name": "Pied-bleu",
        "latin": "Lepista nuda",
        "family": "Tricholomataceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Bon comestible (cuit)",
        "warning": "Parfum anisé très caractéristique, doit être bien cuit.",
        "habitat": "Litière d'aiguilles ou de feuilles mortes, sous-bois d'automne.",
        "season": "Automne tardif jusqu'aux gelées (octobre à décembre).",
        "cap": "Violet lilas à brun violacé avec l'âge, charnu et lisse.",
        "underside": "Lames d'un violet bleuâtre vif, serrées.",
        "stem": "Pied robuste, fibreux, violet bleu poudré de blanc.",
        "confusion": "Cortinaires violets (Cortinarius violaceus ou purpurascens, qui possèdent une cortine rouille).",
        "funFact": "Sa couleur violette spectaculaire surprend souvent les néophytes, mais il est un classique des tables d'automne."
    },
    {
        "id": "clitopile_petite_prune",
        "wiki_title": "Clitopilus_prunulus",
        "name": "Meunier (Clitopile petite prune)",
        "latin": "Clitopilus prunulus",
        "family": "Entolomataceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "⚠️ CONFUSION GRAVE POSSIBLE : Odeur de farine fraîche obligatoire ! Confusions possibles avec clitocybes blancs mortels.",
        "habitat": "Bois de feuillus et de conifères, talus moussus.",
        "season": "Juillet à novembre.",
        "cap": "Blanc crayeux à gris perle, mat, soyeux et fragile.",
        "underside": "Lames décurrentes blanches puis teintées de rose saumon à maturité.",
        "stem": "Pied blanc court, chair friable.",
        "confusion": "Clitocybes blancs mortels (Clitocybe dealbata, rivulosa : odeur différente, lames immuables blanches).",
        "funFact": "Son surnom de 'meunier' vient de sa puissante odeur de farine fraîche et de pâte à pain. On dit que là où il pousse, le cèpe n'est pas loin !"
    },
    {
        "id": "sparassis_crepu",
        "wiki_title": "Sparassis_crispa",
        "name": "Sparassis crépu (Morille des pins)",
        "latin": "Sparassis crispa",
        "family": "Sparassidaceae",
        "category": "edible_choice",
        "edibility": "excellent",
        "edibilityLabel": "🍴 Excellent comestible",
        "warning": "Bien nettoyer les anfractuosités pour enlever aiguilles et sable.",
        "habitat": "Au pied des vieux pins sylvestres et maritimes.",
        "season": "Septembre à novembre.",
        "cap": "Gros buisson circulaire évoquant une éponge de bain ou un chou-fleur, branches ondulées lobées.",
        "underside": "Pas de lames : hyménium recouvrant les lobes crépus.",
        "stem": "Tronc central épais et profondément enraciné.",
        "confusion": "Inconfondable une fois adulte, ressemble à un chou-fleur doré.",
        "funFact": "Il peut atteindre plusieurs kilos à lui seul et dégage une agréable odeur de noisette et d'amande douce."
    },
    {
        "id": "vesse_de_loup_geante",
        "wiki_title": "Calvatia_gigantea",
        "name": "Vesse-de-loup géante",
        "latin": "Calvatia gigantea",
        "family": "Agaricaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Comestible jeune",
        "warning": "Consommer uniquement lorsque la chair intérieure (gléba) est blanc immaculé.",
        "habitat": "Prairies, pâturages, vergers, parcs et bordures de haies.",
        "season": "Août à novembre.",
        "cap": "Gigantesque boule blanche sphérique pouvant dépasser 50 cm de diamètre et 10 kg !",
        "underside": "Aucune lame : sac clos qui brunit et libère une fumée de spores mûres.",
        "stem": "Dépourvu de pied distinct, fixé au sol par des filaments mycéliens.",
        "confusion": "Jeunes amanites en œuf (mais bien plus petites et montrant une silhouette de champignon à la coupe).",
        "funFact": "Elle peut produire jusqu'à 7 000 milliards de spores à maturité !"
    },
    {
        "id": "polypore_soufre",
        "wiki_title": "Laetiporus_sulphureus",
        "name": "Polypore soufré",
        "latin": "Laetiporus sulphureus",
        "family": "Fomitopsidaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Comestible jeune",
        "warning": "Consommer uniquement les bords tendres des jeunes spécimens. Éviter ceux croissant sur robiniers ou ifs.",
        "habitat": "Parasite sur troncs d'arbres vivants ou morts (chênes, châtaigniers, saules).",
        "season": "Mai à octobre.",
        "cap": "Étagères ondulées jaune soufre éclatant à orange saumoné vif.",
        "underside": "Pores minuscules jaune vif citron.",
        "stem": "Sessile (sans pied distinct).",
        "confusion": "Difficile à confondre avec sa couleur jaune soufre fluorée.",
        "funFact": "Les Anglo-Saxons le nomment 'Chicken of the woods' (poulet des bois) car sa chair cuite a la texture et le goût du blanc de poulet !"
    },
    {
        "id": "langue_de_boeuf",
        "wiki_title": "Fistulina_hepatica",
        "name": "Langue de bœuf (Fistuline hépatique)",
        "latin": "Fistulina_hepatica",
        "family": "Fistulinaceae",
        "category": "edible",
        "edibility": "comestible",
        "edibilityLabel": "🍽️ Comestible",
        "warning": "Goût acidulé caractéristique, riche en vitamine C.",
        "habitat": "Troncs de vieux chênes et châtaigniers blessés.",
        "season": "Août à novembre.",
        "cap": "Épais, en forme de demi-lune rouge sang à brun rougeâtre, texture gélatineuse.",
        "underside": "Tubes séparés les uns des autres, jaunâtres à rosâtres.",
        "stem": "Pied court et latéral.",
        "confusion": "Impossible à confondre en raison de son allure de morceau de viande crue.",
        "funFact": "Lorsqu'on la coupe, elle suinte un liquide rouge semblable à du sang et sa chair marbrée imite à la perfection un steak de bœuf !"
    },
    {
        "id": "amanite_phalloide",
        "wiki_title": "Amanita_phalloides",
        "name": "Amanite phalloïde",
        "latin": "Amanita phalloides",
        "family": "Amanitaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL (Le plus dangereux d'Europe)",
        "warning": "Responsable de 90% des intoxications mortelles par les champignons ! Un seul chapeau suffit pour tuer un adulte.",
        "habitat": "Forêts de feuillus (chênes, hêtres, noisetiers) et parcs.",
        "season": "Juillet à novembre.",
        "cap": "Vert olive à jaune verdâtre, soyeux, avec de fines fibrilles radiales innées.",
        "underside": "Lames blanches libres, immuables.",
        "stem": "Pied blanc chiné de zébrures verdâtres, portant un anneau blanc en jupe et une volve blanche membraneuse en sac à la base.",
        "confusion": "Russule verdoyante, Rosé des prés, Tricholome équestre.",
        "funFact": "Ses toxines (amatoxines) détruisent irrémédiablement le foie après une période de latence trompeuse de 6 à 24 heures."
    },
    {
        "id": "amanite_tue_mouches",
        "wiki_title": "Amanite_tue-mouches",
        "name": "Amanite tue-mouches",
        "latin": "Amanita muscaria",
        "family": "Amanitaceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TOXIQUE & Hallucinogène",
        "warning": "Provoque le syndrome panthérinien (délires, convulsions, troubles gastro-intestinaux).",
        "habitat": "Sous bouleaux, épicéas et pins, sur sols acides.",
        "season": "Juillet à décembre.",
        "cap": "Rouge écarlate vif, ponctué de flocons blancs pyramidaux (restes du voile général).",
        "underside": "Lames blanches pures, serrées.",
        "stem": "Pied blanc bulbeux avec anneau membraneux blanc et bourrelets concentriques à la base.",
        "confusion": "Oronge (Amanita caesarea, qui a un chapeau orange sans verrues et des lames JAUNES).",
        "funFact": "C'est l'archétype du champignon des contes de fées et du jeu vidéo Mario, autrefois utilisé mélangé à du lait pour tuer les mouches."
    },
    {
        "id": "amanite_panthere",
        "wiki_title": "Amanita_pantherina",
        "name": "Amanite panthère",
        "latin": "Amanita pantherina",
        "family": "Amanitaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ TRÈS TOXIQUE / Potentiellement mortel",
        "warning": "Plus toxique encore que l'Amanite tue-mouches, risque vital élevé.",
        "habitat": "Forêts de feuillus et de conifères.",
        "season": "Juillet à novembre.",
        "cap": "Brun noisette à brun bistre, constellé de nombreuses verrues blanc pur floconneuses, bord strié.",
        "underside": "Lames blanches libres.",
        "stem": "Pied blanc élancé, anneau bas et volve circoncise formant des bourrelets superposés au-dessus d'un bulbe arrondi.",
        "confusion": "Amanite rougissante (Golmotte, dont la chair rougit) et Amanite épaisse.",
        "funFact": "Sa chair reste désespérément blanche et immuable à la cassure, contrairement à la golmotte."
    },
    {
        "id": "amanite_printaniere",
        "wiki_title": "Amanita_verna",
        "name": "Amanite printanière",
        "latin": "Amanita verna",
        "family": "Amanitaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL",
        "warning": "Même toxicité fatale que l'Amanite phalloïde (syndrome phalloïdien).",
        "habitat": "Forêts chaudes de chênes et châtaigniers, surtout dans le Sud.",
        "season": "Printemps à début de l'automne (mai à octobre).",
        "cap": "Blanc immaculé, satiné et lisse.",
        "underside": "Lames blanches libres.",
        "stem": "Pied blanc avec anneau membraneux et volve en sac.",
        "confusion": "Rosé des prés (dont les lames sont roses puis brunes, jamais blanches) !",
        "funFact": "Sa blancheur immaculée trompe souvent les cueilleurs imprudents qui croient ramasser un champignon de Paris."
    },
    {
        "id": "amanite_virose",
        "wiki_title": "Amanita_virosa",
        "name": "Amanite virose",
        "latin": "Amanita virosa",
        "family": "Amanitaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL",
        "warning": "L'ange destructeur des forêts d'altitude, toxicité foudroyante.",
        "habitat": "Forêts humides d'épicéas et de hêtres, en montagne.",
        "season": "Août à novembre.",
        "cap": "Blanc pur, souvent asymétrique et déjeté d'un côté.",
        "underside": "Lames blanches.",
        "stem": "Pied blanc floconneux pelucheux, anneau fugace déchiqueté, volve en sac engainante.",
        "confusion": "Champignons blancs comestibles.",
        "funFact": "On la surnomme 'l'ange de la mort' en raison de son élégance funèbre."
    },
    {
        "id": "bolet_de_satan",
        "wiki_title": "Rubroboletus_satanas",
        "name": "Bolet de Satan",
        "latin": "Rubroboletus satanas",
        "family": "Boletaceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TOXIQUE (Violent purgatif)",
        "warning": "Provoque de violents malaises gastro-intestinaux et des vomissements continus.",
        "habitat": "Bois aérés de feuillus (chênes, hêtres) sur sols strictement calcaires.",
        "season": "Juin à octobre (espèce thermophile estivale).",
        "cap": "Gros chapeau blanc mastic à grisâtre crayeux, très pâle.",
        "underside": "Pores rouge sang à rouge carmin, jaunissant vers la marge.",
        "stem": "Pied énorme, obèse, rouge sang sur fond jaune avec réseau rouge.",
        "confusion": "Bolet à pied rouge (Neoboletus luridiformis, chapeau brun foncé et comestible bien cuit).",
        "funFact": "Sa chair blanchâtre bleuit modérément à la coupe et dégage une odeur nauséabonde d'eau croupie avec l'âge."
    },
    {
        "id": "cortinaire_couleur_de_rocou",
        "wiki_title": "Cortinarius_orellanus",
        "name": "Cortinaire couleur de rocou",
        "latin": "Cortinarius orellanus",
        "family": "Cortinariaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL (Syndrome orellanien)",
        "warning": "Délai de latence traître de 3 à 17 jours avant la destruction définitive des reins !",
        "habitat": "Forêts de feuillus (chênes, châtaigniers) sur sols acides.",
        "season": "Août à novembre.",
        "cap": "Brun-rouge cannelle à rouille orangé, feutré ou finement écailleux.",
        "underside": "Lames espacées, ocre cannelle à rouille sombre.",
        "stem": "Pied fusiforme jaune d'or à ocre rouille sans anneau mais avec cortine fugace.",
        "confusion": "Chanterelles ou autres cortinaires.",
        "funFact": "L'orellanine qu'il contient provoque une insuffisance rénale aiguë souvent irréversible nécessitant dialyse ou greffe."
    },
    {
        "id": "gyromitre",
        "wiki_title": "Gyromitra_esculenta",
        "name": "Gyromitre (Fausse morille)",
        "latin": "Gyromitra esculenta",
        "family": "Discinaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL (Syndrome gyromitrien)",
        "warning": "Vente strictement interdite en France. Contient de la gyromitrine, décomposée dans le corps en monométhylhydrazine (carburant de fusée) !",
        "habitat": "Bois de conifères (pins, épicéas) sur sol sableux, en montagne.",
        "season": "Printemps (mars à mai).",
        "cap": "Chapeau cérébriforme brun rougeâtre évoquant les circonvolutions d'un cerveau.",
        "underside": "Intérieur lobé et creux avec de multiples replis.",
        "stem": "Pied court, blanc crème, sillonné.",
        "confusion": "Vraies morilles (dont le chapeau est creux et alvéolé façon nid d'abeille, JAMAIS cérébriforme) !",
        "funFact": "Autrefois consommé dans certains pays du Nord, il a causé d'innombrables décès par accumulation de toxines hémolytiques et hépatotoxiques."
    },
    {
        "id": "galere_marginee",
        "wiki_title": "Galerina_marginata",
        "name": "Galère marginée",
        "latin": "Galerina marginata",
        "family": "Hymenogastraceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL",
        "warning": "Contient les mêmes amatoxines mortelles que l'Amanite phalloïde !",
        "habitat": "Pousse en petites troupes sur le bois pourrissant de conifères ou de feuillus.",
        "season": "Août à novembre.",
        "cap": "Brun ocre à jaune miel, strié par transparence au bord.",
        "underside": "Lames ocre brunâtre serrées.",
        "stem": "Pied brun sombre vers le bas, orné d'un petit anneau membraneux fugace.",
        "confusion": "Pholiote changeante (Kuehneromyces mutabilis, comestible croissant en touffes sur bois).",
        "funFact": "Sa petite taille la fait souvent sous-estimer, mais elle détruit le foie exactement comme l'amanite phalloïde."
    },
    {
        "id": "inocybe_de_patouillard",
        "wiki_title": "Inocybe_erubescens",
        "name": "Inocybe de Patouillard",
        "latin": "Inosperma erubescens",
        "family": "Inocybaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL (Syndrome muscarinien majeur)",
        "warning": "Concentration colossale de muscarine, supérieure à celle de l'amanite tue-mouches.",
        "habitat": "Parcs, lisières calcaires et bois de feuillus (hêtres, tilleuls).",
        "season": "Mai à juillet (champignon printanier et estival).",
        "cap": "Conique-campanulé avec mamelon pointu, blanc crème devenant rouge brique aux froissements.",
        "underside": "Lames blanchâtres puis brun olive tachées de rouge.",
        "stem": "Pied blanc rougissant à la manipulation.",
        "confusion": "Tricholome de la Saint-Georges (Calocybe gambosa, excellent comestible du printemps qui sent la farine et ne rougit jamais).",
        "funFact": "Il rougit vivement au toucher, signal d'alarme naturel à ne jamais ignorer !"
    },
    {
        "id": "paxille_enroule",
        "wiki_title": "Paxillus_involutus",
        "name": "Paxille enroulé",
        "latin": "Paxillus involutus",
        "family": "Paxillaceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL à long terme (Syndrome paxillien)",
        "warning": "Responsable d'une immuno-hémolyse fatale par consommation répétée.",
        "habitat": "Bois de feuillus et de résineux, jardins, parcs, très commun.",
        "season": "Juillet à novembre.",
        "cap": "Brun ocre à rouille, velouté, à marge fortement enroulée.",
        "underside": "Lames ocre brunissant fortement au toucher, facilement séparables de la chair.",
        "stem": "Pied court et épais concolore au chapeau.",
        "confusion": "Lactaires (mais ne coule aucun lait) ou bolets.",
        "funFact": "Longtemps considéré à tort comme comestible cuit, il déclenche après plusieurs repas une réaction allergique foudroyante qui détruit les globules rouges."
    },
    {
        "id": "entolome_livide",
        "wiki_title": "Entoloma_sinuatum",
        "name": "Entolome livide",
        "latin": "Entoloma sinuatum",
        "family": "Entolomataceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TRÈS TOXIQUE (Syndrome résinoïdien sévère)",
        "warning": "L'un des champignons les plus perfides causant des intoxications massives chaque automne.",
        "habitat": "Forêts de feuillus (chênes, hêtres) sur sol calcaire ou argileux.",
        "season": "Août à novembre.",
        "cap": "Gris plomb à ocre beige clair, soyeux et charnu.",
        "underside": "Lames d'abord jaune beurre puis rose saumoné avec l'âge.",
        "stem": "Pied robuste, blanc poudré en haut.",
        "confusion": "Meunier (Clitopilus prunulus), Clitocybe nébuleux, Tricholome de la Saint-Georges.",
        "funFact": "Il exhale une agréable odeur trompeuse de farine fraîche qui incite l'imprudent à la consommation."
    },
    {
        "id": "clitocybe_blanchi",
        "wiki_title": "Clitocybe_rivulosa",
        "name": "Clitocybe blanc / blanchi",
        "latin": "Clitocybe rivulosa",
        "family": "Tricholomataceae",
        "category": "deadly",
        "edibility": "mortel",
        "edibilityLabel": "☠️ MORTEL / Très toxique",
        "warning": "Riche en muscarine pure, intoxication respiratoire et cardiaque rapide.",
        "habitat": "Prés, pelouses, bords de routes, parcs, souvent en cercles.",
        "season": "Août à novembre.",
        "cap": "Blanc crayeux givré, déprimé au centre, souvent zoné.",
        "underside": "Lames blanches très serrées un peu décurrentes.",
        "stem": "Pied grêle blanc fibreux.",
        "confusion": "Meunier (qui a des lames rosissant et odeur de farine), Marasme des Oréades (Faux-mousseron).",
        "funFact": "Poussant dans l'herbe des pelouses, il est hélas trop souvent confondu avec les mousserons."
    },
    {
        "id": "agaric_jaunissant",
        "wiki_title": "Agaricus_xanthodermus",
        "name": "Agaric jaunissant",
        "latin": "Agaricus xanthodermus",
        "family": "Agaricaceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TOXIQUE (Gastro-entérite)",
        "warning": "Se distingue par son jaunissement jaune chrome foudroyant à la base du pied et son odeur d'encre/phénol.",
        "habitat": "Parcs, jardins, bords de chemins et prairies.",
        "season": "Juin à novembre.",
        "cap": "Blanc soyeux, s'aplatissant au sommet comme une boîte.",
        "underside": "Lames rose pâle puis brun chocolat foncé.",
        "stem": "Pied blanc dont la base bulbeuse jaunit instantanément d'un jaune de chrome éclatant quand on la gratte.",
        "confusion": "Rosé des prés, Agaric des forêts, Champignon de Paris.",
        "funFact": "À la cuisson, il dégage une odeur pestilentielle d'iodoforme ou d'encre qui alerte immédiatement le cuisinier."
    },
    {
        "id": "hypholome_en_touffes",
        "wiki_title": "Hypholoma_fasciculare",
        "name": "Hypholome en touffes",
        "latin": "Hypholoma fasciculare",
        "family": "Strophariaceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TOXIQUE (Très amer)",
        "warning": "Saveur d'une amertume insoutenable, toxique pour l'estomac.",
        "habitat": "En touffes très denses sur souches d'arbres feuillus ou conifères.",
        "season": "Presque toute l'année (avril à décembre).",
        "cap": "Jaune soufre au bord avec centre orangé à rouille.",
        "underside": "Lames jaune soufre puis vert olive sombre.",
        "stem": "Pieds sinueux jaunâtres soudés ensemble à la base.",
        "confusion": "Pholiote changeante ou armillaire couleur de miel.",
        "funFact": "C'est l'un des champignons lignicoles les plus communs de nos forêts, reconnaissable à ses teintes jaune soufre caractéristiques."
    },
    {
        "id": "clathre_rouge",
        "wiki_title": "Clathrus_ruber",
        "name": "Clathre rouge (Cœur de sorcière)",
        "latin": "Clathrus ruber",
        "family": "Phallaceae",
        "category": "inedible",
        "edibility": "sans_interet",
        "edibilityLabel": "🪵 Non comestible / Nauséabond",
        "warning": "Spectaculaire curiosité de la nature, odeur cadavérique repoussante.",
        "habitat": "Feuillus, jardins, sols riches et chauds du Sud et de la façade atlantique.",
        "season": "Avril à novembre.",
        "cap": "Cage sphérique grillagée rouge vif ajourée comme une dentelle polygonale.",
        "underside": "Gléba noire gluante et malodorante tapissant l'intérieur de la cage.",
        "stem": "Dépourvu de pied, émerge d'un œuf blanchâtre.",
        "confusion": "Inconfondable avec sa structure de lanterne rouge.",
        "funFact": "Son odeur fétide attire les mouches qui se régalent de sa gléba et dispersent ainsi ses spores à distance."
    },
    {
        "id": "satyre_puant",
        "wiki_title": "Phallus_impudicus",
        "name": "Satyre puant",
        "latin": "Phallus impudicus",
        "family": "Phallaceae",
        "category": "inedible",
        "edibility": "sans_interet",
        "edibilityLabel": "🪵 Non comestible / Nauséabond",
        "warning": "Se repère à l'odeur à plus de 20 mètres à la ronde !",
        "habitat": "Forêts de feuillus et conifères, sous-bois humides.",
        "season": "Mai à novembre.",
        "cap": "Conique alvéolé vert olive recouvert d'une gléba fétide puis blanchissant.",
        "underside": "Aucune lame.",
        "stem": "Long pied cylindrique blanc, spongieux et creux.",
        "confusion": "Morille (au stade délavé, mais le satyre a un reste de volve en sac et une odeur d'asticot !).",
        "funFact": "Il naît sous forme d'œuf du diable gélatineux avant de jaillir en quelques heures à sa forme adulte."
    },
    {
        "id": "russule_ematique",
        "wiki_title": "Russula_emetica",
        "name": "Russule émétique",
        "latin": "Russula emetica",
        "family": "Russulaceae",
        "category": "toxic",
        "edibility": "toxique",
        "edibilityLabel": "⚠️ TOXIQUE (Saveur poivrée brûlante)",
        "warning": "Provoque vomissements et coliques violentes.",
        "habitat": "Bois humides de conifères, sphaignes et tourbières.",
        "season": "Juillet à novembre.",
        "cap": "Rouge carmin éclatant brillant, se décolorant parfois en zones rosâtres.",
        "underside": "Lames blanches pures, très fragiles.",
        "stem": "Pied blanc pur friable.",
        "confusion": "Russule charbonnière (dont le chapeau est violacé/vert et les lames lardacées).",
        "funFact": "Une simple miette sur le bout de la langue brûle comme du piment fort après quelques secondes !"
    }
]

def fetch_wiki_images(mushroom_list):
    os.makedirs("images", exist_ok=True)
    results = {}
    
    # We query Wikipedia in batches of 10
    chunks = [mushroom_list[i:i+10] for i in range(0, len(mushroom_list), 10)]
    
    for chunk in chunks:
        titles_map = {m["wiki_title"]: m for m in chunk}
        titles_query = "|".join([m["wiki_title"] for m in chunk])
        url = f"https://fr.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(titles_query)}&prop=pageimages|imageinfo&piprop=thumbnail|original&pithumbsize=900&redirects=1&format=json"
        
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                # Check normalized or redirects
                title_aliases = {}
                for norm in data.get('query', {}).get('normalized', []):
                    title_aliases[norm['to']] = norm['from']
                for red in data.get('query', {}).get('redirects', []):
                    title_aliases[red['to']] = red['from']

                pages = data.get('query', {}).get('pages', {})
                for pid, p in pages.items():
                    curr_title = p.get('title')
                    # Find matching mushroom
                    matched_m = None
                    for m in chunk:
                        if m["wiki_title"].replace('_', ' ') == curr_title:
                            matched_m = m
                            break
                        if m["name"] in curr_title or curr_title in m["name"]:
                            matched_m = m
                            break
                        if m["latin"] in curr_title:
                            matched_m = m
                            break
                    if not matched_m and curr_title in title_aliases:
                        orig = title_aliases[curr_title].replace('_', ' ')
                        for m in chunk:
                            if m["wiki_title"].replace('_', ' ') == orig:
                                matched_m = m
                                break
                    
                    if matched_m:
                        thumb = p.get('thumbnail', {}).get('source')
                        if thumb:
                            results[matched_m["id"]] = thumb
                        else:
                            print(f"[!] Pas de vignette trouvée pour {matched_m['name']} ({curr_title})")
        except Exception as e:
            print(f"[ERR] Erreur API pour chunk: {e}")
        time.sleep(1)
        
    return results

def download_and_optimize(m_id, image_url):
    local_path = f"images/{m_id}.jpg"
    req = urllib.request.Request(image_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            img_data = resp.read()
            img = Image.open(io.BytesIO(img_data)).convert('RGB')
            # Resize max 960x960 while preserving aspect ratio
            img.thumbnail((960, 960), Image.Resampling.LANCZOS)
            img.save(local_path, "JPEG", quality=85, optimize=True)
            size_kb = os.path.getsize(local_path) / 1024
            print(f"[OK] {m_id}.jpg ({size_kb:.1f} KB)")
            return local_path
    except Exception as e:
        print(f"[ERR] Impossible de télécharger {m_id}: {e}")
        return None

def main():
    print("--- Démarrage de la récupération des champignons ---")
    image_urls = fetch_wiki_images(MUSHROOM_DEFINITIONS)
    print(f"Trouvé {len(image_urls)}/{len(MUSHROOM_DEFINITIONS)} URLs d'images.")

    successful_count = 0
    final_data = []

    for m in MUSHROOM_DEFINITIONS:
        m_id = m["id"]
        remote_url = image_urls.get(m_id)
        if not remote_url:
            print(f"[!] Manquant: {m_id}")
            continue

        local_file = download_and_optimize(m_id, remote_url)
        if local_file:
            successful_count += 1
            m_copy = dict(m)
            m_copy["image"] = local_file
            m_copy["remoteImage"] = remote_url
            final_data.append(m_copy)

    # Save to mushrooms.js
    js_content = "/**\n * Base de données des champignons pour MemoChampi\n * Images libres de droit issues de Wikimedia Commons\n */\n"
    js_content += "const MUSHROOMS = " + json.dumps(final_data, ensure_ascii=False, indent=2) + ";\n"

    with open("mushrooms.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"\nTerminé ! {successful_count} champignons enregistrés dans mushrooms.js")

if __name__ == "__main__":
    main()
