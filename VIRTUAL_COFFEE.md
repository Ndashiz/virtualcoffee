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
| L'outro (ou touche `0`) | Il conclut, puis le café ferme (le lien LinkedIn, lui, est là depuis la première option) |
| Pastille ⏭ Skip ou `espace` | Le fait taire — la section reste alors non entendue |
| « 📄 See the resume » / « ⬇ Download it » / « in — LinkedIn » | Sous la boîte dès la première option, même pendant qu'il parle : la feuille remonte (au doigt, c'est la visionneuse plein écran qui s'ouvre — voir plus bas), le CV se télécharge (le **PDF**, `CV_Simon_Goffin_2026.pdf`), ou le profil s'ouvre |
| « 🚶 Leave the table » | Il se lève (même animation qu'à l'assise, jouée à l'envers) et la salle est à vous ; l'anneau se rallume, et en revenant s'asseoir la boîte rouvre telle quelle — sections validées, palier, outro compris |
| Les tables de la vitrine | Deux clients épisodiques entrent par la porte, s'installent aux tables du devant et repartent — les chaises de la vitrine ne sont plus jamais toutes vides bien longtemps |
| Le serveur | Plateau en main, il porte un café à qui vient de s'asseoir — posé **devant** le client, pas au milieu de la table — et revient débarrasser la tasse quand la place se libère |
| Le jukebox du mur avant | Silent disco : casques sans fil, cinq habitués qui viennent danser sur l'audio réel ; la voix de Simon garde toujours la priorité (ducking), s'asseoir renvoie la foule, le son suit la distance à l'émetteur |
| Version texte (sans WebGL, café fermé, ou lien d'évitement au clavier) | Le CV complet, accessible et indexable — sa croix ✕, `Échap` ou un clic dans la marge sombre la referment. La pastille qui l'ouvrait a disparu du café : la feuille sur la table et « See the resume » font le travail |

Sur mobile, la boîte devient un panneau en bas d'écran, sur deux colonnes. Et
« See the resume » n'y remonte pas la feuille : une A4 cadrée dans un téléphone,
c'est 5 px de corps de texte, et la boîte de dialogue — pleine largeur en bas —
en couvre le tiers inférieur. Au doigt, le bouton ouvre donc le CV dans la
visionneuse des journaux : page entière, corps à 17 px, qui se déplace sous le
doigt, et au-dessus de la boîte au lieu d'être dessous. La feuille 3D, elle,
remonte toujours quand on s'assoit, sur tous les appareils.

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
- **Un visiteur épisodique** — entre côté porte, vient lire la carte devant le
  bar, repart. Jamais de demi-tour sur place : il sort comme les gens
  sortent.
- **Tout le monde regarde** — système de regard « les yeux mènent, la tête
  suit », clignement des paupières déclenché par les changements de fixation,
  respiration permanente. L'horloge murale est à l'heure réelle.
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
c'était « pas de presse inventée » : au mur avant pendent désormais,
chacune sous sa lampe à tableau, quatre unes du **Daily Salfari** (`drawArticle()`, même homonymie
douteuse que l'employé du mois) — l'immeuble retapé seul en deux ans
(électricité, plomberie, maçonnerie), le premier triathlon après un an de
préparation, le studio web + IA en indépendant complémentaire, et le mandat de
syndic bénévole de sa propre copropriété (ACP Roodebeek, trois propriétaires,
quatre lots : travaux, appels de provisions, normes légales). Chacune dans un
cadre de chêne à passe-partout ivoire, avec son illustration à l'encre, lisible en zoom
comme tout ce qui s'accroche à un mur — et **une flèche de chaque côté passe
à l'article suivant** sans qu'il faille retourner au mur.
Reste aussi le petit cadre : **« Employee of the Month — Tonio Salfari »**,
décerné pour services rendus derrière un comptoir où personne ne l'a jamais vu.
Peint en canvas comme la carte (`drawEotm()`), repeint sur `VC.fontsReady`.

**Deux télés, un seul flux : HENRY TV** — depuis le 2026-09-29 un vrai petit
plateau en 3D rendu dans une texture : une présentatrice issue de la chaîne
des vrais personnages (blazer bordeaux, bureau laqué, éclairage trois
points), qui parle, cligne des yeux et baisse le regard vers ses notes ; un
écran derrière elle avec un graphique de bourse qui se trace, ou une vraie
scène — le PDG de NdaBank en costume anthracite et cravate, au pupitre en
noyer devant le mur de logos bleu marine, micros de presse et flashs ; les
drapeaux européens devant une façade de verre ; une salle des marchés de
nuit. Pour ces trois sujets, la régie coupe sur l'image plein écran au milieu
du sujet, puis revient à la présentatrice, comme au journal. La petite au-dessus du bout du
comptoir, entre la toile et la carte — depuis la chaise, elle tombe juste
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
(z 2,35→3,94) : vantail affleurant en chêne, cadre bronze fin, tirant
bronze vertical et pictogramme sur un rond de bronze. La
plante qui occupait ce coin a été déplacée le long du mur avant par le
préprocesseur — une porte derrière un ficus n'est pas une porte.

**Et il y a un jukebox — une silent disco.** Sur le mur avant, entre les
unes du Daily Salfari et la plante : un meuble en noyer et laiton brossé à arche lumineuse, repéré
et cliqué comme la plaque ou les télés (même bulle, même tap), mais qui
ouvre un lecteur au lieu d'une image. On choisit un morceau et il distribue
des **casques sans fil** : votre personnage enfile le sien, cinq habitués
(jamais le barista — quelqu'un tient le bar ; jamais la lectrice — dans tout
vrai café quelqu'un ignore la fête) lâchent ce qu'ils faisaient, traversent
la salle en décalé, décrochent un casque du rail en arrivant et dansent sur
**l'amplitude réelle de la piste** — RMS par image, chacun avec sa phase, sa
vitesse et son amplitude propres, jamais de clones. Le signal faiblit avec
la distance caméra→émetteur (plancher à 25 %, jamais coupé), la voix de
Simon écrase la musique quand elle joue déjà (duck à 20 %, relâché 500 ms
après la réplique) ; dans l'autre sens c'est une coupure, pas un duck :
**lancer la musique pendant qu'il parle l'arrête net**, comme la pilule
skip — le clic est la réponse du visiteur, et seul un vrai geste le fait
(l'enchaînement automatique en fin de piste ne le fait jamais taire). Et
**s'asseoir termine le silent disco en entier** — la table est le
territoire de la voix : casques retirés, chacun regagne exactement la
position et l'orientation enregistrées à l'init de la scène, la musique
s'éteint en fondu. Quatre pistes, toutes des chansons de Simon fournies en
master fini — « Balance Sheet Heart », « The Verdict Is The Prod »,
« Arbitrage », « It's the PO » — qui remplacent les trois rendus de
`preprocess_music.py` (toujours dans l'historique git, le script reste
comme partition). Chaque bpm est mesuré sur l'audio parce que l'horloge des
danseurs le lit ; quand la maille des attaques et la structure d'accents
divergent d'une octave, la foule danse le temps ressenti. Et ça se voit
qu'une piste joue : **un CD tourne dans le dôme vitré du meuble** tant que
la musique est à l'antenne — reflets asymétriques exprès, un disque
parfaitement radial tournerait invisiblement — et ralentit en fondu à la
pause au lieu de geler ; le panneau porte le même disque en CSS, animé par
le même état. Pendant qu'une piste joue, les trois suspensions du comptoir
passent en **gélatines de boîte de nuit** — trois roues de teinte décalées
d'un tiers de tour, l'intensité sur le niveau réel de la piste, la lumière
chaude s'effaçant aux deux tiers, les globes opalins prenant eux-mêmes la
couleur, et les réglettes de l'armoire à trophées avec trois lavages
muraux sur les unes, sur la même roue un demi-tour plus loin — la foule danse sur des places écartées
pour que **deux danseurs ne puissent jamais se toucher**, et regarde **le
visiteur** trois regards sur quatre. La sortie du HUD est un bouton en
toutes lettres (« ⏏ Stop the music ») plutôt qu'un pictogramme à deviner.
Sonde console : `__jukebox()`.

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
  netteté relevée —, puis, avec la passe de design 2026, au grade
  **atelier** : pente quasi neutre, contraste doux (1,07), saturation 0,97
  (la palette terreuse porte déjà sa couleur), effets réduits à ce que fait
  un bon objectif, sur une courbe ACES ajustée (Hill). La nuit du café
  fermé garde son grade « vinewoodNight », réexposé pour cette courbe.
- **Éclairage** : environnement IBL (les métaux réfléchissent enfin — la
  machine à café est en inox, pas en béton), contraste chaud/froid (fenêtre
  froide, pratiques chaudes), ombres nettes, brouillard atmosphérique.
- **Matière** : table en lames de bois vernies (clearcoat), briques au bon
  ratio avec crasse en bas de mur, normal maps dérivées automatiquement des
  textures procédurales, ombres de contact sous chaque objet.
- **Caméra** : **fixe**, un ≈ 30 mm (fov 40) à 1,32 m, par-dessus l'épaule
  du visiteur, Simon à droite du centre et la carte entière dans le cadre ;
  objectif **à décentrement** (caméra de niveau, verticales droites),
  respiration imperceptible. Pas de plans de coupe (choix délibéré). Pendant qu'il parle :
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
people.bin          Les corps du cast, vêtements et cheveux compris — un maillage
                    skinné par personne, deux niveaux de détail (~1,1 Mo)
people/             Le pipeline Blender hors ligne qui écrit people.bin
person.obj          Corps segmentés retirés (USE_PERSON_MESH=false, jamais chargés)
three.min.js        three.js r134, vendorisé
fonts/*.woff2       Space Grotesk · Inter · Caveat, auto-hébergées
audio/en/*.mp3      La voix de Simon, une piste par clip (15 clés, cf. README)
audio/en/v1/*.mp3   Les enregistrements v1, retirés du circuit — jamais chargés
audio/music/*       Les quatre pistes du jukebox — les chansons de Simon,
                    chargées paresseusement (rien avant le premier play)
preprocess_music.py Un mini-DAW numpy + afconvert (AAC 128k) — la partition des
                    trois pistes d'origine qu'elles remplacent (vivantes dans git)
og.jpg              Carte de partage 1200×630
```

**Les personnages sont de vrais corps (2026-09).** Tout le monde dans la salle —
le cast, les figurants, l'invité et Simon — est désormais **un seul corps
continu et skinné** et non plus un empilement de capsules. `people.bin` porte la
FinalBaseMesh re-posée dans la pose de repos du rig et pondérée par chaleur
**sur les noms d'articulations du rig lui-même** : un `THREE.Skeleton` se lie
directement aux `THREE.Group` que `buildPerson()` fabrique déjà. Toutes les
couches de comportement, `applyPose()` et ses `LIMITS`, les assises et les
accessoires pilotent les mêmes articulations : rien de la façon dont les gens
bougent n'a été réécrit. Les capsules sont toujours construites d'abord et
remplacées à l'arrivée du fichier (`realizeRig()`) ; si le téléchargement
échoue, l'ancien cast reste en place.

- **Habillés, pas peints.** T-shirt, chemise, pull, blazer, pantalon,
  chaussures et tablier de bistrot sont des coques taillées dans le corps hors
  ligne : ourlets tirés au cordeau, tissu qui tombe de la poitrine et des
  omoplates au lieu de coller dessous, manches qui s'effilent. Les faces du
  corps couvertes par un vêtement sont retirées au chargement, et corps +
  vêtements + cheveux fusionnent en **un seul appel de rendu par personne**
  (une trentaine pour une capsule).
- **Visages.** Les yeux de la tête de base sont ouverts ; de vrais globes
  tournent dans les orbites, sous des paupières supérieures posées sur l'iris
  qui suivent un regard vers le bas. Sourcils, cils, lèvres, barbe et barbe
  naissante, duvet de la ligne d'implantation et rides sont peints, personne
  par personne, sur un canevas projeté autour de la tête. Huit coupes de
  cheveux, chacune une coque qui s'amincit jusqu'à rien à la ligne
  d'implantation.
- **Qui ils sont.** `fem` et `heavy` sont des champs de déplacement appliqués
  au corps, aux vêtements, aux cheveux et aux articulations à la fois (épaules,
  taille, hanches, poitrine, mâchoire, arcade, nez, lèvres ; ventre et
  membres). La taille raccourcit le haut du corps et ne passe **jamais** par
  `root.scale` (voir CLAUDE.md). La fiche du cast — qui porte quoi, quelle
  coupe, quelle barbe — c'est `REAL_TOPS` / `REAL_HAIR` / `REAL_BEARD` /
  `REAL_TRAITS`.
- **Simon** est lui aussi un vrai corps, assis à sa table, les mains posées
  par une petite résolution d'IK, en blazer marine avec les lunettes rondes
  écaille, la moustache et le petit bouc de la photo. Les anciennes poignées
  de tête, d'yeux et de bouche sont relues sur lui à chaque image
  (`mapSimon()`), et sa voix ouvre une vraie bouche.
- **Coût.** Un `MeshStandardMaterial` par personne (programme partagé) avec un
  `onBeforeCompile` pour la peinture, le micro-relief de la peau et des tissus
  et le reflet des cheveux. LOD1 (~35 % des triangles) au-delà de 6 m, et
  partout sur les appareils tactiles sauf Simon. Appels de rendu 772 → 319
  (bureau), triangles 242 k → ~435 k dans la passe principale.

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
restées le look jusqu'aux vrais corps continus décrits plus haut (elles restent
le repli si `people.bin` ne se charge pas). Tout
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
de fenêtre, suspensions, plante, paillasson — habillés depuis autrement par la
passe de design, §6 bis) est prétraité hors-ligne en
**coordonnées monde définitives** : la table T1 devient celle de Simon (plateau
élargi ×1,5 pour la feuille, chaise pivotée face caméra, plateau exactement à
y = 0,8025 — la hauteur que tous les ancrages existants supposent) et carte
décalée hors de la tête de Simon. La scène le parse elle-même (~60 lignes — pas
d'`OBJLoader` dans le build r134, pas besoin : le fichier est notre propre
sortie) et fusionne les faces par matériau : ~55 draw calls pour tout le café.
Les 72 `usemtl` français du modèle (`chene_sol`, `laiton`, `marbre`,
`platre_vert`…) ne sont plus qu'un point de départ depuis la passe de design :
le chargeur réattribue chaque objet au matériau de son RÔLE (`REMAT`), écarte
ce que le nouveau mobilier remplace (`HIDE`) et garde la boîte englobante de
tout ce qu'il reconstruit (`CAPTURE` → `CAFE.boxes`) — la carte des prix est
repeinte par `drawMenu()`, face CLOSED comprise, et les trois ampoules
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
matériau de lettrage, que la scène peint (`drawBravo()`). La sélection se
fait par **boîte englobante** et non par groupe : à l'export, tout le dehors
est un seul groupe, et une primitive ne compte que si elle tient
**entièrement** dans la boîte — c'est ce qui garde les 8 000 triangles
d'asphalte hors du clone.

**Le van a un livreur — et il livre EN SALLE** (2026-08-23). Sur une
boucle lente (~55 s, dont l'essentiel portes fermées — le flanc reste une
affiche lisible), le livreur ICE CUBE surgit de derrière la cabine, ouvre
les deux battants arrière — devenus de vraies portes, coupées sur la
couture ICE|CUBE, chacune emportant sa moitié du décalque —, prend deux
sacs de glaçons siglés au seuil, traverse le parking, monte la bordure puis
le seuil (la fonction de sol connaît les trois niveaux), pousse le battant
du café de l'épaule — mains prises — et porte la charge à travers la salle
jusqu'au bout EST du comptoir, par le couloir déjà tracé pour le barista.
Les sacs se posent au sol à l'entrée de l'allée de service, contre le
frigo : le corps du comptoir les cache à la salle, et ce qui se lit est le
geste — il se penche derrière le bar, il se relève les mains vides. Le
barista se tourne pour regarder la livraison atterrir, les clients y
jettent un œil (le livreur pèse plus lourd que la fenêtre dans la loterie
des regards), le passant cède la porte tant que la tournée l'occupe, et la
paire livrée reste au sol jusqu'au réassort du cycle suivant, hors champ.
Le retour est ce qui rend le personnage crédible : mains vides, bras
ballants en opposition, foulée ample, +18 % d'allure, menton levé — contre
l'aller chargé, buste en contre-flexion, bras rigides collés au corps, pas
courts et lourds, regard au sol. Une demi-seconde d'arrêt au van, il
repousse les deux battants, puis regagne la cabine par le nez. Derrière les
portes, la scène construit la soute que la carte n'a jamais eue (la face
arrière de la caisse fermée est retirée au chargement) : parois sombres,
plancher alu clair, palette entamée, et une réglette 6500 K au linteau — la
seule lumière froide d'une scène chaude, et c'est elle qui dit « frigo ».
Une marque, trois supports : le même canvas floque son t-shirt (poitrine et
dos, à cheval sur la couture UV du cylindre du torse) et les sacs ; le van
garde son PNG cuit.

Autour de la tournée, le dehors a grandi (2026-08-23, Simon aux manettes
depuis la chaise) : les trois véhicules sont **regarés sur la grille des
lignes** qu'ils chevauchaient (corrigé dans le préprocesseur ET dans l'OBJ
livré) ; le fond peint derrière la baie est devenu **sa vraie skyline** —
une maison Big Four et les deux banques dont le café parle déjà, *NdaBank
Private Wealth* et *HENRY Investment Bank*, noms en plaques taillées pour
survivre à la vitre ; et **l'homme volant s'arrête** désormais : il entre,
se pose devant la baie, y flotte un temps à regarder la salle — la loterie
des regards laisse le bar de fenêtre le surprendre — puis repart dans son
sens. La carte d'accueil énonce enfin les vraies règles : le cercle jaune
est où l'entretien commence, et le café cache le reste — approchez-vous des
objets, une bulle dit ce qu'ils savent faire. À l'intérieur, l'écran du
client au comptoir fait tourner LazyPO (board de sprint, burndown), et les
deux faces de l'enseigne VIRTUAL COFFEE comme le bandeau de l'armoire à
trophées se lisent enfin à l'endroit — le canvas de l'enseigne était peint
en miroir pour ses deux quads, le PNG du bandeau stocké tourné de 180°.

Les PNG d'étiquettes se chargent avec **`flipY=false`**, et c'est tout le
piège : l'exportateur écrit du glTF, où `v=0` est le HAUT de l'image, et il
concilie ça avec three.js en retournant les pixels à l'écriture — les fichiers
sont donc stockés à l'envers. Une texture canvas sur les mêmes UV (la carte,
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
la salle se vide, deux globes s'éteignent, la carte passe côté « CLOSED », une
lumière de nuit remplace celle du jour et les réverbères s'allument —
et le CV texte reste servi, parce que le CV est le but de la page. Toute panne
du ping laisse le café **ouvert**.

## 6 bis. La passe de design 2026 — « l'Atelier »

Le café parlait cinq langues à la fois (laiton de bistrot, tapis de diner,
poutres rustiques, vitrine d'entreprise, caisse de musée) ; il n'en parle plus
qu'une : le **minimalisme chaud bruxellois**. Le dossier complet, espace par
espace, est [`DIRECTION_ARTISTIQUE_2026.md`](DIRECTION_ARTISTIQUE_2026.md).
La règle : l'**architecture** est claire et minérale (chaux, chêne clair,
travertin), **tout ce qui se déplace** est sombre et chaud (noyer, bronze noirci,
cuir cognac), et **un seul mur** — le fond du bar, derrière Simon — est olive
profond, parce qu'un visage se lit sur un fond sombre.

- **Rien n'a bougé** : chaises, tables, tabourets, globes et plante sont
  reconstruits sur les boîtes englobantes du modèle, jamais sur des
  coordonnées tapées — assises 0,503, tabourets 0,8051, plateaux 0,8025, tous
  mesurés dans la page. Aucune route à ré-auditer.
- **Une lumière dont on voit la source** : globes opalins au-dessus du bar, un
  grand au-dessus de la table de Simon (le spot est dedans), corniche
  lumineuse sur le mur olive, lampe à tableau sur chaque une, socle du
  comptoir rétroéclairé ; le reste est **cuit** dans des light maps peintes au
  canvas.
- **Le rendu** : environnement qui est une maquette de la nouvelle salle (il
  fait la lumière de rebond), environnement propre pour la rue, dôme de ciel,
  ACES ajusté (Hill), grade `atelier`, SSAO sur le profil « high ».
- **Retirés** : le tapis rond, le ventilateur, le néon, les deux affiches, les
  appliques laiton, la caisse enregistreuse, l'ardoise (devenue une carte
  typographiée, côté CLOSED compris). **Ajoutés** : un radeau de lattes de
  chêne, une grande toile, un strelitzia, une tablette de caisse.
- **Coût** : 771 appels de rendu contre 758 et 238 k triangles contre 215 k sur
  ordinateur ; 489 / 214 k contre 476 / 189 k sur téléphone, où les grandes
  textures et les light maps sont peintes à demi-résolution.

### Audit DA, phase 1 (2026-09-29)

Les gains rapides de l'audit de direction artistique en dix axes :

- **Cadrage** : ≈ 30 mm au lieu de ≈ 21 mm (fov 40), caméra à 1,32 m, Simon
  à droite du centre, carte entière ; objectif à décentrement
  (`setViewOffset`) pour des verticales droites. Arrêt de Superman re-mesuré
  depuis ce plan : inchangé (13 articulations sur 13 visibles).
- **Deux globes encadrent la carte** au lieu de trois qui la coupaient
  (`BAR_GLOBES` : les deux seules places libres entre la télé et la carte,
  depuis toutes les caméras de jeu).
- **Vapeur** : un ruban de fumée au lieu de cinq sphères.
- **Machine à espresso retournée** (les groupes côté barista, `MACHINE_TURN`
  dans le parseur), inox brossé, tasses sur le chauffe-tasses, plaque en
  laiton côté salle.
- **Viennoiseries** : un vrai croissant roulé (`croissantGeo`) dans
  l'assiette de Simon, la vitrine du comptoir garnie de croissants et de
  pains au chocolat.
- **Frigo** : intérieur anthracite, LED dans le cadre et sous chaque
  clayette, jus en bouteille, reflet sur la porte vitrée.
- **Rugosité** : cartes dérivées de la peinture (parquet, travertin, noyer)
  et peintes (cuir, inox) ; globes opalins assombris au bord ; feutre du
  radeau gris chaud, lattes nuancées.
- **La lectrice** du bar de fenêtre se tourne de trois quarts vers la salle.
- **Coût** (plan de jeu, 1440×810) : 292 appels de rendu contre 333, 770 k
  triangles contre 747 k, une lumière de moins ; téléphone 257 / 591 k contre
  269 / 564 k.

## 6 ter. La rue (2026-09-28)

Le dehors lisait comme un écran, pour trois raisons, toutes supprimées :

- **le plan lointain de la caméra était à 25 m** : la rue et tout ce qui
  suivait n'étaient jamais dessinés, et le ciel (des hex bruts lus comme
  linéaires, donc presque blancs) bouchait le trou. `camera.far` passe à 450 ;
  le ciel est un vrai dégradé linéaire, avec le halo du soleil et une couche
  de cumulus qui dérive et se fond dans la brume à l'horizon ;
- **la baie ouest donnait sur une plaque peinte** à 65 cm de la vitre. Elle
  donne maintenant sur une vraie rue à 30 km/h — trottoir, potelets, deux
  jeunes platanes, voitures garées des deux côtés, passage piéton, panneaux —
  et, à 24 m, une rangée de façades bruxelloises : **BIG FOUR**, **NdaBank
  Private Wealth**, une maison de maître blanche, une boulangerie, **HENRY
  Investment Bank**, coupée par une rue transversale, les tours au-delà ;
- **le parking était dans une clairière.** Forêt, glissière et herbe sont
  retirées au chargement (`HIDE`) ; en face, une seconde rangée de maisons
  (une pharmacie et sa croix verte, une brasserie…), et deux îlots ferment
  les côtés du parking.

Comment c'est fait (bloc `THE STREET` d'`index.html`) : **un seul shader
peint toutes les façades** (travées, appuis, châssis et petits bois, rideaux,
briques ou joints de pierre qui s'effacent par axe avant d'aliaser, suie,
vitrines, murs-rideaux, fenêtres allumées la nuit) à partir de huit nombres
par bâtiment — une quarantaine de bâtiments en un seul appel de rendu ; la
rue a **son propre soleil et sa propre brume**, injectés dans ses matériaux
(`streetInject()`) plutôt qu'une lumière de scène qui aurait rééclairé la
salle ; les **voitures sont lissées** à partir d'une silhouette, d'un plan et
d'un « tumblehome » (vernis, vitres teintées, jantes, joints de portes,
plaques belges, ombre de contact) ; les arbres sont des **platanes** à
l'écorce marbrée ; la **profondeur de champ** adoucit ce qui est loin derrière
la vitre ; les camionnettes gardent les caisses du modèle (le livreur est
calé sur leurs portes) et gagnent pare-chocs marchepied, plaques, bavettes,
châssis, baguettes, rails de toit et rétroviseurs. Depuis le 2026-09-29,
tout ce qui est devant la caisse est une **vraie cabine de fourgon**
(pare-brise incliné, capot court, portière vitrée, calandre, pare-chocs
enveloppant, optiques), sur roues arrière jumelées, avec carénage de toit,
passages de roue découpés dans la jupe de la caisse, montants et rail en
alu, et la quincaillerie des portes arrière (charnières, barres de
fermeture, poignée, joint) — qui pivote avec les battants du van ICE CUBE.

**Le menu** est agrandi (2,75 × 1,12 m, de la tête de Simon à l'horloge, de
la machine à 10 cm sous le soffite), en trois colonnes, avec sa propre
applique : il est éclairé comme la salle au lieu de briller tout seul.

**L'homme volant est un homme** : construit par la chaîne des vrais
personnages, 1,88 m, la combinaison peinte au pixel sur le vrai corps, une
cape en tissu qui flotte d'autant plus qu'il va vite, éclairé par le soleil de
la rue. Il survole la rue ouest à trois ou quatre mètres, passe derrière les
jeunes platanes du trottoir, s'arrête au milieu de la rue là où le plan
principal voit à travers la baie, regarde dedans pendant que le comptoir le
regarde, et repart ; son ombre traverse la chaussée. Son point d'arrêt est
**mesuré** : des rayons lancés depuis le plan principal vers treize de ses
articulations, sur une grille de positions — à l'ancien arrêt, un montant de
la baie le coupait en deux ; à x −10,2 / z −12,5 rien ne le masque.

**Le jukebox** porte un bandeau LED ambre sous son fronton : « PICK A RECORD »
(les mots du juke-box, pas ceux du joueur — le « cliquer » est dans la
bulle d'aide de l'interface) clignote tant qu'il est au repos, et
« NOW PLAYING » s'affiche fixe une fois la musique lancée (fixe aussi sous
mouvement réduit). Une guirlande de 27 ampoules fait le tour de l'arche et
descend les montants : chenillard de fête foraine au repos (une sur quatre
allumée, qui court), double éclat de toute la guirlande et du néon toutes les
6,5 s, respiration au rythme du morceau pendant la lecture.

**Le menu se lit depuis la chaise** (7,6 m) : les huit cafés de Simon en deux
colonnes, 54 px sur 832 (7,3 cm au mur), chaque blague sur une ligne, la
boulangerie sur une seule ligne dessous, sans pointillés ; un clic l'ouvre en
grand comme la plaque et les journaux.

**Jamais deux fois la même tenue** : le casting tient en dix couleurs écartées
d'au moins ΔE 16 telles qu'affichées ; le portant des figurants n'en partage
aucune ; chaque tirage (passant, clients de la vitre, invité) prend une couleur
à au moins ΔE 12 de tout ce que portent les autres (`pickDistinct()`). Le
serveur passe en chemise noire et long tablier blanc.

**Les visages de loin** : la version allégée des corps (au-delà de 6 m, donc
la plupart des personnages dans le plan principal) garde désormais la tête
et le cou exactement comme de près. Décimée sans symétrie, elle sortait une
joue plus large que l'autre, et un visage asymétrique se lit comme un visage
décalé. L'avion est un vrai
avion, 330 m plus loin et 110 m plus haut.

Coût mesuré : +13 appels de rendu, +31 % de triangles sur ordinateur, +19 %
sur téléphone (les trottoirs lointains y perdent leurs voitures).

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

**En prod** : tout ce qui précède — décor `cafe.obj.txt`, personnages en vrais
corps skinnés (`people.bin` ; capsules en repli, `person.obj` débranché),
grade `atelier`, entrée
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
- l'ambiance sonore (murmure de salle, babil des conversations, sifflement du
  percolateur) — le code prévoit la dégradation silencieuse, il manque les
  boucles audio ;
- les cheveux longs (la lectrice) tombent encore comme une capuche, et les
  coupes restent des coques pleines : des mèches à bord alpha feraient mieux ;
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
