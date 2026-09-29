# Virtual Coffee — Direction artistique 2026 : « l'Atelier »

> Revue complète du café 3D par un regard d'architecte d'intérieur, de designer
> produit et de directeur artistique, et la refonte qui en découle — **appliquée
> dans `index.html`**, pas seulement proposée. Document de travail, comme
> `ART_DIRECTION_GTA5.md` dont il prend la suite : celui-là cherchait le rendu
> d'un jeu, celui-ci cherche celui d'un lieu.

---

## 0. Le verdict en trente secondes

Le café d'avant n'avait pas de langage : il en avait **cinq**. Laiton et marbre
de bistrot parisien, tapis rond à rayures de diner américain, poutres sombres et
ventilateur de loft rustique, armoire à trophées de hall d'entreprise, caisse
enregistreuse crème à quatorze touches de musée. Chaque objet était défendable
seul ; ensemble, ils disaient « décor assemblé », et c'est ce que l'œil lisait
avant de lire Simon.

À cela s'ajoutaient quatre fautes de rendu qui tiraient tout vers le jeu vidéo
bon marché :

1. **un plafond noir** — la pièce n'avait pas de haut, seulement un vide d'où
   pendaient des lampes ;
2. **une lumière sans source** — le spot qui éclaire Simon ne venait de nulle
   part, et les halos des suspensions (des sprites de 70 cm) mangeaient l'ardoise ;
3. **un parquet en damier** — chaque lame tirait une teinte au hasard dans une
   plage large : de la chaise, un échiquier orange ;
4. **un laiton jaune** — sur les tabourets, les lampes, la caisse, les appliques :
   rendu en peinture jaune, il signait « plastique ».

La refonte tient en une phrase : **une seule matière par rôle, une seule couleur
d'accent, et une lumière dont on voit toujours la source.**

## 1. Le concept : « l'Atelier », minimalisme chaud bruxellois

Simon vit et travaille à Bruxelles ; le café est chez lui (« j'ai fait la
plomberie, l'électricité, tout »). La référence n'est donc ni Paris ni
Brooklyn : c'est le **minimalisme chaud belge** — Vincent Van Duysen,
Axel Vervoordt, les coffee bars de spécialité qui en descendent. Des matières
franches, peu nombreuses, travaillées à la main ; une palette de terre ; des
formes douces ; rien qui crie.

### 1.1 La règle qui fait le système

| Rôle | Matière | Pourquoi |
|---|---|---|
| **Architecture** (murs, plafond) | enduit à la chaux, blanc chaud `#e4ddd1` | nuageux, minéral : une surface qui accroche la lumière au lieu de la renvoyer à plat |
| **Le mur de scène** (mur du fond) | tadelakt **olive profond** `#4a5140` | le fond du plan-héros : un visage se lit sur un fond sombre, pas sur un fond clair |
| **Menuiseries fixes** (comptoir, armoire, bar de fenêtre, porte) | chêne clair huilé, fil vertical | le bois « construit », de la même famille que le sol |
| **Plans de service** (comptoir, arrière-bar, vitrine) | travertin veiné, adouci | la pierre là où tombent les tasses — la seule pierre de la salle |
| **Sol** | chêne fumé en point de Hongrie | le parquet des maisons de maître bruxelloises — le signal « premium » le plus fort qu'un sol puisse donner |
| **Mobilier libre** (chaises, tables, tabourets) | noyer + bronze noirci | tout ce qui se déplace est sombre, sur une architecture claire : le mobilier se détache, la pièce respire |
| **Assises** | cuir cognac | sauf une : la chaise du visiteur garde son **coussin vert** (la voix de Simon le nomme) |
| **Métaux** | trois, un rôle chacun | bronze noirci pour toute structure, inox brossé pour la machine, laiton brossé **seulement là où une main se pose** (poignée de porte, poignées de vitrine, couvercles de bocaux) |

### 1.2 Palette (60 / 30 / 10)

- **60 % — le fond** : chaux blanc chaud, plafond compris.
- **30 % — les matières** : chêne clair, chêne fumé, travertin, noyer.
- **10 % — les accents** : olive (le mur de scène, le coussin), cognac (le cuir),
  terracotta et ocre (la toile, les sodas), champagne (les filets du menu).

Deux couleurs sortent du jeu et c'est voulu : le rouge d'HENRY TV et le jaune de
l'anneau de la chaise. L'un est un écran, l'autre une interface ; ils n'ont pas
à appartenir à la pièce.

### 1.3 La lumière, en couches

1. **Jour** — froid, par les deux vitrages (fenêtre à gauche, devanture à
   droite) ; il tombe au sol en nappes douces près des vitres.
2. **Ambiance** — une **corniche lumineuse** le long du mur olive (bande LED
   dans une retombée de plâtre) qui lèche l'enduit de haut en bas, et un
   **radeau de lattes de chêne** au-dessus des tables dont le halo réchauffe
   le plafond.
3. **Tâche** — deux **globes opalins** qui encadrent la carte au-dessus du bar
   (trois à l'origine ; ils coupaient la carte et la télé, voir §4), un troisième, plus
   grand, au-dessus de la table de Simon : la source enfin visible du spot qui
   l'éclaire.
4. **Accent** — une **lampe à tableau** en bronze sur chaque une du mur
   galerie, les réglettes de l'armoire, le socle rétroéclairé du comptoir.

Techniquement : les couches 2 et 4 sont **cuites** (light maps peintes au
canvas et appliquées en irradiance, donc multipliées par la couleur de la
surface) ; l'éclairage d'ambiance vient d'une **carte d'environnement qui est
une maquette de la nouvelle pièce** ; une **occlusion ambiante** (SSAO) pose
les ombres de contact. Voir §9.

---

## 2. L'enveloppe — murs, plafond, sol, volumes

**2.1 Défauts.** Trois couleurs de mur sans logique (vert sauge au fond, taupe à
l'avant, brun sombre sur la fenêtre), plafond quasi noir, cinq poutres brunes,
parquet à lames contrastées. Volume de 10,5 × 8,8 m pour 3,44 m sous plafond :
une belle hauteur, **invisible** parce que le haut de la pièce était noir.

**2.2 Problèmes fonctionnels.** Un plafond noir absorbe la lumière des suspensions
au lieu de la rediffuser : la salle paraissait éclairée par taches. Aucune
correction acoustique lisible (dans un café réel, c'est la première plainte).

**2.3 Problèmes esthétiques.** Aplats sans matière (le mur avant n'avait même
pas de coordonnées de texture), poutres « rustiques » dans un décor
bistrot, damier orange au sol.

**2.4 Propositions.** Unifier l'enveloppe en chaux ; faire du mur du fond un mur
de scène sombre ; allumer le plafond ; ramener la chaleur par un radeau de bois
plutôt que par la couleur des murs ; un parquet noble et calme.

**2.5 Nouveau concept.** Une boîte claire et minérale, un seul mur sombre
tendu derrière le bar comme un rideau de théâtre, un plafond lumineux avec un
radeau acoustique en chêne au-dessus des tables, un point de Hongrie en chêne
fumé qui unifie tout le sol.

**2.6 À remplacer.**
- enduits (trois teintes) → chaux blanc chaud + tadelakt olive ;
- plafond noir + 5 poutres → plafond chaux + corniche lumineuse + radeau ;
- parquet damier → point de Hongrie chêne fumé (lames ≈ 10,6 × 42 cm) ;
- plinthes crème → plinthe sombre en retrait (détail « joint creux ») ;
- cimaise noyer → cimaise bronze (rail de galerie).

**2.7 À conserver.** Le volume, les ouvertures (fenêtre, devanture, porte), la
hauteur sous plafond — l'architecture du modèle était saine, c'était son
habillage qui ne l'était pas.

**2.8 Résultat.** On entre dans une pièce claire et chaude ; le plafond se lit ;
le mur du fond, vert olive profond, lavé de lumière par le haut, attire l'œil
vers le bar ; au-dessus des tables, des lattes de chêne sur feutre sombre
filent vers le comptoir et y conduisent le regard.

---

## 3. L'entrée et la devanture

**3.1 Défauts.** Menuiseries en noyer épais, enseigne jaune sur noir, paillasson
brun posé, vue extérieure blanchie comme dans le brouillard.

**3.2 Fonctionnels.** Depuis la porte, le chemin vers le bar traversait le tapis
rond (obstacle visuel et, dans un vrai café, risque de chute).

**3.3 Esthétiques.** L'enseigne était celle d'un take-away ; la vitrine,
reflétant l'intérieur sur un fond presque noir, transformait la rue en
voile gris.

**3.4 Propositions.** Menuiseries fines en bronze noirci (esprit atelier
d'artiste), enseigne typographique, tapis de coco encastré, vraie lumière du
jour dehors.

**3.5 Nouveau concept.** Une devanture d'atelier : profils sombres et fins,
grandes glaces claires, poignée laiton brossé longue (la seule pièce de laiton
qu'on touche en entrant), enseigne ivoire espacée sur bronze, et derrière la
vitre une rue en plein jour — ciel, trottoir en dalles, asphalte, arbres.

**3.6 À remplacer.** Menuiseries noyer → bronze ; enseigne → nouvelle typographie ;
paillasson → coco ; verre → moins réfléchissant ; ciel noir + brouillard gris →
dôme de ciel et brume d'horizon ; environnement lumineux de la rue → le sien.

**3.7 À conserver.** La porte battante animée, les vans ICE CUBE et BravoReno, le
livreur et tout son parcours, la voiture, les arbres.

**3.8 Résultat.** De l'intérieur, la devanture est un cadre sombre et net sur
une rue lumineuse ; de la rue, une vitrine d'atelier au lettrage discret.

---

## 4. Le bar — comptoir, arrière-bar, machine, menu, frigo

**4.1 Défauts.** Comptoir en noyer rougeâtre sous un plateau blanc sans veine,
ardoise de **3 × 1,65 m** en Caveat collée derrière la tête de Simon, texture
1024 × 400 étirée sur un cadre 1,8:1 (chaque lettre un tiers trop haute), caisse
enregistreuse crème à quatorze touches laiton, trois abat-jour coniques laiton
aux halos énormes, néon orange de 2,2 m, frigo à sodas aux couleurs primaires.

**4.2 Fonctionnels.** Le comptoir n'avait ni retrait de pied ni lumière basse :
un bloc posé. La caisse n'avait rien d'un poste d'encaissement de 2026.

**4.3 Esthétiques.** Le bar est le **fond du plan-héros** : tout ce qui s'y
trouve s'additionne derrière le visage de Simon. L'ardoise, le néon et les
halos en faisaient l'endroit le plus bruyant de l'image.

**4.4 Propositions.** Un comptoir-sculpture (bois cannelé + pierre), un menu
petit et typographié décalé à droite de Simon, une vraie caisse moderne, des
luminaires qu'on voit sans qu'ils éblouissent.

**4.5 Nouveau concept.** Un comptoir monolithe : façade **cannelée en chêne**
(tasseaux de 3 cm, en vraie géométrie, pour que la lumière rasante les
dessine), plateau en **travertin** de 10 cm, socle en retrait avec un **filet
de lumière 2700 K** qui fait flotter le bloc. Derrière, le mur olive lavé par la
corniche ; à droite de Simon, un **menu de 1,84 × 0,72 m** au ratio exact de sa
toile, cadre bronze, texte ivoire (Inter), prix champagne (Space Grotesk),
points de conduite. Deux **globes opalins** sur tiges bronze, de part et
d'autre de la carte (2026-09-29 : trois la coupaient depuis la chaise). Une **tablette
sur pied pivotant** et un terminal de paiement à la place de la caisse. Le
frigo gainé de bronze, bandeau chêne, intérieur anthracite éclairé par des
LED (montants, haut, bord de chaque clayette — 2026-09-29 : l'intérieur
blanc lumineux sortait blanc pur), des canettes d'une seule marque en quatre
saveurs sourdes et des jus en bouteille. La machine a ses groupes côté
barista et montre à la salle un dos en inox brossé coiffé de tasses ; la
vitrine est garnie de viennoiseries.

**2026-09-29 (audit, phase 2).** L'arrière-bar disparaît et le comptoir perd
12 cm côté barista : son couloir passe de 23–35 cm à 61–69 cm, le mur olive
descend jusqu'au sol derrière elle. Service lisible, en deux langues
(« Commandez ici · Bestel hier », « Retrait · Afhalen »), point d'eau au bout
du comptoir.

**4.6 À remplacer.** Ardoise → menu ; caisse → tablette + TPE ; abat-jour laiton →
globes opalins ; néon → supprimé ; façade du comptoir → cannelures ; plateaux
marbre → travertin ; machine laiton/noir → inox brossé ; vitrine sur socle
laiton → socle travertin ; sodas primaires → gamme sourde.

**4.7 À conserver.** Le comptoir (son volume, sa place, sa hauteur de 1,22 m : le
barista, le livreur et le serveur y ont leurs couloirs), la machine, le
moulin, la vitrine, le frigo, les **deux télés HENRY TV** (un contenu, pas un
décor — redessinées en bronze sombre), l'horloge qui marche (redessinée en
horloge de gare), les jeux de mots du menu, les prix à la virgule belge, le côté
**CLOSED** de la carte.

**4.8 Résultat.** Derrière Simon, un mur vert profond, calme, lavé de lumière
chaude par le haut ; un comptoir de chêne cannelé qui accroche la lumière des
globes ; le menu, discret et lisible, en haut à droite ; plus aucun objet ne se
dispute son visage.

---

## 5. La salle — la table de Simon et les tables

**5.1 Défauts.** Plateaux blancs sur pied noir et semelle en fonte (table de
fast-food), chaises à barreaux en tube noir (la chaise de cantine), tapis rond
orange-turquoise-jaune au milieu du passage.

**5.2 Fonctionnels.** Le **CV — une feuille blanche — posé sur une table
blanche** : le document au centre de toute l'expérience n'avait aucun contraste
avec son support. Le tapis, en plein couloir entre la porte et le bar.

**5.3 Esthétiques.** Le mobilier le plus générique de la scène, dans le plan le
plus regardé.

**5.4 Propositions.** Des tables sombres pour faire sortir la feuille ; des
chaises dessinées ; retirer le tapis.

**5.5 Nouveau concept.** Guéridons en **noyer** au chant arrondi (tore plein) sur
**pied tulipe en bronze noirci** ; chaises « Atelier » en noyer — pieds
fuselés, dossier cintré en bois courbé, galette de cuir cognac à 50,3 cm ; la
table de Simon est **la même table** à sa taille, et au-dessus d'elle pend le
grand globe d'où vient la lumière.

**5.6 À remplacer.** 5 tables, 10 chaises, le tapis, la chaise du visiteur
(redessinée, coussin vert conservé en bouclette).

**5.7 À conserver.** **Chaque position au millimètre** : chaises, tables et
tabourets sont reconstruits sur les boîtes englobantes du modèle (jamais sur
des coordonnées tapées), donc hauteurs d'assise, centres, rayons, tasses et
postes du serveur sont inchangés — mesuré, voir §11.

**5.8 Résultat.** Sur le noyer sombre, le CV blanc éclate ; autour, des chaises
fines et chaleureuses, un sol calme, et une lumière qui tombe d'une lampe qu'on
voit.

---

## 6. Le bar de fenêtre et le coin du trio

**6.1 Défauts.** Plateau noyer sur pieds noirs, repose-pied laiton jaune, six
tabourets à fût laiton ; au mur du fond, le néon et une affiche « arc sur
crème » ; dans la baie, une ville **au coucher du soleil** aux fenêtres
allumées — en plein matin.

**6.2 Fonctionnels.** Plateau de 66 cm : confortable, gardé.

**6.3 Esthétiques.** La ligne de tabourets laiton dessinait des pointillés
jaunes dans tous les plans ; la vue était un décor peint de jeu.

**6.4 Propositions.** Chêne clair pour le plateau (menuiserie fixe), bronze pour
la structure, tabourets cognac assortis au comptoir, une vraie vue de jour, une
seule grande œuvre au mur du fond.

**6.5 Nouveau concept.** Un long plan de chêne le long de la baie, tabourets
cuir sur piètement bronze, et dans la fenêtre **Bruxelles en plein jour** :
ciel avec cumulus, verre des tours qui reflète le ciel, une rangée de façades
en pierre bleue et ardoises à mansardes, les cimes des platanes à hauteur
d'allège. Big Four, NdaBank et HENRY gardent leurs plaques. Au fond, au-dessus
du trio qui discute : **une toile abstraite de 1,05 × 1,35 m** (arche
terracotta, soleil ocre, bloc olive, un geste au fusain) en caisse américaine
de chêne.

**6.6 À remplacer.** Pieds et repose-pied → bronze ; plateau → chêne ; tabourets →
cognac ; affiche + néon → une toile ; ville au couchant → ville de jour ; porte
des toilettes à panneaux → porte **affleurante** en chêne, cadre bronze fin,
tirant bronze vertical, pictogramme sur rond bronze.

**6.7 À conserver.** Le bar, sa place, les six tabourets (positions et hauteurs
exactes : la buveuse et le lecteur y sont assis), l'avion et l'homme volant
qui passent entre la toile peinte et le mur.

**6.8 Résultat.** Un comptoir de fenêtre lumineux, une vue qui dit l'heure qu'il
est, un coin du fond tenu par une seule œuvre forte.

---

## 7. Le mur galerie — armoire à trophées, unes, plaque, jukebox, plante

**7.1 Défauts.** Quatre unes dans des boîtes noires, petites sur un grand mur
taupe ; trois appliques bistrot en laiton **au-dessus** des cadres (qui les
laissaient dans l'ombre) plus une quatrième reconstruite ; un jukebox
Wurlitzer orange à néon turquoise ; une plante faite de sept sphères vertes ;
l'armoire à trophées en noyer.

**7.2 Fonctionnels.** Les unes sont des objets à lire (on s'approche, elles
s'ouvrent) : elles méritent d'être présentées comme telles.

**7.3 Esthétiques.** Des trous noirs sur un mur clair ; un jukebox venu d'une
autre pièce ; une plante en boules.

**7.4 Propositions.** Un accrochage de galerie ; des lampes à tableau ; le
jukebox rhabillé dans les matières de la salle ; une vraie plante.

**7.5 Nouveau concept.** Un mur de galerie : chaque une dans un **cadre chêne
fin avec passe-partout ivoire**, une **lampe à tableau bronze** sur chaque
station (son halo est peint dans la light map du mur) ; la plaque « Employé du
mois » au même régime ; le **jukebox** en noyer, laiton brossé et arcs lumineux
ambre et blanc chaud, marquise en capitales espacées ; un **strelitzia
nicolai** dans un bac de pierre, qui monte au lieu de s'étaler ; l'armoire en
chêne clair avec un fond olive qui fait ressortir les trophées.

**7.6 À remplacer.** Cadres, appliques, plante, habillage du jukebox, noyer de
l'armoire.

**7.7 À conserver.** Les quatre unes vraies et leurs articles, la plaque, les
libellés PNG de l'armoire, le jukebox (position, disque qui tourne, casques,
silent disco, gélatines — elles teintent désormais aussi les globes et les
réglettes de l'armoire), la position de la plante (un repère de collision et
une place de danseur en dépendent).

**7.8 Résultat.** Un mur blanc chaud rythmé par quatre cadres clairs éclairés
chacun par sa lampe, une grande plante verticale entre deux d'entre eux, le
jukebox en meuble de musique et non en borne d'arcade, et l'armoire comme une
vitrine d'atelier.

---

## 8. L'extérieur

**8.1 Défauts.** Fond de scène presque noir, brouillard gris-bleu, vitres qui
reflètent l'intérieur : le parking et les vans apparaissaient comme des
fantômes blanchis ; la voiture rouge métallisée renvoyait le plafond du café.

**8.2 Fonctionnels.** Dehors, les matériaux lisaient **l'environnement de
l'intérieur** — ils étaient éclairés par un plafond et une fenêtre qui étaient
derrière eux.

**8.3 Esthétiques.** Sans ciel, pas d'heure ; sans heure, pas de lieu.

**8.4 Propositions.** Un ciel, une brume d'horizon, un environnement lumineux
propre à la rue, des matières de voirie.

**8.5 Nouveau concept.** Un dôme de ciel en dégradé (non éclairé, dessiné en
premier, sans profondeur), un brouillard à la couleur de l'horizon et au tiers
de sa densité (1,4 % au mur du fond, un cinquième à la lisière des arbres), une
carte d'environnement « rue » (ciel, sol gris, soleil) pour tout ce qui est
derrière la vitre, un asphalte grenu, un trottoir en dalles, une voiture vert
anglais.

**8.6 À remplacer.** Fond, brouillard, verre, matières de voirie et de la
voiture, réverbères allumés de jour (éteints le jour, allumés à la fermeture).

**8.7 À conserver.** Toute la géométrie extérieure, les deux vans et leurs
livrées, la tournée du livreur.

**8.8 Résultat.** Par la devanture, une rue calme en plein jour ; la nuit, une
rue bleue où les réverbères s'allument.

---

## 9. Lumière et rendu (transversal)

| Avant | Après | Pourquoi |
|---|---|---|
| hémisphérique `.42` servant de remplissage | `.30`, simple plancher | le vrai remplissage vient de l'environnement |
| environnement : 4 émetteurs génériques | **maquette de la nouvelle pièce** (plafond clair, mur olive, sol chêne, deux vitrages, globes, corniche), rendue à hauteur d'œil | l'IBL nourrit aussi la diffusion : c'est la lumière de rebond de la salle |
| spot `0xffb867` sans source | `0xffcf9e` (≈ 2900 K) dans le grand globe | une lumière dont on voit la source |
| halos de 70 cm à 85 % | 46 cm à 32 % | un halo, pas un ballon |
| ACES approximé (Narkowicz) | ACES ajusté (Hill, matrices d'entrée/sortie) | la teinte des hautes lumières tend vers le blanc au lieu de saturer en orange |
| grade `cleanDay` (contraste 1,22, sat 1,06) | grade `atelier` (1,07, 0,97) | une photo d'intérieur haut de gamme a des ombres douces, et la palette porte déjà sa couleur |
| — | **SSAO** (demi-résolution, 12 échantillons, flou 4×4 conscient de la profondeur, profil « high » seulement) | les pièces claires vivent de leurs ombres de contact |
| — | **light maps peintes** (corniche, lampes à tableau, nappes de jour, socle du comptoir, halos du plafond) | la lumière d'un vrai lieu, pour le prix d'une lecture de texture |
| nuit : même environnement que le jour | environnement de nuit construit à la fermeture, exposition du grade de nuit recalée pour la nouvelle courbe | sinon toute la salle gardait sa lumière de jour |

---

## 10. Les personnages (habillage seulement)

Anatomie, rig, animations : **inchangés**. Seule la garde-robe rejoint la pièce :
le prune et le moutarde, rendus lilas et jaune pastel sous la nouvelle lumière,
cèdent la place au bordeaux et au camel. La barista garde son vert, Simon son
bleu marine.

---

## 11. Contraintes tenues, et chiffres

- **Aucune route, aucune station, aucun point de passage n'a bougé.** Chaises,
  tables, tabourets, globes et plante sont construits sur les boîtes du modèle
  (`CAFE.boxes`) — jamais sur des coordonnées recopiées.
- Hauteurs mesurées par lancer de rayon dans la page : **assises 0,503** (modèle
  0,5032) ×9, **tabourets 0,8051** ×10 (identiques), **plateaux 0,8025** ×4.
- Pieds de tables plafonnés au rayon des semelles qu'ils remplacent (0,23–0,28 m
  contre 0,275–0,28) : les corps restent à 0,55 m des centres, leur bord à 0,29.
- Plante : feuille la plus proche à **0,483 m** du centre de la place du danseur
  (corps 0,26 → **22 cm** de marge) et à **0,328 m** du centre le plus proche
  possible du visiteur (marge **7 cm**).
- Coût GPU, passe de scène, bureau « high » : **771** appels (758 avant),
  **238 k** triangles (215 k). Téléphone « low » : **489** (476), **214 k**
  (189 k) ; textures en demi-résolution sur tactile.

## 12. Ce qui n'a pas été fait — et ce que je recommande ensuite

1. **Le plan n'a pas été redessiné.** C'était la tentation, et c'est un choix :
   onze corps partagent la pièce sur des routes auditées ; déplacer une table,
   c'est ré-auditer serveur, livreur, clients, danseurs et visiteur. Les
   propositions de plan à instruire, dans l'ordre :
   - une **banquette** le long du mur galerie à la place des tables T1/T4 (plus
     de places, dos au mur, circulation libérée devant l'armoire) ;
   - un **point de commande et de retrait** matérialisé au bout est du
     comptoir, là où passent déjà livreur et serveur ;
   - une **terrasse** de deux tables sur le trottoir, hors du couloir du livreur.
2. **L'interface** (pilules, boîte de dialogue, carte d'accueil) garde son or
   `#f4b740` : c'est aussi l'or de la feuille de CV et du PDF. L'harmoniser en
   champagne demande de ré-exporter le PDF.
3. **`og.jpg`** a été re-rendue depuis la nouvelle scène (1200 × 630, titre en
   Space Grotesk). LinkedIn garde l'ancienne en cache une semaine : passer le
   lien dans le Post Inspector après la mise en ligne.
4. **Le personnage de Simon** (et le cast capsule) reste stylisé ; c'est cohérent
   avec la page, mais c'est désormais l'élément le moins « premium » du plan.
