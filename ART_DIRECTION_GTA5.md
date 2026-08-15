# Virtual Coffee — Revue de direction artistique : viser le rendu GTA V

> Revue complète du rendu 3D de `index.html` (three.js **r134**, vanilla, sans build,
> tout vendorisé). Objectif demandé : **faire ressembler les graphismes à GTA V**.
> Ce document contient le diagnostic, la stratégie, et les instructions techniques
> exécutables ligne par ligne.
>
> Contexte de la revue : scène observée en local (`localhost:4321`, 1280×720, DPR 2),
> three r134 confirmé, dépôt propre au moment de l'écriture.

---

## 0. Le verdict en trente secondes

**Ce que tu as aujourd'hui** : une DA *low-poly soft-shaded* cohérente et sympathique.
Famille visuelle : Bruno Simon / Alto's Odyssey / Duolingo / Fisher-Price. Tout est en
`MeshStandardMaterial` couleur plate, arêtes vives, aucune réflexion spéculaire,
aucun post-traitement, caméra fixe centrée. Ça lit comme **de la pâte à modeler bien
éclairée**. Ce n'est pas un défaut — c'est juste une autre planète que GTA V.

**Ce qui est atteignable** : environ **70 % du « feeling » GTA V**, sans toucher à un
seul polygone de plus qu'aujourd'hui. Parce que — et c'est l'insight central de cette
revue :

> **GTA V ne ressemble pas à GTA V à cause de sa géométrie. Il ressemble à GTA V à
> cause de son objectif de caméra et de son étalonnage.**
> Sors un screenshot de ton café, passe-le dans Lightroom avec un LUT Los Santos,
> du grain, un vignettage, une aberration chromatique et un flou de profondeur :
> 60 % du chemin est fait. Aucun asset n'a bougé.

**Ce qui n'est PAS atteignable** en vanilla three.js écrit à la main : les
**personnages**. GTA V, c'est du scan 3D, du rigging facial à 200 os, des shaders de
peau à diffusion sous-surfacique et des textures 4K peintes. Tes bonshommes sont des
sphères et des cylindres. C'est le mur, et il faut le contourner intelligemment
(section 10) plutôt que s'y écraser.

**Le risque à connaître** : un rendu *presque* photoréaliste est pire qu'une
stylisation assumée. La vallée de l'étrange est réelle, et elle est brutale sur les
visages. Le plan ci-dessous est donc construit pour **ne jamais franchir la ligne** :
on va vers un **« GTA V stylisé »** (l'objectif, l'étalonnage, la grammaire de mise en
scène, le HUD, la crasse, la densité) et **pas** vers du faux photoréalisme.

Un dernier point d'honnêteté avant d'entrer dedans : si l'objectif profond est
« impressionner un recruteur avec les graphismes », une DA **totalement** assumée
(cel-shading Persona, aplats Firewatch, néo-noir Kentucky Route Zero) est *plus facile
à rendre excellente* qu'un quasi-GTA. Je le dis une fois, puis je te livre le plan GTA
que tu as demandé, en entier.

---

## 1. Les cinq lois de GTA V

Tout ce document découle de ces cinq règles. Si tu ne retiens que ça, retiens ça.

| # | Loi | Ce que ça veut dire chez toi |
|---|---|---|
| **1** | **L'objectif d'abord** | Bloom, profondeur de champ, grain, vignettage, aberration chromatique, étalonnage. C'est 60 % du look. Tu n'en as **rien**. |
| **2** | **Rien n'est mat, rien n'a d'arête vive** | Chaque surface renvoie *quelque chose*. Chaque arête a un chanfrein qui accroche un highlight. Ton café n'a **aucune** réflexion (pas d'`envMap`) et **que** des arêtes à 90°. C'est *la* cause du look « plastique ». |
| **3** | **GTA est sale** | Traces de doigts, cernes d'humidité, usure sur les angles, poussière dans les coins, gras sur le comptoir. Ton café est un showroom IKEA neuf. |
| **4** | **Densité de props** | Règle interne AAA : *toute surface horizontale porte au moins trois objets*. Tes tables sont vides, ton comptoir a 3 tasses, tes murs ont 3 posters. |
| **5** | **Le monde bouge et fait du bruit** | Trafic, vent, TV, **radio**. Tu as déjà un moteur audio : la radio est le truc le plus « GTA » que tu puisses ajouter pour 0 ligne de shader. |

---

## 2. Diagnostic du rendu actuel — pourquoi ça ne lit pas GTA

Classé par impact décroissant sur le « GTA-mètre ».

### 2.1 — Aucun post-traitement (impact : ★★★★★)

`index.html:526-535`. Tu rends la scène directement dans le canvas. ACES + exposition
1.18, c'est tout. Il manque **toute** la chaîne : bright-pass, bloom, DOF, SSAO,
god-rays, étalonnage, CA, grain, sharpen, dithering.

Les deux overlays CSS (`.vig` et `.grade`, `index.html:54-57`) sont une astuce maligne
mais elles travaillent **en sRGB après coup, en aveugle, sans profondeur**. Un
`mix-blend-mode: soft-light` ne remplacera jamais un étalonnage HDR pré-tonemapping.
Elles devront **disparaître** au moment où le vrai post arrive, sinon tu étalonnes deux
fois (section 5.7).

### 2.2 — Zéro éclairage image-based (impact : ★★★★★)

`index.html:725-741`. Tu as `HemisphereLight` + `SpotLight` + `DirectionalLight` +
2 `PointLight`. Aucun `scene.environment`. Conséquence directe : **le terme spéculaire
des matériaux PBR n'a rien à réfléchir**. Toutes tes surfaces ne renvoient que du
diffus → aspect craie / pâte à modeler. La machine à café (`index.html:851-853`) est
en `metalness: 0.65` : sans environnement, un métal PBR sans réflexion rend **noir et
mort**. C'est visible sur le screenshot : elle ressemble à un bloc de béton gris.

**C'est la modification qui a le meilleur ratio impact / lignes de code de tout ce
document.** ~40 lignes.

### 2.3 — Aucune normal map, aucune roughness map (impact : ★★★★☆)

Toutes les textures procédurales (`index.html:546-645`) sont des textures **diffuse
uniquement**. La brique n'a pas de joint en creux, le parquet n'a pas de rainure, le
plâtre n'a pas de grain, le bois n'a pas de veine en relief. Sous une lumière rasante,
un mur de brique GTA explose de micro-relief ; le tien reste plat comme un papier peint.

Bonne nouvelle : tu génères déjà tout en canvas → tu peux dériver les normal maps
**automatiquement** à partir des mêmes canvas (section 6.3).

### 2.4 — Arêtes vives partout (impact : ★★★★☆)

`BoxGeometry` brut sur le comptoir, le cadre du menu, les poutres, les plinthes, le
livre, le tablier, la lame de la machine. Dans un moteur AAA, **une arête à 90° parfait
n'existe pas** : elle est toujours chanfreinée sur 1–3 mm, précisément pour accrocher
un liseré spéculaire. C'est ce liseré qui fait « objet réel ». Sans lui : maquette.

### 2.5 — La caméra est un appel Zoom (impact : ★★★★☆)

`index.html:520-522` + `1426-1436` + `1511-1516`. Caméra **frontale**, **parfaitement
centrée**, **symétrique**, **fixe**, 50° de FOV, avec un léger parallaxe souris. C'est
l'exact opposé du langage GTA : angle 3/4, jamais dans l'axe, léger roulis, respiration
« caméra épaule », focale plus large, et surtout **un découpage en plans** quand
quelqu'un parle.

Tu as déjà une machinerie de cutscene qui s'ignore : quand Simon parle, `speaking`
passe à `true`. C'est ton *trigger* de cinématique.

### 2.6 — Palette monochrome chaude (impact : ★★★☆☆)

Ambiance hémisphérique `0xffe4c0`, spot `0xffd9a0`, sol brun, murs bruns, table brune,
bois brun. Tout le rendu vit dans une bande de 30° de teinte. GTA V (jour, Los Santos)
c'est : **noirs écrasés teintés cyan, mid-tones désaturés légèrement verts, hautes
lumières ocre-jaune, contraste local élevé**. Tu ne peux pas obtenir ce look en
étalonnant du brun sur du brun — tu obtiens de la boue.

**Il faut d'abord neutraliser/refroidir le rendu, puis laisser l'étalonnage remettre
le chaud.** Voir 6.1.

### 2.7 — Le monde est vide et propre (impact : ★★★☆☆)

Trois tables, cinq chaises, trois plantes, trois posters, trois tasses. Le comptoir est
nu. Les tables sont nues. Les murs sont nus entre les posters. Aucune trace d'usage :
pas de tasse sale, pas de journal, pas de sucre renversé, pas de câble, pas de prise,
pas d'extincteur, pas de plaque d'égout, pas de chewing-gum. La densité de props est le
signal n°1 de production AAA.

### 2.8 — La fenêtre est un autocollant (impact : ★★★☆☆)

`index.html:794-796` : un `PlaneGeometry` avec `MeshBasicMaterial`. Aucun parallaxe,
aucune vitre, aucun reflet, aucune vie derrière. Dans GTA, une fenêtre est un **portail
vers le monde** — et le monde est le sujet du jeu. C'est un énorme gisement.

### 2.9 — Ombres mal budgétées (impact : ★★☆☆☆)

`index.html:730` : `shadow.mapSize 1024` pour le spot ; `index.html:738-739` : la caméra
d'ombre directionnelle couvre `[-5,5] × [-2,4]` — soit 10 × 6 m — pour un décor jouable
qui tient dans **3 × 3 m** autour de la table. Résultat : ~1 cm de texel utile, contacts
mous, pas d'ombre de contact nette sous les objets. Tu paies plein pot pour une ombre
floue.

Aussi : `shadow.bias` négatif seul provoque du peter-panning. `shadow.normalBias`
(dispo depuis r112) est bien meilleur.

### 2.10 — Détails de scène relevés à l'œil sur le rendu

| Où | Problème | Fix |
|---|---|---|
| `index.html:616-624` `tableTex` | Cernes concentriques 512² étirés sur une table de 1,9 m → **cible de fléchettes** floue, échelle fausse. Une table n'a pas de cernes, elle a des **lames**. | Refaire en lames + normal map + `clearcoat` (vernis). |
| `index.html:588-603` `brickTex` | `repeat.set(6, 2.6)` sur un mur de 22 × 4,6 m → briques **étirées non uniformément**. Joints pas en creux. Pas de dégradé de crasse. | Corriger le ratio, ajouter normal + grunge multiplicatif. |
| `index.html:586` `floorTex.repeat 4.5` | Tuilage visible : le même motif de 8 rangées revient 4,5 fois. | Deuxième octave de détail + variation par lame. |
| `index.html:771-778` plafond + poutres | Plafond plat 22 × 22 à y=3,4 ; poutres de **12 m** qui traversent les murs et flottent dans le vide. | Réduire aux dimensions de la pièce, ajouter chevrons + solives. |
| `index.html:751-756` ampoule pendante | `MeshBasicMaterial` + sprite additif. Pas d'`emissive`, pas de flaque de lumière au plafond. | `emissiveIntensity` élevé + le bloom fera le reste, + un `PointLight` faible orienté plafond. |
| `index.html:904-906` tapis | Cercle plat, anneaux concentriques → **cible de tir**, gros aliasing. | Motif kilim/persan + normal map, `roughness: 1`. |
| `index.html:788-792` plinthes | Boîtes de 3 cm sans `castShadow` → elles **flottent**. | `castShadow` + occlusion de contact. |
| `index.html:518-519` brouillard | `Fog(0x151011, 7.5, 16)` linéaire, dans une pièce de 10 m de profondeur → le fog ne se déclenche jamais. | `FogExp2` avec la couleur d'ombre de l'étalonnage. |
| `index.html:1030-1052` bras de Simon | Deux capsules **disjointes** + une main-boule qui flotte. Trou visible au coude et à l'épaule sur le rendu. | Sphères de jonction épaule/coude/poignet. |
| `index.html:1098-1110` yeux/bouche | Sphères qui **sortent du visage**, pas de paupière ; le clignement est un `scale.y = 0.12` qui écrase la sphère. La bouche est une boîte qui grossit sur un sinus **non synchronisé à l'audio**. | Paupières géométriques + bouche pilotée par l'amplitude audio (section 9.4). |
| `index.html:931-976` `person()` | ~10 `new MeshStandardMaterial` **par personnage** × 5 = 50 matériaux, tous identiques par famille. | Hoister les matériaux hors de la fonction. |

---

## 3. La grammaire visuelle de GTA V, décomposée

Pour savoir quoi construire, il faut nommer précisément ce qu'on copie.

### Couche 1 — L'objectif (le plus gros levier)
- **Bloom** anamorphique doux, seuil haut, très large rayon, faible intensité.
- **Profondeur de champ** : bokeh hexagonal, net sur le sujet, flou proche **et** lointain.
- **Grain** animé, plus présent dans les ombres, jamais dans les blancs purs.
- **Aberration chromatique** radiale, ~1,5 px aux coins, 0 au centre.
- **Vignettage** doux et large, pas un rond noir.
- **Sharpen** léger appliqué *après* tout le reste (le fameux « croustillant » AAA).
- **Motion blur** caméra.

### Couche 2 — L'étalonnage « Los Santos »
- Noirs **écrasés** et **teintés cyan/sarcelle**.
- Mid-tones **désaturés de 10–20 %**, poussés très légèrement vers le vert-jaune.
- Hautes lumières **ocre / doré**, jamais blanc pur.
- Courbe en S : contraste local élevé, mais highlights *roll-off* filmique.
- Séparation chaud/froid marquée : soleil chaud vs ombre froide.

### Couche 3 — La matière
- Env-map partout. Métal = réflexion, pas gris.
- Micro-relief (normal maps) sur **toutes** les grandes surfaces.
- Variation de rugosité (une table vernie a des zones mates d'usure et des zones brillantes).
- Chanfreins.
- Crasse : gradient sombre en bas des murs, cernes autour des poignées, gras sur le comptoir.

### Couche 4 — La mise en scène
- Angle 3/4, jamais frontal. Règle des tiers.
- Cinématiques : **letterbox**, coupes franches entre plans de couverture, sous-titres.
- Respiration caméra (bruit basse fréquence, faible amplitude).
- Rack focus : la mise au point *raconte* où regarder.

### Couche 5 — Le HUD
- Typo **condensée, capitales, très fine**, jamais arrondie.
- Ombre portée dure de 1 px, jamais de blur.
- Pas de conteneur, pas de pilule, pas de `border-radius`, pas de `backdrop-filter`.
- Minimap ronde en bas-gauche, argent en vert en haut-droite, étoiles.
- Cartons de mission qui glissent depuis le bord gauche.

### Couche 6 — La vie
- Radio avec stations et jingles DJ.
- Room tone + machine à café + rue.
- PNJ qui ont des boucles crédibles (pas des allers-retours sur un rail).

---

## 4. Le plan par paliers

| Palier | Contenu | Effort | Gain « GTA-mètre » | Risque |
|---|---|---|---|---|
| **P0** | Chaîne de post-traitement complète + étalonnage | 1–2 j | **+40 pts** | Faible (isolé du reste) |
| **P1** | IBL, normal/roughness maps, chanfreins, ombres retaillées, crasse | 2–3 j | **+20 pts** | Faible |
| **P2** | Caméra cinématographique, letterbox, plans de coupe, rack focus, sous-titres | 1–2 j | **+15 pts** | Moyen (touche l'UX) |
| **P3** | HUD façon GTA + minimap + progression + radio | 2 j | **+10 pts** | Moyen (juridique, cf. 8.5) |
| **P4** | Los-Santos-isation du décor, fenêtre-portail, densité de props | 3–5 j | **+10 pts** | Faible |
| **P5** | Personnages | ∞ | +5 pts au mieux, −20 si raté | **Élevé** |

Fais P0 en premier, tout seul, et regarde le résultat avant de décider de la suite.
Tu seras surpris.

---

## 5. P0 — La chaîne de post-traitement (le gros morceau)

### 5.1 — Contrainte : pas de build, pas de CDN

Le dépôt interdit les scripts externes (`README.md` § « Everything is vendored »).
`three.min.js` r134 est un build UMD sans les `examples/`. Deux options :

| Option | Verdict |
|---|---|
| Vendoriser `examples/js/postprocessing/*` de r134 | Marche (r134 embarque encore `examples/js` non-module), mais ~15 fichiers, `UnrealBloomPass` lourd et peu réglable, et tu hérites d'une API que tu ne maîtrises pas. |
| **Écrire la chaîne à la main** | **Recommandé.** ~300 lignes, 0 Ko de dépendance, contrôle total, et tu peux fusionner 6 effets dans **une seule passe de composite** (ce que ne fait pas `EffectComposer`, qui blitte entre chaque passe). |

On part sur la seconde.

### 5.2 — Les pièges r134 à connaître AVANT d'écrire une ligne

Ces quatre points font perdre une journée chacun si on les découvre en route.

1. **`antialias: true` ne sert plus à rien.** Dès que tu rends dans un
   `WebGLRenderTarget`, le MSAA du canvas est ignoré. Il faut soit un
   `WebGLMultisampleRenderTarget` (WebGL2 seulement, et incompatible avec la lecture
   de profondeur), soit un **FXAA dans la passe de composite**. → on prend FXAA.

2. **Le tone mapping doit sortir du renderer.** Mets
   `renderer.toneMapping = THREE.NoToneMapping` et fais ACES **toi-même** dans le
   shader de composite. Sinon tu tonemappes en HDR *avant* le bloom, et ton bloom ne
   voit plus aucune valeur > 1 : il n'y a plus rien à faire briller.

3. **L'encodage sRGB doit sortir du renderer aussi.** Un `ShaderMaterial` brut ne
   reçoit **pas** l'injection `<encodings_fragment>` de three. Fais l'encodage sRGB
   à la main, tout à la fin du composite. Oubli classique → image délavée (double
   gamma) ou trop sombre.
   Les `CanvasTexture` d'entrée gardent `encoding = sRGBEncoding` (déjà fait,
   `index.html:550`), et les textures de render target passent en `LinearEncoding`.

4. **Les normal maps ne sont JAMAIS en sRGB.** `t.encoding = THREE.LinearEncoding`
   obligatoire, sinon le relief est faux et tu vas croire que ton code de dérivation
   est buggé.

Bonus : baisse `camera.far` de 40 (`index.html:520`) à **≈ 25**. La `DepthTexture`
en `UnsignedShortType` est très imprécise sur une plage longue, et ta pièce fait 10 m.

### 5.3 — Architecture des passes

```
                                     ┌──────────────┐
  scene ──► RT_HDR (HalfFloat)       │ DepthTexture │
            + depthTexture ──────────┴──────┬───────┘
                 │                          │
                 ├──► brightPass ──► down×4 ──► up×4  = RT_BLOOM
                 │         │
                 │         └──► radialBlur (godrays)  = RT_RAYS   [option]
                 │
                 ├──► SSAO (½ rés, depth-only) ──► blur 4×4 = RT_AO
                 │
                 └──► DOF (½ rés, CoC depuis depth) = RT_DOF
                            │
                            ▼
        ┌─────────────────────────────────────────────────┐
        │  COMPOSITE (une seule passe, écrit dans null)   │
        │  1. CA radiale sur RT_DOF                       │
        │  2. × RT_AO                                     │
        │  3. + RT_BLOOM × intensité  + RT_RAYS           │
        │  4. exposition                                  │
        │  5. tonemap ACES                                │
        │  6. étalonnage : CDL + saturation + contraste   │
        │  7. vignettage                                  │
        │  8. grain animé pondéré par la luminance        │
        │  9. FXAA + unsharp mask                         │
        │ 10. dithering ordonné                           │
        │ 11. encodage sRGB                               │
        └─────────────────────────────────────────────────┘
```

Coût cible : **< 3 ms** à 1280×720 sur iGPU récent (bloom et DOF en demi-résolution,
SSAO en demi-résolution).

### 5.4 — Le socle (à coller après `app.appendChild(renderer.domElement)`, ~`index.html:535`)

```js
/* ---------------- POST-PROCESSING : socle ---------------- */
renderer.toneMapping = THREE.NoToneMapping;   /* ACES part dans le composite */
camera.far = 25; camera.updateProjectionMatrix();

const HALF = THREE.HalfFloatType;
function makeRT(w, h, opts){
  return new THREE.WebGLRenderTarget(Math.max(1, w|0), Math.max(1, h|0), Object.assign({
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    format: THREE.RGBAFormat,
    type: HALF,
    encoding: THREE.LinearEncoding,   /* jamais sRGB sur un RT intermédiaire */
    depthBuffer: false,
    stencilBuffer: false
  }, opts || {}));
}

/* Quad plein écran réutilisé par toutes les passes */
const fsScene = new THREE.Scene();
const fsCam   = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const fsQuad  = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), null);
fsQuad.frustumCulled = false;
fsScene.add(fsQuad);
function blit(material, target){
  fsQuad.material = material;
  renderer.setRenderTarget(target || null);
  renderer.clear();
  renderer.render(fsScene, fsCam);
}

/* Cibles */
let RT_HDR, RT_BRIGHT, RT_AO, RT_DOF, MIPS = [];
const BLOOM_MIPS = 4;
function allocTargets(){
  const dpr = renderer.getPixelRatio();
  const w = Math.floor(innerWidth * dpr), h = Math.floor(innerHeight * dpr);
  [RT_HDR, RT_BRIGHT, RT_AO, RT_DOF].forEach(rt => rt && rt.dispose());
  MIPS.forEach(rt => rt.dispose()); MIPS = [];

  RT_HDR = makeRT(w, h, { depthBuffer: true });
  const dt = new THREE.DepthTexture(w, h);
  dt.type = THREE.UnsignedIntType;          /* précision correcte sur far=25 */
  dt.minFilter = dt.magFilter = THREE.NearestFilter;
  RT_HDR.depthTexture = dt;

  RT_BRIGHT = makeRT(w / 2, h / 2);
  RT_AO     = makeRT(w / 2, h / 2, { format: THREE.RGBAFormat, type: THREE.UnsignedByteType });
  RT_DOF    = makeRT(w, h);
  for (let i = 0; i < BLOOM_MIPS; i++) MIPS.push(makeRT(w / (4 << i), h / (4 << i)));
}
allocTargets();
```

Et dans `onResize()` (`index.html:537-542`), ajouter `allocTargets();` et mettre à jour
les uniformes de résolution.

### 5.5 — Bright pass + bloom (soft-knee façon Unreal)

```js
const QUAD_VS = `
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const brightMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uThreshold:{value:1.05}, uKnee:{value:0.45} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform float uThreshold, uKnee;
    varying vec2 vUv;
    void main(){
      vec3 c  = texture2D(tSrc, vUv).rgb;
      float br = max(c.r, max(c.g, c.b));
      float soft = clamp(br - uThreshold + uKnee, 0.0, 2.0 * uKnee);
      soft = soft * soft / (4.0 * uKnee + 1e-4);
      float k = max(soft, br - uThreshold) / max(br, 1e-4);
      gl_FragColor = vec4(c * k, 1.0);
    }`,
  depthTest:false, depthWrite:false
});

/* down : box 4 taps ; up : tente 3×3, additif */
const downMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uTexel:{value:new THREE.Vector2()} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform vec2 uTexel; varying vec2 vUv;
    void main(){
      vec3 s = texture2D(tSrc, vUv + uTexel * vec2(-1.0,-1.0)).rgb
             + texture2D(tSrc, vUv + uTexel * vec2( 1.0,-1.0)).rgb
             + texture2D(tSrc, vUv + uTexel * vec2(-1.0, 1.0)).rgb
             + texture2D(tSrc, vUv + uTexel * vec2( 1.0, 1.0)).rgb;
      gl_FragColor = vec4(s * 0.25, 1.0);
    }`,
  depthTest:false, depthWrite:false
});

const upMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uTexel:{value:new THREE.Vector2()}, uRadius:{value:1.0} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform vec2 uTexel; uniform float uRadius; varying vec2 vUv;
    void main(){
      vec2 o = uTexel * uRadius;
      vec3 s = texture2D(tSrc, vUv + vec2(-o.x,-o.y)).rgb
             + texture2D(tSrc, vUv + vec2( 0.0,-o.y)).rgb * 2.0
             + texture2D(tSrc, vUv + vec2( o.x,-o.y)).rgb
             + texture2D(tSrc, vUv + vec2(-o.x, 0.0)).rgb * 2.0
             + texture2D(tSrc, vUv).rgb                    * 4.0
             + texture2D(tSrc, vUv + vec2( o.x, 0.0)).rgb * 2.0
             + texture2D(tSrc, vUv + vec2(-o.x, o.y)).rgb
             + texture2D(tSrc, vUv + vec2( 0.0, o.y)).rgb * 2.0
             + texture2D(tSrc, vUv + vec2( o.x, o.y)).rgb;
      gl_FragColor = vec4(s / 16.0, 1.0);
    }`,
  blending: THREE.AdditiveBlending, transparent:true,
  depthTest:false, depthWrite:false
});

function renderBloom(){
  brightMat.uniforms.tSrc.value = RT_HDR.texture;
  blit(brightMat, RT_BRIGHT);

  let src = RT_BRIGHT;
  for (let i = 0; i < BLOOM_MIPS; i++){
    downMat.uniforms.tSrc.value = src.texture;
    downMat.uniforms.uTexel.value.set(1 / src.width, 1 / src.height);
    blit(downMat, MIPS[i]); src = MIPS[i];
  }
  /* remontée additive : le plus petit mip donne le halo large */
  for (let i = BLOOM_MIPS - 1; i > 0; i--){
    upMat.uniforms.tSrc.value = MIPS[i].texture;
    upMat.uniforms.uTexel.value.set(1 / MIPS[i].width, 1 / MIPS[i].height);
    upMat.uniforms.uRadius.value = 1.0 + i * 0.6;
    fsQuad.material = upMat;
    renderer.setRenderTarget(MIPS[i - 1]);
    renderer.render(fsScene, fsCam);      /* pas de clear : c'est additif */
  }
}
```

**Réglages GTA** : `uThreshold` 1.0–1.2, `uKnee` 0.4, intensité finale **0.35 max**.
Le bloom GTA est *large et discret*, pas un glow d'écran de veille. Si tu vois le
bloom, c'est trop.

### 5.6 — Profondeur de champ (bokeh hexagonal, ½ résolution)

```js
const dofMat = new THREE.ShaderMaterial({
  uniforms:{
    tSrc:{value:null}, tDepth:{value:null},
    uTexel:{value:new THREE.Vector2()},
    uFocus:{value:2.6},        /* distance de MAP en mètres */
    uRange:{value:1.2},        /* profondeur de la zone nette */
    uMaxCoC:{value:9.0},       /* rayon max en px */
    cameraNear:{value:0.1}, cameraFar:{value:25.0}
  },
  vertexShader: QUAD_VS,
  fragmentShader:`
    #include <packing>
    uniform sampler2D tSrc, tDepth;
    uniform vec2 uTexel; uniform float uFocus, uRange, uMaxCoC, cameraNear, cameraFar;
    varying vec2 vUv;

    float viewDist(vec2 uv){
      float d = texture2D(tDepth, uv).x;
      return -perspectiveDepthToViewZ(d, cameraNear, cameraFar);
    }
    float coc(vec2 uv){
      float z = viewDist(uv);
      return clamp((abs(z - uFocus) - uRange) / uRange, 0.0, 1.0);
    }
    void main(){
      float c = coc(vUv);
      vec3 sum = texture2D(tSrc, vUv).rgb;
      float wsum = 1.0;
      if (c > 0.01){
        float r = c * uMaxCoC;
        /* 2 anneaux hexagonaux = 18 taps, bokeh propre et pas cher */
        for (int ring = 1; ring <= 2; ring++){
          float rr = r * float(ring) / 2.0;
          for (int i = 0; i < 6; i++){
            float a = float(i) / 6.0 * 6.2831853 + float(ring) * 0.5236;
            vec2 off = vec2(cos(a), sin(a)) * rr * uTexel;
            float cs = coc(vUv + off);
            /* on ne laisse baver que ce qui est AU MOINS aussi flou (anti-bleeding) */
            float w = step(c * 0.75, cs);
            sum  += texture2D(tSrc, vUv + off).rgb * w;
            wsum += w;
          }
        }
      }
      gl_FragColor = vec4(sum / wsum, c);   /* alpha = CoC, réutilisé au composite */
    }`,
  depthTest:false, depthWrite:false
});
```

**C'est ici que se joue le plus gros du look.** Réglages :

| Plan | `uFocus` | `uRange` | Effet |
|---|---|---|---|
| Gameplay (assis à table) | 2.6 | 1.4 | Simon net, mur du fond doux, bord de table doux |
| Gros plan Simon parle | 1.35 | 0.30 | Uniquement le visage net → **très** cinéma |
| Insert sur le CV | 0.85 | 0.20 | La feuille nette, tout le reste fondu |

Et le détail qui tue : **quand on survole la feuille, on tire la mise au point dessus**
(rack focus). C'est joli *et* c'est fonctionnel — ça guide l'œil vers l'interactif.

```js
/* dans animate(), après le calcul de paperT */
const focusTarget = paperHover ? 0.95 : (speaking ? 1.35 : 2.6);
const rangeTarget = paperHover ? 0.25 : (speaking ? 0.35 : 1.4);
dofMat.uniforms.uFocus.value += (focusTarget - dofMat.uniforms.uFocus.value) * Math.min(1, dt * 3.2);
dofMat.uniforms.uRange.value += (rangeTarget - dofMat.uniforms.uRange.value) * Math.min(1, dt * 3.2);
```

### 5.7 — Le composite : étalonnage Los Santos

C'est le shader qui fait dire « ah oui, ça fait GTA ».

```js
const compMat = new THREE.ShaderMaterial({
  uniforms:{
    tSrc:{value:null}, tBloom:{value:null}, tAO:{value:null},
    uRes:{value:new THREE.Vector2()}, uTime:{value:0},
    uExposure:{value:1.15},
    uBloom:{value:0.32},
    uCA:{value:0.85},          /* px aux coins */
    uGrain:{value:0.055},
    uVig:{value:0.55},
    uSharp:{value:0.35},
    /* --- étalonnage --- */
    uSlope:{value:new THREE.Vector3(1.06, 1.015, 0.935)},   /* gain : highlights ocre */
    uOffset:{value:new THREE.Vector3(-0.010, 0.002, 0.022)},/* lift : noirs sarcelle */
    uPower:{value:new THREE.Vector3(1.00, 0.975, 1.030)},   /* gamma : mids vert-jaune */
    uSat:{value:0.86},
    uContrast:{value:1.14},
    uPivot:{value:0.42}
  },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc, tBloom, tAO;
    uniform vec2 uRes; uniform float uTime, uExposure, uBloom, uCA, uGrain, uVig, uSharp;
    uniform vec3 uSlope, uOffset, uPower; uniform float uSat, uContrast, uPivot;
    varying vec2 vUv;

    float luma(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }

    /* ACES filmique (approximation Narkowicz) */
    vec3 aces(vec3 x){
      const float a = 2.51, b = 0.03, c = 2.43, d = 0.59, e = 0.14;
      return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
    }
    /* ASC CDL — le vocabulaire standard des étalonneurs */
    vec3 cdl(vec3 c){ return pow(max(c * uSlope + uOffset, 0.0), uPower); }

    void main(){
      vec2 texel = 1.0 / uRes;
      vec2 d = vUv - 0.5;
      float r2 = dot(d, d);

      /* 1. aberration chromatique radiale */
      vec2 ca = d * r2 * uCA * texel * 6.0;
      vec3 col = vec3(
        texture2D(tSrc, vUv + ca).r,
        texture2D(tSrc, vUv).g,
        texture2D(tSrc, vUv - ca).b
      );

      /* 2. occlusion ambiante */
      col *= texture2D(tAO, vUv).r;

      /* 3. bloom */
      col += texture2D(tBloom, vUv).rgb * uBloom;

      /* 4-5. exposition + tonemap */
      col = aces(col * uExposure);

      /* 6. étalonnage */
      col = cdl(col);
      col = mix(vec3(luma(col)), col, uSat);
      col = clamp((col - uPivot) * uContrast + uPivot, 0.0, 1.0);

      /* 7. vignettage (corrigé de l'aspect ratio, sinon il est ovale) */
      float v = smoothstep(0.98, 0.28, length(d * vec2(uRes.x / uRes.y, 1.0)));
      col *= mix(1.0, v, uVig);

      /* 8. grain animé, plus fort dans les ombres */
      float g = hash(vUv * uRes + fract(uTime) * 419.7) - 0.5;
      col += g * uGrain * (1.0 - smoothstep(0.0, 0.65, luma(col)));

      /* 9. unsharp mask (le « croustillant » AAA) */
      vec3 blur = (
        texture2D(tSrc, vUv + vec2( texel.x, 0.0)).rgb +
        texture2D(tSrc, vUv + vec2(-texel.x, 0.0)).rgb +
        texture2D(tSrc, vUv + vec2(0.0,  texel.y)).rgb +
        texture2D(tSrc, vUv + vec2(0.0, -texel.y)).rgb) * 0.25;
      col += (col - aces(blur * uExposure)) * uSharp;

      /* 10. dithering — indispensable dans un café sombre, sinon banding */
      col += (hash(vUv * uRes + 7.13) - 0.5) / 255.0;

      /* 11. encodage sRGB manuel (three ne le fait pas pour un ShaderMaterial) */
      vec3 lo = col * 12.92;
      vec3 hi = 1.055 * pow(max(col, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055;
      gl_FragColor = vec4(mix(hi, lo, step(col, vec3(0.0031308))), 1.0);
    }`,
  depthTest:false, depthWrite:false
});
```

**Deux presets à câbler sur un toggle** (jour / soir) :

```js
const GRADES = {
  /* Los Santos, midi, smog — l'ADN GTA V */
  losSantosDay: {
    slope:[1.060, 1.015, 0.935], offset:[-0.010, 0.002, 0.022], power:[1.00, 0.975, 1.030],
    sat:0.86, contrast:1.14, pivot:0.42, exposure:1.15, bloom:0.32, vig:0.55, grain:0.055
  },
  /* Vinewood, nuit, néons — plus proche de ton café actuel */
  vinewoodNight: {
    slope:[0.965, 0.985, 1.090], offset:[-0.014, -0.004, 0.030], power:[1.04, 1.00, 0.96],
    sat:0.94, contrast:1.22, pivot:0.36, exposure:1.05, bloom:0.48, vig:0.70, grain:0.075
  }
};
```

> ⚠️ **Au moment où ce composite est en place, supprime `.vig` et `.grade`**
> (`index.html:54-57` et `index.html:160`). Sinon tu appliques deux vignettages et
> deux étalonnages, dont un en aveugle sur du sRGB. Le rendu deviendra boueux et tu
> chercheras le bug dans le shader.

### 5.8 — La boucle de rendu finale

Remplacer `renderer.render(scene, camera)` (`index.html:1518`) par :

```js
  /* 1. scène → HDR */
  renderer.setRenderTarget(RT_HDR);
  renderer.clear();
  renderer.render(scene, camera);

  /* 2. AO (si qualité >= medium) */
  if (QUALITY.ao) renderSSAO();

  /* 3. bloom */
  renderBloom();

  /* 4. DOF */
  dofMat.uniforms.tSrc.value   = RT_HDR.texture;
  dofMat.uniforms.tDepth.value = RT_HDR.depthTexture;
  dofMat.uniforms.uTexel.value.set(1 / RT_HDR.width, 1 / RT_HDR.height);
  dofMat.uniforms.cameraNear.value = camera.near;
  dofMat.uniforms.cameraFar.value  = camera.far;
  blit(dofMat, RT_DOF);

  /* 5. composite → écran */
  compMat.uniforms.tSrc.value   = QUALITY.dof ? RT_DOF.texture : RT_HDR.texture;
  compMat.uniforms.tBloom.value = MIPS[0].texture;
  compMat.uniforms.tAO.value    = QUALITY.ao ? RT_AO.texture : whiteTex;
  compMat.uniforms.uTime.value  = t;
  compMat.uniforms.uRes.value.set(RT_HDR.width, RT_HDR.height);
  blit(compMat, null);
```

### 5.9 — SSAO (optionnel mais très rentable)

Depth-only, normales reconstruites par dérivées, 12 échantillons en hémisphère, ½ rés,
puis flou 4×4. ~70 lignes. C'est ce qui « colle » les objets au sol et donne les coins
sombres typiques de GTA.

**Alternative gratuite si tu ne veux pas coder ça** : des *blob shadows*. Un
`PlaneGeometry` horizontal avec une texture radiale alpha, en `MultiplyBlending`, sous
chaque table, chaise, plante et personnage. 20 lignes, 90 % de l'effet visuel du SSAO
dans une scène statique.

```js
const blobTex = ctex(128, 128, x => {
  const g = x.createRadialGradient(64, 64, 4, 64, 64, 62);
  g.addColorStop(0,   'rgba(0,0,0,0.55)');
  g.addColorStop(0.6, 'rgba(0,0,0,0.22)');
  g.addColorStop(1,   'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
});
const blobMat = new THREE.MeshBasicMaterial({
  map: blobTex, transparent: true, depthWrite: false,
  blending: THREE.MultiplyBlending, opacity: 1
});
function contactShadow(x, z, radius, y){
  const m = new THREE.Mesh(new THREE.PlaneGeometry(radius * 2, radius * 2), blobMat);
  m.rotation.x = -Math.PI / 2;
  m.position.set(x, (y || 0) + 0.006, z);
  m.renderOrder = 1;
  scene.add(m);
  return m;
}
```

---

## 6. P1 — Lumière et matière

### 6.1 — Refroidir le rendu AVANT d'étalonner

C'est contre-intuitif mais c'est la clé du look GTA : le **contraste chaud/froid**.
Aujourd'hui tout est chaud, donc il n'y a pas de contraste, donc l'étalonnage ne peut
rien séparer.

Modifs sur `index.html:725-741` :

```js
/* AVANT : ambiance chaude partout */
scene.add(new THREE.HemisphereLight(0xffe4c0, 0x241a12, .5));

/* APRÈS : ambiance FROIDE (c'est le ciel par la fenêtre),
   le chaud ne vient plus QUE des ampoules. */
scene.add(new THREE.HemisphereLight(0x9fc4e8, 0x1a1410, 0.42));

/* le spot de table reste chaud, mais plus saturé pour trancher */
const keySpot = new THREE.SpotLight(0xffb867, 2.1, 9, 0.68, 0.6, 1.6);
keySpot.shadow.mapSize.set(2048, 2048);
keySpot.shadow.normalBias = 0.02;     /* remplace le bias négatif */
keySpot.shadow.bias = -0.0002;
keySpot.shadow.radius = 3;

/* la fenêtre devient franchement bleue et plus forte */
const winDir = new THREE.DirectionalLight(0xa8ccf0, 0.85);
winDir.shadow.camera.left = -3.5; winDir.shadow.camera.right = 3.5;
winDir.shadow.camera.top  =  3.0; winDir.shadow.camera.bottom = -0.5;
winDir.shadow.mapSize.set(2048, 2048);
winDir.shadow.normalBias = 0.02;
```

> **Pourquoi rétrécir la caméra d'ombre** : elle couvrait 10 × 6 m
> (`index.html:738-739`) pour une zone jouable de ~3 × 3 m. Passer à 7 × 3,5 m avec
> une map 2048 fait passer la résolution de ~1 cm/texel à ~1,7 mm/texel. **Ombres 6×
> plus nettes, pour le même coût GPU.** C'est le fix le plus rentable de la section.

Envisage aussi `renderer.physicallyCorrectLights = true` (atténuation en 1/d² réelle),
mais **il faut retuner toutes les intensités** : les `PointLight` passent en unités
photométriques et deviennent ~10× trop faibles. À faire en une passe dédiée, pas en
passant.

### 6.2 — IBL : la ligne qui tue le « plastique »

`PMREMGenerator.fromScene()` est dans le core r134. On construit une mini-pièce
d'environnement à la main (c'est exactement ce que fait `RoomEnvironment`) :

```js
/* ---------------- ENVIRONNEMENT (IBL) ---------------- */
(function buildEnvironment(){
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0x14161c);

  const shell = new THREE.Mesh(
    new THREE.BoxGeometry(12, 7, 12),
    new THREE.MeshBasicMaterial({ color: 0x2b2620, side: THREE.BackSide })
  );
  envScene.add(shell);

  function emitter(w, h, d, x, y, z, hex, power){
    const mat = new THREE.MeshBasicMaterial({ color: hex });
    mat.color.multiplyScalar(power);            /* > 1 = émetteur HDR */
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x, y, z);
    envScene.add(m);
  }
  emitter(7, 0.2, 7,  0.0, 3.2,  -1.0, 0xffcf8e, 7);   /* plafonniers chauds */
  emitter(0.2, 3.2, 4.5, -5.6, 2.1, -1.2, 0xbcd8ff, 12);/* fenêtre froide */
  emitter(4, 0.2, 1.2,  2.7, 1.9, -3.6, 0xffe0b0, 3);   /* néon du comptoir */

  const pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  const rt = pmrem.fromScene(envScene, 0.04);
  scene.environment = rt.texture;        /* ← LA ligne */
  pmrem.dispose();
  shell.geometry.dispose();
})();
```

Puis règle `envMapIntensity` par famille de matériau :

| Matériau | `roughness` | `metalness` | `envMapIntensity` |
|---|---|---|---|
| Machine à café, pieds de table, cadres | 0.25 | 0.9 | 1.4 |
| Plateau de comptoir (pierre) | 0.32 | 0.05 | 1.0 |
| Table vernie | 0.35 + `clearcoat: 1` | 0 | 0.9 |
| Sol parquet | 0.62 | 0 | 0.7 |
| Brique, plâtre | 0.95 | 0 | 0.35 |
| Tissu (vêtements, tapis) | 0.9 | 0 | 0.25 |
| Peau | 0.55 | 0 | 0.5 |
| Céramique (tasses) | 0.18 | 0 | 1.2 |

Ta table mérite un `MeshPhysicalMaterial` avec vernis :

```js
new THREE.MeshPhysicalMaterial({
  map: tableTex, normalMap: tableNrm, roughnessMap: tableRgh,
  roughness: 0.45, clearcoat: 1.0, clearcoatRoughness: 0.16,
  envMapIntensity: 0.9
});
```

Le `clearcoat` seul transformera le rendu de la table sous le pendant. Elle occupe 40 %
de l'écran : c'est de loin ta surface la plus rentable.

### 6.3 — Générer les normal maps depuis tes canvas

Tu as déjà tout le travail fait : chaque texture est un canvas. On dérive le relief par
sobel sur la luminance.

```js
/* height → normal, à coller à côté de ctex() (~index.html:552) */
function normalFromCanvas(srcCanvas, strength, downscale){
  const ds  = downscale || 1;
  const w   = Math.floor(srcCanvas.width / ds), h = Math.floor(srcCanvas.height / ds);
  const tmp = document.createElement('canvas'); tmp.width = w; tmp.height = h;
  const tc  = tmp.getContext('2d');
  tc.drawImage(srcCanvas, 0, 0, w, h);
  const s = tc.getImageData(0, 0, w, h).data;

  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const oc  = out.getContext('2d'), img = oc.createImageData(w, h), o = img.data;
  const L = (x, y) => {
    x = (x + w) % w; y = (y + h) % h;
    const i = (y * w + x) * 4;
    return (s[i] * 0.299 + s[i + 1] * 0.587 + s[i + 2] * 0.114) / 255;
  };
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    const dx = (L(x + 1, y) - L(x - 1, y)) * strength;
    const dy = (L(x, y + 1) - L(x, y - 1)) * strength;
    const len = Math.hypot(dx, dy, 1);
    const i = (y * w + x) * 4;
    o[i]     = ((-dx / len) * 0.5 + 0.5) * 255;
    o[i + 1] = ((-dy / len) * 0.5 + 0.5) * 255;
    o[i + 2] = (( 1  / len) * 0.5 + 0.5) * 255;
    o[i + 3] = 255;
  }
  oc.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(out);
  t.encoding = THREE.LinearEncoding;      /* ← OBLIGATOIRE */
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = maxAniso;
  return t;
}
```

Il faut alors garder une référence au canvas dans `ctex()` :

```js
function ctex(w, h, draw){
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.encoding = THREE.sRGBEncoding; t.anisotropy = maxAniso;
  t.userData.canvas = c;                 /* ← pour normalFromCanvas */
  return t;
}
```

Usage :

```js
const brickNrm = normalFromCanvas(brickTex.userData.canvas, 3.2);
brickNrm.repeat.copy(brickTex.repeat);
backWall.material.normalMap = brickNrm;
backWall.material.normalScale.set(1.4, 1.4);

const floorNrm = normalFromCanvas(floorTex.userData.canvas, 2.0, 2);  /* ÷2 = 4× plus rapide */
floorNrm.repeat.copy(floorTex.repeat);
```

**Coût** : 1024² = 1 M pixels en JS ≈ 40–80 ms. Fais-le **une seule fois au chargement**,
en `downscale: 2` pour le sol, et **après** le premier `render()` (pour ne pas retarder
le premier frame). Idéalement dans un `requestIdleCallback`.

**Astuce roughness gratuite** : la même luminance en niveaux de gris, inversée, fait
une `roughnessMap` très crédible (les creux sont plus mats que les reliefs). three lit
le canal **vert** pour la rugosité.

### 6.4 — Chanfreins

```js
function roundedRectShape(w, h, r){
  const s = new THREE.Shape();
  s.moveTo(-w / 2 + r, -h / 2);
  s.lineTo( w / 2 - r, -h / 2); s.quadraticCurveTo( w / 2, -h / 2,  w / 2, -h / 2 + r);
  s.lineTo( w / 2,  h / 2 - r); s.quadraticCurveTo( w / 2,  h / 2,  w / 2 - r,  h / 2);
  s.lineTo(-w / 2 + r,  h / 2); s.quadraticCurveTo(-w / 2,  h / 2, -w / 2,  h / 2 - r);
  s.lineTo(-w / 2, -h / 2 + r); s.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2);
  return s;
}
/* remplaçant direct de BoxGeometry(w,h,d) */
function bevelBox(w, h, d, bevel){
  const b = bevel === undefined ? Math.min(0.012, d * 0.15) : bevel;
  const g = new THREE.ExtrudeGeometry(roundedRectShape(w, h, b * 1.6), {
    depth: Math.max(0.001, d - b * 2),
    bevelEnabled: true, bevelThickness: b, bevelSize: b,
    bevelSegments: 2, curveSegments: 3
  });
  g.translate(0, 0, -d / 2 + b);
  g.computeVertexNormals();
  return g;
}
```

À appliquer sur : comptoir (`:837`), plateau de comptoir (`:840`), cadre du menu
(`:849`), machine (`:851`), poutres (`:775`), plinthes (`:789`), assises et dossiers de
chaises (`:894-897`), livre (`:1016`), tablier (`:995`), rebord de fenêtre (`:802`).

⚠️ `ExtrudeGeometry` génère des UV en **unités monde**, pas normalisées. Si la face
est texturée, il faut réécrire l'attribut `uv` ou n'utiliser `bevelBox` que sur les
objets de couleur unie (c'est le cas de presque tous ceux listés).

### 6.5 — La crasse (loi n°3)

Une seule texture de grunge réutilisée partout, multipliée :

```js
const grungeTex = ctex(512, 512, (x, w, h) => {
  x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, h);
  /* grosses taches douces */
  for (let i = 0; i < 40; i++){
    const g = x.createRadialGradient(
      Math.random() * w, Math.random() * h, 5,
      Math.random() * w, Math.random() * h, 60 + Math.random() * 160);
    g.addColorStop(0, 'rgba(60,50,40,0.30)');
    g.addColorStop(1, 'rgba(60,50,40,0)');
    x.fillStyle = g; x.fillRect(0, 0, w, h);
  }
  /* coulures verticales */
  x.globalAlpha = 0.14;
  for (let i = 0; i < 70; i++){
    x.fillStyle = '#3a2f22';
    x.fillRect(Math.random() * w, Math.random() * h, 1 + Math.random() * 3, 30 + Math.random() * 180);
  }
  x.globalAlpha = 1;
  speckle(x, w, h, 4000, 0.06);
});
```

Trois applications à faire à la main dans les fonctions de dessin existantes :
1. **Bas de murs plus sombres** : dans `brickTex` / `plasterTex`, ajouter un dégradé
   vertical `rgba(0,0,0,0.35)` → transparent sur les 25 % du bas. Un mur de café est
   *toujours* plus sale en bas.
2. **Cernes sur le comptoir** : 5–8 anneaux `rgba(0,0,0,0.10)` de rayon 45 px dans la
   texture du plateau. Immédiatement lisible comme « traces de tasses ».
3. **Usure sur les arêtes du bois** : dans `tableTex`, éclaircir un liseré de 8 px sur
   le pourtour (le bois s'use et blanchit sur les bords).

### 6.6 — Brouillard atmosphérique

```js
/* remplace index.html:519 */
scene.fog = new THREE.FogExp2(0x1a2228, 0.055);   /* teinté vers l'ombre froide */
scene.background = new THREE.Color(0x11151a);
```

La couleur du fog **doit** matcher la teinte des ombres de ton étalonnage, sinon la
profondeur se casse.

---

## 7. P2 — Caméra et mise en scène

C'est le palier le plus « game design » du document, et c'est là que ton projet peut
devenir mémorable.

### 7.1 — L'idée directrice

> **Quand Simon parle, ce n'est plus du gameplay : c'est une cinématique.**

Tu as déjà l'état (`speaking`, `index.html:509`). Il suffit de lui donner un langage
visuel. Ça règle en même temps trois problèmes que ton `README.md` identifie déjà :
l'absence de sous-titres, l'absence de dynamique, et le fait que la caméra fixe rende
les longues tirades statiques.

### 7.2 — Système de plans

```js
const SHOTS = {
  gameplay: { pos:[ 0.42, 1.30,  1.62], look:[0.00, 1.06, -0.95], fov:47, focus:2.6,  range:1.40 },
  closeup:  { pos:[ 0.34, 1.56,  0.18], look:[0.00, 1.58, -1.08], fov:34, focus:1.30, range:0.30 },
  overShldr:{ pos:[-0.62, 1.46,  0.62], look:[0.06, 1.52, -1.08], fov:40, focus:1.85, range:0.55 },
  insert:   { pos:[ 0.08, 1.62,  0.48], look:[0.00, 0.82,  0.22], fov:38, focus:0.95, range:0.22 },
  wide:     { pos:[ 1.90, 1.72,  2.30], look:[0.10, 1.10, -1.30], fov:52, focus:3.4,  range:2.20 }
};

let shot = SHOTS.gameplay, shotBlend = 1;
const camPos = new THREE.Vector3(), camLook = new THREE.Vector3();

function cutTo(name, hard){
  shot = SHOTS[name];
  shotBlend = hard ? 1 : 0;      /* hard = coupe franche façon montage */
  if (hard){
    camPos.fromArray(shot.pos);
    camLook.fromArray(shot.look);
  }
}
```

**Règle de montage GTA** : pendant une réplique longue, **coupe** (pas de transition)
toutes les 6–9 s entre `closeup`, `overShldr` et `insert`. Un plan qui dure 40 s est
mort ; trois coupes et la même réplique devient du cinéma.

```js
let nextCutAt = 0;
const COVERAGE = ['closeup', 'overShldr', 'closeup', 'insert'];
let coverageIdx = 0;
/* dans animate() */
if (speaking){
  if (t > nextCutAt){
    cutTo(COVERAGE[coverageIdx++ % COVERAGE.length], true);
    nextCutAt = t + 6 + Math.random() * 3;
  }
} else if (shot !== SHOTS.gameplay){
  cutTo('gameplay', false);        /* retour en douceur au « gameplay » */
  nextCutAt = 0; coverageIdx = 0;
}
```

### 7.3 — Respiration caméra (« handheld »)

Le détail qui sépare une caméra 3D d'une caméra de film. Amplitude minuscule,
fréquences irrationnelles pour éviter toute périodicité perceptible.

```js
function fbm1(t, s){
  return Math.sin(t * s) * 0.6
       + Math.sin(t * s * 2.17 + 1.3) * 0.3
       + Math.sin(t * s * 4.31 + 2.7) * 0.1;
}
/* après camera.lookAt() */
if (!RM){
  camera.position.x += fbm1(t, 0.37) * 0.0065;
  camera.position.y += fbm1(t, 0.31) * 0.0045;
  camera.rotation.z += fbm1(t, 0.23) * 0.0038;      /* ← le roulis, essentiel */
}
```

Le **roulis** est ce qui casse le plus efficacement le look « rendu 3D ». Une caméra
parfaitement horizontale n'existe pas au cinéma.

### 7.4 — Letterbox

```css
.bars{position:fixed;left:0;right:0;height:9vh;background:#000;z-index:22;
  pointer-events:none;transition:transform .5s cubic-bezier(.16,1,.3,1);}
.bars.top   {top:0;    transform:translateY(-100%);}
.bars.bottom{bottom:0; transform:translateY(100%);}
body.cinematic .bars{transform:translateY(0);}
```

`document.body.classList.toggle('cinematic', speaking)` — une ligne, effet immédiat.
Pendant la cinématique, masque aussi `.sign` et `.prompt`.

### 7.5 — Sous-titres façon GTA (et un vrai gain d'accessibilité)

Ton `README.md` reconnaît explicitement le trou : *« Anyone with sound off, in a quiet
office, or hard of hearing now gets nothing from the spoken sections. »* Le langage
GTA le comble.

Style GTA : blanc pur, **pas de fond**, ombre portée dure, centré bas, une à deux
lignes, sans-serif condensée.

```css
.subs{position:fixed;left:50%;bottom:calc(9vh + 22px);transform:translateX(-50%);
  z-index:24;max-width:min(72ch,86vw);text-align:center;
  font:400 20px/1.35 "Barlow Condensed","Space Grotesk",sans-serif;
  color:#fff;text-shadow:1px 1px 0 #000, 2px 2px 0 rgba(0,0,0,.55);
  pointer-events:none;opacity:0;transition:opacity .18s;}
.subs.on{opacity:1;}
```

Découpe le texte de `DATA[lang].speech[key]` en phrases (tu as déjà l'expression
régulière à `index.html:1330`) et avance sur `audioEl.currentTime`. Comme les mp3 n'ont
pas de timings, répartis **au prorata du nombre de caractères** sur `audioEl.duration` :
c'est approximatif à ±0,4 s, largement suffisant.

```js
function buildCues(text, duration){
  const parts = text.match(/[^.!?…]+[.!?…]+["']?|\S[^.!?…]*$/g) || [text];
  const total = parts.reduce((a, p) => a + p.length, 0);
  let acc = 0;
  return parts.map(p => {
    const start = acc / total * duration;
    acc += p.length;
    return { start, end: acc / total * duration, text: p.trim() };
  });
}
```

### 7.6 — Rack focus sur la feuille

Déjà décrit en 5.6. C'est le meilleur mariage entre effet cinéma et affordance d'UI de
tout le projet : **la mise au point dit où cliquer**.

---

## 8. P3 — HUD et interface

### 8.1 — Ce qui doit disparaître

Tout ton chrome actuel est du langage « web app 2024 » : `border-radius: 999px`,
`backdrop-filter: blur(3px)`, cartes arrondies, ombres douces, emoji. C'est l'exact
opposé de GTA.

| Actuel | Version GTA |
|---|---|
| `.pill` arrondie avec blur | Texte nu, capitales, condensé, ombre 1 px dure |
| `.lang` toggle pilule | `EN` et `FR` séparés par une fine barre verticale |
| `.sign` (enseigne Caveat) | Carton de mission bas-gauche qui glisse à l'entrée |
| `.howto` carte modale avec 6 emoji | Un prompt contextuel en bas d'écran, une ligne |
| `.prompt` flottant en Caveat | Prompt d'action : `[CLIC] EXAMINER LE CV` |

### 8.2 — Typographie

Tu auto-héberges déjà tes polices (`fonts.css`). Ajoute **une** famille condensée.
Recommandations OFL, sûres juridiquement :

| Rôle | Police | Note |
|---|---|---|
| HUD / prompts / sous-titres | **Barlow Condensed** ou **Archivo Narrow** | proche du Chalet de GTA sans en être |
| Titre / logo | **Anton** ou **Archivo Black** en oblique −8° | l'esprit Pricedown sans le Pricedown |
| Corps du CV texte | garde **Inter** | il doit rester lisible pour un recruteur |

Supprime **Caveat** de la scène 3D (mais garde-la sur le tableau noir — c'est de la
craie, c'est justifié).

### 8.3 — La minimap (l'élément le plus reconnaissable, et il peut être *utile*)

Un canvas 2D de 180 px, plan du café vu de dessus, blips pour chaque section du CV.
Ça devient ton **navigateur de sections** : cliquer un blip = déclencher la section.
Un élément de HUD parodique qui remplit une vraie fonction, c'est du bon design.

```
┌─ minimap ────────┐
│    ▫ comptoir    │
│  ●  ← Simon      │      ● jaune  = Simon (le sujet actif)
│  ◆ ◆ ◆ ◆         │      ◆ blanc  = sections non écoutées
│  ▪ toi           │      ◆ vert   = sections déjà écoutées
└──────────────────┘
```

Bas-gauche, contour 2 px blanc à 60 %, rotation avec le yaw caméra.

### 8.4 — Progression

GTA affiche un pourcentage de complétion. Tu as 7 sections + « about » + « outro ».

- **Carton de mission** à l'entrée : `MISSION — CAFÉ VIRTUEL` glisse depuis la gauche.
- **Toast de fin de section** : `SECTION TERMINÉE  ·  +1 RESPECT`, 2,5 s, bas-gauche.
- **À 100 %** : un panneau plein écran `COMPLÉTION 100 %` avec le récap des sections.
  C'est le moment où tu poses le CTA « on prend un vrai café ? » — un recruteur qui
  atteint 100 % est un recruteur intéressé.

C'est aussi la boucle de feedback qui manque totalement aujourd'hui : rien ne dit au
visiteur ce qu'il a déjà entendu, ni combien il en reste.

### 8.5 — ⚠️ Note juridique (à lire avant de dessiner le HUD)

Rockstar protège son *trade dress*. Concrètement, à éviter sur une page publique
indexée qui porte ton nom et sert à te faire embaucher :

- La police **Pricedown** (celle du logo GTA) et ses clones.
- Le HUD reproduit à l'identique : étoiles de recherche, minimap avec le tracé rose de
  GPS, compteur d'argent avec la typo et le vert exacts.
- Les écrans **WASTED** / **BUSTED** avec leur formulation et leur traitement.
- Le logo, le mot-marque, les noms de lieux (Los Santos, Vinewood, Del Perro…).

Ce qui est parfaitement sûr : **la grammaire**. Étalonnage, objectif, letterbox,
sous-titres, cartons de mission, minimap, pourcentage de complétion, typo condensée.
Personne ne possède ça. Vise « on dirait un jeu AAA moderne », pas « c'est GTA V ».

Et honnêtement, c'est aussi meilleur pour le message : un recruteur qui reconnaît
l'inspiration sourit ; un recruteur qui voit une contrefaçon se pose une question sur
ton jugement.

---

## 9. P4 — Le monde et la vie

### 9.1 — Los-Santos-iser le décor

Ton café est un café bruxellois. GTA, c'est un *diner* californien. La bonne DA n'est
pas de choisir : c'est de **tendre les deux** — un diner de Los Santos où le menu est
en français et où on sert des bières belges. La tension est la blague, et elle est déjà
amorcée par tes noms de boissons (`index.html:658-665`), qui sont excellents.

À ajouter, par ordre de rentabilité :

1. **Néon `VIRTUAL COFFEE`** au-dessus du comptoir : matériau `emissive` fort → le
   bloom fait tout le travail. Le halo néon est le signal « jeu moderne » n°1.
2. **Ventilateur de plafond** qui tourne, avec son ombre qui balaye la table.
3. **Sol en damier** vinyle sous le comptoir (zone diner) qui laisse place au parquet
   côté salle.
4. **Banquette vinyle** rouge capitonnée en fond de salle.
5. **Chrome** : rail de comptoir, tabourets, distributeur de serviettes, présentoir à
   gâteaux. Le chrome + IBL = réflexion = « ah, c'est du PBR ».
6. **Palmiers en silhouette** derrière la fenêtre + collines type Vinewood au loin.

### 9.2 — La fenêtre-portail

Remplacer le plan `MeshBasicMaterial` (`index.html:794-796`) par :

- une **boîte de profondeur** (intérieur d'un cube texturé) → parallaxe réelle quand la
  caméra bouge ;
- **3 couches de silhouettes** à distances différentes (immeubles proches / lointains /
  collines) → parallaxe multiplan ;
- 2–3 **voitures** = quads texturés qui traversent en boucle, avec un léger flou ;
- une **vitre** : `MeshPhysicalMaterial` `{transmission: 0.9, roughness: 0.08,
  thickness: 0.02}` + une normal map de traînées de pluie + un reflet du néon intérieur ;
- le **soleil** derrière → les shafts existants (`index.html:805-813`) deviennent
  justifiés, et le bloom leur donne enfin du corps.

Coût : ~120 lignes. Gain : la scène cesse d'être une boîte fermée.

### 9.3 — La radio (meilleur ratio « GTA » / effort de tout le document)

Tu as déjà un moteur audio complet. Ajoute :

- 2–3 « stations » = boucles mp3 courtes (jazz café / lo-fi / talk radio).
- Un sélecteur dans le HUD, typo condensée, avec le nom de station.
- Un **jingle DJ** de 3 s au changement de station.
- Ducking : la radio descend à −18 dB pendant que Simon parle, remonte après.
  (`GainNode` + `setTargetAtTime`, 6 lignes.)

Une station peut évidemment être une blague dans le ton du menu :
`RADIO SCRUM FM — « la seule station qui finit ses sprints »`.

### 9.4 — Bouche synchronisée à l'audio (gros gain de crédibilité)

Aujourd'hui : `mouthMesh.scale.y = 1 + |sin(t·14)| · 2.6` (`index.html:1478`), c'est-à-dire
une bouche qui bat à fréquence fixe, complètement décorrélée de la voix. L'œil le
détecte immédiatement.

L'amplitude réelle du signal audio pilote la mâchoire. ~15 lignes, effet massif :

```js
let actx = null, analyser = null, freqData = null, jawOpen = 0;
function attachAnalyser(el){
  if (!actx) actx = new (window.AudioContext || window.webkitAudioContext)();
  if (actx.state === 'suspended') actx.resume();     /* le clic « Take a seat » autorise */
  const src = actx.createMediaElementSource(el);     /* UNE seule fois par élément ! */
  analyser = actx.createAnalyser();
  analyser.fftSize = 256;
  analyser.smoothingTimeConstant = 0.55;
  freqData = new Uint8Array(analyser.frequencyBinCount);
  src.connect(analyser);
  analyser.connect(actx.destination);
}
/* dans speak(), juste après audioEl = new Audio(f) : */
try { attachAnalyser(audioEl); } catch(_) { analyser = null; }

/* dans animate() : */
let target = 0;
if (speaking && analyser){
  analyser.getByteFrequencyData(freqData);
  let s = 0; for (let i = 2; i < 26; i++) s += freqData[i];   /* ~100–1100 Hz = mâchoire */
  target = Math.min(1, (s / 24) / 105);
} else if (speaking){
  target = Math.abs(Math.sin(t * 11)) * 0.6;                  /* repli TTS */
}
jawOpen += (target - jawOpen) * Math.min(1, dt * 20);
mouthMesh.scale.y = 1 + jawOpen * 3.2;
mouthMesh.scale.x = 1 - jawOpen * 0.15;   /* la bouche se pince en s'ouvrant */
```

**Pièges** : `createMediaElementSource` ne peut être appelé qu'**une fois par élément
`<audio>`** — comme tu crées un `new Audio()` à chaque `speak()` (`index.html:1337`),
c'est bon. L'`AudioContext` doit être créé/repris après un geste utilisateur : le clic
« Take a seat » (`index.html:1415`) fait l'affaire.

### 9.5 — Ambiance sonore

Room tone de café en boucle à −32 dB + sifflement de machine toutes les ~40 s. Le
cerveau accepte beaucoup plus facilement une image imparfaite quand le son est riche.
C'est un truc de sound designer et ça marche à tous les coups.

### 9.6 — PNJ crédibles

Aujourd'hui les deux marcheurs font des allers-retours sur un rail (`index.html:1442-1459`),
ce qui est le tell n°1 du « jeu amateur ». Corrections peu coûteuses :

- **Pauses** : s'arrêter 2–5 s à un waypoint, regarder autour, repartir.
- **Vitesses variées** et légère variation de taille (±4 %) par personnage.
- **Regard** : orienter la tête vers Simon ou vers le comptoir plutôt qu'un sinus.
- **Ne pas faire demi-tour sur place** : ajouter un waypoint de sortie hors champ, et
  faire réapparaître par l'autre bout. Un PNJ qui pivote à 180° au milieu de la pièce
  brise l'illusion à lui tout seul.
- **Le barista doit faire quelque chose** : cycle de 12 s (moudre → tasser → tirer →
  servir), même grossier. Une boucle lisible bat une animation aléatoire.

---

## 10. Les personnages — le mur, et comment le contourner

C'est la seule partie où je te déconseille de viser GTA.

**Pourquoi c'est perdu d'avance à la main** : les visages GTA V, c'est du scan photo,
du rig facial FACS, des shaders de peau à diffusion sous-surfacique, des textures 4K
albedo/normal/spéculaire/cavité, et des cheveux en cartes alpha triées. Un rendu
« presque humain » raté est **immédiatement** plus repoussant qu'une stylisation
assumée. Sur une page de CV, l'effet serait catastrophique.

Trois voies :

### Option A — Assumer la stylisation (recommandée)
Garde des personnages nettement stylisés et laisse **le décor** porter le look AAA.
C'est ce que font *Fortnite*, *Overwatch*, *Astro Bot* : rendu photoréaliste, humains
stylisés. La combinaison marche très bien et personne ne crie à l'incohérence.
Coût : 0. C'est ce que je ferais.

### Option B — Passe de silhouette (bon compromis, ~1 j)
Sans changer de style, corriger ce qui trahit l'amateurisme :

1. **Tête** : pas une sphère. `SphereGeometry` mise à l'échelle `(1, 1.18, 0.92)` +
   une boîte de mâchoire chanfreinée en bas.
2. **Cou** : allongé et incliné de 6° vers l'avant (un cou vertical = un mannequin).
3. **Jonctions** : sphères aux épaules, coudes, poignets → plus de trous
   (`index.html:1040-1052`).
4. **Membres coniques** : `CylinderGeometry(0.052, 0.038, …)`, pas de cylindres droits.
5. **Yeux** : ajouter deux **paupières** = calottes sphériques de la couleur de la peau
   qui pivotent. Le clignement devient une rotation, pas un écrasement.
6. **Cheveux** : remplacer l'amas de 17 sphères (`index.html:1067-1074`) par une coque
   unique déformée, plus un `alphaMap` de mèches sur le pourtour.
7. **Vêtements** : un léger `normalMap` de tissu + `roughness: 0.9` +
   `envMapIntensity: 0.25`. Une chemise qui n'a aucun micro-relief lit « plastique ».
8. **Épaules tombantes** : ta sphère d'épaules est trop haute et trop ronde
   (`index.html:1032-1033`) — d'où le côté bonhomme de neige.

À elles seules, les corrections 3, 5 et 8 changent radicalement la lecture de Simon.

### Option C — Importer un avatar riggé (à faire seulement en connaissance de cause)
`GLTFLoader` existe en version non-module dans `examples/js` de r134 → vendorisable
sans build. Un avatar Ready Player Me fait 3–6 Mo avec ses textures.

Ce que ça coûte : **+4 à 8 Mo** sur une page que des recruteurs ouvrent en 4G, un
changement de DA qui rendra les PNJ procéduraux incohérents (il faudra tous les
remplacer), et un rig facial à animer. Ce que ça rapporte : un Simon crédible.

Mon avis : **non**, sauf si tu remplaces *tous* les personnages et acceptes de doubler
le poids de la page. Le rapport n'y est pas pour un CV.

---

## 11. Performance et paliers de qualité

### 11.1 — Mesurer d'abord

`renderer.info` est ta source de vérité. Expose-la temporairement :

```js
if (location.hash === '#debug'){
  window.__vcStats = () => ({
    calls: renderer.info.render.calls,
    tris:  renderer.info.render.triangles,
    progs: renderer.info.programs.length,
    mem:   renderer.info.memory
  });
}
```

D'après la lecture du code, tu es autour de **≈ 200 objets = ≈ 200 draw calls**, chacun
avec son propre matériau dans plusieurs cas. C'est beaucoup pour si peu de triangles.
Deux optimisations qui financent le post-traitement :

1. **Hoister les matériaux** hors de `person()` (`index.html:931-976`), `chair()`,
   `stool()`, `plant()`, `pendant()`. Tu passeras de ~90 matériaux à ~15.
2. **`InstancedMesh`** pour les pieds de chaises, les feuilles de plantes et les
   tabourets. −60 draw calls.

### 11.2 — Paliers

```js
const QUALITY = (function(){
  const dpr = devicePixelRatio || 1;
  const coarse = matchMedia('(pointer: coarse)').matches;
  const small  = Math.min(innerWidth, innerHeight) < 700;
  if (coarse || small) return { name:'low',    dpr:1.0, shadows:1024, bloom:2, dof:false, ao:false, grain:0.03 };
  if (dpr > 2)         return { name:'medium', dpr:1.5, shadows:2048, bloom:3, dof:true,  ao:false, grain:0.05 };
  return                      { name:'high',   dpr:2.0, shadows:2048, bloom:4, dof:true,  ao:true,  grain:0.055 };
})();
```

Plus une **sonde d'auto-dégradation** : mesurer le FPS moyen sur les 90 premières
frames après l'entrée ; si < 45, descendre d'un palier et réallouer les RT. Silencieux,
et ça sauve les vieilles machines.

### 11.3 — Budget cible

| Plateforme | Cible | Post activé |
|---|---|---|
| Desktop récent | 60 fps @ DPR 2 | tout |
| Desktop ancien / iGPU | 60 fps @ DPR 1.5 | pas de SSAO |
| Mobile haut de gamme | 30–60 fps @ DPR 1 | grade + vignette + grain + bloom 2 mips |
| Mobile entrée de gamme | 30 fps @ DPR 1 | **grade uniquement** (garder les overlays CSS dans ce cas) |

⚠️ Sur mobile le bloom en `HalfFloat` peut ne pas être filtrable
(`OES_texture_half_float_linear` absent) : prévoir un repli en `UnsignedByteType` avec
un tone-mapping partiel avant le bright-pass. Teste sur un vrai iPhone, pas dans le
simulateur.

### 11.4 — Poids de page

Tu es déjà à ~5,4 Mo (`three.min.js` 615 Ko + audio 4,6 Mo + fonts). Le post-traitement
n'ajoute **0 Ko de dépendance** (c'est du code inline). Mais si tu ajoutes radio +
ambiance, passe l'audio en `preload="none"` et charge à la demande — un CV doit
s'afficher vite.

---

## 12. Accessibilité et garde-fous

Le langage GTA est agressif visuellement. Trois garde-fous obligatoires.

1. **`prefers-reduced-motion`** (déjà géré partiellement, `index.html:510`) doit
   désormais aussi couper : la respiration caméra, le grain **animé** (garder un grain
   statique), les coupes de plans (rester sur `gameplay`), l'aberration chromatique,
   la poussière.

2. **Un vrai toggle « Réduire les effets »** dans le HUD, persisté en `localStorage`.
   Le bloom + le grain + la CA + la DOF déclenchent des gênes réelles (migraine,
   photosensibilité) chez une partie du public. Sur un site dont l'objectif est
   « qu'un recruteur lise mon CV », c'est non négociable.

3. **Le CV texte reste roi.** Tout ce document ne touche que la scène 3D. Le panneau
   `#cv-text` (`index.html:183-302`) et le repli `VC.textOnly()` doivent rester
   intacts, et la bascule de langue doit continuer de vivre hors du script de scène —
   c'est l'invariant que ton `README.md` défend, et il a raison.

4. **Clavier** : la scène est aujourd'hui 100 % souris. Ajoute `1`–`7` pour déclencher
   les sections, `0` pour l'outro, `Espace` pour couper la parole. C'est de
   l'accessibilité **et** c'est très « jeu vidéo » — affiche le mapping en HUD.

5. **`og.jpg` devra être re-rendu** après le changement de DA : c'est aujourd'hui un
   rendu cartoon (`og.jpg`, 1200×630) et ce sera la seule image que verront LinkedIn,
   Slack et les prévisualisations de lien. Si elle ne matche plus la page, tu perds
   l'effet de surprise au moment où il compte le plus.

---

## 13. Ordre d'exécution recommandé

Chaque étape est livrable et testable indépendamment.

```
□  1. Socle post-processing : RT HDR + quad plein écran + composite passthrough
      → vérifier que l'image est IDENTIQUE à avant (test du double-gamma)
□  2. Supprimer .vig et .grade du CSS
□  3. Étalonnage dans le composite (preset losSantosDay) + vignette + grain
      → PREMIER GROS CHOC VISUEL, arrête-toi et regarde
□  4. IBL (scene.environment) + envMapIntensity par matériau
      → DEUXIÈME GROS CHOC, le plastique disparaît
□  5. Bloom
□  6. Ombres retaillées + normalBias + mapSize 2048
□  7. Refroidir l'éclairage (hemisphere bleu, spot chaud saturé)
□  8. DOF + rack focus sur la feuille
□  9. Normal maps dérivées des canvas + roughness maps
□ 10. Chanfreins sur les 12 objets listés en 6.4
□ 11. Crasse : gradients bas de murs, cernes de tasses, usure d'arêtes
□ 12. Bouche pilotée par l'audio
□ 13. Caméra : plans, coupes, respiration, letterbox
□ 14. Sous-titres
□ 15. Paliers de qualité + sonde FPS + toggle « réduire les effets »
□ 16. HUD condensé + carton de mission + progression + minimap
□ 17. Radio + ambiance
□ 18. Fenêtre-portail + néon + densité de props
□ 19. Passe de silhouette sur les personnages (option B)
□ 20. Re-rendre og.jpg
```

Les étapes **1 à 8** représentent ~2 jours et **environ 70 % du résultat final**. Si tu
ne fais que ça, tu auras déjà gagné.

---

## 14. Ce que je ne ferais surtout pas

| À éviter | Pourquoi |
|---|---|
| Chasser la peau photoréaliste | Vallée de l'étrange. Perte sèche. |
| Ajouter un CDN pour un lib de post-processing | Règle du dépôt, et la CSP du Worker LazyPO t'a déjà mordu deux fois. Tout inline. |
| Vendoriser `EffectComposer` + 8 passes | Chaque passe = un blit plein écran. Une passe de composite fusionnée fait mieux, plus vite, plus réglable. |
| Un moteur physique | Zéro apport ici, +200 Ko. |
| Pousser le bloom / la CA / le grain « pour que ça se voie » | GTA est subtil. Si on remarque l'effet, il est trop fort. Règle : monte jusqu'à ce que ça se voie, puis divise par deux. |
| Reproduire le HUD GTA à l'identique | Trade dress Rockstar, sur une page qui porte ton nom. Cf. 8.5. |
| Rendre le CV moins lisible au nom de la DA | La DOF sur la feuille, le grain sur le texte, le letterbox qui coupe : à chaque effet, revérifie que **le CV reste lisible**. C'est l'unique métier de cette page. |
| Dépasser ~8 Mo de page | Un recruteur en 4G entre deux réunions ferme l'onglet. |

---

## 15. Les huit changements à faire ce soir si tu n'as qu'une heure

Par ordre décroissant de ratio impact / effort :

1. **`scene.environment`** via `PMREMGenerator.fromScene()` (§6.2) — 40 lignes.
   *Le plastique disparaît.*
2. **Réduire la caméra d'ombre** de 10 × 6 m à 7 × 3,5 m et passer en 2048 (§6.1) —
   4 lignes. *Ombres 6× plus nettes, gratuit.*
3. **`shadow.normalBias = 0.02`** sur les deux lumières porteuses d'ombre — 2 lignes.
4. **`clearcoat: 1`** sur la table (`MeshPhysicalMaterial`) — 3 lignes. *La plus grande
   surface de l'écran devient du vrai bois verni.*
5. **`HemisphereLight` en bleu** `0x9fc4e8` et spot en `0xffb867` (§6.1) — 2 lignes.
   *Le contraste chaud/froid apparaît.*
6. **Roulis + respiration caméra** (§7.3) — 6 lignes. *Ça cesse d'être un rendu 3D.*
7. **Letterbox pendant `speaking`** (§7.4) — 8 lignes CSS + 1 ligne JS.
8. **Bouche pilotée par l'audio** (§9.4) — 15 lignes. *Simon devient vivant.*

Total : ~80 lignes, une heure, et le résultat est déjà méconnaissable.

---

## Annexe A — Références visuelles à garder ouvertes

- **GTA V, intérieurs de jour** : observer précisément le rapport entre la lumière de
  fenêtre (froide, forte) et les pratiques intérieures (chaudes, faibles). C'est
  exactement l'inverse de ta scène actuelle.
- **GTA V, cinématiques** : chronométrer les coupes. Elles tombent toutes les 5 à 9 s.
- **Red Dead Redemption 2, saloons** : la référence absolue pour un intérieur en bois
  éclairé aux pratiques. Regarder la crasse et la densité de props.
- **The Last of Us Part II** : la référence pour le grain et la DOF discrète.
- **Fortnite / Astro Bot** : la preuve qu'un rendu AAA + des personnages stylisés,
  ça marche (cf. option A, §10).

## Annexe B — Fichiers et lignes cités

| Sujet | Emplacement |
|---|---|
| Overlays CSS à supprimer | `index.html:54-57`, `index.html:160` |
| Renderer / tone mapping | `index.html:526-535` |
| Caméra + `far` | `index.html:520-522`, `index.html:1426-1436` |
| Helper de texture `ctex()` | `index.html:546-552` |
| Textures procédurales | `index.html:560-722` |
| Rig de lumières | `index.html:725-765` |
| Pièce, murs, fenêtre | `index.html:768-832` |
| Comptoir | `index.html:834-876` |
| Tables / chaises / tapis | `index.html:878-928` |
| Fabrique de personnages | `index.html:931-1022` |
| Simon | `index.html:1024-1175` |
| Feuille de CV (canvas) | `index.html:1177-1258` |
| Interaction / picking | `index.html:1260-1298` |
| Audio et parole | `index.html:1300-1356` |
| Boucle d'animation | `index.html:1423-1520` |
| Point de rendu à remplacer | `index.html:1518` |

---

*Revue rédigée après lecture intégrale de `index.html` (1 524 lignes) et observation du
rendu en cours d'exécution. Les extraits de code ciblent three.js r134 sans étape de
build et sans dépendance externe, conformément aux contraintes du dépôt.*
