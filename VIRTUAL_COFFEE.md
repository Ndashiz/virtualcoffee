# Virtual Coffee ☕

> **Un CV qu'on ne lit pas : on s'assied en face.**
> Café 3D interactif servi sur <https://ndashiz.be/virtualcoffee/> — on est assis
> à la table de Simon Goffin, on lit son CV, on le repose — et il raconte,
> section par section, à voix haute. Les cinq sections du CV
> entendues, un second palier s'ouvre : la personne derrière le CV.

---

## 1. Le concept

Une page de CV classique dit « voilà ce que j'ai fait ». Virtual Coffee dit
« installez-vous, je vous raconte ». Le déplacement est double :

- **Le support** : au lieu d'un PDF, un lieu. Un petit café en 3D, chaleureux,
  vivant, dans lequel le visiteur est physiquement assis face au candidat.
- **La voix** : au lieu de puces à lire, des sections **parlées** — écrites par
  Simon, plus longues et plus personnelles que le texte du CV.

Le site est aussi sa propre démonstration : Simon est Product Manager et
revendique de construire avec l'IA — le café est l'exhibit A, et il en parle
lui-même dans « How I built this », au second palier.

**Anglais uniquement** : les scripts n'existent qu'en anglais. La narration est
rendue hors ligne par Kokoro (voix `bm_george`) à partir de ces mêmes textes —
les mots sont de Simon, la voix non, et la carte d'accueil le dit.

## 2. Ce qu'on peut y faire

**Rien ne bouge tant que vous ne bougez pas.** Le personnage entre côté
porte et **reste là** : il n'y a plus d'autopilote, la marche est
l'invitation et un personnage qui s'en va tout seul y répond à votre
place. Alors Simon vous accueille, de l'autre bout de la salle
(`welcome`) : le lieu est à lui, il en a fait la plomberie et
l'électricité, faites-en le tour — et quand vous êtes prêt, **la chaise au
coussin vert** est la vôtre. Deux façons de le déplacer : **les flèches**,
ou **un tap sur le sol** — la seule dont dispose un téléphone, et la
raison pour laquelle elle existe.

« Take a seat » ne téléporte plus : **votre personnage entre côté porte et
les flèches sont à vous** (WASD physique aussi — ZQSD sur un AZERTY,
déplacement relatif à l'écran), **caméra à la troisième personne** dans son
dos. La chaise libre porte une **balise** : anneau au sol, flèche qui flotte
au-dessus, colonne de lumière visible d'un bout à l'autre de la salle — et si
vous lui tournez le dos, un curseur en bord d'écran pointe vers elle. Entrez
dans l'anneau et **l'entretien démarre** : la feuille monte en quasi plein
écran et il parle par-dessus tout de suite (`seated`) — sa réplique est la
légende de ce que vous êtes en train de lire, *« a resume only tells you what I
did, not how, or why »*. La feuille redescend toute seule quand il a fini — ou
dès un clic à côté d'elle — et c'est là que la **boîte de dialogue** s'ouvre.
La pastille Skip et `espace` l'écourtent aussi. L'anneau dessiné au sol a exactement le rayon du
déclencheur (`SEAT_TRIGGER`) — ce que vous voyez est ce dans quoi il faut
entrer. Collisions : tables, comptoir, bar de fenêtre — et Simon. Sous `prefers-reduced-motion`, pas de marche : déjà assis, accueil
immédiat.

**La caméra est une vraie caméra de jeu.** Elle se tient derrière et
au-dessus, assez reculée pour montrer la salle, et :

- **orbite librement** — glissez à la souris (ou au doigt) pour tourner
  autour du personnage, molette pour rapprocher ou reculer ;
- **se recentre toute seule** dans son dos après une seconde sans regard, en
  dérive amortie, jamais d'un coup ;
- **traîne** derrière ses virages : le cadre a du poids au lieu d'être soudé
  aux épaules, et un coup de souris relâché en pleine course continue sur son
  élan avant de s'éteindre ;
- **recule et s'ouvre** quand il sprinte (Maj) ;
- **se rapproche** quand un mur, le comptoir ou le frigo passe entre l'objectif
  et lui — et prend de la hauteur en même temps, parce qu'un plan d'épaule à
  1,25 m n'est plus qu'une nuque.

Le déplacement est **relatif à la caméra** : « en avant » veut dire « loin de
l'objectif », pas « au nord ». Le recentrage vise **strictement le plein dos**,
et ce n'est pas une préférence : avec des touches relatives à la caméra, le
pencher vers le côté habillé de la salle fait une boucle — la caméra dérive,
« en avant » tourne avec elle, le personnage tourne, la caméra dérive encore ;
une direction tenue s'incurve toute seule. Le plein dos est le seul point
fixe. Contrepartie assumée : le café est un décor habillé pour être vu depuis
la chaise du client, donc en tournant franchement l'objectif on finit par
apercevoir les coulisses.

**Le son se coupe** (la pastille haut-droite, ou touche `M`, choix
mémorisé). Pas via `audioEl.muted` : la bouche de Simon est pilotée par
l'amplitude réelle du mp3 via un `AnalyserNode`, donc couper l'élément lui
figerait la mâchoire. Un `GainNode` maître est placé **après** l'analyseur —
en muet il parle toujours, sous-titres compris, on ne l'entend simplement pas.

| Action | Résultat |
|---|---|
| Flèches / WASD (pendant la marche) | Vous pilotez votre personnage jusqu'à la chaise |
| Clic / tap sur le sol | Il marche jusqu'au point visé (la seule commande d'un mobile) |
| Glisser à la souris · molette · `Maj` | Tourner la caméra · reculer · sprinter |
| Pastille 🔊 ou touche `M` | Coupe / rétablit la voix (mémorisé) |
| Touche `0` (l'outro) | …et le café ferme : le serveur vient vous le dire, la salle se vide |
| Feuille en plein écran | Il la commente ; elle redescend quand il a fini — ou dès un clic à côté d'elle, ou sur sa croix ✕ — et la boîte s'ouvre |
| Survoler le CV sur la table | La feuille se soulève, la mise au point se tire dessus (rack focus) |
| Une section de la boîte (ou touches `1`–`5`) | Simon la raconte, sous-titres à l'écran, letterbox cinéma ; entendue en entier, elle garde un point vert |
| Une section déjà entendue | *« Ah, you weren't listening »* (`reclick`), puis il la rejoue en entier |
| Les cinq entendues | Second palier : off the clock, l'IA, pourquoi la banque, comment j'ai construit ça — plus l'outro |
| Cliquer Simon | La section « off the clock » (deux bières sur la table), une fois le palier ouvert |
| L'outro (ou touche `0`) | Le lien LinkedIn apparaît, puis le café ferme |
| Pastille ⏭ Skip ou `espace` | Le fait taire — la section reste alors non entendue |
| « 📄 See the resume » / « ⬇ Download it » | Sous la boîte dès la première option, même pendant qu'il parle : la feuille remonte, ou le CV se télécharge |
| « 🚶 Leave the table » | Il se lève (même animation qu'à l'assise, jouée à l'envers) et la salle est à vous ; l'anneau se rallume, et en revenant s'asseoir la boîte rouvre telle quelle — sections validées, palier, outro compris |
| Le jukebox du mur avant | Silent disco : casques sans fil, cinq habitués qui viennent danser sur l'audio réel ; la voix de Simon garde toujours la priorité (ducking), s'asseoir renvoie la foule, le son suit la distance à l'émetteur |
| Version texte (sans WebGL, café fermé, ou lien d'évitement au clavier) | Le CV complet, accessible et indexable — sa croix ✕, `Échap` ou un clic dans la marge sombre la referment. La pastille qui l'ouvrait a disparu du café : la feuille sur la table et « See the resume » font le travail |

Sur mobile, la boîte devient un panneau en bas d'écran, sur deux colonnes.

**Un rechargement ne coûte rien.** La visite tient dans `sessionStorage` — un
onglet, effacée à sa fermeture. Si la page revient (un téléphone qui vide un
onglet d'arrière-plan, la raison habituelle du « laissé dix minutes, ça
recommence à l'entrée »), on se retrouve directement à table : points verts,
palier débloqué, outro. Ni accueil, ni marche, ni monologue — et volontairement
aucun son, puisqu'un rechargement n'apporte aucun geste utilisateur : c'est la
première section cliquée qui rallume la voix.

## 3. Le décor vit

Le fond n'est pas un tableau : c'est un café en activité, et chaque personnage
a sa propre horloge interne (jamais deux animations synchrones).

- **Un trio en pleine discussion** — vraie conversation : un locuteur à la fois
  (tours de 3 à 9 s, jamais deux fois le même), gestes de parole du locuteur,
  hochements de tête des auditeurs, changements de posture, éclats de rire
  collectifs légèrement décalés entre eux.
- **Le barista travaille** — boucle lisible en cinq temps : moudre → tasser
  (deux pressions franches) → extraction (il se redresse, essuie le comptoir,
  balaie la salle du regard) → **fait glisser la tasse** sur le comptoir →
  range, consulte, salue.
- **Un client sur son laptop, au comptoir** — il tape (avec de vraies pauses de
  réflexion), lève les yeux, main au menton, s'étire. L'écran éclaire son
  visage, et la tasse que le barista fait glisser arrive jusqu'à lui.
- **Une cliente qui boit, au bar de la fenêtre** — gorgée en quatre phases
  (saisir, porter, boire, reposer), la tasse suit sa main.
- **Un lecteur, un tabouret plus loin** — à contre-jour de la fenêtre, tourne
  une page toutes les ~40 secondes.
- **Un visiteur épisodique** — entre côté porte, vient lire l'ardoise devant la
  vitrine, repart. Jamais de demi-tour sur place : il sort comme les gens
  sortent.
- **Tout le monde regarde** — système de regard « les yeux mènent, la tête
  suit », clignement des paupières déclenché par les changements de fixation,
  respiration permanente. Le ventilateur tourne, l'horloge murale est à
  l'heure réelle.
- **Et surtout, on se regarde.** Simon avait des pupilles peintes droit devant
  qui ne bougeaient jamais : dès qu'il tournait la tête, son regard partait
  dans le vide — fuyant, sur la seule page où il doit vous regarder. Il vise
  maintenant votre avatar, la tête prend les 35 premiers degrés et **les yeux
  font le reste**. L'invité assis, lui, soutient le regard de Simon au lieu de
  repartir en balayage libre, avec un coup d'œil au CV toutes les ~9 s — ce
  que fait quelqu'un qui écoute. Le balayage aléatoire des figurants a été
  affaibli dans la foulée : toute la salle vérifiait les coins.

**Les coupures de presse ont sauté — puis trois sont revenues, vraies.** Les
cinq cuites dans la carte (trois sur le mur avant, deux repeintes au fond)
racontaient des titres inventés — un café tapissé de manchettes sur son patron,
ça se lit comme de la vantardise. La règle n'a jamais été « pas de presse »,
c'était « pas de presse inventée » : sous les trois appliques du mur avant
pendent désormais trois unes du **Daily Salfari** (`drawArticle()`, même
homonymie douteuse que l'employé du mois) — l'immeuble retapé seul en deux ans
(électricité, plomberie, maçonnerie), le premier triathlon après un an de
préparation, le studio web + IA en indépendant complémentaire. Chacune avec son
illustration à l'encre, lisible en zoom comme tout ce qui s'accroche à un mur.
Reste aussi le petit cadre : **« Employee of the Month — Tonio Salfari »**,
décerné pour services rendus derrière un comptoir où personne ne l'a jamais vu.
Peint en canvas comme l'ardoise (`drawEotm()`), repeint sur `VC.fontsReady`.

**Deux télés, un seul flux : HENRY TV.** La petite au-dessus du bout du
comptoir, entre le néon et l'ardoise — depuis la chaise, elle tombe juste
par-dessus l'épaule de Simon ; la grande sur le pan vert nu à droite du frigo,
sous l'étagère à bocaux, là où la salle sonnait creux. Son coupé, bug de chaîne
en haut à gauche, présentateur qui articule, ticker qui défile, et **six sujets
en boucle de huit secondes** — soit une « vidéo » de 48 s, ce que la barre du
lecteur mesure vraiment.

Le conducteur est **en anglais**, comme le reste de la page. Trois sujets sont
la cote, et **la cote ne contient que ce que Simon a donné** (MSCI World,
semi-conducteurs, ATOS) plus l'euro/dollar : un indice inventé sur un écran
qu'on montre reste un indice inventé. Les trois autres portent une image plutôt
qu'un graphe — la couronne d'étoiles européennes barrée d'**AMLR** pour le
dossier PSD3, une carte mot-clé pour l'émission IA du soir, et pour la sanction
NdaBank **le PDG en costume au pupitre**, main levée, en plein discours, devant
le fond répété de sa propre banque. C'est là que la boucle se referme : Tonio
Salfari est aussi la plaque du mois à deux murs d'écart, et son graphe est le
seul qui descend. Un canvas 512×288 repeint 15 fois par seconde
(`drawTV()`), en matériau non éclairé : un écran est une source, il ne doit pas
s'éteindre avec la salle.

**Et on peut lire tout ça.** Un écran ou un cadre accroché à deux mètres de
haut, ça reste « un écran » et « un cadre » — jamais des mots. Approchez-vous et
une bulle le dit (`updateReadHint()`, 3,4 m) ; un clic ou un tap le décroche.
`openZoom()` **rejoue le peintre à 2×** dans un canvas plein écran au lieu
d'agrandir la texture du mur, donc le ticker est réellement lisible, et la télé
continue d'émettre pendant la lecture — avec **une seconde de connexion au
direct** puis la barre de progression, position dans la boucle et titre du sujet
en cours. Le retour est une grosse flèche « Back to the café » — Échap et un
clic hors cadre marchent aussi, mais une croix de 24 px dans un coin n'est pas
une sortie sur téléphone.

**Le piège du cadre.** L'image et la face avant du cadre étaient à 1 mm l'une de
l'autre : à distance de salle ça *z-fight*, le cadre gagne par plaques et
l'image se lit comme recadrée. `polygonOffset` sur le cadre et 7 mm de recul
pour la dalle — même correctif sur le cadre du mois.

**Une porte de toilettes** sur le seul pan de mur-fenêtre sans fenêtre
(z 2,35→3,94), avec chambranle, panneaux, béquille laiton et pictogramme. La
plante qui occupait ce coin a été déplacée le long du mur avant par le
préprocesseur — une porte derrière un ficus n'est pas une porte.

**Et il y a un jukebox — une silent disco.** Sur le mur avant, entre les
unes du Daily Salfari et la plante : un meuble en bois à arche néon, repéré
et cliqué comme la plaque ou les télés (même bulle, même tap), mais qui
ouvre un lecteur au lieu d'une image. On choisit un morceau et il distribue
des **casques sans fil** : votre personnage enfile le sien, cinq habitués
(jamais le barista — quelqu'un tient le bar ; jamais la lectrice — dans tout
vrai café quelqu'un ignore la fête) lâchent ce qu'ils faisaient, traversent
la salle en décalé, décrochent un casque du rail en arrivant et dansent sur
**l'amplitude réelle de la piste** — RMS par image, chacun avec sa phase, sa
vitesse et son amplitude propres, jamais de clones. Le signal faiblit avec
la distance caméra→émetteur (plancher à 25 %, jamais coupé), la voix de
Simon écrase toujours la musique (duck à 20 %, relâché 500 ms après la
réplique), et **s'asseoir renvoie la foule** — chacun regagne exactement la
position et l'orientation enregistrées à l'init de la scène — pendant que la
musique continue dans votre casque. Les trois pistes sont composées par
`preprocess_music.py` (numpy + afconvert, −14 LUFS, AAC 128k) : rien de
licencié, rien d'externe, comme tout le reste du café. Sonde console :
`__jukebox()`.

**Et dehors, ça bouge.** Toutes les ~30 s un avion traverse la baie, entre la
plaque peinte (x = −3,9) et le mur (x = −3,25) : ce sont les jambages de la baie
qui le font entrer et sortir du champ, aucun fondu. Une fois sur quatre ce n'est
pas un avion mais une petite silhouette à cape, sept secondes, et vous n'êtes
jamais tout à fait sûr de l'avoir vue.

**Et à la fin, on ferme.** Quand Simon termine l'outro, la salle fait ce que
fait un café en fin de service : le barista sort de derrière son comptoir,
vient jusqu'à la table, lâche la phrase de toutes les fermetures — *« Excuse
me — we're closing now. »* — et les habitués s'en vont un par un vers la
porte, en décalé (une salle qui se vide au pas cadencé, c'est un exercice
d'évacuation). C'est **du décor et rien d'autre** : Simon reste, la boîte de
dialogue reste ouverte, les sections se rejouent. Vider la page, c'est le travail de
`closeCafe()` — le bar fermé à distance — et ce n'est pas celui-ci.

## 4. Le rendu

Look visé : « jeu AAA stylisé » — l'objectif de caméra et l'étalonnage font le
travail, les personnages restent volontairement stylisés (pas de vallée de
l'étrange sur une page de recrutement).

- **Pipeline de post-traitement** écrit à la main, inline, zéro dépendance :
  rendu HDR → bloom soft-knee → profondeur de champ (bokeh hexagonal) →
  composite fusionné (aberration chromatique, étalonnage, vignette, grain
  animé, dithering) → FXAA. L'étalonnage de jour est passé du lavis « Los
  Santos » (désaturé, noirs bleutés levés) au grade **cleanDay** — « des
  couleurs nettes » : pente quasi neutre, noirs posés, saturation > 1,
  brouillard réduit de moitié, aberration/grain/bloom fortement baissés,
  netteté relevée. La nuit du café fermé garde son grade « vinewoodNight ».
- **Éclairage** : environnement IBL (les métaux réfléchissent enfin — la
  machine à café est en inox, pas en béton), contraste chaud/froid (fenêtre
  froide, pratiques chaudes), ombres nettes, brouillard atmosphérique, néon.
- **Matière** : table en lames de bois vernies (clearcoat), briques au bon
  ratio avec crasse en bas de mur, normal maps dérivées automatiquement des
  textures procédurales, ombres de contact sous chaque objet.
- **Caméra** : **fixe, en plan large** — reculée à 2,6 m de la table (fov 52)
  pour que le café entier — comptoir, caisse, ardoise, bar de fenêtre — fasse
  partie du plan, angle d'assise légèrement décentré, respiration
  imperceptible. Pas de plans de coupe (choix délibéré). Pendant qu'il parle :
  letterbox + sous-titres façon jeu vidéo. La feuille survolée vient à la
  rencontre de la caméra (elle serait illisible sinon).
- **Voix** : mp3 enregistrés ; la bouche de Simon est synchronisée à
  l'amplitude réelle de l'audio (AnalyserNode), pas à un métronome.

Trois paliers de qualité auto-détectés (mobile → effets réduits), sonde de
framerate, et `prefers-reduced-motion` respecté partout (caméra immobile,
grain figé, figurants calmes).

## 5. L'accessibilité n'est pas une option

- Le **CV texte** (`#cv-text`) est du markup statique complet : lecteurs
  d'écran, clavier, crawlers, visiteurs sans WebGL — tous ont tout.
- Les sections parlées sont **sous-titrées** (répartition au prorata sur la
  durée du mp3 ; la synthèse vocale de secours sous-titre phrase par phrase).
- Navigation clavier complète : `1`–`5` (les sections du CV), `6`–`9` (le
  second palier, une fois ouvert), `0` (l'outro), `espace` (le faire taire, ou
  reposer la feuille), `M` (couper le son), `Échap`.
- Si la 3D échoue (pas de WebGL, driver, three.js absent), le CV texte
  **devient** la page — le shell `VC` vit dans un script séparé précisément
  pour survivre à la mort de la scène.

## 6. Sous le capot

```
index.html          Tout : markup, CSS, shell VC, ping, scène 3D (~3 400 lignes)
cafe.obj.txt        Le café lui-même — vrai modèle 3D, ~95 k triangles
                    (5,1 Mo bruts, ~980 Ko sur le fil)
tex/*.png           13 étiquettes cuites — armoire à trophées, diplômes, van (376 Ko)
person.obj          Corps des PNJ masculins — base mesh en 15 segments (547 Ko)
three.min.js        three.js r134, vendorisé
fonts/*.woff2       Space Grotesk · Inter · Caveat, auto-hébergées
audio/en/*.mp3      La voix de Simon, une piste par clip (15 clés, cf. README)
audio/en/v1/*.mp3   Les enregistrements v1, retirés du circuit — jamais chargés
audio/music/*.m4a   Les trois pistes du jukebox — composées par preprocess_music.py,
                    chargées paresseusement (rien avant le premier play)
preprocess_music.py La partition : un mini-DAW numpy + afconvert (AAC 128k)
og.jpg              Carte de partage 1200×630
```

**Le cast capsule a eu sa passe d'anatomie** (2026-08-22) : des **mains à
cinq doigts** (paume, quatre doigts, un pouce — géométries partagées par les
neuf personnages et moins chères que la boule qu'elles remplacent), des
**oreilles** (de profil, tout le monde était un œuf, et c'est l'angle où la
caméra passe sa vie), des **épaules soudées au corps** — une coupole de
deltoïde enterre son bord interne dans le torse, l'emmanchure rentrée d'un
centimètre — et **un cou qu'on voit** : le pad de trapèze s'arrêtait à un
centimètre et demi sous le crâne, ce qui donne une tête posée directement sur
les épaules. Simon a eu le même traitement : col descendu, tête remontée à
1,67 (`SIMON_HEAD_Y`, autour de quoi la boucle d'animation la fait respirer). Pas plus — à .198 le torse (qui s'évase à .205 à
l'ourlet) avalait le bras entier : de face, plus personne n'avait de bras.
Attaché, oui ; absorbé, non. Enfin **la moitié du café est féminine**
(`fem`) : cheveux longs tombant sur la nuque, et la silhouette que demande la
fiche morphologique — épaules/hanches 1,45 chez l'homme, 0,92 chez la femme,
lui qui s'affine à la taille, elle qui s'évase à la hanche. Cheveux détachés
veut dire oreilles couvertes (pas dessinées du tout, plutôt que dessinées et
traversant les mèches), et la masse passe **derrière** la gorge, pour que le
cou se lise devant les cheveux.

**[`ANATOMIE.md`](ANATOMIE.md) fait foi** — deux fiches morphologiques et cent
critères d'articulation — et ce n'est pas de la doc décorative : la table
`LIMITS` encode ces critères et s'applique dans `applyPose()`, le seul endroit
où toutes les poses atterrissent. Un coude ne s'hyperétend pas, un genou ne
plie pas à l'envers, une charnière ne plie pas de côté, et rien ne tourne à
plus de 300°/s — quoi qu'écrive une gesticulation ajoutée plus tard. Ce garde-
fou existe parce que l'inverse avait déjà échoué : la pose de repos de Simon
tenait un coude à +.5, avant-bras replié à l'envers hors du bras, pendant des
mois sans que personne le voie.

La pose de frappe est **résolue, pas estimée** : cinématique inverse à deux
segments sur les vrais chiffres (épaule à 1,335, clavier à 1,231 et .50 devant,
bras .30, avant-bras .25) — les poignets tombent sur les touches, là où les
angles choisis à la main les laissaient 12 cm trop bas et pointés dans le
vide.
Le passant et l'invité tirent leur genre au sort avec le reste du vestiaire
dans `reskin()`. Et **l'horloge du mur tourne** — heure locale du visiteur,
trotteuse comprise, au lieu d'être figée à l'heure du chargement.

**Les corps `person.obj` sont RETIRÉS** (`USE_PERSON_MESH=false` dans la
scène) : à côté du cast capsule, les corps segmentés faisaient mannequins en
loques — « ils ne ressemblent à rien » (Simon, 2026-08-12). Les capsules sont
redevenues le look, cohérentes avec Simon qui a toujours été sur mesure. Tout
le pipeline de swap reste dans le fichier et l'asset dans le repo pour un
futur mesh mieux découpé : FinalBaseMesh décimée à ~10 k triangles, découpée
hors-ligne en quinze segments exportés **dans le repère local de
l'articulation du rig qui les porte** — le swap retire le cylindre sous
l'articulation et pose le segment au même endroit, et tout le système de vie
(regards, tours de parole, gorgées, marche, `reskin()`) pilote l'un ou
l'autre corps sans une ligne changée. Remettre le flag à `true` pour
réessayer.

**Le décor est un modèle, plus une reconstruction.** `cafe.obj.txt` (murs,
devanture vitrée avec porte et enseignes, comptoir noyer + marbre, machine à
laiton, caisse à touches, vitrine, frigo à sodas et sandwichs, cinq tables, bar
de fenêtre, suspensions, plante, paillasson) est prétraité hors-ligne en
**coordonnées monde définitives** : la table T1 devient celle de Simon (plateau
élargi ×1,5 pour la feuille, chaise pivotée face caméra, plateau exactement à
y = 0,8025 — la hauteur que tous les ancrages existants supposent) et carte
décalée hors de la tête de Simon. La scène le parse elle-même (~60 lignes — pas
d'`OBJLoader` dans le build r134, pas besoin : le fichier est notre propre
sortie) et fusionne les faces par matériau : ~55 draw calls pour tout le café.
Les 72 `usemtl` français du modèle (`chene_sol`, `laiton`, `marbre`,
`platre_vert`…) reçoivent les textures procédurales existantes — l'ardoise des
prix est repeinte par `drawMenu()`, face CLOSED comprise, et les trois ampoules
restent des meshes séparés pour que la fermeture puisse en éteindre deux. Si le
fetch échoue : la salle disparaît mais table, Simon et feuille sont
procéduraux — la conversation survit sur un parquet nu.

**Le `.txt` n'est pas une coquille.** Pages sert le `.obj` en
`application/x-tgif`, un type que le CDN refuse de compresser : l'ancien modèle
partait entier, 1,35 Mo. En `text/plain` le même fichier gzippe à mieux que
5:1 — un modèle presque quatre fois plus gros arrive donc **plus léger** que
celui qu'il remplace (~980 Ko contre 1,35 Mo). Le loader fait un `fetch` et
parse du texte ; l'extension ne lui dit rien.

**Ce que la carte de 2026-08-14 a apporté.** Un **mur avant** — invisible
jusqu'ici parce que le modèle ne le construisait pas — avec l'armoire à
trophées de Simon (PSPO, PSM I, Dynamics 365, Azure, le diplôme Solvay, Le
Wagon) ; et un **vrai dehors** derrière la devanture : trottoir, parking marqué,
van « ICE CUBE », voiture, lampadaires et une lisière d'arbres. Les étiquettes
de l'armoire sont des PNG cuits sous `tex/` (elles portent des intitulés
décernés et des marques éditeur, qu'aucun peintre procédural ne réinventera) ;
le reste du décor reste procédural.

Le préprocesseur ne se contente plus de rejouer les trois gestes de mise en
scène : il **jette** les trois articles encadrés du mur avant (`DROP_NAMES`),
**remet d'équerre les huit roues** — l'export les monte de profil, disques dans
le plan y/z alors que les deux véhicules roulent selon x —, **recopie le
lettrage ICE CUBE sur les portes arrière** du van (la carte ne lettre que les
flancs, et depuis la salle c'est l'arrière qu'on voit : il est garé nez dehors)
et **déplace la plante** du coin avant-gauche vers le mur avant, pour libérer le
seul pan de mur où une porte de toilettes tient. Il **clone** enfin la
camionnette une place de parking plus loin, pour une deuxième boîte —
*BravoReno, votre électricien avec qui le courant passe* — avec son propre
matériau de lettrage, que la scène peint (`drawBravo()`). La sélection se fait
par **boîte englobante** et non par groupe : à l'export, tout le dehors est un
seul groupe, et une primitive ne compte que si elle tient **entièrement** dans
la boîte — c'est ce qui garde les 8 000 triangles d'asphalte hors du clone.

Les PNG d'étiquettes se chargent avec **`flipY=false`**, et c'est tout le
piège : l'exportateur écrit du glTF, où `v=0` est le HAUT de l'image, et il
concilie ça avec three.js en retournant les pixels à l'écriture — les fichiers
sont donc stockés à l'envers. Une texture canvas sur les mêmes UV (l'ardoise,
l'enseigne de porte) sort à l'endroit parce que ses pixels n'ont jamais été
retournés ; passer un PNG pré-retourné dans le même réglage par défaut le pose
sur la tête. Couper `flipY` annule le retournement de l'exportateur au lieu de
le répéter.

**Contraintes assumées** : vanilla JS, aucun build, aucun bundler, aucun CDN
(tout est vendorisé — vie privée du visiteur + déterminisme des polices peintes
en canvas). Trois `<script>` étanches : le shell `VC` (survit à tout), le ping
`VCPing` (compteur de visites minimal et respectueux — pas de cookie, pas d'IP,
GPC/DNT honorés — et interrupteur « bar fermé » pilotable depuis Jarvis), puis
la scène.

**Le café peut fermer** : si l'interrupteur distant répond `{"open":false}`,
la salle se vide, deux pendants s'éteignent, l'ardoise passe côté « CLOSED » —
et le CV texte reste servi, parce que le CV est le but de la page. Toute panne
du ping laisse le café **ouvert**.

## 7. Déploiement

```
git push  →  GitHub Pages  →  ndashiz.be/virtualcoffee/
             (~1-2 min de build, puis ~10 min de cache Cloudflare)
```

Pas de serveur à redémarrer. Le VPS ne répond qu'à une question (ouvert ou
fermé ?) ; le CV lui-même ne dépend jamais d'une machine personnelle.

En local :

```bash
npx serve -l 4321 .
```

## 8. État et suite

**En prod** : tout ce qui précède — décor `cafe.obj.txt`, personnages capsule
(les corps `person.obj` sont débranchés), grade `cleanDay`, entrée
**pilotable aux flèches** avec caméra à la troisième personne et balise sur la
chaise (ou au clic sur le sol ; l'entretien démarre à l'entrée dans l'anneau),
plan large fixe une fois assis, mute mémorisé, et un vrai contact visuel entre
Simon et son invité.

**Bloqué — Sophia à la caisse** : le package Renderpeople téléchargé
(`41-rp_sophia_animated_003_idling_ue4`) est la variante **UE4** : son FBX ne
contient que l'animation (1 047 courbes, zéro géométrie — vérifié dans le
binaire), le mesh est enfermé dans `rp_sophia_rigged_003_ue4.uasset`,
inexploitable hors Unreal. Il faut re-télécharger le même produit en variante
**FBX standard** (3ds Max/Maya/C4D/Blender) ou OBJ — le pipeline (pose d'idle
figée via Blender headless, décimation, quantification, placement caisse à
(-1.11, 0, -4.33) face +z) est prêt dans `preprocess_person_obj.py` et la
session sait le rejouer. Côté budget, le passage au `.txt` compressé a rendu de
l'air : le décor coûte ~980 Ko sur le fil au lieu de 1,35 Mo, et les étiquettes
376 Ko — la page reste sous le plafond de 8 Mo malgré un modèle trois fois plus
lourd. Prévoir tout de même dif en 768 px et ~12 k triangles.

**Sur la table, non fait** :
- `og.jpg` à re-rendre — l'aperçu LinkedIn/Slack montre encore l'ancien look
  (d'autant plus vrai depuis le passage au modèle et au plan large) ;
- l'ambiance sonore (murmure de salle, babil des conversations, sifflement du
  percolateur) — le code prévoit la dégradation silencieuse, il manque les
  boucles audio ;
- une passe de silhouette sur Simon (jonctions des coudes) — et, un jour, le
  même traitement base-mesh pour lui et pour un corps féminin (la buveuse) ;
- **la fenêtre côté rue est faite** (parking, van, lisière d'arbres derrière la
  devanture), **la fenêtre du mur gauche non** : elle garde le dégradé de ville
  peint. La carte livrait bien une forêt de ce côté-là, élaguée à la demande —
  seuls les arbres côté parking sont embarqués ;
- l'armoire à trophées est en **français** (« MON PALMARÈS », « Parcours
  certifié », « Diplôme ») sur une page passée à l'anglais seul. Les intitulés
  décernés (Microsoft Certified, Full Stack Developer, PSM I) le sont déjà en
  anglais ; il n'y a que l'habillage à reprendre, dans la carte ou en
  repeignant `plaque_palmares` et les `etq_*` en procédural.

**Documents de travail** (non publiés, dans le dossier du projet) :
- `ART_DIRECTION_GTA5.md` — la revue de direction artistique complète ;
- `BRIEF_IA_3D.md` — le brief d'implémentation exhaustif (5 000 lignes) ;
- `preprocess_cafe_glb.py` — **le** prétraitement du décor : lit
  `~/Downloads/cafe.glb` (l'export glTF-binaire de l'outil de mise en scène,
  18,3 Mo, 414 k triangles), aplatit l'arbre de nœuds en monde (1 940 des
  3 789 nœuds portent une rotation ou une échelle : matrice 4×4 complète,
  normales par l'inverse-transposée), élague, re-met T1 en scène, quantifie,
  déduplique et sort `cafe.obj.txt` + les PNG de `tex/`. À relancer à chaque
  réexport ; les ancres monde qu'il imprime sont celles du code de scène.
  Ce qu'il jette, et pourquoi :
  - `moi_au_comptoir` et `moi_assis_table_haute` (90 k triangles) — deux Simon
    cuits en dur, alors que la scène en anime déjà un et pilote tout un cast ;
  - la forêt hors du **cône de la devanture** (229 k triangles sur 280 k) : un
    cône depuis la table de Simon vers les deux montants de la porte, élargi
    ×1,6 pour le débattement de la caméra, borné à 50 m. Ne restent que les
    arbres côté parking, ceux qu'on peut réellement voir ;
- `preprocess_cafe_obj.py` — **périmé**, gardé pour mémoire : il lisait l'ancien
  export Wavefront. L'outil exporte désormais du glTF ;
- `preprocess_person_obj.py` — la découpe qui a produit `person.obj` depuis la
  FinalBaseMesh (`~/Downloads/fdx54mtvuz28-FinalBaseMesh.rar`). Étape amont :
  décimation à ~10 k tris dans Blender headless (importer l'OBJ, TRIANGULATE
  puis DECIMATE, exporter `person_dec.obj` — cinq lignes de bpy). Le script
  détecte entrejambe/cou/axes de bras, affecte les faces par région, et sort
  chaque segment dans le repère local de son articulation (`HUMAN_PARTS` dans
  index.html liste le mapping articulation → segment → slot).

---

*three.js — MIT · Space Grotesk, Inter, Caveat — SIL OFL 1.1 · Voix : Simon
Goffin · Construit en vanilla JS avec une assistance IA, ce qui est un peu le
sujet de la page.*
