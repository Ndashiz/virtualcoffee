# Anatomie & articulations — la référence du cast

> Ce fichier fait foi pour tout ce qui touche au corps des personnages de
> Virtual Coffee. Les mesures viennent de deux fiches morphologiques
> fournies par Simon ; les cent critères d'articulation qui suivent sont
> repris tels quels.
>
> **Ce n'est pas de la documentation décorative** : la table `LIMITS`
> dans `index.html` encode les critères 1 à 100 et s'applique dans
> `applyPose()`, le seul endroit où toutes les poses atterrissent. Une
> gesticulation écrite plus tard ne peut donc plus sortir des clous —
> c'est délibéré, parce qu'un squelette tenu geste par geste ne tient
> pas (le coude de Simon était à +.5, plié à l'envers, et personne ne
> l'avait vu pendant des mois).

## Comment le code s'en sert

| Critère | Où |
|---|---|
| 1-10 tête / cou | `LIMITS.head`, `LIMITS.neck` |
| 11-25 tronc | `LIMITS.chest`, `LIMITS.spine`, `LIMITS.pelvis` |
| 26-40 épaule | `LIMITS.shoulder` (`zIn`/`zOut` asymétriques : le même z rapproche à gauche et écarte à droite) |
| 41-50 coude | `LIMITS.elbow` — charnière : `z:[0,0]`, et `x` ne passe jamais 5° au-delà du tendu |
| 51-60 poignet | `LIMITS.wrist` |
| 61-80 main | géométrie de `buildHand()` : paume, quatre doigts, pouce opposé |
| 81-90 hanche | `LIMITS.hip` |
| 91-95 genou | `LIMITS.knee` — charnière, sens inverse du coude |
| 96-100 cheville | pas d'articulation animée à ce jour |
| 7, 25, 60 (vitesse) | `MAX_RATE` = 300°/s, appliqué en limite de variation par image |

## Morphologie de référence

Les deux fiches ci-dessous fixent les proportions. Le rig est **stylisé**
(tête volontairement surdimensionnée), donc les longueurs de membres
suivent les rapports plutôt que les centimètres bruts — mais les
rapports, eux, sont tenus : épaules/hanches 1,45 chez l'homme et 0,92
chez la femme, main atteignant la mi-cuisse au repos, écartement des yeux
entre 0,8 et 1,2 largeur d'œil, cou de 8 à 15 cm.

### Homme — 28 ans, 180 cm, 72 kg

| Zone | Mesures retenues |
|---|---|
| Tête | hauteur 23,5 · largeur 15,7 · profondeur 20,1 cm |
| Yeux | largeur 3,1 · écartement 3,2 · iris 12 mm |
| Nez | longueur 5,5 · largeur 3,6 cm |
| Bouche | largeur 5,2 cm |
| Oreilles | 6,4 × 3,4 cm · saillie 1,8 cm |
| Cou | hauteur 11,5 · largeur 11,5 cm |
| Torse | épaules 47 · thorax 31 · taille 28 · hanches 33 cm |
| Bras | bras 34 · avant-bras 28 · main 19,5 (paume 10,8) cm |
| Jambes | cuisse 44 · mollet 41 · pied 27,2 cm |

### Femme — 28 ans, 168 cm, 61 kg

| Zone | Mesures retenues |
|---|---|
| Tête | hauteur 22,8 · largeur 15,2 · profondeur 19,5 cm |
| Yeux | largeur 3,0 · écartement 3,1 |
| Nez | longueur 5,0 · largeur 3,2 cm |
| Bouche | largeur 4,9 cm |
| Oreilles | 6,0 × 3,1 cm · saillie 1,5 cm |
| Cou | hauteur 11 · largeur 10 cm |
| Torse | épaules 39 · thorax 28 · taille 24 · hanches 42 cm |
| Bras | bras 31 · avant-bras 25 · main 17,5 cm |
| Jambes | cuisse 41 · mollet 38 · pied 24,5 cm |

## Couleurs d'yeux autorisées

Marron, noisette, bleu, vert, ambre. **Le gris est interdit** — et le
quasi-noir qui servait d'iris avant cette passe l'était de fait.

---

# 100 critères d'articulations 3D réalistes

Contexte : personnage capable de marcher, s'asseoir à un comptoir, saisir une tasse de café, boire et taper sur un ordinateur.

1. Rotation gauche/droite limitée à ±80°.
2. Inclinaison avant limitée à 45°.
3. Extension arrière limitée à 45°.
4. Inclinaison latérale limitée à ±40°.
5. Rotation et inclinaison combinées réduites de 20%.
6. La tête reste attachée à l'axe cervical.
7. Aucune rotation instantanée supérieure à 300°/s.
8. Le regard suit progressivement la rotation du cou.
9. La tête ne traverse jamais les épaules.
10. Le menton ne traverse jamais le thorax.
11. Flexion lombaire maximale de 60°.
12. Extension lombaire maximale de 25°.
13. Inclinaison latérale du tronc limitée à ±35°.
14. Rotation thoracique limitée à ±45°.
15. Rotation lombaire limitée à ±15°.
16. La colonne conserve une courbure continue.
17. Aucun segment vertébral ne se plie à angle vif.
18. Le bassin entraîne la base de la colonne.
19. En position assise, le bassin pivote vers l'arrière.
20. Le thorax reste au-dessus du bassin en posture neutre.
21. La respiration peut provoquer un léger soulèvement thoracique.
22. La poitrine ne traverse jamais la table ou le comptoir.
23. Le tronc compense les mouvements des bras étendus.
24. Le centre de masse reste entre les appuis.
25. Les mouvements brusques sont amortis.
26. Élévation frontale jusqu'à 180°.
27. Élévation latérale jusqu'à 180°.
28. Extension arrière limitée à 60°.
29. Rotation interne limitée à 90°.
30. Rotation externe limitée à 90°.
31. Les clavicules accompagnent l'élévation.
32. Les omoplates glissent sur le thorax.
33. Le bras ne traverse pas le torse.
34. Le bras ne traverse pas la tête.
35. Les épaules montent légèrement lors d'un effort.
36. Les deux épaules restent indépendantes.
37. Une tasse tenue à la main conserve son orientation relative.
38. Les épaules compensent lors de la frappe clavier.
39. La portée maximale dépend de la longueur du bras.
40. Pas d'hyperextension articulaire.
41. Flexion maximale de 150°.
42. Extension maximale de 0 à 5°.
43. Le coude ne se plie pas dans l'autre sens.
44. La rotation principale est une charnière.
45. La pronation accompagne certains gestes.
46. La supination accompagne certains gestes.
47. Le coude reste aligné avec l'avant-bras.
48. Le coude ne traverse pas le torse.
49. Le coude peut reposer sur un comptoir.
50. Les mouvements sont continus sans cassure.
51. Flexion palmaire jusqu'à 80°.
52. Extension jusqu'à 70°.
53. Déviation radiale jusqu'à 20°.
54. Déviation ulnaire jusqu'à 35°.
55. Le poignet reste aligné pendant la marche.
56. Le poignet s'adapte à la prise d'une tasse.
57. Le poignet reste proche du neutre au clavier.
58. Aucune torsion impossible du carpe.
59. Le poignet absorbe les micro-ajustements.
60. La vitesse angulaire est limitée.
61. Le pouce possède une opposition fonctionnelle.
62. Le pouce peut toucher chaque doigt.
63. L'index se plie indépendamment.
64. Le majeur se plie indépendamment.
65. L'annulaire se plie indépendamment.
66. L'auriculaire se plie indépendamment.
67. Les doigts ont trois phalanges sauf le pouce.
68. La fermeture complète produit un poing.
69. La prise cylindrique serre une tasse.
70. La prise de précision utilise pouce et index.
71. Les doigts reposent naturellement en légère flexion.
72. Les doigts suivent les touches du clavier.
73. Les doigts ne traversent pas les objets.
74. Les articulations MCP ont un écartement limité.
75. Les articulations IP ne s'hyperétendent pas.
76. La force de préhension influence la fermeture.
77. La paume peut reposer sur une table.
78. Les doigts s'écartent jusqu'à une limite réaliste.
79. Le relâchement revient vers une pose neutre.
80. Les contacts déclenchent des ajustements IK.
81. Flexion jusqu'à 120°.
82. Extension jusqu'à 20°.
83. Abduction jusqu'à 45°.
84. Adduction jusqu'à 30°.
85. Rotation interne jusqu'à 40°.
86. Rotation externe jusqu'à 60°.
87. Les hanches pilotent la marche.
88. Le bassin pivote lors des pas.
89. La position assise maintient environ 90° de flexion.
90. Les jambes ne traversent jamais le bassin.
91. Flexion jusqu'à 150°.
92. Extension limitée à 0-5°.
93. Aucune flexion inversée.
94. Le genou suit l'axe de la hanche et de la cheville.
95. La marche conserve un amortissement du genou.
96. Flexion dorsale jusqu'à 20°.
97. Flexion plantaire jusqu'à 50°.
98. Inversion limitée à 35°.
99. Éversion limitée à 20°.
100. Le pied reste en contact cohérent avec le sol.