# Brief d'implémentation 3D — Virtual Coffee → rendu GTA V + vie de fond

> **Destinataire : agent d'implémentation spécialisé en 3D temps réel.**
> Ce document est un contrat d'exécution, pas une note d'intention. Il est autoportant :
> tout ce qui est nécessaire pour livrer est ici ou dans les fichiers cités en §0.2.
>
> Document amont (contexte et argumentaire de direction artistique) :
> [`ART_DIRECTION_GTA5.md`](ART_DIRECTION_GTA5.md). Ce brief-ci en est la traduction
> exécutable, approfondie et vérifiée contre le build réel de three.js.

---

## 0. Contrat d'exécution

### 0.1 — Ce que tu dois produire

Une modification de **`index.html`** — et uniquement de ce fichier, plus `fonts.css` /
`fonts/` si tu ajoutes une famille typographique (§8.2), plus des boucles audio si tu
implémentes le babil (§7.10) et la radio (§8.9).

Il n'y a **aucun autre fichier source**. Tout le JS de la scène vit inline dans
`index.html`, dans une IIFE qui commence ligne 436 et se termine ligne 1521.

### 0.2 — Ce que tu dois lire AVANT d'écrire une ligne

| Fichier | Pourquoi |
|---|---|
| `index.html` (1 524 lignes) | La totalité du projet. Lis-le **en entier**, pas en diagonale. |
| `ART_DIRECTION_GTA5.md` | Le pourquoi de chaque décision. Ce brief donne le comment. |
| `README.md` | Les invariants du dépôt et les pièges de déploiement. |
| `three.min.js` | **Ta source de vérité sur l'API.** Grep-le avant d'utiliser une classe ou une propriété (méthode en Annexe C). |

### 0.3 — Contraintes non négociables

| Contrainte | Conséquence pratique |
|---|---|
| **three.js r134**, build UMD vendorisé | Pas d'`examples/jsm`. Pas d'`import`. Pas d'`EffectComposer`, pas de `GLTFLoader`, pas de `RoomEnvironment`, pas de `RectAreaLightUniformsLib`. |
| **Aucun build step** | Pas de bundler, pas de transpilation, pas de `package.json`. Le fichier doit fonctionner ouvert directement dans un navigateur. |
| **Aucun CDN, jamais** | Toute ressource est servie depuis le dépôt. Un `<script src="https://…">` fonctionne en local et casse en production. Régression déjà survenue deux fois sur les projets frères. |
| **Le CV texte est intouchable** | `#cv-text` (`index.html:183-302`), le shell `VC` (`:316-419`) et le repli `VC.textOnly()` (`:398-408`) sont la version accessible du site. Un visiteur sans WebGL, un lecteur d'écran ou un robot d'indexation ne voient QUE ça. |
| **`prefers-reduced-motion`** | Chaque effet ajouté doit avoir un comportement défini quand la préférence est active. La variable existe déjà : `RM`, `index.html:510`. |
| **Budget de page** | ≈ 5,4 Mo aujourd'hui (three 615 Ko + audio 4,6 Mo + polices). Plafond dur : **8 Mo**. |
| **Page publique indexée** | Elle porte le nom réel d'une personne et sert à la faire embaucher. Voir la note de conformité §8.2. |

### 0.4 — Comment travailler

1. **Par lots, dans l'ordre du §9.** Chaque lot est livrable et testable seul.
2. **Après chaque lot, exécute la recette de validation correspondante (§8.13).**
   Tu n'as pas d'yeux : les critères d'acceptation et les tests console sont ta seule
   boucle de retour. Ne passe pas au lot suivant si un test échoue.
3. **Vérifie l'API avant de l'utiliser.** Ta mémoire d'une version plus récente de
   three.js n'est pas une preuve — r134 date de novembre 2021 et plusieurs propriétés
   ont été renommées depuis.
4. **Ne réorganise pas le fichier.** Le style d'indentation plat de la scène est
   délibéré (commentaire `index.html:432-434`) : il garde le diff lisible contre le
   prototype.
5. **Un seul système à la fois.** Ne mélange pas une refonte de post-traitement et une
   refonte de rig dans la même passe : si l'image casse, tu ne sauras pas d'où ça vient.

### 0.5 — Conventions du fichier existant

- Indentation plate dans l'IIFE de la scène.
- Bannières de section : `/* ---------------- TITRE ---------------- */`.
- Commentaires en anglais dans la scène, en français dans la documentation.
- Toute texture procédurale passe par `ctex(w, h, draw)` (`index.html:546-552`).
- Le mouchetis partagé est `speckle(ctx, w, h, n, alpha)` (`index.html:553-558`).
- Toute nouvelle texture reçoit `anisotropy = maxAniso` (`index.html:536`).

### 0.6 — Résultat de l'audit d'API r134 (déjà fait, ne le refais pas)

Vérifié par grep sur `three.min.js`. `THREE.REVISION === "134"`.

| Symbole | Présent | Note |
|---|---|---|
| `MeshPhysicalMaterial.clearcoat` / `.clearcoatRoughness` | ✅ | En **minuscule** : `clearcoat`, jamais `clearCoat`. |
| `.transmission` / `.thickness` / `.ior` | ✅ | Coûteux, voir §3.6. |
| `PMREMGenerator.fromScene` | ✅ | Signature `(scene, sigma, near, far)`. |
| `Light.shadow.normalBias` | ✅ | |
| `renderer.physicallyCorrectLights` | ✅ | Nom r134. Renommé `useLegacyLights` plus tard : **n'utilise pas** ce nom-là. |
| `renderer.outputEncoding`, `sRGBEncoding`, `LinearEncoding` | ✅ | Noms r134. `outputColorSpace` / `SRGBColorSpace` **n'existent pas**. |
| `DepthTexture`, `UnsignedIntType`, `HalfFloatType` | ✅ | |
| `WebGLMultisampleRenderTarget` | ✅ | Mais inutilisable ici, voir §2.2 point 6. |
| `camera.projectionMatrixInverse` | ✅ | ⚠️ `inverseProjectionMatrix` **n'existe pas** (0 occurrence). |
| `InstancedMesh`, `Frustum`, `Box3`, `MathUtils`, `Quaternion` | ✅ | |
| `AudioListener`, `PositionalAudio`, `Audio`, `AudioLoader` | ✅ | |
| `ExtrudeGeometry`, `LatheGeometry`, `TubeGeometry`, `CatmullRomCurve3` | ✅ | |
| `Object3D.attach` | ✅ | Reparente en conservant la transformée monde. |
| `onBeforeCompile` | ✅ | Pour patcher un shader intégré sans le réécrire. |
| **`RectAreaLight`** | ⚠️ | La classe existe et les chunks `LTC_*` sont dans le build, **mais `RectAreaLightUniformsLib` est absent** (0 occurrence) : les textures LTC ne peuvent pas être uploadées. **N'utilise pas `RectAreaLight`.** Remplace par un émetteur dans l'environnement IBL (§3.4) plus un `PointLight` faible. |
| `#include <packing>` / `perspectiveDepthToViewZ` | ✅ | Fonctionne dans un `ShaderMaterial` brut. |

---

## 1. État des lieux et cible

### 1.1 — Ce qui existe

Une scène three.js entièrement procédurale, sans aucun asset 3D : ~200 objets
construits à partir de primitives, et une dizaine de textures peintes dans des
`<canvas>` au chargement.

| Domaine | État |
|---|---|
| Rendu | Direct dans le canvas. ACES + exposure 1.18. **Aucun post-traitement.** |
| Éclairage | Hemisphere chaude + spot chaud + directionnelle froide faible + 2 points. **Aucun `scene.environment`.** |
| Matériaux | `MeshStandardMaterial` couleur plate + `roughness`. **Aucune normal map, aucune roughness map, aucune AO.** |
| Géométrie | Primitives à arêtes vives. Aucun chanfrein. |
| Caméra | Fixe, frontale, centrée, FOV 50, parallaxe souris ±0,10 m. |
| Personnages | 6 agents animés par des sinus en boucle ouverte. |
| Audio | mp3 de la vraie voix (EN) + repli `SpeechSynthesis`. Aucun son d'ambiance. |
| Interface | Chrome web moderne : pilules arrondies, `backdrop-filter`, carte modale, emoji. |

### 1.2 — Pourquoi ça lit « pâte à modeler »

Deux causes racines dominent tout le reste :

1. **Aucun éclairage image-based.** Sans `scene.environment`, le terme spéculaire des
   matériaux PBR n'a rien à réfléchir. La machine à café en `metalness: 0.65`
   (`index.html:851-853`) rend grise et morte, parce qu'un métal sans réflexion **est**
   gris et mort.
2. **Aucun post-traitement.** L'identité visuelle d'un jeu AAA moderne se joue à 60 %
   dans l'objectif et l'étalonnage, pas dans la géométrie.

S'y ajoutent, par ordre d'impact : arêtes vives partout, palette monochrome chaude qui
ne laisse rien à étalonner, caméra statique frontale, monde vide et neuf, ombres mal
budgétées, personnages animés par des fonctions périodiques.

### 1.3 — La cible

**« GTA V stylisé »**, en six couches :

| Couche | Section |
|---|---|
| L'objectif et l'étalonnage | §2 |
| La lumière et la matière | §3 |
| La crasse, le relief, la densité | §4 |
| La mise en scène | §5 |
| **La vie** | **§6 et §7** |
| L'interface et le son | §8 |

**Hors cible, explicitement :** le photoréalisme des personnages. Un humain « presque
réel » est plus repoussant qu'un humain franchement stylisé. Le décor porte le rendu
AAA ; les personnages gagnent en crédibilité par le **comportement**, pas par le
shading. C'est la stratégie de *Fortnite* et d'*Astro Bot*.

### 1.4 — Les deux systèmes à créer de zéro

- **La vie de fond** (§6, §7). Les clients doivent **discuter** entre eux et
  **travailler**. Demande explicite du commanditaire, et partie du chantier au plus
  fort rendement perçu.
- **La grammaire cinématographique** (§5). Quand Simon parle, on passe en cinématique.
  Règle aussi trois manques que le `README.md` reconnaît lui-même.

---

## 2. Pipeline de rendu et post-traitement

**Objectif visuel :** faire passer l'image d'un rendu 3D brut à une image d'objectif —
bloom large et discret, profondeur de champ, grain, aberration chromatique, vignettage,
et un étalonnage à noirs froids / hautes lumières ocre.

### 2.1 — État actuel

`index.html:515-543`. Le renderer rend directement dans le canvas, avec ACES et
`toneMappingExposure = 1.18`. Les deux overlays CSS `.vig` et `.grade`
(`index.html:54-57`, insérés `:160`) simulent un vignettage et un étalonnage en
`mix-blend-mode`, en aveugle, après coup, sur du sRGB. Ils devront disparaître (§2.13).

### 2.2 — Les six pièges r134, à connaître avant d'écrire

| # | Piège | Symptôme si ignoré |
|---|---|---|
| 1 | `renderer.toneMapping` doit passer à `THREE.NoToneMapping`. ACES part dans le composite. | Le bloom ne capte plus rien : le tonemapping a déjà écrasé toutes les valeurs > 1. Image plate, bloom invisible quel que soit le seuil. |
| 2 | Un `ShaderMaterial` brut ne reçoit **pas** l'injection `<encodings_fragment>` de three. L'encodage sRGB final est à ta charge. | Image délavée (double gamma) ou anormalement sombre. C'est le bug le plus fréquent de cette architecture. |
| 3 | Les textures de render target intermédiaires en `LinearEncoding`. Les `CanvasTexture` de couleur restent en `sRGBEncoding` (déjà fait, `index.html:550`). | Couleurs qui dérivent à chaque passe. |
| 4 | Toute donnée non-couleur (normal map, roughness, AO, bruit) en `LinearEncoding`. | Relief faux, rugosité fausse — et tu chercheras le bug dans ton code de dérivation. |
| 5 | `antialias: true` (`index.html:526`) devient **inopérant** dès qu'on rend dans un render target. | Escaliers sur toutes les arêtes. Il faut FXAA (§2.8). |
| 6 | `WebGLMultisampleRenderTarget` existe mais résout la couleur par blit depuis des *renderbuffers* : une `DepthTexture` attachée n'est pas remplie. | Pas de MSAA **et** pas de profondeur. **Choisis : MSAA sans DOF/SSAO, ou profondeur + FXAA.** Ce brief choisit profondeur + FXAA. |

Piège annexe : baisse `camera.far` de 40 (`index.html:520`) à **25**. La pièce fait
10 m de profondeur ; une plage de 40 gaspille la précision de la depth texture.

### 2.3 — Socle : cibles et quad plein écran

À insérer juste après `app.appendChild(renderer.domElement)` (`index.html:535`).

```js
/* ---------------- POST : SOCLE ---------------- */
renderer.toneMapping = THREE.NoToneMapping;      /* ACES part dans le composite */
camera.far = 25; camera.updateProjectionMatrix();

const IS_GL2 = renderer.capabilities.isWebGL2;
const gl = renderer.getContext();
const CAN_HALF_LINEAR = IS_GL2 || !!gl.getExtension('OES_texture_half_float_linear');
const CAN_DEPTH_TEX   = IS_GL2 || !!gl.getExtension('WEBGL_depth_texture');
const HDR_TYPE = CAN_HALF_LINEAR ? THREE.HalfFloatType : THREE.UnsignedByteType;

function makeRT(w, h, opts){
  return new THREE.WebGLRenderTarget(Math.max(1, w | 0), Math.max(1, h | 0), Object.assign({
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    format: THREE.RGBAFormat,
    type: HDR_TYPE,
    encoding: THREE.LinearEncoding,
    depthBuffer: false,
    stencilBuffer: false
  }, opts || {}));
}

const fsScene = new THREE.Scene();
const fsCam   = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const fsQuad  = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), null);
fsQuad.frustumCulled = false;
fsScene.add(fsQuad);

function blit(material, target, additive){
  fsQuad.material = material;
  renderer.setRenderTarget(target || null);
  if (!additive) renderer.clear();
  renderer.render(fsScene, fsCam);
}

const QUAD_VS = `
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

/* texture blanche 1×1 : neutre quand l'AO est désactivée */
const whiteTex = (function(){
  const d = new Uint8Array([255, 255, 255, 255]);
  const t = new THREE.DataTexture(d, 1, 1, THREE.RGBAFormat);
  t.needsUpdate = true; return t;
})();
```

### 2.4 — Allocation et resize

**C'est la source de fuite mémoire n°1 de cette architecture.** Un render target non
disposé garde sa texture GPU vivante ; à chaque resize tu en fabriques huit de plus.

```js
let RT_HDR = null, RT_BRIGHT = null, RT_AO = null, RT_AOB = null,
    RT_DOF = null, RT_LDR = null, MIPS = [];
const BLOOM_MIPS = 4;

function disposeTargets(){
  [RT_HDR, RT_BRIGHT, RT_AO, RT_AOB, RT_DOF, RT_LDR].forEach(rt => {
    if (!rt) return;
    if (rt.depthTexture) rt.depthTexture.dispose();
    rt.dispose();
  });
  MIPS.forEach(rt => rt.dispose());
  MIPS = [];
}

function allocTargets(){
  disposeTargets();
  const size = renderer.getDrawingBufferSize(new THREE.Vector2());
  const w = size.x, h = size.y;

  RT_HDR = makeRT(w, h, { depthBuffer: true });
  if (CAN_DEPTH_TEX){
    const dt = new THREE.DepthTexture(w, h);
    dt.type = IS_GL2 ? THREE.UnsignedIntType : THREE.UnsignedShortType;
    dt.minFilter = dt.magFilter = THREE.NearestFilter;
    RT_HDR.depthTexture = dt;
  }
  RT_BRIGHT = makeRT(w / 2, h / 2);
  RT_AO     = makeRT(w / 2, h / 2, { type: THREE.UnsignedByteType });
  RT_AOB    = makeRT(w / 2, h / 2, { type: THREE.UnsignedByteType });
  RT_DOF    = makeRT(w, h);
  RT_LDR    = makeRT(w, h, { type: THREE.UnsignedByteType });
  for (let i = 0; i < BLOOM_MIPS; i++) MIPS.push(makeRT(w / (4 << i), h / (4 << i)));

  /* propager la résolution à TOUS les uniformes qui en dépendent */
  compMat.uniforms.uRes.value.set(w, h);
  fxaaMat.uniforms.uRes.value.set(w, h);
  dofMat.uniforms.uTexel.value.set(1 / w, 1 / h);
  ssaoMat.uniforms.uRes.value.set(w / 2, h / 2);
}
```

Et dans `onResize()` (`index.html:537-542`), après `renderer.setSize(...)`, ajouter
`allocTargets();`. **Attention à l'ordre d'initialisation** : `allocTargets` référence
`compMat`, `fxaaMat`, `dofMat`, `ssaoMat` — déclare les matériaux avant, et n'appelle
`allocTargets()` la première fois qu'après leur création. `onResize()` est déjà appelé
ligne 543, donc protège-le comme le fait déjà `stagingReady` :

```js
let postReady = false;
function onResize(){
  camera.aspect = innerWidth / innerHeight;
  renderer.setSize(innerWidth, innerHeight);
  if (postReady) allocTargets();
  if (stagingReady) applyStaging();
  else { camera.fov = camera.aspect < 0.75 ? 64 : 50; camera.updateProjectionMatrix(); }
}
```

### 2.5 — Bright pass et bloom

**Objectif visuel :** un halo large et discret autour des ampoules, du néon et des
hautes lumières. Si tu remarques le bloom, il est trop fort.

```js
const brightMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uThreshold:{value:1.05}, uKnee:{value:0.45} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform float uThreshold, uKnee;
    varying vec2 vUv;
    void main(){
      vec3 c = texture2D(tSrc, vUv).rgb;
      float br = max(c.r, max(c.g, c.b));
      float soft = clamp(br - uThreshold + uKnee, 0.0, 2.0 * uKnee);
      soft = soft * soft / (4.0 * uKnee + 1e-4);
      float k = max(soft, br - uThreshold) / max(br, 1e-4);
      gl_FragColor = vec4(c * k, 1.0);
    }`,
  depthTest:false, depthWrite:false
});

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
             + texture2D(tSrc, vUv).rgb                   * 4.0
             + texture2D(tSrc, vUv + vec2( o.x, 0.0)).rgb * 2.0
             + texture2D(tSrc, vUv + vec2(-o.x, o.y)).rgb
             + texture2D(tSrc, vUv + vec2( 0.0, o.y)).rgb * 2.0
             + texture2D(tSrc, vUv + vec2( o.x, o.y)).rgb;
      gl_FragColor = vec4(s / 16.0, 1.0);
    }`,
  blending: THREE.AdditiveBlending, transparent: true,
  depthTest:false, depthWrite:false
});

function renderBloom(mipCount){
  brightMat.uniforms.tSrc.value = RT_HDR.texture;
  blit(brightMat, RT_BRIGHT);
  let src = RT_BRIGHT;
  for (let i = 0; i < mipCount; i++){
    downMat.uniforms.tSrc.value = src.texture;
    downMat.uniforms.uTexel.value.set(1 / src.width, 1 / src.height);
    blit(downMat, MIPS[i]); src = MIPS[i];
  }
  for (let i = mipCount - 1; i > 0; i--){
    upMat.uniforms.tSrc.value = MIPS[i].texture;
    upMat.uniforms.uTexel.value.set(1 / MIPS[i].width, 1 / MIPS[i].height);
    upMat.uniforms.uRadius.value = 1.0 + i * 0.6;
    blit(upMat, MIPS[i - 1], true);        /* additif : pas de clear */
  }
}
```

| Réglage | Valeur | Effet |
|---|---|---|
| `uThreshold` | 1.05 | En dessous de 1.0, les surfaces claires bavent. Au-dessus de 1.3, seules les ampoules bloomeront. |
| `uKnee` | 0.45 | Transition douce autour du seuil. À 0, le bloom apparaît d'un coup et ça se voit. |
| `uBloom` (composite) | **0.32 max** | C'est le réglage qu'on est tenté de monter. Ne le monte pas. |

### 2.6 — Profondeur de champ

**Objectif visuel :** net sur le sujet, doux sur le mur du fond et sur le bord de table.
C'est le plus gros contributeur unique au « look objectif ».

```js
const dofMat = new THREE.ShaderMaterial({
  uniforms:{
    tSrc:{value:null}, tDepth:{value:null},
    uTexel:{value:new THREE.Vector2()},
    uFocus:{value:2.6}, uRange:{value:1.4}, uMaxCoC:{value:9.0},
    cameraNear:{value:0.1}, cameraFar:{value:25.0}
  },
  vertexShader: QUAD_VS,
  fragmentShader:`
    #include <packing>
    uniform sampler2D tSrc, tDepth;
    uniform vec2 uTexel;
    uniform float uFocus, uRange, uMaxCoC, cameraNear, cameraFar;
    varying vec2 vUv;

    float viewDist(vec2 uv){
      float d = texture2D(tDepth, uv).x;
      return -perspectiveDepthToViewZ(d, cameraNear, cameraFar);
    }
    float coc(vec2 uv){
      float z = viewDist(uv);
      return clamp((abs(z - uFocus) - uRange) / max(uRange, 1e-3), 0.0, 1.0);
    }
    void main(){
      float c = coc(vUv);
      vec3 sum = texture2D(tSrc, vUv).rgb;
      float wsum = 1.0;
      float r = c * uMaxCoC;
      for (int ring = 1; ring <= 2; ring++){
        float rr = r * float(ring) * 0.5;
        for (int i = 0; i < 6; i++){
          float a = float(i) / 6.0 * 6.2831853 + float(ring) * 0.5236;
          vec2 off = vec2(cos(a), sin(a)) * rr * uTexel;
          float cs = coc(vUv + off);
          /* n'accepte que les échantillons AU MOINS aussi flous : anti-bleeding */
          float w = step(c * 0.75, cs) * step(0.011, c);
          sum  += texture2D(tSrc, vUv + off).rgb * w;
          wsum += w;
        }
      }
      gl_FragColor = vec4(sum / wsum, c);   /* alpha = CoC, réutilisable */
    }`,
  depthTest:false, depthWrite:false
});
```

> **Note WebGL1** : les bornes de boucle doivent être des constantes littérales. Les
> boucles ci-dessus le sont (`ring <= 2`, `i < 6`). Ne les rends pas dynamiques.

Réglages par plan (les valeurs sont pilotées par §5.7) :

| Plan | `uFocus` | `uRange` | Effet |
|---|---|---|---|
| `gameplay` | 2.6 | 1.40 | Simon net, mur du fond doux, bord de table doux |
| `closeup` (Simon parle) | 1.35 | 0.30 | Seul le visage net — très cinéma |
| `insert` (sur le CV) | 0.95 | 0.22 | La feuille nette, tout le reste fondu |
| Survol de la feuille | 0.95 | 0.25 | Rack focus : la MAP dit où cliquer |

### 2.7 — Occlusion ambiante

**Objectif visuel :** coller les objets au sol et noircir les angles. Sans ça, tout
flotte.

Deux implémentations selon le palier de qualité.

#### 2.7.a — SSAO depth-only (palier `high`)

```js
const ssaoMat = new THREE.ShaderMaterial({
  uniforms:{
    tDepth:{value:null},
    uRes:{value:new THREE.Vector2()},
    uProjInv:{value:new THREE.Matrix4()},
    uProj:{value:new THREE.Matrix4()},
    uRadius:{value:0.30}, uBias:{value:0.022}, uIntensity:{value:1.15},
    cameraNear:{value:0.1}, cameraFar:{value:25.0}
  },
  vertexShader: QUAD_VS,
  fragmentShader:`
    #include <packing>
    uniform sampler2D tDepth;
    uniform vec2 uRes; uniform mat4 uProjInv, uProj;
    uniform float uRadius, uBias, uIntensity, cameraNear, cameraFar;
    varying vec2 vUv;

    /* 12 directions en hémisphère, longueurs croissantes (poisson-ish, en dur
       car WebGL1 interdit l'indexation dynamique de tableau) */
    vec3 kernel(int i){
      if(i==0)  return vec3( 0.5381, 0.1856, 0.4319);
      if(i==1)  return vec3( 0.1379, 0.2486, 0.4430);
      if(i==2)  return vec3( 0.3371, 0.5679, 0.0057);
      if(i==3)  return vec3(-0.6999,-0.0451, 0.0019);
      if(i==4)  return vec3( 0.0689,-0.1598, 0.8547);
      if(i==5)  return vec3( 0.0560, 0.0069, 0.1843);
      if(i==6)  return vec3(-0.0146, 0.1402, 0.0762);
      if(i==7)  return vec3( 0.0100,-0.1924,-0.0344);
      if(i==8)  return vec3(-0.3577,-0.5301,-0.4358);
      if(i==9)  return vec3(-0.3169, 0.1063, 0.0158);
      if(i==10) return vec3( 0.0103,-0.5869, 0.0046);
      return          vec3(-0.0897,-0.4940, 0.3287);
    }
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }

    vec3 viewPos(vec2 uv){
      float d = texture2D(tDepth, uv).x;
      vec4 ndc = vec4(uv * 2.0 - 1.0, d * 2.0 - 1.0, 1.0);
      vec4 v = uProjInv * ndc;
      return v.xyz / v.w;
    }
    void main(){
      float d = texture2D(tDepth, vUv).x;
      if (d >= 0.9999){ gl_FragColor = vec4(1.0); return; }   /* ciel / vide */

      vec3 P = viewPos(vUv);
      vec3 N = normalize(cross(dFdx(P), dFdy(P)));
      float rnd = hash(vUv * uRes) * 6.2831853;
      float c = cos(rnd), s = sin(rnd);
      mat2 rot = mat2(c, -s, s, c);

      float occ = 0.0;
      for (int i = 0; i < 12; i++){
        vec3 k = kernel(i);
        k.xy = rot * k.xy;
        if (dot(k, N) < 0.0) k = -k;                 /* rabat dans l'hémisphère */
        vec3 sp = P + k * uRadius;
        vec4 cp = uProj * vec4(sp, 1.0);
        vec2 suv = (cp.xy / cp.w) * 0.5 + 0.5;
        if (suv.x < 0.0 || suv.x > 1.0 || suv.y < 0.0 || suv.y > 1.0) continue;
        float sz = viewPos(suv).z;
        float rangeCheck = smoothstep(0.0, 1.0, uRadius / max(0.0001, abs(P.z - sz)));
        occ += (sz >= sp.z + uBias ? 1.0 : 0.0) * rangeCheck;
      }
      float ao = 1.0 - (occ / 12.0) * uIntensity;
      gl_FragColor = vec4(vec3(clamp(ao, 0.0, 1.0)), 1.0);
    }`,
  extensions:{ derivatives: true },
  depthTest:false, depthWrite:false
});

/* flou 4×4 séparable pour casser le bruit du kernel */
const aoBlurMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uTexel:{value:new THREE.Vector2()}, uDir:{value:new THREE.Vector2(1,0)} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform vec2 uTexel, uDir; varying vec2 vUv;
    void main(){
      vec2 o = uTexel * uDir;
      float s = texture2D(tSrc, vUv - o * 1.5).r * 0.25
              + texture2D(tSrc, vUv - o * 0.5).r * 0.25
              + texture2D(tSrc, vUv + o * 0.5).r * 0.25
              + texture2D(tSrc, vUv + o * 1.5).r * 0.25;
      gl_FragColor = vec4(vec3(s), 1.0);
    }`,
  depthTest:false, depthWrite:false
});

function renderSSAO(){
  ssaoMat.uniforms.tDepth.value = RT_HDR.depthTexture;
  ssaoMat.uniforms.uProj.value.copy(camera.projectionMatrix);
  ssaoMat.uniforms.uProjInv.value.copy(camera.projectionMatrixInverse);
  ssaoMat.uniforms.cameraNear.value = camera.near;
  ssaoMat.uniforms.cameraFar.value  = camera.far;
  blit(ssaoMat, RT_AO);
  aoBlurMat.uniforms.tSrc.value = RT_AO.texture;
  aoBlurMat.uniforms.uTexel.value.set(1 / RT_AO.width, 1 / RT_AO.height);
  aoBlurMat.uniforms.uDir.value.set(1, 0);  blit(aoBlurMat, RT_AOB);
  aoBlurMat.uniforms.tSrc.value = RT_AOB.texture;
  aoBlurMat.uniforms.uDir.value.set(0, 1);  blit(aoBlurMat, RT_AO);
}
```

> `camera.projectionMatrixInverse` est tenu à jour par `updateProjectionMatrix()`.
> **Le nom `inverseProjectionMatrix` n'existe pas en r134** (vérifié : 0 occurrence).

#### 2.7.b — Blob shadows (paliers `medium` et `low`)

90 % de l'effet perçu dans une scène statique, pour 20 lignes et zéro coût GPU notable.

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
  blending: THREE.MultiplyBlending
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

À poser sous : chaque table (r 0.9 / 0.7 / 0.6), chaque chaise (0.35), chaque tabouret
(0.28), chaque plante (0.3 / 0.24 / 0.14), le comptoir (rectangle 3.4 × 1.0), et **sous
chaque agent** — dans ce dernier cas le blob suit l'agent à chaque frame.

### 2.8 — FXAA

**Il faut une passe séparée, après le composite.** FXAA détecte les contours par la
luminance de l'image **finale en LDR** : l'exécuter avant le tonemapping donnerait des
contours faux. Le composite écrit donc dans `RT_LDR`, et FXAA fait `RT_LDR → écran`.
C'est un blit de plus, ~0,2 ms. C'est le prix du MSAA perdu (§2.2 piège 6).

```js
const fxaaMat = new THREE.ShaderMaterial({
  uniforms:{ tSrc:{value:null}, uRes:{value:new THREE.Vector2()} },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc; uniform vec2 uRes; varying vec2 vUv;
    const float SPAN = 8.0, REDUCE_MUL = 0.125, REDUCE_MIN = 0.0078125;
    float luma(vec3 c){ return dot(c, vec3(0.299, 0.587, 0.114)); }
    void main(){
      vec2 t = 1.0 / uRes;
      vec3 rgbNW = texture2D(tSrc, vUv + vec2(-t.x, -t.y)).rgb;
      vec3 rgbNE = texture2D(tSrc, vUv + vec2( t.x, -t.y)).rgb;
      vec3 rgbSW = texture2D(tSrc, vUv + vec2(-t.x,  t.y)).rgb;
      vec3 rgbSE = texture2D(tSrc, vUv + vec2( t.x,  t.y)).rgb;
      vec3 rgbM  = texture2D(tSrc, vUv).rgb;
      float lNW = luma(rgbNW), lNE = luma(rgbNE),
            lSW = luma(rgbSW), lSE = luma(rgbSE), lM = luma(rgbM);
      float lMin = min(lM, min(min(lNW, lNE), min(lSW, lSE)));
      float lMax = max(lM, max(max(lNW, lNE), max(lSW, lSE)));

      vec2 dir = vec2(-((lNW + lNE) - (lSW + lSE)), ((lNW + lSW) - (lNE + lSE)));
      float reduce = max((lNW + lNE + lSW + lSE) * 0.25 * REDUCE_MUL, REDUCE_MIN);
      float rcp = 1.0 / (min(abs(dir.x), abs(dir.y)) + reduce);
      dir = clamp(dir * rcp, vec2(-SPAN), vec2(SPAN)) * t;

      vec3 rgbA = 0.5 * (texture2D(tSrc, vUv + dir * (1.0 / 3.0 - 0.5)).rgb +
                         texture2D(tSrc, vUv + dir * (2.0 / 3.0 - 0.5)).rgb);
      vec3 rgbB = rgbA * 0.5 + 0.25 * (texture2D(tSrc, vUv - dir * 0.5).rgb +
                                       texture2D(tSrc, vUv + dir * 0.5).rgb);
      float lB = luma(rgbB);
      gl_FragColor = vec4((lB < lMin || lB > lMax) ? rgbA : rgbB, 1.0);
    }`,
  depthTest:false, depthWrite:false
});
```

### 2.9 — Le composite

**Une seule passe, l'ordre est impératif.** Un effet placé au mauvais endroit produit
un résultat plausible mais faux — par exemple un grain appliqué avant le tonemapping
disparaît dans les hautes lumières au lieu de s'y raréfier.

```js
const compMat = new THREE.ShaderMaterial({
  uniforms:{
    tSrc:{value:null}, tBloom:{value:null}, tAO:{value:null},
    uRes:{value:new THREE.Vector2()}, uTime:{value:0},
    uExposure:{value:1.15}, uBloom:{value:0.32},
    uCA:{value:0.85}, uGrain:{value:0.055}, uVig:{value:0.55},
    uSharp:{value:0.35}, uBarrel:{value:0.020},
    uSlope:{value:new THREE.Vector3(1.060, 1.015, 0.935)},
    uOffset:{value:new THREE.Vector3(-0.010, 0.002, 0.022)},
    uPower:{value:new THREE.Vector3(1.000, 0.975, 1.030)},
    uSat:{value:0.86}, uContrast:{value:1.14}, uPivot:{value:0.42},
    uDebug:{value:0}
  },
  vertexShader: QUAD_VS,
  fragmentShader:`
    uniform sampler2D tSrc, tBloom, tAO;
    uniform vec2 uRes; uniform float uTime, uExposure, uBloom, uCA, uGrain,
                                    uVig, uSharp, uBarrel;
    uniform vec3 uSlope, uOffset, uPower;
    uniform float uSat, uContrast, uPivot;
    uniform int uDebug;
    varying vec2 vUv;

    float luma(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }

    /* matrice de Bayer 4×4 : un dithering ORDONNÉ ne scintille pas d'une frame
       à l'autre, contrairement à un hash aléatoire. */
    float bayer4(vec2 p){
      vec2 f = floor(mod(p, 4.0));
      float i = f.y * 4.0 + f.x;
      if(i< 1.0) return  0.0/16.0; if(i< 2.0) return  8.0/16.0;
      if(i< 3.0) return  2.0/16.0; if(i< 4.0) return 10.0/16.0;
      if(i< 5.0) return 12.0/16.0; if(i< 6.0) return  4.0/16.0;
      if(i< 7.0) return 14.0/16.0; if(i< 8.0) return  6.0/16.0;
      if(i< 9.0) return  3.0/16.0; if(i<10.0) return 11.0/16.0;
      if(i<11.0) return  1.0/16.0; if(i<12.0) return  9.0/16.0;
      if(i<13.0) return 15.0/16.0; if(i<14.0) return  7.0/16.0;
      if(i<15.0) return 13.0/16.0; return          5.0/16.0;
    }
    vec3 aces(vec3 x){
      const float a = 2.51, b = 0.03, c = 2.43, d = 0.59, e = 0.14;
      return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
    }
    vec3 cdl(vec3 c){ return pow(max(c * uSlope + uOffset, 0.0), uPower); }
    vec3 sRGB(vec3 c){
      vec3 lo = c * 12.92;
      vec3 hi = 1.055 * pow(max(c, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055;
      return mix(hi, lo, step(c, vec3(0.0031308)));
    }

    void main(){
      vec2 texel = 1.0 / uRes;
      vec2 d = vUv - 0.5;
      float r2 = dot(d, d);

      /* 0. distorsion en barillet — très légère, sinon le CV devient illisible */
      vec2 uv = vUv + d * r2 * uBarrel;

      /* 1. aberration chromatique radiale, nulle au centre */
      vec2 ca = d * r2 * uCA * texel * 6.0;
      vec3 col = vec3(
        texture2D(tSrc, uv + ca).r,
        texture2D(tSrc, uv).g,
        texture2D(tSrc, uv - ca).b
      );
      vec3 base = col;

      /* 2. occlusion ambiante */
      col *= texture2D(tAO, uv).r;

      /* 3. bloom */
      col += texture2D(tBloom, uv).rgb * uBloom;

      /* 4-5. exposition puis tonemap */
      col = aces(col * uExposure);

      /* 6. étalonnage : CDL, saturation, contraste sur pivot */
      col = cdl(col);
      col = mix(vec3(luma(col)), col, uSat);
      col = clamp((col - uPivot) * uContrast + uPivot, 0.0, 1.0);

      /* 7. vignettage, corrigé de l'aspect (sinon il est ovale) */
      float v = smoothstep(0.98, 0.28, length(d * vec2(uRes.x / uRes.y, 1.0)));
      col *= mix(1.0, v, uVig);

      /* 8. grain animé, plus dense dans les ombres */
      float g = hash(vUv * uRes + fract(uTime * 0.717) * 419.7) - 0.5;
      col += g * uGrain * (1.0 - smoothstep(0.0, 0.65, luma(col)));

      /* 9. unsharp mask, sur l'image tonemappée pour rester perceptuel */
      vec3 blur = (
        texture2D(tSrc, uv + vec2( texel.x, 0.0)).rgb +
        texture2D(tSrc, uv + vec2(-texel.x, 0.0)).rgb +
        texture2D(tSrc, uv + vec2(0.0,  texel.y)).rgb +
        texture2D(tSrc, uv + vec2(0.0, -texel.y)).rgb) * 0.25;
      col += (aces(base * uExposure) - aces(blur * uExposure)) * uSharp;

      /* 10. dithering ordonné : indispensable dans un café sombre */
      col += (bayer4(gl_FragCoord.xy) - 0.5) / 255.0;

      /* 11. encodage sRGB manuel — three ne le fait pas pour un ShaderMaterial */
      vec3 outc = sRGB(clamp(col, 0.0, 1.0));

      if (uDebug == 1) outc = sRGB(clamp(base, 0.0, 1.0));
      if (uDebug == 2) outc = sRGB(clamp(texture2D(tBloom, uv).rgb, 0.0, 1.0));
      if (uDebug == 3) outc = vec3(texture2D(tAO, uv).r);
      if (uDebug == 4) outc = vec3(texture2D(tSrc, uv).a);   /* CoC */

      gl_FragColor = vec4(outc, 1.0);
    }`,
  depthTest:false, depthWrite:false
});
```

### 2.10 — Presets d'étalonnage

```js
const GRADES = {
  /* Neutre — sert de référence pour valider le passthrough (§2.14) */
  neutral: { slope:[1,1,1], offset:[0,0,0], power:[1,1,1],
             sat:1.00, contrast:1.00, pivot:0.42,
             exposure:1.18, bloom:0.00, vig:0.00, grain:0.000, ca:0.0, barrel:0.0 },

  /* Los Santos, midi, smog — l'ADN GTA V */
  losSantosDay: { slope:[1.060, 1.015, 0.935], offset:[-0.010, 0.002, 0.022],
                  power:[1.000, 0.975, 1.030],
                  sat:0.86, contrast:1.14, pivot:0.42,
                  exposure:1.15, bloom:0.32, vig:0.55, grain:0.055, ca:0.85, barrel:0.020 },

  /* Vinewood, nuit, néons — plus proche de l'ambiance actuelle du café */
  vinewoodNight:{ slope:[0.965, 0.985, 1.090], offset:[-0.014,-0.004, 0.030],
                  power:[1.040, 1.000, 0.960],
                  sat:0.94, contrast:1.22, pivot:0.36,
                  exposure:1.05, bloom:0.48, vig:0.70, grain:0.075, ca:1.10, barrel:0.024 }
};
function applyGrade(name){
  const g = GRADES[name] || GRADES.losSantosDay;
  const u = compMat.uniforms;
  u.uSlope.value.fromArray(g.slope);
  u.uOffset.value.fromArray(g.offset);
  u.uPower.value.fromArray(g.power);
  u.uSat.value = g.sat; u.uContrast.value = g.contrast; u.uPivot.value = g.pivot;
  u.uExposure.value = g.exposure; u.uBloom.value = g.bloom;
  u.uVig.value = g.vig; u.uGrain.value = g.grain;
  u.uCA.value = g.ca; u.uBarrel.value = g.barrel;
}
```

Lecture perceptuelle des triplets, pour que tu saches quoi bouger :

| Paramètre | Ce qu'il fait |
|---|---|
| `offset` (lift) | Décale les **noirs**. `[-0.010, 0.002, 0.022]` = noirs écrasés et teintés sarcelle. C'est la signature GTA la plus reconnaissable. |
| `slope` (gain) | Multiplie les **hautes lumières**. `[1.060, 1.015, 0.935]` = highlights ocre, jamais blanc pur. |
| `power` (gamma) | Courbe les **mid-tones**. `[1.000, 0.975, 1.030]` = mids poussés vers le vert-jaune. |
| `sat` 0.86 | Désature de 14 %. Sans ça, l'étalonnage vire à la carte postale. |
| `contrast` 1.14 sur `pivot` 0.42 | Courbe en S. Le pivot bas préserve les ombres. |

### 2.11 — Mode debug

Indispensable : tu n'as pas d'yeux, il te faut des vues isolées.

```js
const DEBUG_VIEWS = { '': 0, '#raw': 1, '#bloom': 2, '#ao': 3, '#coc': 4 };
function syncDebug(){ compMat.uniforms.uDebug.value = DEBUG_VIEWS[location.hash] || 0; }
addEventListener('hashchange', syncDebug); syncDebug();
```

### 2.12 — Boucle de rendu

Remplace `renderer.render(scene, camera)` (`index.html:1518`) par :

```js
  compMat.uniforms.uTime.value = t;

  /* 1. scène → HDR */
  renderer.setRenderTarget(RT_HDR);
  renderer.clear();
  renderer.render(scene, camera);

  /* 2. AO */
  if (QUALITY.ssao) renderSSAO();

  /* 3. bloom */
  if (QUALITY.bloom > 0) renderBloom(QUALITY.bloom);

  /* 4. DOF */
  let srcTex = RT_HDR.texture;
  if (QUALITY.dof && RT_HDR.depthTexture){
    dofMat.uniforms.tSrc.value   = RT_HDR.texture;
    dofMat.uniforms.tDepth.value = RT_HDR.depthTexture;
    dofMat.uniforms.cameraNear.value = camera.near;
    dofMat.uniforms.cameraFar.value  = camera.far;
    blit(dofMat, RT_DOF);
    srcTex = RT_DOF.texture;
  }

  /* 5. composite → LDR */
  compMat.uniforms.tSrc.value   = srcTex;
  compMat.uniforms.tBloom.value = QUALITY.bloom > 0 ? MIPS[0].texture : whiteTex;
  compMat.uniforms.tAO.value    = QUALITY.ssao ? RT_AO.texture : whiteTex;
  blit(compMat, QUALITY.fxaa ? RT_LDR : null);

  /* 6. FXAA → écran */
  if (QUALITY.fxaa){
    fxaaMat.uniforms.tSrc.value = RT_LDR.texture;
    blit(fxaaMat, null);
  }
  renderer.setRenderTarget(null);
```

> ⚠️ Quand `uBloom` vaut 0, `tBloom` reçoit `whiteTex` : la ligne
> `col += texture2D(tBloom, uv).rgb * uBloom` donne alors `+ blanc × 0 = 0`. Correct.
> Ne remplace pas `whiteTex` par `null` : un sampler non lié rend du noir sur certains
> pilotes et du bruit sur d'autres.

### 2.13 — Suppression des overlays CSS

Supprime **`index.html:54-57`** (les règles `.vig` et `.grade`) et
**`index.html:160`** (`<div class="vig"></div><div class="grade"></div>`).

`VC.textOnly()` les retire déjà via `document.querySelectorAll('.vig, .grade')`
(`index.html:404`) — cette ligne devient inopérante mais inoffensive, laisse-la ou
nettoie-la, au choix.

Si tu ne les supprimes pas, tu appliques **deux** vignettages et **deux** étalonnages,
dont un en aveugle sur du sRGB. Le rendu devient boueux et tu chercheras le bug dans
le shader.

### 2.14 — Ordre d'implémentation interne

1. Socle (§2.3) + allocation (§2.4) + composite en mode `neutral` avec `uBloom=0`,
   `uVig=0`, `uGrain=0`, `uCA=0`, `uBarrel=0`, `uSharp=0`, AO neutre, pas de DOF, pas
   de FXAA. **L'image doit être identique à l'actuelle.** C'est le test du double
   gamma : si elle est délavée, l'encodage sRGB est appliqué deux fois ; si elle est
   sombre et saturée, il ne l'est pas du tout.
2. Suppression des overlays CSS (§2.13).
3. Étalonnage `losSantosDay` (§2.10) + vignettage + grain + dithering.
4. Bloom (§2.5).
5. FXAA (§2.8).
6. AO (§2.7) — SSAO ou blobs selon ce que tu veux livrer.
7. DOF (§2.6) — le pilotage vient avec §5.7.

### Critères d'acceptation

- [ ] `THREE.NoToneMapping` est assigné à `renderer.toneMapping` et l'exposition est
      gérée par l'uniforme `uExposure`, pas par `toneMappingExposure`.
- [ ] En mode `neutral` avec tous les effets à zéro, une capture est **visuellement
      indiscernable** de la version d'avant modification.
- [ ] `.vig` et `.grade` n'existent plus, ni dans le CSS ni dans le DOM.
- [ ] Après 50 appels à `onResize()` en boucle,
      `renderer.info.memory.textures` est **stable à ±2** (pas de fuite).
- [ ] `location.hash = '#bloom'` affiche uniquement la contribution du bloom ;
      `#ao` affiche un masque en niveaux de gris ; `#coc` affiche le cercle de
      confusion. Les quatre vues de debug fonctionnent.
- [ ] Sur un contexte WebGL1 sans `WEBGL_depth_texture`, la page **ne plante pas** :
      DOF et SSAO se désactivent, le reste fonctionne.
- [ ] Aucune allocation dans la boucle de rendu : `new THREE.` n'apparaît nulle part
      dans le corps de `animate()`.
- [ ] `renderer.info.render.calls` augmente de **6 à 9** au maximum par rapport à
      avant (les passes de post), pas de dizaines.

---

## 3. Éclairage, IBL et matériaux PBR

**Objectif visuel :** que la matière cesse d'être de la craie. Deux leviers : donner
quelque chose à réfléchir (IBL), et créer un contraste chaud/froid que l'étalonnage
puisse exploiter.

### 3.1 — Pourquoi « tout chaud » empêche l'étalonnage de fonctionner

Le rig actuel (`index.html:725-741`) est intégralement chaud : ambiance `0xffe4c0`,
spot `0xffd9a0`, et une seule source froide à `0.45` d'intensité — quatre fois plus
faible que le spot. Ajoute à ça un sol brun, des murs bruns et une table brune : toute
l'image vit dans une bande de 30° de teinte.

Un étalonnage ne **crée** pas de séparation, il **exploite** celle qui existe. Appliquer
le preset `losSantosDay` sur cette image donne de la boue : les « noirs sarcelle » n'ont
pas d'ombre froide à teinter, et les « highlights ocre » sont déjà ocre.

**La règle : on refroidit le rendu, et l'étalonnage remet le chaud.** C'est
contre-intuitif et c'est la clé.

### 3.2 — Le nouveau rig

Remplace `index.html:725-741`.

```js
/* ---------------- LIGHTS ---------------- */
/* ambiance = le ciel par la fenêtre, donc FROIDE */
scene.add(new THREE.HemisphereLight(0x9fc4e8, 0x1a1410, 0.42));

/* clé chaude au-dessus de la table de Simon */
const keySpot = new THREE.SpotLight(0xffb867, 2.10, 9, 0.68, 0.60, 1.6);
keySpot.position.set(0, 2.62, -0.30);
keySpot.target.position.set(0, 0.80, -0.30);
keySpot.castShadow = true;
keySpot.shadow.mapSize.set(2048, 2048);
keySpot.shadow.camera.near = 0.5;
keySpot.shadow.camera.far  = 6;
keySpot.shadow.normalBias  = 0.020;
keySpot.shadow.bias        = -0.0002;
keySpot.shadow.radius      = 3;
scene.add(keySpot, keySpot.target);

/* fenêtre : franchement bleue et forte, c'est elle qui crée le contraste */
const winDir = new THREE.DirectionalLight(0xa8ccf0, 0.85);
winDir.position.set(-5.0, 3.2, -0.8);
winDir.target.position.set(0, 0.6, -1.2);
winDir.castShadow = true;
winDir.shadow.mapSize.set(2048, 2048);
winDir.shadow.camera.left   = -3.5;
winDir.shadow.camera.right  =  3.5;
winDir.shadow.camera.top    =  3.0;
winDir.shadow.camera.bottom = -0.5;
winDir.shadow.camera.near   =  0.5;
winDir.shadow.camera.far    = 14;
winDir.shadow.normalBias    = 0.020;
winDir.shadow.bias          = -0.0002;
scene.add(winDir, winDir.target);
```

Tableau avant / après :

| Source | Avant | Après | Intention |
|---|---|---|---|
| Hemisphere | `0xffe4c0` / `0x241a12`, 0.5 | `0x9fc4e8` / `0x1a1410`, **0.42** | Le remplissage devient le ciel. Toutes les ombres virent au bleu. |
| `keySpot` | `0xffd9a0`, 1.5, angle .72, penumbra .55 | `0xffb867`, **2.10**, angle **.68**, penumbra **.60** | Plus chaud, plus saturé, plus serré. C'est la seule chose vraiment chaude de la scène. |
| `winDir` | `0xcfe0e6`, **0.45** | `0xa8ccf0`, **0.85** | Presque doublée. C'est elle qui sculpte le côté gauche du visage de Simon. |
| Points des pendants | `0xffb64f`, 0.85, dist 6.5 | `0xffa83c`, **0.70**, dist **5.5** | Légèrement réduits : le key spot et le bloom prennent le relais. |

### 3.3 — `physicallyCorrectLights` : le compromis

`renderer.physicallyCorrectLights = true` active une atténuation en 1/d² physiquement
correcte et interprète les intensités en unités photométriques (candela pour
point/spot, lux pour directionnelle).

| | Avantage | Coût |
|---|---|---|
| **Activé** | Chutes de lumière crédibles, cohérence entre sources, comportement prévisible quand on déplace une lampe. | **Toutes** les intensités sont à retuner. Les `PointLight` et `SpotLight` deviennent ~10 à 60× trop faibles avec les valeurs legacy. |
| **Désactivé** (actuel) | Les valeurs ci-dessus fonctionnent telles quelles. | La lumière ne décroît pas correctement ; une lampe éclaire trop loin. |

**Recommandation : garde-le désactivé.** Dans une pièce de 10 m avec trois pratiques
décoratives et un key light artistique, le gain physique est marginal et le risque de
casser un réglage déjà validé est réel. Si tu l'actives quand même, voici le jeu
d'intensités correspondant, à substituer intégralement :

| Source | Legacy | Physically correct |
|---|---|---|
| Hemisphere | 0.42 | 1.4 |
| `keySpot` | 2.10 | 55 (cd) |
| `winDir` | 0.85 | 2.6 (lux) |
| Points pendants | 0.70 | 18 (cd) |

### 3.4 — IBL : la modification la plus rentable du projet

`PMREMGenerator.fromScene(scene, sigma, near, far)` existe en r134 (vérifié). On
construit la scène d'environnement à la main — c'est exactement ce que fait
`RoomEnvironment`, qui vit dans `examples/jsm` et n'est donc pas disponible.

Les positions ci-dessous sont alignées sur la géométrie **réelle** du café : fenêtre à
`x = -4.97`, comptoir à `(2.7, -3.6)`, pendants à `(0, -0.25)`, `(-2.6, -2.4)`,
`(2.6, -2.8)` avec ampoules à `y = 2.37`, plafond à `y = 3.4`, murs à `x = ±5` et
`z = -5`.

À insérer **après** la création du renderer et **avant** la création des matériaux.

```js
/* ---------------- ENVIRONMENT (IBL) ---------------- */
(function buildEnvironment(){
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0x14161c);

  const shellGeo = new THREE.BoxGeometry(12, 7, 12);
  const shell = new THREE.Mesh(shellGeo,
    new THREE.MeshBasicMaterial({ color: 0x2b2620, side: THREE.BackSide }));
  envScene.add(shell);

  const tmp = [];
  function emitter(w, h, d, x, y, z, hex, power){
    const mat = new THREE.MeshBasicMaterial({ color: hex });
    mat.color.multiplyScalar(power);            /* > 1 : émetteur HDR */
    const geo = new THREE.BoxGeometry(w, h, d);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    envScene.add(m); tmp.push(geo, mat);
  }
  /* plafonniers chauds — la nappe lumineuse du haut */
  emitter(7.0, 0.20, 7.0,   0.0, 3.25, -1.0, 0xffcf8e,  7);
  /* la fenêtre, mur gauche : la grande source froide */
  emitter(0.20, 3.20, 4.50, -5.60, 2.10, -1.20, 0xbcd8ff, 12);
  /* le néon du comptoir (cf. §3.10) */
  emitter(3.00, 0.16, 0.60,  2.70, 2.00, -3.60, 0xffe0b0,  3);
  /* rebond du sol : indispensable, sinon le dessous des objets est noir */
  emitter(9.0, 0.10, 9.0,    0.0, -0.10, -1.0, 0x6b4a32,  1.2);

  const pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  const rt = pmrem.fromScene(envScene, 0.04);
  scene.environment = rt.texture;               /* ← LA ligne */
  pmrem.dispose();

  shellGeo.dispose(); shell.material.dispose();
  tmp.forEach(o => o.dispose());
})();
```

> **`scene.environment` n'affecte QUE le terme spéculaire et le diffus IBL des
> matériaux `MeshStandardMaterial` / `MeshPhysicalMaterial`.** Il ne remplace pas les
> lumières, il ne projette pas d'ombre, et il n'a aucun effet sur les
> `MeshBasicMaterial` (donc ni sur la fenêtre `index.html:794-796`, ni sur le tableau
> de menu `:843-844`, ni sur les ampoules `:751-753`). C'est normal.
>
> **`scene.environment` ne change pas non plus le fond visible** : ça, c'est
> `scene.background`, qui reste `0x151011` (`index.html:518`).

### 3.5 — Table des matériaux

Passe sur **tous** les matériaux du fichier. La colonne « effet » dit ce que tu dois
constater.

| Objet | Ligne | `roughness` | `metalness` | `envMapIntensity` | Effet attendu |
|---|---|---|---|---|---|
| Sol parquet | `768-770` | 0.90 → **0.62** | 0 | **0.70** | Reflet diffus des pendants dans le vernis. |
| Plafond | `771-773` | 1.0 | 0 | **0.20** | Reste mat, juste un peu de rebond. |
| Poutres | `774-778` | 0.95 → **0.85** | 0 | **0.35** | Arêtes qui accrochent la lumière. |
| Mur brique | `779-781` | 1.0 → **0.94** | 0 | **0.35** | Micro-variation sur le relief (avec §4.4). |
| Murs plâtre | `782-786` | 1.0 → **0.96** | 0 | **0.30** | |
| Plinthes | `788-792` | — | 0 | **0.4** | |
| Cadre de fenêtre | `797` | 0.6 → **0.42** | **0.15** | **1.0** | Métal peint, pas plastique. |
| **Plateau de table** | `884-886` | 0.55 → **0.45** + `clearcoat` | 0 | **0.90** | **Le plus gros gain de l'écran** — voir §3.6. |
| Pied de table | `881-883` | 0.45 → **0.30** | 0.5 → **0.85** | **1.30** | Métal noir qui réfléchit enfin. |
| Rim de table | `887-888` | 0.95 → **0.55** | 0 | 0.8 | |
| Comptoir | `837-839` | 0.90 → **0.70** | 0 | 0.6 | Bois gras, cf. crasse §4.5. |
| Plateau de comptoir | `840-842` | 0.35 → **0.28** | 0.25 → **0.05** | **1.00** | Pierre polie, pas métal. |
| **Machine à café** | `851-853` | 0.30 → **0.22** | 0.65 → **0.92** | **1.40** | Passe de bloc gris à inox. Vérifie ce point en premier. |
| Dessus de machine | `854-856` | 0.4 → **0.35** | 0.5 → **0.80** | 1.2 | |
| Tasses | `857-861`, `1117-1129` | (défaut 1.0) → **0.18** | 0 | **1.20** | Céramique émaillée. |
| Chaises / tabourets | `862-903` | 0.85 → **0.75** | 0 | 0.5 | |
| Pieds de tabouret | `868-869` | 0.4 → **0.32** | 0.6 → **0.85** | 1.3 | |
| Pots de plante | `915-917` | 0.8 → **0.72** | 0 | 0.45 | Terre cuite. |
| Feuilles | `920-922` | 0.8 → **0.55** | 0 | 0.65 | Les feuilles sont **brillantes**. |
| Tapis | `904-906` | 1.0 | 0 | **0.18** | |
| Vêtements (PNJ + Simon) | `933-936`, `1028` | 0.85 → **0.90** | 0 | **0.25** | Tissu = très mat, très peu de réflexion. |
| Peau | `935`, `1029` | 0.65 → **0.55** | 0 | **0.50** | Un peu de spéculaire, sinon visage plat. |
| Cheveux | `936`, `1064` | 0.92 → **0.80** | 0 | **0.45** | Les cheveux brillent. |
| Lunettes | `1082` | 0.35 → **0.25** | 0.3 → **0.85** | **1.5** | Monture métallique. |
| Verres à bière | `1141-1146` | 0.15 | 0 | **1.2** | Voir §3.6 pour `transmission`. |
| Papier du CV | `1251-1252` | 0.85 → **0.78** | 0 | **0.35** | Le papier a un léger satiné. |
| Assiette / soucoupe | `1117`, `1167` | 0.5 → **0.22** | 0 | 1.2 | Porcelaine. |

Écris un helper plutôt que 40 lignes répétées :

```js
function pbr(mat, roughness, metalness, envInt){
  mat.roughness = roughness;
  mat.metalness = metalness === undefined ? 0 : metalness;
  mat.envMapIntensity = envInt === undefined ? 1 : envInt;
  mat.needsUpdate = true;
  return mat;
}
```

### 3.6 — `MeshPhysicalMaterial` là où ça compte

Vérifié en r134 : `clearcoat`, `clearcoatRoughness`, `transmission`, `thickness`, `ior`
existent tous, en **minuscules**.

**La table (`index.html:884-886`)** — 40 % de la surface écran. Le vernis est ce qui
sépare une table réelle d'un panneau texturé.

```js
const top = new THREE.Mesh(new THREE.CylinderGeometry(r, r, .055, 40),
  new THREE.MeshPhysicalMaterial({
    map: tableTex,
    normalMap: tableNrm,            /* §4.4 */
    roughnessMap: tableRgh,         /* §4.3 */
    roughness: 0.45,
    metalness: 0.0,
    clearcoat: 1.0,
    clearcoatRoughness: 0.16,
    envMapIntensity: 0.9
  }));
```

**Les verres à bière (`index.html:1141-1146`)** — ils n'apparaissent que dans le
« mode bière » (`setBeerMode`, `:1153-1158`), donc le coût est intermittent.

```js
const glass = new THREE.Mesh(new THREE.CylinderGeometry(.042, .036, .13, 16),
  new THREE.MeshPhysicalMaterial({
    color: 0xd98a2b, roughness: 0.08, metalness: 0,
    transmission: 0.92, thickness: 0.012, ior: 1.45,
    envMapIntensity: 1.2, transparent: true
  }));
```

> ⚠️ **Coût de `transmission`** : chaque matériau à transmission déclenche un rendu de
> la scène dans un buffer de transmission. C'est cher. Limite-le aux **2 verres** et à
> la vitre de la fenêtre, et **désactive-le sur les paliers `medium` et `low`** en
> retombant sur `MeshStandardMaterial({ transparent: true, opacity: 0.85 })`.

### 3.7 — Ombres

Le défaut actuel est un problème de budget mal alloué, pas de puissance.

| | Avant | Après | Gain |
|---|---|---|---|
| Zone couverte par `winDir` | 10 × 6 m (`index.html:738-739`) | **7 × 3,5 m** | La zone jouable réelle tient dans 3 × 3 m. |
| `mapSize` | 1024² | **2048²** | |
| Résolution effective | 10 000 mm / 1024 ≈ **9,8 mm/texel** | 7 000 mm / 2048 ≈ **3,4 mm/texel** | **≈ 3× plus net**, pour 4× le coût mémoire de la map (16 Mo → 64 Mo côté GPU, acceptable). |
| Correction d'artefacts | `bias: -0.0005` seul | `normalBias: 0.020` + `bias: -0.0002` | |

**`bias` vs `normalBias`** — à comprendre, c'est le piège classique :

- `bias` décale la profondeur comparée. Trop faible → **acné** (rayures sombres sur les
  surfaces éclairées de biais). Trop fort → **peter-panning** (l'ombre se détache du
  pied de l'objet, qui a l'air de flotter). C'est exactement ce qu'on observe
  aujourd'hui sur les chaises.
- `normalBias` décale le **point échantillonné** le long de la normale de surface. Il
  corrige l'acné sans détacher l'ombre. C'est presque toujours le bon outil.
- Règle : `normalBias` autour de 0.02 comme réglage principal, `bias` négatif très
  petit (−0.0002) en appoint.

**Qui doit projeter une ombre :**

| `castShadow = true` | `castShadow = false` |
|---|---|
| Simon (torse, tête, bras), les 5 PNJ, les meubles (tables, chaises, comptoir, tabourets), les plantes, les props posés sur les tables, la feuille de CV | Les plinthes *(ajoute-leur plutôt un blob, §2.7.b)*, les feuilles de plantes individuelles (17 par plante = 51 ombres inutiles), les curls de cheveux de Simon (`index.html:1071-1074`), les yeux, les sourcils, la monture des lunettes, le mouchetis de props < 3 cm |

`receiveShadow = true` sur : sol, murs, plateaux de table, comptoir, assises de chaises,
tapis. Rien d'autre.

### 3.8 — Les pendants comme sources pratiques

`index.html:743-765`. Aujourd'hui : une sphère `MeshBasicMaterial` + un sprite additif.
Elle ne nourrit pas le bloom (une `MeshBasicMaterial` à `0xffe2a8` vaut ~0.9 en
linéaire, sous le seuil de 1.05).

```js
/* dans pendant(), remplace le bulb ligne 751-753 */
const bulb = new THREE.Mesh(new THREE.SphereGeometry(.045, 16, 12),
  new THREE.MeshStandardMaterial({
    color: 0x1a1208,
    emissive: 0xffd9a0,
    emissiveIntensity: 4.2,      /* > 1 : passe le seuil du bright pass */
    roughness: 1
  }));
bulb.position.y = 2.37; g.add(bulb);

/* flaque de lumière au plafond : un disque additif juste sous le plafond */
const pool = new THREE.Mesh(new THREE.CircleGeometry(0.55, 24),
  new THREE.MeshBasicMaterial({
    map: glowTex, color: 0xffb84a, transparent: true, opacity: 0.35,
    blending: THREE.AdditiveBlending, depthWrite: false
  }));
pool.rotation.x = Math.PI / 2;          /* face vers le bas */
pool.position.y = 3.38; g.add(pool);
```

**Le scintillement** (`index.html:1508-1509`) est un sinus pur — donc parfaitement
périodique, donc perceptible comme une pulsation mécanique. Remplace par une somme de
sinus incommensurables :

```js
function flick(t, seed){
  return Math.sin(t * 8.7 + seed) * 0.55
       + Math.sin(t * 19.3 + seed * 2.1) * 0.30
       + Math.sin(t * 41.1 + seed * 3.7) * 0.15;
}
keySpot.intensity = 2.10 + flick(t, 0.0) * 0.035;
lampPts.forEach((p, i) => { p.intensity = 0.70 + flick(t, i * 2.3 + 1.1) * 0.045; });
```

### 3.9 — Brouillard

```js
/* remplace index.html:518-519 */
scene.background = new THREE.Color(0x11151a);
scene.fog = new THREE.FogExp2(0x1a2228, 0.055);
```

`Fog` linéaire avec `near = 7.5` dans une pièce de 10 m ne se déclenche jamais.
`FogExp2` agit dès le premier mètre et donne la perspective atmosphérique.

**La couleur du fog doit correspondre à la teinte des ombres de l'étalonnage**
(`0x1a2228` est un gris-sarcelle cohérent avec `offset: [-0.010, 0.002, 0.022]`). Si
tu changes de preset, change le fog.

### 3.10 — Le néon du comptoir

Une source pratique visible qui justifie le bloom et qui « date » le décor en jeu
moderne.

```js
/* après le boardFrame, index.html:850 */
const neonGeo = new THREE.CapsuleGeometry
  ? null                                     /* CapsuleGeometry n'existe pas en r134 */
  : null;
const neonTube = new THREE.Mesh(
  new THREE.CylinderGeometry(0.028, 0.028, 2.2, 12, 1, false),
  new THREE.MeshStandardMaterial({
    color: 0x2a1c10, emissive: 0xff9d4a, emissiveIntensity: 5.5, roughness: 1
  }));
neonTube.rotation.z = Math.PI / 2;
neonTube.position.set(2.70, 1.98, -3.55);
scene.add(neonTube);

const neonGlow = new THREE.Sprite(new THREE.SpriteMaterial({
  map: glowTex, color: 0xff9d4a, blending: THREE.AdditiveBlending,
  depthWrite: false, opacity: 0.55
}));
neonGlow.scale.set(3.2, 0.9, 1);
neonGlow.position.copy(neonTube.position);
scene.add(neonGlow);

const neonPt = new THREE.PointLight(0xff9d4a, 0.35, 4.0, 2);
neonPt.position.set(2.70, 1.90, -3.40);
scene.add(neonPt);
```

> `CapsuleGeometry` **n'existe pas** en r134 (ajoutée en r136). Utilise
> `CylinderGeometry`, comme ci-dessus. Le stub dans le code est là pour te le rappeler :
> supprime-le.

### 3.11 — Débogage lumière par lumière

```js
const LIGHTS = { hemi: null, key: keySpot, win: winDir, pendants: lampPts, neon: neonPt };
window.__solo = function(name){
  Object.keys(LIGHTS).forEach(k => {
    const l = LIGHTS[k];
    const on = (name === 'all' || k === name);
    if (Array.isArray(l)) l.forEach(x => x.visible = on);
    else if (l) l.visible = on;
  });
};
```

Isoler une source est le seul moyen fiable de savoir laquelle produit un artefact.

### Critères d'acceptation

- [ ] `scene.environment` est assigné et `scene.background` reste distinct.
- [ ] La machine à café (`index.html:851`) présente un dégradé de réflexion sur ses
      faces. En `#raw` elle ne doit plus être un aplat gris uniforme.
- [ ] Le générateur PMREM est disposé (`pmrem.dispose()`) et les géométries/matériaux
      temporaires aussi. `renderer.info.memory.geometries` ne doit pas contenir la
      coque d'environnement après l'init.
- [ ] `__solo('win')` laisse une scène bleue et directionnelle ; `__solo('key')` une
      scène orange et concentrée. Le contraste chaud/froid est vérifiable ainsi.
- [ ] Aucune ombre détachée du pied de son objet (peter-panning) et aucune rayure
      d'acné sur le sol ni sur le plateau de table.
- [ ] Le nombre d'objets avec `castShadow = true` est **inférieur à 60** (compte-les :
      `let n=0; scene.traverse(o=>{if(o.castShadow)n++}); n`).
- [ ] `RectAreaLight` n'apparaît **nulle part** dans le code.
- [ ] Le fog est un `FogExp2` et sa couleur est cohérente avec le preset d'étalonnage
      actif.

---

## 4. Textures procédurales, matière et géométrie

**Objectif visuel :** donner du micro-relief, de la variation de rugosité, de la crasse
et de la densité. C'est ce qui sépare un décor « propre et neuf » d'un décor habité.

### 4.1 — Refonte de `ctex()`

`index.html:546-552`. Une seule ligne à ajouter, mais elle débloque toute la section.

```js
function ctex(w, h, draw){
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  t.encoding = THREE.sRGBEncoding; t.anisotropy = maxAniso;
  t.userData.canvas = c;                 /* ← permet la dérivation de maps */
  return t;
}
```

### 4.2 — Dérivation des normal maps

```js
/* height → normal par Sobel sur la luminance.
   strength : 1 = plat, 4 = très marqué. downscale : 2 = 4× plus rapide. */
function normalFromCanvas(srcCanvas, strength, downscale){
  const ds = downscale || 1;
  const w = Math.max(4, Math.floor(srcCanvas.width  / ds));
  const h = Math.max(4, Math.floor(srcCanvas.height / ds));
  const tmp = document.createElement('canvas'); tmp.width = w; tmp.height = h;
  const tc = tmp.getContext('2d');
  tc.drawImage(srcCanvas, 0, 0, w, h);
  const s = tc.getImageData(0, 0, w, h).data;

  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const oc = out.getContext('2d');
  const img = oc.createImageData(w, h), o = img.data;

  function L(x, y){
    x = (x + w) % w; y = (y + h) % h;              /* wrap torique : pas de couture */
    const i = (y * w + x) * 4;
    return (s[i] * 0.299 + s[i + 1] * 0.587 + s[i + 2] * 0.114) / 255;
  }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    /* Sobel 3×3 plutôt qu'une différence centrale : moins bruité */
    const tl=L(x-1,y-1), tm=L(x,y-1), tr=L(x+1,y-1);
    const ml=L(x-1,y  ),              mr=L(x+1,y  );
    const bl=L(x-1,y+1), bm=L(x,y+1), br=L(x+1,y+1);
    const dx = ((tr + 2*mr + br) - (tl + 2*ml + bl)) * strength;
    const dy = ((bl + 2*bm + br) - (tl + 2*tm + tr)) * strength;
    const len = Math.sqrt(dx*dx + dy*dy + 1);
    const i = (y * w + x) * 4;
    o[i]     = ((-dx / len) * 0.5 + 0.5) * 255;
    o[i + 1] = ((-dy / len) * 0.5 + 0.5) * 255;
    o[i + 2] = (( 1  / len) * 0.5 + 0.5) * 255;
    o[i + 3] = 255;
  }
  oc.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(out);
  t.encoding  = THREE.LinearEncoding;      /* ← OBLIGATOIRE */
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = maxAniso;
  return t;
}
```

**Symptôme d'une normal map laissée en `sRGBEncoding`** : le relief part dans une seule
diagonale, les creux et les bosses sont inversés par endroits, et l'éclairage semble
venir d'une direction absurde. Tu chercheras le bug dans ton Sobel : il n'y est pas.

**Coût CPU** : 1024² = 1 M pixels avec 8 lectures chacun ≈ **60 à 120 ms** en JS. C'est
un gel de frame visible. Impose donc :

```js
/* après le premier render, hors du chemin critique */
const idle = window.requestIdleCallback || (fn => setTimeout(fn, 200));
idle(() => {
  const brickNrm = normalFromCanvas(brickTex.userData.canvas, 3.2);
  brickNrm.repeat.copy(brickTex.repeat);
  backWall.material.normalMap = brickNrm;
  backWall.material.normalScale.set(1.4, 1.4);
  backWall.material.needsUpdate = true;
  /* … idem pour les autres, cf. tableau 4.4 */
});
```

**N'oublie jamais `repeat.copy()`** : une normal map sans le même `repeat` que la
diffuse produit un relief déphasé par rapport au motif — l'erreur la plus difficile à
diagnostiquer de cette section.

### 4.3 — Roughness, AO et packing ORM

three lit les canaux suivants sur un matériau `MeshStandardMaterial` :

| Map | Canal lu |
|---|---|
| `aoMap` | **R** — et nécessite un **deuxième jeu d'UV** (`uv2`) |
| `roughnessMap` | **G** |
| `metalnessMap` | **B** |

Les trois peuvent donc vivre dans une seule texture RGB, dite ORM :

```js
function ormFromCanvas(srcCanvas, opts){
  const o = Object.assign({ roughBase: 0.7, roughVar: 0.35, invert: true,
                            metal: 0, downscale: 2 }, opts || {});
  const ds = o.downscale;
  const w = Math.max(4, Math.floor(srcCanvas.width / ds));
  const h = Math.max(4, Math.floor(srcCanvas.height / ds));
  const tmp = document.createElement('canvas'); tmp.width = w; tmp.height = h;
  tmp.getContext('2d').drawImage(srcCanvas, 0, 0, w, h);
  const s = tmp.getContext('2d').getImageData(0, 0, w, h).data;

  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const oc = out.getContext('2d');
  const img = oc.createImageData(w, h), d = img.data;
  for (let i = 0; i < w * h; i++){
    const j = i * 4;
    let l = (s[j] * 0.299 + s[j+1] * 0.587 + s[j+2] * 0.114) / 255;
    if (o.invert) l = 1 - l;                 /* les creux sont plus mats */
    const rough = Math.min(1, Math.max(0, o.roughBase + (l - 0.5) * o.roughVar));
    d[j]     = 255;                          /* R : AO neutre (pas d'uv2 ici) */
    d[j + 1] = rough * 255;                  /* G : roughness */
    d[j + 2] = o.metal * 255;                /* B : metalness */
    d[j + 3] = 255;
  }
  oc.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(out);
  t.encoding = THREE.LinearEncoding;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = maxAniso;
  return t;
}
```

Usage : `mat.roughnessMap = orm;` — et `mat.roughness` devient un **multiplicateur**
de la valeur lue, pas une valeur absolue. Mets-le à 1.0 quand tu utilises une map, ou
tu multiplieras deux fois.

> N'utilise **pas** `aoMap` sur ces textures : il exige un attribut `uv2` que les
> primitives de three ne fournissent pas. L'occlusion vient du SSAO (§2.7).

### 4.4 — Refonte texture par texture

| Texture | Ligne | Diagnostic | `normalFromCanvas` | Notes |
|---|---|---|---|---|
| `floorTex` | `560-586` | Tuilage visible à `repeat 4.5` : le même motif de 8 rangées revient 4,5 fois et l'œil l'attrape. | strength **2.0**, downscale 2 | Voir 4.4.a. |
| `brickTex` | `588-603` | `repeat.set(6, 2.6)` sur un mur 22 × 4,6 m : ratio des briques **faux** (104 × 44 px sur une texture carrée étirée non uniformément). Joints non creusés. Pas de crasse. | strength **3.2** | Voir 4.4.b. |
| `plasterTex` | `605-614` | Trop propre, trop uniforme. | strength **1.6** | Ajouter fissures et auréoles. |
| `tableTex` | `616-624` | **Le pire défaut du rendu.** Des cernes concentriques sur 512² étirés sur une table de 1,9 m de diamètre donnent une cible de fléchettes floue. Une table est faite de **lames**, pas d'un tronc coupé. | strength **1.8** | Voir 4.4.c. |
| `rugTex` | `686-694` | Anneaux concentriques → lit comme une cible de tir, et alias fortement. | strength **2.4** | Motif kilim, cf. 4.4.d. |
| `menuTex` | `646-684` | Correcte (craie sur ardoise, justifié). | strength **1.2** | Ajouter poussière de craie et traces d'effacement. |
| `viewTex` | `626-645` | Traité en §4.7 (fenêtre-portail). | — | |
| CV | `1187-1245` | **La lisibilité est sacrée.** | strength **0.6** | Grain papier très léger + un pli. Ne touche à rien d'autre. |

#### 4.4.a — Sol

Ajoute une seconde octave et une variation par lame. Le principe : le tuilage se voit
quand un motif reconnaissable se répète ; casse-le avec du bruit de basse fréquence.

```js
const floorTex = ctex(1024, 1024, (x, w, h) => {
  x.fillStyle = "#553d2b"; x.fillRect(0, 0, w, h);
  const rows = 8, rh = h / rows;
  for (let r = 0; r < rows; r++){
    const off = (r % 2) * w / 4;
    for (let px = -1; px < 5; px++){
      const X = px * w / 4 + off, Y = r * rh;
      /* variation par lame, plus large qu'avant (±26 → ±40) */
      const c = 74 + Math.random() * 40;
      x.fillStyle = `rgb(${c},${c * .68 | 0},${c * .46 | 0})`;
      x.fillRect(X + 2, Y + 2, w / 4 - 4, rh - 4);
      /* veines */
      x.strokeStyle = "rgba(35,20,10,.5)"; x.lineWidth = 1;
      for (let g = 0; g < 7; g++){
        x.beginPath();
        const gy = Y + 6 + Math.random() * (rh - 12);
        x.moveTo(X + 6, gy);
        x.bezierCurveTo(X + w/12, gy + Math.random()*4 - 2,
                        X + w/6,  gy + Math.random()*4 - 2, X + w/4 - 6, gy);
        x.stroke();
      }
      if (Math.random() < .3){
        x.fillStyle = "rgba(40,22,10,.6)";
        x.beginPath();
        x.ellipse(X + 20 + Math.random() * (w/4 - 40), Y + rh/2, 4, 7, 0, 0, 7);
        x.fill();
      }
      /* joint en creux entre lames : sombre + fin */
      x.fillStyle = "rgba(18,10,4,.7)";
      x.fillRect(X, Y + 2, 2, rh - 4);
    }
    x.fillStyle = "rgba(20,10,5,.55)"; x.fillRect(0, r * rh - 1, w, 2);
  }
  /* seconde octave : grandes taches douces qui cassent le tuilage */
  for (let i = 0; i < 14; i++){
    const g = x.createRadialGradient(Math.random()*w, Math.random()*h, 20,
                                     Math.random()*w, Math.random()*h, 200 + Math.random()*220);
    g.addColorStop(0, `rgba(${Math.random()<.5?0:255},${Math.random()<.5?0:230},180,0.05)`);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(0, 0, w, h);
  }
  /* usure dans l'axe de passage (bande centrale plus claire et plus mate) */
  const wear = x.createLinearGradient(0, h*0.35, 0, h*0.65);
  wear.addColorStop(0,   'rgba(255,240,210,0)');
  wear.addColorStop(0.5, 'rgba(255,240,210,0.07)');
  wear.addColorStop(1,   'rgba(255,240,210,0)');
  x.fillStyle = wear; x.fillRect(0, 0, w, h);
  speckle(x, w, h, 2600, .05);
});
floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping;
floorTex.repeat.set(4.5, 4.5);
```

#### 4.4.b — Brique : corriger le ratio

Le mur fait 22 m × 4,6 m. À `repeat.set(6, 2.6)`, une tuile couvre 3,67 m × 1,77 m —
soit un ratio de 2,07 — alors que la texture est carrée. Les briques sont donc étirées
horizontalement d'un facteur 2.

Une brique réelle fait ~21 × 6,5 cm joints compris. Pour une tuile de 3,67 m de large,
il faut ~17,5 briques ; pour 1,77 m de haut, ~27 rangées. Avec une texture de 512 :

```js
const brickTex = ctex(512, 512, (x, w, h) => {
  x.fillStyle = "#3a2f28"; x.fillRect(0, 0, w, h);   /* mortier, plus sombre */
  const bw = w / 17.5, bh = h / 27;                  /* ratio corrigé */
  for (let r = 0; r * bh < h + bh; r++){
    const off = (r % 2) * bw / 2;
    for (let c = -1; c * bw < w + bw; c++){
      const v = Math.random() * 34 - 17;              /* variation élargie */
      const X = c * bw + off, Y = r * bh;
      x.fillStyle = `rgb(${104+v},${72+v*.7},${56+v*.5})`;
      x.fillRect(X + 1.5, Y + 1.5, bw - 3, bh - 3);
      /* arête supérieure claire = le joint est en CREUX une fois en normal map */
      x.fillStyle = "rgba(255,255,255,.07)";
      x.fillRect(X + 1.5, Y + 1.5, bw - 3, 2);
      x.fillStyle = "rgba(0,0,0,.12)";
      x.fillRect(X + 1.5, Y + bh - 3.5, bw - 3, 2);
      /* 1 brique sur 25 est ébréchée */
      if (Math.random() < 0.04){
        x.fillStyle = "rgba(60,44,34,.55)";
        x.beginPath();
        x.ellipse(X + Math.random()*bw, Y + Math.random()*bh, 3, 2.2, Math.random()*3, 0, 7);
        x.fill();
      }
    }
  }
  /* crasse : un mur de café est TOUJOURS plus sale en bas */
  const dirt = x.createLinearGradient(0, h * 0.72, 0, h);
  dirt.addColorStop(0, 'rgba(0,0,0,0)');
  dirt.addColorStop(1, 'rgba(12,8,5,0.42)');
  x.fillStyle = dirt; x.fillRect(0, 0, w, h);
  speckle(x, w, h, 1600, .06);
});
brickTex.wrapS = brickTex.wrapT = THREE.RepeatWrapping;
brickTex.repeat.set(6, 2.6);
```

> Le dégradé de crasse est dans la **tuile**, donc il se répète 2,6 fois en hauteur. Ce
> n'est pas idéal. La solution propre : mettre le dégradé sur un **plan séparé** posé
> devant le mur, en `MultiplyBlending`, non répété. Fais-le si tu as le temps.

#### 4.4.c — Table : refaire en lames

Le plateau fait 1,90 m de diamètre. Pour 4 texels/mm il faudrait 7 600 px — hors budget.
Vise **2 texels/mm** : `1900 × 2 = 3800` → arrondi à **2048** (≈ 1,1 texel/mm), ce qui
est suffisant parce que la table est vue de biais et que la DOF adoucit son bord.

```js
const tableTex = ctex(2048, 2048, (x, w, h) => {
  const plank = w / 9;                       /* 9 lames de ~21 cm : réaliste */
  for (let i = 0; i < 9; i++){
    const X = i * plank;
    const base = 118 + Math.random() * 26;
    x.fillStyle = `rgb(${base},${base*.66|0},${base*.44|0})`;
    x.fillRect(X, 0, plank, h);
    /* fil du bois : longues courbes quasi verticales */
    for (let g = 0; g < 26; g++){
      const gx = X + 6 + Math.random() * (plank - 12);
      x.strokeStyle = `rgba(${60+Math.random()*30},${34+Math.random()*18},14,${.18+Math.random()*.22})`;
      x.lineWidth = 0.8 + Math.random() * 2.2;
      x.beginPath(); x.moveTo(gx, -10);
      for (let y = 0; y < h + 20; y += 64){
        x.lineTo(gx + Math.sin(y * 0.004 + i) * 5 + (Math.random() - .5) * 3, y);
      }
      x.stroke();
    }
    /* nœuds : 0 à 2 par lame */
    const knots = Math.random() < .55 ? (Math.random() < .3 ? 2 : 1) : 0;
    for (let k = 0; k < knots; k++){
      const kx = X + plank * (0.25 + Math.random() * 0.5), ky = Math.random() * h;
      for (let r = 9; r > 0; r--){
        x.strokeStyle = `rgba(48,26,10,${0.08 + r * 0.03})`;
        x.lineWidth = 1.4;
        x.beginPath(); x.ellipse(kx, ky, r * 2.6, r * 4.1, 0.2, 0, 7); x.stroke();
      }
    }
    /* joint entre lames, en creux */
    x.fillStyle = 'rgba(26,14,6,.85)'; x.fillRect(X, 0, 3, h);
  }
  /* usure : le centre est plus mat et plus clair (les coudes, les tasses) */
  const g = x.createRadialGradient(w/2, h/2, w*0.05, w/2, h/2, w*0.45);
  g.addColorStop(0, 'rgba(255,238,205,0.10)');
  g.addColorStop(1, 'rgba(255,238,205,0)');
  x.fillStyle = g; x.fillRect(0, 0, w, h);
  /* cernes de tasses : 6 anneaux, cf. §4.5 */
  for (let i = 0; i < 6; i++){
    const cx = w*0.2 + Math.random()*w*0.6, cy = h*0.2 + Math.random()*h*0.6;
    x.strokeStyle = 'rgba(48,28,12,0.13)'; x.lineWidth = 4 + Math.random()*3;
    x.beginPath(); x.arc(cx, cy, 42 + Math.random()*14, 0, 7); x.stroke();
  }
  /* bord usé : liseré clair sur 14 px de pourtour */
  x.strokeStyle = 'rgba(225,200,165,0.16)'; x.lineWidth = 14;
  x.strokeRect(7, 7, w - 14, h - 14);
  speckle(x, w, h, 3200, .04);
});
```

> La table est un `CylinderGeometry` : ses UV de face supérieure sont un disque inscrit
> dans le carré `[0,1]²`. La texture de lames ci-dessus s'y applique correctement, avec
> les lames orientées selon l'axe X local. C'est le comportement voulu.

#### 4.4.d — Tapis

```js
const rugTex = ctex(1024, 1024, (x, w, h) => {
  const cx = w/2, cy = h/2;
  x.fillStyle = "#5e3226"; x.beginPath(); x.arc(cx, cy, 500, 0, 7); x.fill();
  /* champ central : motif de losanges, pas des anneaux */
  const cols = ["#8f4632", "#c98f5c", "#2f6f68", "#d9a578", "#3a2118"];
  for (let ring = 0; ring < 9; ring++){
    const r0 = 60 + ring * 46;
    const n = 8 + ring * 4;
    for (let i = 0; i < n; i++){
      const a = i / n * Math.PI * 2 + ring * 0.13;
      const px = cx + Math.cos(a) * r0, py = cy + Math.sin(a) * r0;
      x.save(); x.translate(px, py); x.rotate(a);
      x.fillStyle = cols[(ring + i) % cols.length];
      x.beginPath();
      x.moveTo(0, -16); x.lineTo(11, 0); x.lineTo(0, 16); x.lineTo(-11, 0);
      x.closePath(); x.fill();
      x.restore();
    }
  }
  /* bordures concentriques fines, en périphérie seulement */
  ["#d9a578", "#2f6f68", "#f4b740"].forEach((c, i) => {
    x.strokeStyle = c; x.lineWidth = 9 - i * 2;
    x.beginPath(); x.arc(cx, cy, 470 - i * 20, 0, 7); x.stroke();
  });
  /* franges */
  x.strokeStyle = "#c9b291"; x.lineWidth = 3;
  for (let i = 0; i < 220; i++){
    const a = i / 220 * Math.PI * 2;
    x.beginPath();
    x.moveTo(cx + Math.cos(a) * 500, cy + Math.sin(a) * 500);
    x.lineTo(cx + Math.cos(a) * 512, cy + Math.sin(a) * 512);
    x.stroke();
  }
  /* usure : le tapis est plus clair au centre */
  const g = x.createRadialGradient(cx, cy, 20, cx, cy, 340);
  g.addColorStop(0, 'rgba(240,225,200,0.10)');
  g.addColorStop(1, 'rgba(240,225,200,0)');
  x.fillStyle = g; x.fillRect(0, 0, w, h);
  speckle(x, w, h, 5200, .07);
});
```

Et le poil : `normalFromCanvas(rugTex.userData.canvas, 2.4)` avec
`normalScale.set(0.6, 0.6)`.

### 4.5 — La crasse partagée

```js
const grungeTex = ctex(512, 512, (x, w, h) => {
  x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, h);
  for (let i = 0; i < 40; i++){
    const g = x.createRadialGradient(Math.random()*w, Math.random()*h, 5,
                                     Math.random()*w, Math.random()*h, 60 + Math.random()*160);
    g.addColorStop(0, 'rgba(60,50,40,0.30)');
    g.addColorStop(1, 'rgba(60,50,40,0)');
    x.fillStyle = g; x.fillRect(0, 0, w, h);
  }
  x.globalAlpha = 0.14;
  for (let i = 0; i < 70; i++){
    x.fillStyle = '#3a2f22';
    x.fillRect(Math.random()*w, Math.random()*h, 1 + Math.random()*3, 30 + Math.random()*180);
  }
  x.globalAlpha = 1;
  speckle(x, w, h, 4000, 0.06);
});
grungeTex.wrapS = grungeTex.wrapT = THREE.RepeatWrapping;
```

Les six applications, avec l'intensité :

| Surface | Méthode | Intensité |
|---|---|---|
| Bas des murs (brique, plâtre) | Dégradé dans la texture (fait en 4.4.b) | 0.42 |
| Plateau de comptoir | Plan `MultiplyBlending` posé 1 mm au-dessus | 0.30 |
| Plateau de table | Cernes de tasses dans la texture (fait en 4.4.c) | 0.13 par cerne |
| Sol, zone de passage | Bande d'usure dans la texture (fait en 4.4.a) | 0.07 |
| Arêtes du bois | Liseré clair de 14 px (fait en 4.4.c) | 0.16 |
| Vitre de la fenêtre | Traînées verticales en normal map | 0.20 |

### 4.6 — Chanfreins

**Objectif visuel :** dans un moteur AAA, une arête à 90° parfait n'existe pas. Le
chanfrein de 1 à 3 mm accroche un liseré spéculaire, et c'est ce liseré qui fait
« objet réel ».

```js
function roundedRectShape(w, h, r){
  const s = new THREE.Shape();
  const rr = Math.min(r, w / 2 - 0.001, h / 2 - 0.001);
  s.moveTo(-w/2 + rr, -h/2);
  s.lineTo( w/2 - rr, -h/2); s.quadraticCurveTo( w/2, -h/2,  w/2, -h/2 + rr);
  s.lineTo( w/2,  h/2 - rr); s.quadraticCurveTo( w/2,  h/2,  w/2 - rr,  h/2);
  s.lineTo(-w/2 + rr,  h/2); s.quadraticCurveTo(-w/2,  h/2, -w/2,  h/2 - rr);
  s.lineTo(-w/2, -h/2 + rr); s.quadraticCurveTo(-w/2, -h/2, -w/2 + rr, -h/2);
  return s;
}

/* remplaçant de BoxGeometry(w, h, d). Repère identique : centré à l'origine. */
function bevelBox(w, h, d, bevel){
  const b = Math.min(bevel === undefined ? 0.012 : bevel,
                     w * 0.24, h * 0.24, d * 0.45);
  const g = new THREE.ExtrudeGeometry(roundedRectShape(w, h, b * 1.6), {
    depth: Math.max(0.0005, d - b * 2),
    bevelEnabled: true, bevelThickness: b, bevelSize: b,
    bevelSegments: 2, curveSegments: 3
  });
  g.translate(0, 0, -d / 2 + b);
  g.computeVertexNormals();
  return g;
}
```

**Le problème des UV**, à traiter explicitement : `ExtrudeGeometry` génère les UV des
faces avant/arrière **en unités monde** (`uv = (x, y)` du plan de la forme), pas
normalisées dans `[0,1]`. Un objet texturé aura donc une texture à la mauvaise échelle.

Deux solutions :

```js
/* A — remap des UV dans [0,1] à partir de la bounding box. Suffit pour une face plane. */
function remapUV(geom){
  geom.computeBoundingBox();
  const bb = geom.boundingBox;
  const sx = 1 / Math.max(1e-6, bb.max.x - bb.min.x);
  const sy = 1 / Math.max(1e-6, bb.max.y - bb.min.y);
  const uv = geom.attributes.uv, pos = geom.attributes.position;
  for (let i = 0; i < uv.count; i++){
    uv.setXY(i, (pos.getX(i) - bb.min.x) * sx, (pos.getY(i) - bb.min.y) * sy);
  }
  uv.needsUpdate = true;
  return geom;
}
/* B — règle simple : n'utilise bevelBox QUE sur les objets de couleur unie. */
```

**Règle B suffit pour tous les objets listés ci-dessous** : ils sont tous en couleur
unie aujourd'hui.

| Objet | Ligne | `bevel` | Coût tri. |
|---|---|---|---|
| Comptoir | `837` | 0.010 | +160 |
| Plateau de comptoir | `840` | 0.006 | +160 |
| Cadre du menu | `849` | 0.008 | +160 |
| Machine à café | `851` | 0.010 | +160 |
| Dessus de machine | `854` | 0.005 | +160 |
| Poutres × 5 | `775` | 0.008 | +800 |
| Plinthes × 3 | `789` | 0.004 | +480 |
| Montants de fenêtre × 4 | `798` | 0.005 | +640 |
| Rebord de fenêtre | `802` | 0.006 | +160 |
| Assises de chaises × 5 | `894` | 0.006 | +800 |
| Dossiers × 5 | `896` | 0.006 | +800 |
| Livre + pages | `1016`, `1019` | 0.003 | +320 |
| Tablier du barista | `995` | 0.004 | +160 |
| Placket de Simon | `1037` | 0.003 | +160 |
| Pieds des PNJ × 12 | `941` | 0.006 | +1 920 |
| **Total** | | | **≈ +7 000 triangles** |

Négligeable pour une scène qui doit tourner à 60 fps sur iGPU. Fais-le.

### 4.7 — La fenêtre-portail

`index.html:794-796` : un `PlaneGeometry` avec `MeshBasicMaterial`. Aucun parallaxe,
aucune vitre, aucune vie. Une fenêtre est un **portail vers le monde**, et dans le
langage GTA le monde est le sujet.

```js
/* ------- Fenêtre : boîte de profondeur + 3 plans de silhouette + vitre ------- */
const WIN_X = -4.97, WIN_Y = 2.10, WIN_Z = -1.20, WIN_W = 2.40, WIN_H = 1.70;

/* 1. le ciel, au fond de la boîte */
const skyTex = ctex(512, 512, (x, w, h) => {
  const g = x.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0,   "#8fbfd6");
  g.addColorStop(.52, "#e8d9b0");
  g.addColorStop(1,   "#f2b76a");
  x.fillStyle = g; x.fillRect(0, 0, w, h);
  const sun = x.createRadialGradient(150, 180, 8, 150, 180, 190);
  sun.addColorStop(0, "rgba(255,248,214,1)");
  sun.addColorStop(1, "rgba(255,248,214,0)");
  x.fillStyle = sun; x.fillRect(0, 0, w, h);
  /* smog : une bande horizontale plus dense en bas */
  const smog = x.createLinearGradient(0, h * .55, 0, h);
  smog.addColorStop(0, "rgba(226,206,170,0)");
  smog.addColorStop(1, "rgba(226,206,170,.55)");
  x.fillStyle = smog; x.fillRect(0, 0, w, h);
});
function layerPlane(tex, dist, wMul){
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(WIN_W * wMul, WIN_H * wMul),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false })
  );
  m.rotation.y = Math.PI / 2;
  m.position.set(WIN_X - dist, WIN_Y, WIN_Z);
  scene.add(m);
  return m;
}
layerPlane(skyTex, 6.0, 3.2);

/* 2. collines lointaines (silhouette type Vinewood) */
const hillsTex = ctex(512, 256, (x, w, h) => {
  x.clearRect(0, 0, w, h);
  x.fillStyle = "rgba(120,124,116,.55)";
  x.beginPath(); x.moveTo(0, h);
  for (let i = 0; i <= w; i += 8){
    x.lineTo(i, h - 60 - Math.sin(i * .012) * 28 - Math.sin(i * .031 + 2) * 16);
  }
  x.lineTo(w, h); x.closePath(); x.fill();
});
layerPlane(hillsTex, 4.2, 2.6);

/* 3. immeubles proches */
const cityTex = ctex(512, 512, (x, w, h) => {
  x.clearRect(0, 0, w, h);
  const blocks = [[0,300,90,212],[92,262,72,250],[168,320,104,192],
                  [276,286,86,226],[366,312,74,200],[444,268,68,244]];
  blocks.forEach(b => {
    x.fillStyle = "#6a7078"; x.fillRect(b[0], b[1], b[2], b[3]);
    x.fillStyle = "rgba(255,214,130,.8)";
    for (let wy = b[1] + 14; wy < h - 14; wy += 26)
      for (let wx = b[0] + 9; wx < b[0] + b[2] - 9; wx += 21)
        if (Math.random() < .38) x.fillRect(wx, wy, 7, 9);
  });
  /* deux palmiers : le signal « Los Santos » le moins cher du monde */
  x.strokeStyle = "#4a4436"; x.lineWidth = 6;
  [[120, 500], [400, 500]].forEach(p => {
    x.beginPath(); x.moveTo(p[0], p[1]);
    x.quadraticCurveTo(p[0] + 10, p[1] - 110, p[0] + 4, p[1] - 210); x.stroke();
    for (let i = 0; i < 7; i++){
      const a = -Math.PI/2 + (i - 3) * 0.42;
      x.beginPath(); x.moveTo(p[0] + 4, p[1] - 210);
      x.quadraticCurveTo(p[0] + 4 + Math.cos(a) * 40, p[1] - 210 + Math.sin(a) * 40,
                         p[0] + 4 + Math.cos(a) * 74, p[1] - 200 + Math.sin(a) * 74);
      x.stroke();
    }
  });
});
layerPlane(cityTex, 2.4, 1.9);

/* 4. trafic : deux quads qui traversent en boucle */
const carTex = ctex(128, 64, (x, w, h) => {
  x.clearRect(0, 0, w, h);
  x.fillStyle = "#2b3138"; x.fillRect(8, 26, 112, 26);
  x.fillStyle = "#1c2126"; x.fillRect(30, 10, 62, 18);
  x.fillStyle = "rgba(255,220,150,.9)"; x.fillRect(114, 32, 10, 8);
  x.fillStyle = "rgba(255,80,60,.9)";   x.fillRect(6, 32, 8, 8);
});
const cars = [];
for (let i = 0; i < 2; i++){
  const c = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.24),
    new THREE.MeshBasicMaterial({ map: carTex, transparent: true, depthWrite: false }));
  c.rotation.y = Math.PI / 2;
  c.position.set(WIN_X - 1.7, 1.44, WIN_Z);
  c.userData = { t: i * 0.5, speed: 0.16 + i * 0.05, dir: i === 0 ? 1 : -1 };
  scene.add(c); cars.push(c);
}
/* dans animate() :
   cars.forEach(c => {
     c.userData.t = (c.userData.t + dt * c.userData.speed) % 1;
     c.position.z = WIN_Z + (c.userData.t * 5.2 - 2.6) * c.userData.dir;
     c.scale.x = c.userData.dir;          // retourne la voiture selon le sens
   });                                                                        */

/* 5. la vitre */
const glassPane = new THREE.Mesh(new THREE.PlaneGeometry(WIN_W, WIN_H),
  new THREE.MeshPhysicalMaterial({
    color: 0xdfe9ee, roughness: 0.06, metalness: 0,
    transmission: 0.94, thickness: 0.008, ior: 1.5,
    envMapIntensity: 1.4, transparent: true, side: THREE.DoubleSide
  }));
glassPane.rotation.y = Math.PI / 2;
glassPane.position.set(WIN_X + 0.01, WIN_Y, WIN_Z);
scene.add(glassPane);
```

> Sur les paliers `medium` et `low`, remplace `glassPane` par un
> `MeshBasicMaterial({ transparent: true, opacity: 0.10, color: 0xcfe4ee })` : la
> transmission est le poste le plus cher de cette section.

Les shafts existants (`index.html:805-813`) deviennent enfin justifiés : le soleil est
maintenant visible derrière la fenêtre.

### 4.8 — Densité de props

**La loi AAA : toute surface horizontale porte au moins trois objets.** Aujourd'hui le
comptoir a 3 tasses, les tables voisines sont nues, les murs ont 3 posters.

Voici 32 props à ajouter, tous en primitives, tous en couleur unie (donc `bevelBox`
possible), avec position et coût.

| # | Prop | Position `(x, y, z)` | Primitive | Zone |
|---|---|---|---|---|
| 1 | Sucrier | `(-0.18, 0.83, -0.30)` | `CylinderGeometry` + couvercle | Table Simon |
| 2 | Salière / poivrière | `(-0.10, 0.82, -0.34)` ×2 | `CylinderGeometry` | Table Simon |
| 3 | Serviette froissée | `(0.22, 0.806, -0.44)` | `PlaneGeometry` plié | Table Simon |
| 4 | Petite cuillère | `(0.52, 0.818, -0.58)` | 2 boîtes fines | Table Simon |
| 5 | Ticket de caisse | `(-0.34, 0.806, -0.18)` | `PlaneGeometry` | Table Simon |
| 6 | Téléphone posé face contre table | `(0.30, 0.812, -0.16)` | `bevelBox(.07,.14,.008)` | Table Simon |
| 7 | Trousseau de clés | `(-0.30, 0.812, -0.06)` | 3 boîtes fines | Table Simon |
| 8 | Moulin à café | `(2.05, 1.30, -3.72)` | Cylindre + trémie conique | Comptoir |
| 9 | Tamper | `(2.30, 1.16, -3.42)` | Cylindre + disque | Comptoir |
| 10 | Chiffon plié | `(2.42, 1.13, -3.38)` | `bevelBox(.14,.02,.10)` | Comptoir |
| 11 | Pile de tasses ×2 | `(1.75, 1.18, -3.55)` | 4 cylindres empilés | Comptoir |
| 12 | Présentoir à gâteaux | `(1.45, 1.26, -3.62)` | Cylindre + dôme transparent | Comptoir |
| 13 | Caisse enregistreuse | `(3.95, 1.24, -3.55)` | 2 `bevelBox` + écran émissif | Comptoir |
| 14 | Pot à pourboires | `(3.62, 1.16, -3.40)` | Cylindre + pièces | Comptoir |
| 15 | Distributeur de serviettes | `(2.62, 1.16, -3.38)` | `bevelBox(.10,.10,.06)` | Comptoir |
| 16 | Bouteilles de sirop ×3 | `(3.20, 1.22, -3.75)` | Cylindres fins | Comptoir |
| 17 | Ardoise de trottoir | `(-4.20, 0.45, -0.20)` | 2 plans en A | Sol, près fenêtre |
| 18 | Porte-manteau | `(4.55, 0.90, -1.40)` | Cylindre + 4 crochets | Sol droit |
| 19 | Manteau accroché | `(4.55, 1.35, -1.40)` | Cône aplati | Sur le porte-manteau |
| 20 | Extincteur | `(4.94, 0.55, -3.40)` | Cylindre rouge | Mur droit |
| 21 | Prise murale ×2 | `(-4.96, 0.32, -2.10)` | `bevelBox(.02,.08,.08)` | Murs |
| 22 | Interrupteur | `(4.94, 1.25, -4.20)` | `bevelBox(.02,.08,.08)` | Mur droit |
| 23 | Câble qui court le long de la plinthe | `(-4.93, 0.16, -1→-4)` | `TubeGeometry` | Mur gauche |
| 24 | Carton de gobelets | `(4.20, 0.18, -4.55)` | `bevelBox(.36,.36,.30)` | Sol, derrière comptoir |
| 25 | Poubelle | `(3.95, 0.28, -4.65)` | Cylindre + couvercle | Sol |
| 26 | Balai | `(4.80, 0.70, -4.70)` | Cylindre incliné + boîte | Coin |
| 27 | Plante morte | `(1.10, 0.16, -4.70)` | Pot + 3 cônes bruns | Sol |
| 28 | Journal plié | `(-2.62, 0.815, -2.30)` | `bevelBox(.24,.01,.17)` | Table gauche |
| 29 | Tasse sale + soucoupe | `(2.14, 0.805, -1.72)` | Cylindre + disque | Table droite |
| 30 | Sac à dos posé au sol | `(2.72, 0.20, -1.28)` | Sphère aplatie + sangles | Sol |
| 31 | Horloge murale | `(0.90, 2.75, -4.97)` | Cylindre + 2 aiguilles animées | Mur du fond |
| 32 | Ventilateur de plafond | `(0.00, 3.18, -2.40)` | Cylindre + 4 pales | Plafond |

**Coût total** : ~48 meshes supplémentaires. Avec le hoisting de matériaux (§4.9), le
delta net de draw calls est d'environ **+30**, pour un gain visuel considérable.

**Les deux props animés** :
- L'horloge (#31) : `hourHand.rotation.z` et `minuteHand.rotation.z` sur l'heure réelle.
  Détail que personne ne remarque consciemment et que tout le monde ressent.
- Le ventilateur (#32) : `fan.rotation.y += dt * 1.6`. Son ombre balaye la table — c'est
  un mouvement de lumière gratuit sur la plus grande surface de l'écran.

### 4.9 — Optimisation géométrique

**Hoisting des matériaux.** Aujourd'hui `person()` (`index.html:931-976`) crée
**10 matériaux par appel** — soit 60 pour 6 personnages, tous identiques par famille.
Idem pour `chair()`, `stool()`, `plant()`, `pendant()`.

```js
/* AVANT — dans person() */
const mS = new THREE.MeshStandardMaterial({color: shirt, roughness: .85});

/* APRÈS — cache par couleur, hors de la fonction */
const MAT_CACHE = new Map();
function stdMat(color, roughness, metalness, envInt){
  const key = color + '|' + roughness + '|' + (metalness||0) + '|' + (envInt||1);
  let m = MAT_CACHE.get(key);
  if (!m){
    m = new THREE.MeshStandardMaterial({
      color: color, roughness: roughness,
      metalness: metalness || 0, envMapIntensity: envInt === undefined ? 1 : envInt
    });
    MAT_CACHE.set(key, m);
  }
  return m;
}
```

Gain : de ~90 matériaux à ~20. Moins de compilations de programme, moins d'uploads
d'uniformes, et surtout la possibilité pour three de regrouper les rendus.

**`InstancedMesh`** — vérifié présent en r134.

| Cible | Instances | Draw calls avant → après |
|---|---|---|
| Pieds de chaises | 5 chaises × 4 = 20 | 20 → 1 |
| Pieds de tabourets | 2 × 4 = 8 | 8 → 1 |
| Feuilles de plantes | 3 × 7 = 21 | 21 → 1 |
| Curls de cheveux de Simon | 17 | 17 → 1 |
| Props répétés (tasses, bouteilles) | ~12 | 12 → 1 |
| **Total** | | **78 → 5** |

```js
/* exemple : les pieds de chaises */
const legGeo = new THREE.CylinderGeometry(.02, .02, .45, 8);
const chairLegs = new THREE.InstancedMesh(legGeo, woodDark, 20);
chairLegs.castShadow = false;
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(1,1,1);
let li = 0;
CHAIRS.forEach(c => {                 /* CHAIRS = tableau {x, z, ry} */
  for (const dx of [-.17, .17]) for (const dz of [-.17, .17]){
    const lx = c.x + Math.cos(c.ry) * dx - Math.sin(c.ry) * dz;
    const lz = c.z + Math.sin(c.ry) * dx + Math.cos(c.ry) * dz;
    _q.setFromEuler(new THREE.Euler(0, c.ry, 0));
    _m.compose(new THREE.Vector3(lx, .225, lz), _q, _s);
    chairLegs.setMatrixAt(li++, _m);
  }
});
chairLegs.instanceMatrix.needsUpdate = true;
scene.add(chairLegs);
```

**Autres nettoyages** :
- Appelle `geometry.dispose()` sur les géométries temporaires de l'environnement IBL.
- Les `PlaneGeometry(22, 22)` du sol et du plafond sont surdimensionnées pour une pièce
  visible de 10 × 10 m — mais elles coûtent 2 triangles chacune. Laisse.
- `computeBoundingSphere()` est appelé automatiquement par three. N'y touche pas.

### 4.10 — Corrections de géométrie de la pièce

| Problème | Ligne | Correction |
|---|---|---|
| Poutres de **12 m** de long qui traversent les murs (`z` de −7 à +5) et flottent dans le vide au-delà. | `774-778` | `BoxGeometry(.2, .16, 10)` positionnée `z = -1`, ce qui la fait courir de −6 à +4. Mieux : `9.9` de long centrée à `z = -0.05` pour tenir entre le mur du fond (−5) et l'entrée virtuelle (+4.85). |
| Plafond plat sans solives. | `771-773` | Ajoute 14 solives transversales `BoxGeometry(9.8, .09, .07)` tous les 0,7 m, entre les poutres. Coût : 14 draw calls, ou 1 avec `InstancedMesh`. |
| Plinthes sans `castShadow` → elles flottent. | `788-792` | `sk.castShadow = true`, ou un blob (§2.7.b). |
| Le mur du fond fait 22 m pour une pièce de 10 m. | `779-781` | `PlaneGeometry(10.2, 4.6)`. Réduit aussi le gaspillage de résolution de la texture de brique. |
| Les murs latéraux font 12 m de profondeur. | `783-786` | `PlaneGeometry(10, 4.6)` centrée `z = -0.1`. |

### Critères d'acceptation

- [ ] `ctex()` expose `userData.canvas` et toutes les normal maps ont
      `encoding === THREE.LinearEncoding`.
- [ ] Chaque normal map a le **même `repeat`** que sa diffuse
      (`nrm.repeat.equals(diffuse.repeat)` renvoie `true`).
- [ ] La dérivation des maps s'exécute **après** le premier frame : mesure le temps
      entre le chargement et le premier `requestAnimationFrame`, il ne doit pas
      augmenter de plus de 20 ms par rapport à avant.
- [ ] La table ne présente plus de motif concentrique. Les lames sont visibles et
      orientées dans un seul sens.
- [ ] Les briques ont un ratio largeur/hauteur proche de 3,2 (une brique réelle) et non
      de 6,5 (l'étirement actuel).
- [ ] `bevelBox` est utilisé sur les 15 familles d'objets listées en §4.6 et le total
      de triangles de la scène a augmenté de **moins de 10 000**.
- [ ] Au moins **30** des 32 props du §4.8 sont présents.
- [ ] `renderer.info.render.calls` après optimisation est **inférieur** au chiffre
      d'avant, malgré les 48 meshes ajoutés.
- [ ] Aucune poutre ni solive ne dépasse des murs : vérifie en plaçant temporairement
      la caméra à `(0, 6, 6)` regardant `(0, 2, -2)`.
- [ ] L'horloge murale affiche l'heure réelle et le ventilateur tourne.

---

## 5. Caméra, mise en scène et grammaire cinématographique

**Idée directrice : quand Simon parle, ce n'est plus du gameplay, c'est une
cinématique.** L'état `speaking` (`index.html:509`) est le déclencheur, il existe déjà.

Cette section résout en même temps trois manques que le `README.md` reconnaît
lui-même : l'absence de sous-titres, l'absence de dynamique, et le fait qu'une caméra
fixe rende insoutenable une tirade de 90 secondes.

### 5.1 — Diagnostic

`index.html:520-522` (caméra à `(0, 1.34, 1.6)`, FOV 50), `:1426-1436` (`applyStaging`),
`:1511-1516` (parallaxe souris ±0,10 m en X, ±0,05 m en Y), `:1425` (cible fixe
`(0, 1.08, -0.95)`).

La caméra est **frontale, centrée, symétrique, fixe, à hauteur d'yeux**. C'est
exactement le cadrage d'un appel visio — et c'est un cadrage que le cerveau associe à
« webcam », pas à « cinéma ». Aucun film ne place la caméra dans l'axe du regard d'un
personnage qui parle pendant 90 secondes.

Les quatre écarts avec le langage GTA :

| | Actuel | GTA |
|---|---|---|
| Angle | Dans l'axe, symétrique | 3/4, jamais dans l'axe, règle des tiers |
| Roulis | 0 exactement | 0,2 à 1,5° en permanence |
| Découpage | Un seul plan, indéfiniment | Coupe toutes les 5 à 9 s |
| Mise au point | Tout net | La MAP raconte où regarder |

### 5.2 — Système de plans

Les coordonnées ci-dessous sont cohérentes avec la géométrie réelle : Simon à
`(0, 0, -1.08)`, tête à `y = 1.6`, table à `(0, -0.15)` rayon `0.95`, plateau à
`y = 0.775`, feuille au repos à `(0, 0.802, 0.24)`, feuille levée à `(0, 1.0, 0.50)`.

```js
/* ---------------- SHOTS ---------------- */
const SHOTS = {
  /* le plan « jouable » : légèrement décentré, c'est déjà énorme */
  gameplay:  { pos:[ 0.42, 1.30,  1.62], look:[ 0.00, 1.06, -0.95],
               fov:47, focus:2.60, range:1.40, roll: 0.006, shake:1.00 },

  /* gros plan visage — le plan de dialogue par défaut */
  closeup:   { pos:[ 0.34, 1.56,  0.16], look:[ 0.02, 1.58, -1.08],
               fov:34, focus:1.32, range:0.30, roll:-0.010, shake:0.55 },

  /* par-dessus l'épaule du visiteur : on est DANS la conversation */
  overShldr: { pos:[-0.64, 1.46,  0.62], look:[ 0.06, 1.52, -1.08],
               fov:40, focus:1.85, range:0.55, roll: 0.013, shake:0.85 },

  /* insert sur le CV — utilisé quand il parle d'une section précise */
  insert:    { pos:[ 0.10, 1.60,  0.50], look:[ 0.00, 0.83,  0.22],
               fov:38, focus:0.95, range:0.22, roll:-0.008, shake:0.45 },

  /* plan large : établit le lieu, s'utilise 2 s max */
  wide:      { pos:[ 1.94, 1.74,  2.34], look:[ 0.10, 1.10, -1.30],
               fov:52, focus:3.40, range:2.20, roll: 0.009, shake:1.20 },

  /* profil : pour couper la monotonie du champ/contrechamp */
  profile:   { pos:[ 1.18, 1.48, -0.42], look:[-0.06, 1.52, -1.08],
               fov:42, focus:1.55, range:0.45, roll:-0.012, shake:0.70 },

  /* réaction : un PNJ du fond qui écoute (cf. §7.7). Cible fournie au runtime. */
  reaction:  { pos:[ 0.90, 1.55,  0.30], look:[-2.70, 1.50, -3.05],
               fov:44, focus:3.20, range:0.60, roll: 0.011, shake:0.90 }
};
```

> **Règle des 180°** : tous les plans ci-dessus sont du **même côté** de l'axe
> Simon↔visiteur (côté +X, sauf `overShldr` qui est le contrechamp légitime depuis
> derrière le visiteur). Ne crée jamais un plan à `x < -0.7` avec `look` vers Simon :
> le spectateur perdrait l'orientation spatiale.

### 5.3 — Machine de montage

```js
let shot = SHOTS.gameplay;
let shotName = 'gameplay';
const camPos  = new THREE.Vector3().fromArray(SHOTS.gameplay.pos);
const camLook = new THREE.Vector3().fromArray(SHOTS.gameplay.look);
let camFov  = SHOTS.gameplay.fov;
let camRoll = SHOTS.gameplay.roll;
let hardCut = false;

function cutTo(name, hard){
  if (!SHOTS[name]) return;
  shot = SHOTS[name]; shotName = name;
  hardCut = !!hard;
  if (hard){
    camPos.fromArray(shot.pos);
    camLook.fromArray(shot.look);
    camFov  = shot.fov;
    camRoll = shot.roll;
  }
}

/* Couverture : jamais deux fois le même plan d'affilée, et le plan large
   n'apparaît qu'en ouverture. */
const COVERAGE = ['closeup', 'overShldr', 'closeup', 'profile', 'closeup', 'insert'];
let coverageIdx = 0, nextCutAt = 0, wasSpeaking = false;

function updateDirection(t){
  if (RM){ if (shotName !== 'gameplay') cutTo('gameplay', false); return; }

  if (speaking && !wasSpeaking){
    /* début de réplique : plan large 1,8 s pour établir, puis on entre */
    cutTo('wide', true);
    nextCutAt = t + 1.8;
    coverageIdx = 0;
  } else if (speaking && t > nextCutAt){
    cutTo(COVERAGE[coverageIdx++ % COVERAGE.length], true);
    nextCutAt = t + 6 + Math.random() * 3;        /* 6 à 9 s */
  } else if (!speaking && wasSpeaking){
    /* fin de réplique : retour EN FONDU, pas en coupe */
    cutTo('gameplay', false);
    nextCutAt = 0; coverageIdx = 0;
  }
  wasSpeaking = speaking;
}
```

| Situation | Type de transition | Pourquoi |
|---|---|---|
| Début de réplique | **Coupe franche** vers `wide` | Marque la rupture gameplay → cinématique. |
| Pendant la réplique, toutes les 6–9 s | **Coupe franche** | Un travelling pendant un dialogue attire l'attention sur la caméra ; une coupe est invisible. C'est la règle de base du montage. |
| Fin de réplique | **Fondu** vers `gameplay` sur ~1,2 s | Rend la main au joueur en douceur. |
| Survol de la feuille (hors parole) | Pas de changement de plan, seulement un **rack focus** (§5.7) | On reste en gameplay. |

### 5.4 — Interpolation indépendante du framerate

```js
/* Lissage exponentiel correct : k est la fraction rattrapée EN UNE SECONDE.
   `a += (b-a) * dt * k` est faux — il dépend du framerate et diverge si dt*k > 1. */
function damp(current, target, k, dt){
  return current + (target - current) * (1 - Math.pow(1 - k, dt * 60));
}
function dampV3(v, target, k, dt){
  v.x = damp(v.x, target[0], k, dt);
  v.y = damp(v.y, target[1], k, dt);
  v.z = damp(v.z, target[2], k, dt);
}
```

| Cible | `k` | Temps de réponse ≈ |
|---|---|---|
| Position caméra en fondu | 0.055 | 1,2 s |
| Cible de regard caméra | 0.070 | 0,9 s |
| FOV | 0.045 | 1,5 s |
| Rack focus (§5.7) | 0.038 | ~0,6 s pour 90 % |

### 5.5 — Respiration caméra

```js
/* fbm 1D : somme de sinus à fréquences INCOMMENSURABLES.
   Un sinus pur est perçu comme mécanique en moins de 4 secondes. */
function fbm1(t, s, seed){
  return Math.sin(t * s + seed) * 0.60
       + Math.sin(t * s * 2.17 + seed * 1.7 + 1.3) * 0.30
       + Math.sin(t * s * 4.31 + seed * 2.9 + 2.7) * 0.10;
}
```

Amplitudes, modulées par `shot.shake` :

| Axe | Amplitude de base | Note |
|---|---|---|
| Position X | 0.0065 m | |
| Position Y | 0.0045 m | |
| Position Z | 0.0030 m | Le moins perceptible, garde-le petit. |
| **Roulis (Z rotation)** | **0.0038 rad ≈ 0,22°** | **Le paramètre le plus important de la section.** Une caméra parfaitement horizontale n'existe pas au cinéma ; c'est ce qui trahit le plus un rendu 3D. |

### 5.6 — Application dans `animate()`

Remplace les lignes `1511-1516`.

```js
  /* --- direction --- */
  updateDirection(t);

  if (hardCut){ hardCut = false; }
  else {
    dampV3(camPos,  shot.pos,  0.055, dt);
    dampV3(camLook, shot.look, 0.070, dt);
    camFov  = damp(camFov,  shot.fov,  0.045, dt);
    camRoll = damp(camRoll, shot.roll, 0.050, dt);
  }

  camera.position.copy(camPos);

  /* parallaxe souris : UNIQUEMENT en gameplay, sinon la cinématique tremble */
  if (!RM && !TOUCH && shotName === 'gameplay'){
    camera.position.x += THREE.MathUtils.clamp(pointer.x, -1, 1) * 0.10;
    camera.position.y += THREE.MathUtils.clamp(pointer.y, -1, 1) * 0.05;
  }

  /* respiration */
  if (!RM){
    const sh = shot.shake;
    camera.position.x += fbm1(t, 0.37, 0.0) * 0.0065 * sh;
    camera.position.y += fbm1(t, 0.31, 1.9) * 0.0045 * sh;
    camera.position.z += fbm1(t, 0.27, 3.3) * 0.0030 * sh;
  }

  camera.lookAt(camLook);

  /* le roulis DOIT venir après lookAt : lookAt écrase la rotation. */
  camera.rotation.z += camRoll + (RM ? 0 : fbm1(t, 0.23, 5.1) * 0.0038 * shot.shake);

  if (Math.abs(camera.fov - camFov) > 0.01){
    camera.fov = camFov;
    camera.updateProjectionMatrix();
  }
```

> **Piège** : `camera.lookAt()` reconstruit intégralement la rotation. Tout roulis
> appliqué **avant** est perdu. C'est l'erreur classique de cette implémentation.

### 5.7 — Rack focus

**Objectif visuel :** la mise au point comme affordance d'interface. Quand le visiteur
survole la feuille, la MAP se tire dessus : ça lui dit où cliquer sans un mot d'UI.

```js
  /* pilote les uniformes DOF de §2.6 */
  let fTarget = shot.focus, rTarget = shot.range;
  if (paperHover || paperLifted){ fTarget = 0.95; rTarget = 0.25; }

  dofMat.uniforms.uFocus.value = damp(dofMat.uniforms.uFocus.value, fTarget, 0.038, dt);
  dofMat.uniforms.uRange.value = damp(dofMat.uniforms.uRange.value, rTarget, 0.038, dt);
```

Le `k = 0.038` donne ~0,6 s pour atteindre 90 % : c'est la vitesse d'un vrai tirage de
point. Un tirage instantané (`k = 1`) lit comme un bug d'affichage.

### 5.8 — Letterbox

CSS à ajouter. **Insère-toi dans l'ordre de z-index documenté** dans le fichier
(`index.html:66-71`) : `overlays 12 · sign 20 · prompt 20 · how-to 50 · CV texte 60 ·
tools 70`. Les barres vont à **22**, les sous-titres à **24** : au-dessus de la scène
et de l'enseigne, en dessous du how-to et du CV texte.

```css
.bars{position:fixed;left:0;right:0;height:9vh;background:#000;z-index:22;
  pointer-events:none;transition:transform .5s cubic-bezier(.16,1,.3,1);}
.bars.t{top:0;transform:translateY(-101%);}
.bars.b{bottom:0;transform:translateY(101%);}
body.cine .bars{transform:translateY(0);}
/* pendant la cinématique, l'enseigne et le prompt s'effacent */
body.cine .sign,
body.cine .prompt{opacity:0;transition:opacity .3s;}
@media(prefers-reduced-motion:reduce){
  .bars{transition:none;}
}
```

```html
<div class="bars t"></div><div class="bars b"></div>
```

```js
/* dans animate(), une ligne */
document.body.classList.toggle('cine', speaking && !RM);
```

> `101%` et non `100%` : à certains ratios de DPI, `100%` laisse une bande d'un pixel
> visible en haut de l'écran.

### 5.9 — Sous-titres

Le `README.md` note explicitement : *« Anyone with sound off, in a quiet office, or
hard of hearing now gets nothing from the spoken sections. »* Le langage GTA comble ce
trou — les sous-titres GTA sont une convention forte du jeu **et** une obligation
d'accessibilité.

Style : blanc pur, **aucun fond**, ombre portée dure, condensé, centré bas.

```css
.subs{position:fixed;left:50%;bottom:calc(9vh + 22px);transform:translateX(-50%);
  z-index:24;max-width:min(70ch,86vw);text-align:center;
  font:400 20px/1.35 "Barlow Condensed","Space Grotesk",sans-serif;
  color:#fff;text-shadow:1px 1px 0 #000,2px 2px 0 rgba(0,0,0,.6);
  pointer-events:none;opacity:0;transition:opacity .16s;
  padding:0 12px;}
.subs.on{opacity:1;}
@media(max-width:640px){ .subs{font-size:16px;bottom:calc(9vh + 14px);} }
```

#### 5.9.a — Cues pour les mp3

Les enregistrements n'ont pas de piste de timings. On répartit **au prorata du nombre
de caractères** sur `audioEl.duration`. La précision est de l'ordre de ±0,4 s, ce qui
est parfaitement acceptable pour du sous-titrage de confort.

```js
const subsEl = document.getElementById('subs');
let cues = [], cueIdx = -1;

function buildCues(text, duration){
  /* même découpe que le TTS, index.html:1330 */
  const parts = text.match(/[^.!?…]+[.!?…]+["']?|\S[^.!?…]*$/g) || [text];
  const total = parts.reduce((a, p) => a + p.length, 0) || 1;
  let acc = 0;
  return parts.map(p => {
    const start = acc / total * duration;
    acc += p.length;
    return { start: start, end: acc / total * duration, text: p.trim() };
  });
}
function showCue(txt){
  if (!txt){ subsEl.classList.remove('on'); return; }
  subsEl.textContent = txt;
  subsEl.classList.add('on');
}
function clearCues(){ cues = []; cueIdx = -1; showCue(''); }
```

Branchement dans `speak()` (`index.html:1333-1344`) :

```js
function speak(text, key){
  stopSpeaking(); speaking = true;
  const f = key && AUDIO[lang][key];
  if (f){
    audioEl = new Audio(f);
    try { attachAnalyser(audioEl); } catch(_) {}          /* §8.7 */
    audioEl.addEventListener('loadedmetadata', () => {
      cues = buildCues(text, audioEl.duration || 1);
    });
    audioEl.addEventListener('timeupdate', () => {
      const ct = audioEl.currentTime;
      let i = -1;
      for (let k = 0; k < cues.length; k++){
        if (ct >= cues[k].start && ct < cues[k].end){ i = k; break; }
      }
      if (i !== cueIdx){ cueIdx = i; showCue(i >= 0 ? cues[i].text : ''); }
    });
    audioEl.onended = () => { endSpeech(); clearCues(); };
    audioEl.onerror = () => { audioEl = null; clearCues(); ttsStart(text); };
    audioEl.play().catch(() => { audioEl = null; clearCues(); ttsStart(text); });
    return;
  }
  ttsStart(text);
}
```

#### 5.9.b — Cues pour la TTS

La `SpeechSynthesisUtterance` expose `onboundary`, qui donne l'index du caractère en
cours. C'est **plus précis** que le prorata — exploite-le.

```js
function next(code, v){
  if (!queue.length){ endSpeech(); clearCues(); return; }
  const sentence = queue.shift().trim();
  const u = new SpeechSynthesisUtterance(sentence);
  u.lang = code; u.rate = .98; if (v) u.voice = v;
  showCue(sentence);
  u.onboundary = e => {
    /* On sous-titre par phrase ; onboundary sert surtout à confirmer que la
       synthèse avance (certains moteurs n'émettent jamais onend). */
    if (e.charIndex >= sentence.length - 1) showCue(sentence);
  };
  u.onend = () => setTimeout(() => next(code, v), 140);
  u.onerror = () => { endSpeech(); clearCues(); };
  speechSynthesis.speak(u);
}
```

#### 5.9.c — Changement de langue en cours de lecture

`applyLang()` (`index.html:1362-1369`) appelle déjà `stopSpeaking()`. Ajoute
`clearCues()` juste après, sinon le dernier sous-titre reste affiché dans l'ancienne
langue.

### 5.10 — Cadrage portrait

`applyStaging()` (`index.html:1426-1436`) ne gère aujourd'hui qu'un seul plan. Il doit
maintenant transformer **tous** les plans.

Stratégie : en portrait, on **recule et on élargit**. La règle est de conserver la
largeur de champ à hauteur du sujet.

```js
function applyStaging(){
  const portrait = camera.aspect < 0.75;
  const fovMul  = portrait ? 1.30 : 1.00;    /* 47° → 61° */
  const backMul = portrait ? 1.12 : 1.00;    /* recule de 12 % */

  Object.keys(SHOTS).forEach(k => {
    const s = SHOTS[k];
    if (!s.base) s.base = { pos: s.pos.slice(), fov: s.fov, focus: s.focus };
    s.fov = s.base.fov * fovMul;
    const L = s.look;
    s.pos = [
      L[0] + (s.base.pos[0] - L[0]) * backMul,
      L[1] + (s.base.pos[1] - L[1]) * backMul,
      L[2] + (s.base.pos[2] - L[2]) * backMul
    ];
    s.focus = s.base.focus * backMul;        /* la MAP recule avec la caméra */
  });

  camera.fov = SHOTS[shotName].fov;
  camera.updateProjectionMatrix();
  camPos.fromArray(SHOTS[shotName].pos);

  /* poses de la feuille : inchangées par rapport à l'existant */
  paperRest.pos.set(0, .802, portrait ? .20 : .24);
  paperUp.pos.set(0, portrait ? 1.06 : 1.0, portrait ? .66 : .5);
  paperUp.rot = portrait ? -.98 : -.85;
}
```

> Le champ `s.base` est mémorisé au premier appel : sans ça, chaque resize
> multiplierait à nouveau les valeurs déjà multipliées, et la caméra partirait à
> l'infini au bout de quelques redimensionnements. C'est un bug réel et fréquent.

### 5.11 — `prefers-reduced-motion`

| Effet | Comportement quand `RM` est vrai |
|---|---|
| Respiration caméra | **Coupée** entièrement (position et roulis). |
| Coupes de plan | **Coupées** : on reste en `gameplay`. |
| Letterbox | **Pas affiché** (`speaking && !RM`). |
| Rack focus | **Conservé** mais instantané au changement de section, pas animé. |
| DOF statique | **Conservée** : ce n'est pas du mouvement. |
| Distorsion en barillet | **Coupée** (`uBarrel = 0`). |
| Aberration chromatique | **Réduite** de moitié. |
| Grain animé | **Figé** : `uTime` non mis à jour, le grain devient statique. |
| Sous-titres | **Conservés**, évidemment. |

### Critères d'acceptation

- [ ] En gameplay, la caméra n'est **pas** à `x = 0` : le décentrement est visible.
- [ ] `camera.rotation.z` est non nul et varie dans le temps (log-le pendant 5 s).
- [ ] Le roulis est appliqué **après** `camera.lookAt()`.
- [ ] Pendant une réplique, on compte au moins **3 coupes** sur 25 secondes, avec des
      intervalles tous différents.
- [ ] Aucun plan avec `look` vers Simon n'a `pos[0] < -0.7` sauf `overShldr`.
- [ ] Le letterbox apparaît et disparaît proprement avec `speaking`, et l'enseigne
      s'efface avec lui.
- [ ] Les sous-titres affichent la bonne phrase à ±0,6 s pendant tout un mp3, testé sur
      `about.mp3` (le plus long, 1,08 Mo).
- [ ] Basculer EN→FR en cours de lecture n'affiche pas un sous-titre orphelin.
- [ ] Après **20 redimensionnements** de la fenêtre, `SHOTS.gameplay.pos` est identique
      à sa valeur d'origine à ±0,001 (test du bug d'accumulation §5.10).
- [ ] Avec `prefers-reduced-motion: reduce`, la caméra est parfaitement immobile et
      aucun letterbox n'apparaît.
- [ ] Survoler la feuille tire la mise au point dessus en ~0,6 s, et la relâcher la
      ramène sur Simon.

---

## 6. Système de vie de fond — architecture

**C'est la section la plus importante du document.** Demande explicite du
commanditaire : *« je veux que les autres personnes en arrière-fond aient l'air
vivantes : discussion en fond, en train de travailler… »*

Cette section définit l'**infrastructure**. Le §7 définit les comportements concrets.

### 6.1 — Ce qui ne va pas aujourd'hui

`index.html:930-1022` (les rigs) et `:1442-1467` (l'animation).

```js
/* l'état de l'art actuel, index.html:1453-1458 */
w.phase += dt * 6;
const s = Math.sin(w.phase) * .5;
w.P.lLeg.rotation.x = s;  w.P.rLeg.rotation.x = -s;
w.P.lArm.rotation.x = -s * .6; w.P.rArm.rotation.x = s * .6;
```

Sept défauts, tous identifiables en moins de dix secondes par un spectateur :

| # | Défaut | Où | Pourquoi c'est un tell |
|---|---|---|---|
| 1 | **Sinus purs en boucle ouverte** | `1453-1467` | Périodicité parfaite. Le cerveau détecte une répétition exacte en 2 à 3 cycles. |
| 2 | **Demi-tour à 180° sur place** | `1444`, `1448` (`w.dir *= -1`) | Personne ne fait ça. C'est le tell n°1 du prototype. |
| 3 | **Aucun regard** | `1458` (`head.rotation.y = sin(...)`) | La tête balaye au hasard, sans jamais regarder quoi que ce soit. |
| 4 | **Aucune interaction entre agents** | — | Cinq personnes dans une pièce qui s'ignorent totalement. |
| 5 | **Agents synchronisés** | `1460-1467` | Le barista et la personne qui boit partagent la même horloge `t`. |
| 6 | **Rig insuffisant** | `931-976` | Pas de coude, pas de torse, pas de tête indépendante du corps. **Impossible** de faire du regard ou de la gestuelle avec ce squelette. |
| 7 | **Aucune anticipation** | partout | Les mouvements démarrent et s'arrêtent brutalement. |

Le défaut 6 est bloquant : il faut refaire le rig avant tout le reste.

### 6.2 — Le nouveau rig

Hiérarchie de `THREE.Group` imbriqués, avec les offsets **locaux** en mètres. Les
proportions reproduisent exactement celles de l'existant (hanches à 0,86 ; torse à
1,12 ; épaules à 1,36 ; tête à 1,64 ; sommet du crâne à 1,79).

```
root                              (0, 0, 0)
└─ pelvis                         (0, 0.86, 0)
   ├─ hipL   (-0.09, 0, 0)  ─ mesh cuisse (cyl 0.055→0.050, L 0.44) à y=-0.22
   │  └─ kneeL  (0, -0.44, 0) ─ mesh tibia (cyl 0.050→0.044, L 0.38) à y=-0.19
   │     └─ ankleL (0, -0.38, 0) ─ mesh pied (box 0.09×0.05×0.17) à (0,-0.025,0.045)
   ├─ hipR   (+0.09, 0, 0)   [miroir]
   └─ spine                       (0, 0.10, 0)      → monde 0.96
      └─ chest                    (0, 0.16, 0)      → monde 1.12
         ├─ mesh torse (cyl 0.165→0.205, L 0.52) à y=0
         ├─ mesh épaules (sphère 0.17, scale 1/0.55/0.9) à y=0.26
         ├─ neck                  (0, 0.28, 0)      → monde 1.40
         │  ├─ mesh cou (cyl 0.05, L 0.10) à y=0.05
         │  └─ head               (0, 0.24, 0)      → monde 1.64
         │     ├─ mesh crâne (sphère 0.15) à y=0
         │     ├─ eyeL / eyeR     (±0.052, 0.022, 0.128)
         │     ├─ lidL / lidR     (±0.052, 0.022, 0.128)   ← paupières, cf. §7 option B
         │     └─ mouth           (0, -0.052, 0.140)
         ├─ shoulderL             (-0.225, 0.24, 0) → monde 1.36
         │  ├─ mesh bras (cyl 0.045→0.040, L 0.28) à y=-0.14
         │  └─ elbowL             (0, -0.28, 0)
         │     ├─ mesh avant-bras (cyl 0.040→0.036, L 0.24) à y=-0.12
         │     └─ wristL          (0, -0.24, 0)     → monde 0.84
         │        └─ mesh main (sphère 0.045)
         └─ shoulderR             [miroir]
```

**14 articulations nommées** : `pelvis`, `spine`, `chest`, `neck`, `head`, `hipL/R`,
`kneeL/R`, `shoulderL/R`, `elbowL/R`, `wristL/R`. C'est le minimum pour du regard et de
la gestuelle crédibles.

```js
/* ---------------- RIG ---------------- */
function joint(parent, name, x, y, z, store){
  const g = new THREE.Group();
  g.name = name;
  g.position.set(x, y, z);
  parent.add(g);
  store[name] = g;
  return g;
}

function buildPerson(opts){
  const o = Object.assign({
    shirt:0x8a5540, pants:0x2e2e38, skin:0xe8b58c, hair:0x1d1d24,
    scale:1.0
  }, opts || {});

  const root = new THREE.Group();
  const J = {};                                     /* les articulations */
  const mS  = stdMat(o.shirt, 0.90, 0, 0.25);       /* cf. §4.9 */
  const mP  = stdMat(o.pants, 0.92, 0, 0.22);
  const mSk = stdMat(o.skin,  0.55, 0, 0.50);
  const mH  = stdMat(o.hair,  0.80, 0, 0.45);
  const mSh = stdMat(0x1d1d22, 0.70, 0, 0.35);

  function put(parent, geo, mat, x, y, z, cast){
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    if (cast) m.castShadow = true;
    parent.add(m);
    return m;
  }

  const pelvis = joint(root, 'pelvis', 0, 0.86, 0, J);
  for (const s of [-1, 1]){
    const S = s < 0 ? 'L' : 'R';
    const hip = joint(pelvis, 'hip' + S, 0.09 * s, 0, 0, J);
    put(hip, new THREE.CylinderGeometry(.055, .050, .44, 10), mP, 0, -.22, 0, true);
    const knee = joint(hip, 'knee' + S, 0, -.44, 0, J);
    put(knee, new THREE.CylinderGeometry(.050, .044, .38, 10), mP, 0, -.19, 0, true);
    const ankle = joint(knee, 'ankle' + S, 0, -.38, 0, J);
    put(ankle, bevelBox(.09, .05, .17, .006), mSh, 0, -.025, .045, true);
  }

  const spine = joint(pelvis, 'spine', 0, .10, 0, J);
  const chest = joint(spine, 'chest', 0, .16, 0, J);
  const torso = put(chest, new THREE.CylinderGeometry(.165, .205, .52, 16), mS, 0, 0, 0, true);
  const pad = put(chest, new THREE.SphereGeometry(.17, 16, 12), mS, 0, .26, 0, true);
  pad.scale.set(1, .55, .9);

  const neck = joint(chest, 'neck', 0, .28, 0, J);
  put(neck, new THREE.CylinderGeometry(.05, .05, .10, 10), mSk, 0, .05, 0, false);
  const head = joint(neck, 'head', 0, .24, 0, J);
  const skull = put(head, new THREE.SphereGeometry(.15, 18, 16), mSk, 0, 0, 0, true);
  const hair = put(head, new THREE.SphereGeometry(.155, 18, 14), mH, 0, .06, -.015, false);
  hair.scale.set(1, .72, 1);

  const eyes = [];
  for (const e of [-1, 1]){
    const eg = new THREE.Group();
    eg.position.set(.052 * e, .022, .118);
    head.add(eg);
    put(eg, new THREE.SphereGeometry(.019, 10, 10), stdMat(0xf3efe7, .35), 0, 0, 0, false);
    put(eg, new THREE.SphereGeometry(.011, 8, 8),  stdMat(0x23232b, .40), 0, 0, .013, false);
    /* paupière : calotte couleur peau qui descend par rotation, pas par écrasement */
    const lid = new THREE.Mesh(
      new THREE.SphereGeometry(.0205, 10, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), mSk);
    lid.position.set(0, 0, 0);
    eg.add(lid);
    eyes.push({ eg: eg, lid: lid });
  }
  const mouth = put(head, bevelBox(.048, .012, .014, .003),
                    stdMat(0x8a4a3a, .60), 0, -.052, .140, false);

  for (const s of [-1, 1]){
    const S = s < 0 ? 'L' : 'R';
    const sh = joint(chest, 'shoulder' + S, .225 * s, .24, 0, J);
    put(sh, new THREE.CylinderGeometry(.045, .040, .28, 10), mS, 0, -.14, 0, true);
    const el = joint(sh, 'elbow' + S, 0, -.28, 0, J);
    put(el, new THREE.CylinderGeometry(.040, .036, .24, 10), mS, 0, -.12, 0, true);
    const wr = joint(el, 'wrist' + S, 0, -.24, 0, J);
    put(wr, new THREE.SphereGeometry(.045, 10, 10), mSk, 0, 0, 0, false);
  }

  root.scale.setScalar(o.scale);
  scene.add(root);
  return { root: root, J: J, eyes: eyes, mouth: mouth, torso: torso, opts: o };
}
```

> **Interdiction absolue de mélanger anciens et nouveaux rigs.** Supprime `person()`
> (`index.html:931-976`) et reconstruis les six agents (les cinq PNJ `:977-1022` **et**
> Simon `:1024-1114`) sur `buildPerson`. Un rig hybride rendra le système de regard
> impossible à déboguer.

### 6.3 — Couches d'animation additives

**Pourquoi additif et non par remplacement** : si la locomotion écrit
`shoulderL.rotation.x = walkValue`, un geste de la main écrasera la marche, ou
inversement selon l'ordre d'exécution. Résultat : des mouvements qui « clignotent »
selon la frame. En additionnant dans un tampon puis en appliquant une seule fois, l'ordre
des couches n'a plus d'importance et chaque couche peut avoir son propre poids.

```js
const JOINT_NAMES = ['pelvis','spine','chest','neck','head',
                     'hipL','hipR','kneeL','kneeR',
                     'shoulderL','shoulderR','elbowL','elbowR','wristL','wristR'];

function makePoseBuffer(){
  const b = {};
  for (let i = 0; i < JOINT_NAMES.length; i++) b[JOINT_NAMES[i]] = { x:0, y:0, z:0 };
  return b;
}
function clearPose(b){
  for (let i = 0; i < JOINT_NAMES.length; i++){
    const j = b[JOINT_NAMES[i]]; j.x = 0; j.y = 0; j.z = 0;
  }
}
/* additionne une pose (objet {joint:{x,y,z}}) dans le tampon, pondérée */
function addPose(buf, pose, w){
  if (w <= 0) return;
  for (const k in pose){
    const t = buf[k]; if (!t) continue;
    const s = pose[k];
    if (s.x) t.x += s.x * w;
    if (s.y) t.y += s.y * w;
    if (s.z) t.z += s.z * w;
  }
}
/* applique le tampon au rig, en une seule passe */
function applyPose(rig, buf){
  for (let i = 0; i < JOINT_NAMES.length; i++){
    const n = JOINT_NAMES[i], j = rig.J[n], v = buf[n];
    if (!j) continue;
    j.rotation.set(v.x, v.y, v.z);
  }
}
```

Les cinq couches, dans l'ordre conceptuel (l'ordre d'exécution n'importe pas) :

| Couche | Contenu | Poids | Écrit sur |
|---|---|---|---|
| **L0 — Posture** | Pose statique de l'archétype : debout, assis, penché sur un comptoir. | 1.0 | Toutes les articulations. |
| **L1 — Locomotion** | Cycle de marche, transfert de poids, oscillation du bassin. | 0 → 1 selon la vitesse | `hip*`, `knee*`, `ankle*`, `pelvis`, `chest`, `shoulder*` |
| **L2 — Geste** | Gestes de parole, auto-contact, one-shots. | 0 → 1 par enveloppe | `shoulder*`, `elbow*`, `wrist*`, `chest`, `head` |
| **L3 — Regard** | Orientation tête/cou/torse vers une cible. | 1.0 | `neck`, `head`, `chest` (au-delà de 60°) |
| **L4 — Respiration** | Micro-mouvement du torse. | 1.0 | `chest` (+ scale du mesh torse) |

> **Exception** : `root.position`, `root.rotation.y` et l'échelle du mesh torse ne
> passent pas par le tampon — ce sont des transformées de racine et de mesh, pas des
> rotations d'articulation. Écris-les directement.

### 6.4 — Le tick comportemental

**Deux horloges séparées.** Le rendu tourne à la fréquence d'affichage (60, 120,
parfois 30 Hz) ; les décisions tournent à **10 Hz fixes**.

Pourquoi c'est indispensable :
- **Déterminisme** : une décision prise « toutes les 6 frames » se prend deux fois plus
  souvent sur un écran 120 Hz. Le café serait deux fois plus agité sur un MacBook Pro
  que sur un vieux portable.
- **Coût** : la sélection de cible de regard, les tests de séparation et l'évaluation
  des états sont les parties chères. À 10 Hz elles coûtent six fois moins qu'à 60 Hz.
- **Lisibilité** : les comportements humains changent à l'échelle de la seconde, pas de
  la frame.

```js
const TICK_HZ = 10;
const TICK_DT = 1 / TICK_HZ;
let tickAcc = 0;

/* dans animate() */
tickAcc += dt;
let guard = 0;
while (tickAcc >= TICK_DT && guard++ < 4){    /* garde anti-rattrapage explosif */
  behaviourTick(TICK_DT, t);
  tickAcc -= TICK_DT;
}
if (guard >= 4) tickAcc = 0;                  /* onglet réveillé après une pause */
animateAgents(dt, t);                         /* 60 Hz : les couches d'animation */
```

> Le garde à 4 itérations est essentiel : quand l'onglet revient au premier plan après
> une minute en arrière-plan, `dt` est borné à 0,05 par `index.html:1440` — mais si tu
> retires ce clamp un jour, `tickAcc` pourrait valoir 60 et tu ferais 600 ticks en une
> frame.

### 6.5 — Machine à états

```
                    ┌──────────────────────────────────────┐
                    ▼                                      │
  SPAWN ──► WALK_TO ──► IDLE ──► CONVERSE ──────────────────┤
              │  ▲        │         │                       │
              │  │        ▼         ▼                       │
              │  └──── ORDER ──► SIT_DOWN ──► SEATED ───────┤
              │                                 │           │
              ▼                                 ▼           │
            WORK ◄──────────────────────────  LEAVE ──► DESPAWN
```

| État | Durée (avec jitter) | Sortie | Description |
|---|---|---|---|
| `SPAWN` | instantané | `WALK_TO` | Placé à la porte, invisible pendant 1 frame. |
| `WALK_TO` | jusqu'à arrivée | `IDLE`, `ORDER`, `SIT_DOWN`, `CONVERSE`, `LEAVE` | Suit un chemin de waypoints. |
| `IDLE` | 3 – 9 s | `WALK_TO`, `CONVERSE` | Debout, regarde autour, change de posture. |
| `ORDER` | 8 – 16 s | `WALK_TO` | Au comptoir, parle au barista, attend. |
| `SIT_DOWN` | 1,2 s | `SEATED` | Transition d'assise (one-shot, cf. §7.1). |
| `SEATED` | 40 – 180 s | `LEAVE`, `CONVERSE` | Boit, lit, travaille (cf. §7.6, §7.8). |
| `CONVERSE` | 25 – 90 s | `IDLE`, `SEATED`, `LEAVE` | Membre d'un groupe (§6.7). |
| `WORK` | permanent | — | Le barista uniquement (§7.5). |
| `LEAVE` | jusqu'à la porte | `DESPAWN` | Marche vers la porte, ne fait plus demi-tour. |
| `DESPAWN` | instantané | `SPAWN` | Rendu au pool, réapparence variée (§6.8). |

```js
const ST = { SPAWN:0, WALK_TO:1, IDLE:2, ORDER:3, SIT_DOWN:4, SEATED:5,
             CONVERSE:6, WORK:7, LEAVE:8, DESPAWN:9 };

/* Toute durée passe par jit() : AUCUNE durée en dur dans le code. */
function jit(base, spread){ return base * (1 + (Math.random() * 2 - 1) * spread); }

function setState(a, s, dur){
  a.state = s;
  a.stateT = 0;
  a.stateDur = dur === undefined ? Infinity : dur;
  a.onEnter = true;
}

function behaviourTick(dtT, t){
  updateGroups(dtT, t);                        /* §6.7 */
  for (let i = 0; i < agents.length; i++){
    const a = agents[i];
    if (a.lod === 3) continue;                 /* gelé hors du frustum, §6.11 */
    a.stateT += dtT;
    switch (a.state){
      case ST.SPAWN:    onSpawn(a);                break;
      case ST.WALK_TO:  tickWalkTo(a, dtT);        break;
      case ST.IDLE:     tickIdle(a, dtT, t);       break;
      case ST.ORDER:    tickOrder(a, dtT, t);      break;
      case ST.SIT_DOWN: tickSitDown(a, dtT);       break;
      case ST.SEATED:   tickSeated(a, dtT, t);     break;
      case ST.CONVERSE: tickConverse(a, dtT, t);   break;
      case ST.WORK:     tickWork(a, dtT, t);       break;
      case ST.LEAVE:    tickLeave(a, dtT);         break;
      case ST.DESPAWN:  onDespawn(a);              break;
    }
    a.onEnter = false;
    if (a.lod < 2) updateGaze(a, dtT);            /* §6.6 */
  }
}
```

### 6.6 — Système de regard

**Le comportement au plus fort rendement du document.** Un personnage qui regarde
quelque chose est vivant ; un personnage qui fixe le vide est un mannequin, quelle que
soit la qualité du reste.

#### Anatomie de la réponse

Les faits qu'il faut modéliser, dans l'ordre d'importance :

1. **Les yeux mènent, la tête suit.** L'œil atteint sa cible en ~50 ms (saccade), la
   tête met 150 à 400 ms à s'aligner. Modéliser ce décalage est ce qui distingue un
   regard crédible d'un regard robotique.
2. **Limites articulaires.** Yeux ±25°, tête ±60° en lacet et ±25° en tangage. Au-delà,
   c'est le **torse** qui tourne.
3. **Latence de décision.** On ne regarde pas instantanément ce qui bouge : 150 à 400 ms
   de délai entre l'événement et le début de la saccade.
4. **Micro-saccades de fixation.** Même en fixant, l'œil bouge de 0,2 à 0,5° à ~2 Hz.
5. **Clignement déclenché par le changement de fixation.** C'est un fait
   physiologique : on cligne au moment où on change de point de regard. Extrêmement
   lisible et quasi jamais implémenté.

#### Saillance

```js
/* Chaque agent choisit une cible dans une liste pondérée, réévaluée toutes les
   1,5 à 5 s (jitter). Poids plus élevé = regardé plus souvent. */
const GAZE_KINDS = {
  SPEAKER:   { w: 6.0 },   /* qui parle dans mon groupe */
  SIMON:     { w: 2.5 },   /* le sujet de la scène */
  DOOR:      { w: 1.5 },   /* quand quelqu'un entre */
  MOTION:    { w: 3.0 },   /* un agent qui passe à moins de 3 m */
  OWN_PROP:  { w: 2.0 },   /* ma tasse, mon écran, mon livre */
  AMBIENT:   { w: 1.0 }    /* un point au hasard dans la pièce */
};

const _gv = new THREE.Vector3();       /* scratch — jamais de new dans la boucle */
const _gl = new THREE.Vector3();

function pickGazeTarget(a){
  const cands = [];
  if (a.group && a.group.speaker && a.group.speaker !== a){
    cands.push({ w: GAZE_KINDS.SPEAKER.w, obj: a.group.speaker.rig.J.head });
  }
  if (a.distToSimon < 6) cands.push({ w: GAZE_KINDS.SIMON.w, obj: simonHead });
  if (a.prop)            cands.push({ w: GAZE_KINDS.OWN_PROP.w, obj: a.prop });
  if (doorBusy > 0)      cands.push({ w: GAZE_KINDS.DOOR.w, pos: W.DOOR });
  if (a.nearMover)       cands.push({ w: GAZE_KINDS.MOTION.w, obj: a.nearMover.rig.J.chest });
  cands.push({ w: GAZE_KINDS.AMBIENT.w,
               pos: [ (Math.random() - .5) * 6, 1.0 + Math.random() * 0.9,
                      -1 - Math.random() * 3 ] });

  let total = 0; for (let i = 0; i < cands.length; i++) total += cands[i].w;
  let r = Math.random() * total;
  for (let i = 0; i < cands.length; i++){ r -= cands[i].w; if (r <= 0) return cands[i]; }
  return cands[cands.length - 1];
}

function updateGaze(a, dtT){
  a.gazeT -= dtT;
  if (a.gazeT <= 0){
    a.gazeNext  = pickGazeTarget(a);
    a.gazeDelay = 0.15 + Math.random() * 0.25;     /* latence de décision */
    a.gazeT     = jit(3.2, 0.55);                  /* 1,4 à 5 s */
    a.blinkQueue = true;                           /* on cligne au changement */
  }
  if (a.gazeDelay > 0){
    a.gazeDelay -= dtT;
    if (a.gazeDelay <= 0) a.gaze = a.gazeNext;
  }
}
```

#### Résolution en angles

```js
/* Convertit une cible monde en lacet/tangage LOCAUX à la tête au repos.
   Le repère de la tête est celui du chest, lui-même tourné par root.rotation.y. */
function gazeAngles(a, out){
  const g = a.gaze;
  if (!g){ out.yaw = 0; out.pitch = 0; return; }
  if (g.obj) g.obj.getWorldPosition(_gv);
  else _gv.set(g.pos[0], g.pos[1], g.pos[2]);

  a.rig.J.head.getWorldPosition(_gl);
  _gv.sub(_gl);                                    /* vecteur monde tête → cible */

  /* passe dans le repère « avant » de l'agent : root.rotation.y */
  const ry = a.rig.root.rotation.y;
  const cx =  Math.cos(-ry) * _gv.x - Math.sin(-ry) * _gv.z;
  const cz =  Math.sin(-ry) * _gv.x + Math.cos(-ry) * _gv.z;

  out.yaw   = Math.atan2(cx, cz);                  /* +cz = devant l'agent */
  out.pitch = Math.atan2(_gv.y, Math.hypot(cx, cz));
}

const LIM = {
  eyeYaw:   0.44,   /* 25° */
  eyePitch: 0.30,
  headYaw:  1.05,   /* 60° */
  headPitch:0.44,   /* 25° */
  chestYaw: 0.70    /* 40° : au-delà, l'agent devrait se retourner */
};

const _ga = { yaw:0, pitch:0 };

function gazeLayer(a, buf, dt){
  gazeAngles(a, _ga);

  /* distribution : yeux d'abord, puis tête, puis torse */
  const eyeY  = THREE.MathUtils.clamp(_ga.yaw,   -LIM.eyeYaw,   LIM.eyeYaw);
  const eyeP  = THREE.MathUtils.clamp(_ga.pitch, -LIM.eyePitch, LIM.eyePitch);
  const restY = _ga.yaw   - eyeY;
  const restP = _ga.pitch - eyeP;
  const headY = THREE.MathUtils.clamp(restY, -LIM.headYaw,  LIM.headYaw);
  const headP = THREE.MathUtils.clamp(restP, -LIM.headPitch, LIM.headPitch);
  const chestY= THREE.MathUtils.clamp(restY - headY, -LIM.chestYaw, LIM.chestYaw);

  /* les yeux atteignent la cible presque instantanément (saccade ≈ 50 ms) */
  a.eyeY = damp(a.eyeY, eyeY, 0.55, dt);
  a.eyeP = damp(a.eyeP, eyeP, 0.55, dt);
  /* la tête suit avec retard */
  a.headY = damp(a.headY, headY, 0.085, dt);
  a.headP = damp(a.headP, headP, 0.085, dt);
  /* le torse encore plus lentement */
  a.chestY = damp(a.chestY, chestY, 0.030, dt);

  /* micro-saccades de fixation */
  const ms = a.lod === 0 ? 0.004 : 0;
  addPose(buf, {
    neck:  { y: a.headY * 0.35, x: -a.headP * 0.35 },
    head:  { y: a.headY * 0.65 + fbm1(a.clock, 1.7, a.seed) * ms,
             x: -a.headP * 0.65 },
    chest: { y: a.chestY }
  }, 1);

  /* les yeux ne passent pas par le tampon : ce sont des Groups enfants de head */
  for (let i = 0; i < a.rig.eyes.length; i++){
    a.rig.eyes[i].eg.rotation.y = a.eyeY;
    a.rig.eyes[i].eg.rotation.x = -a.eyeP;
  }
}
```

#### Clignement

```js
function blinkLayer(a, dt){
  a.blinkT -= dt;
  if (a.blinkQueue){ a.blinkQueue = false; a.blinkT = Math.min(a.blinkT, 0.06); }
  if (a.blinkT <= 0){
    a.blinkPhase = 1;
    /* 1 clignement sur 6 est un double-clignement */
    a.blinkT = Math.random() < 0.17 ? 0.20 : jit(4.2, 0.55);
  }
  if (a.blinkPhase > 0){
    a.blinkPhase -= dt * 8.5;                        /* ~120 ms de fermeture */
    const k = Math.sin(Math.max(0, a.blinkPhase) * Math.PI);
    for (let i = 0; i < a.rig.eyes.length; i++){
      /* la paupière DESCEND par rotation : jamais d'écrasement de sphère */
      a.rig.eyes[i].lid.rotation.x = k * Math.PI * 0.92;
    }
  }
}
```

> **Ne réutilise pas** l'approche actuelle (`eg.scale.y = 0.12`, `index.html:1473-1474`).
> Écraser une sphère produit une lentille aplatie qui traverse le visage. La paupière
> est un hémisphère couleur peau qui pivote de ~166°.

### 6.7 — Groupes de conversation (F-formations)

**C'est ce qui produit littéralement « discussion en fond ».**

#### Géométrie

En sociologie de l'interaction, un groupe en conversation forme une **F-formation** :
les participants se placent autour d'un espace partagé (*o-space*), corps orientés vers
ce centre, à une distance qui dépend du nombre de participants.

| Taille | Rayon | Angles | Note |
|---|---|---|---|
| 2 | 0.62 m | 0° / 180°, mais **décalés de 15°** | Deux personnes ne se font jamais exactement face : c'est le cadrage « vis-à-vis » qui lit comme un affrontement. |
| 3 | 0.72 m | 0° / 125° / 235° | Triangle légèrement irrégulier. |
| 4 | 0.84 m | 0° / 95° / 180° / 265° | Presque un carré, jamais parfait. |

**Buste vs pieds** : les pieds pointent vers le centre à ±20° près ; le buste pivote de
±25° supplémentaires vers le locuteur courant. C'est ce décalage pieds/buste qui rend
un groupe crédible.

```js
const FORMATIONS = {
  2: { r: 0.62, ang: [0, 195] },
  3: { r: 0.72, ang: [0, 125, 235] },
  4: { r: 0.84, ang: [0, 95, 180, 265] }
};

function groupSlot(group, index, out){
  const f = FORMATIONS[Math.min(4, Math.max(2, group.members.length))];
  const a = (f.ang[index % f.ang.length] + group.rot) * Math.PI / 180;
  out[0] = group.center[0] + Math.sin(a) * f.r;
  out[1] = group.center[2] + Math.cos(a) * f.r;
  out[2] = a + Math.PI;                     /* orientation : vers le centre */
}
```

#### Tour de parole

```js
function makeGroup(center, rot){
  return {
    center: center, rot: rot || 0,
    members: [],
    speaker: null,
    turnT: 0, turnDur: 0,
    gapT: 0,                       /* silence entre deux tours */
    laughT: jit(28, 0.6),          /* prochain éclat de rire */
    laughing: 0
  };
}

function updateGroups(dtT, t){
  for (let gi = 0; gi < groups.length; gi++){
    const g = groups[gi];
    if (g.members.length < 2){ g.speaker = null; continue; }

    /* --- rire collectif --- */
    g.laughT -= dtT;
    if (g.laughT <= 0){ g.laughing = 1.0; g.laughT = jit(32, 0.55); }
    if (g.laughing > 0) g.laughing = Math.max(0, g.laughing - dtT * 0.55);

    /* --- tour de parole --- */
    if (g.gapT > 0){ g.gapT -= dtT; if (g.gapT <= 0) g.speaker = null; }

    g.turnT += dtT;
    if (!g.speaker || g.turnT >= g.turnDur){
      /* chevauchement court : 1 fois sur 5, le suivant démarre avant la fin */
      const overlap = Math.random() < 0.20;
      const prev = g.speaker;
      let next = g.members[(Math.random() * g.members.length) | 0];
      let tries = 0;
      /* jamais deux tours consécutifs pour la même personne */
      while (next === prev && tries++ < 6){
        next = g.members[(Math.random() * g.members.length) | 0];
      }
      g.speaker  = next;
      g.turnT    = overlap ? 0.25 : 0;
      g.turnDur  = jit(6.0, 0.50);                 /* 3 à 9 s */
      g.gapT     = Math.random() < 0.30 ? jit(0.9, 0.6) : 0;   /* silence 1 fois sur 3 */
      if (g.speaker) g.speaker.gestureQueue = true;            /* §7.2 */
    }
  }
}
```

#### Deux groupes concrets dans le café

| Groupe | Centre | `rot` | Taille | Où |
|---|---|---|---|---|
| `G_STAND` | `(-1.10, 0, -3.40)` | 25° | 3 | Debout, entre la table gauche et le mur du fond. Visible derrière l'épaule gauche de Simon. |
| `G_TABLE` | `(1.55, 0, -2.35)` | -40° | 2 | Assis à la table de droite. Visible derrière l'épaule droite de Simon. |

Les deux positions sont **choisies pour être dans le cadre** du plan `gameplay` et du
plan `closeup` — un groupe qui discute hors champ ne sert à rien. Vérifie-le en mode
debug (§6.13).

### 6.8 — Navigation

#### Graphe de waypoints

Coordonnées vérifiées contre le mobilier réel : comptoir à `(2.7, -3.6)` occupant
`x ∈ [1.1, 4.3]` et `z ∈ [-3.98, -3.23]` ; table de Simon à `(0, -0.15)` rayon `0.95` ;
table gauche à `(-2.7, -2.4)` rayon `0.7` ; table droite à `(2.3, -1.6)` rayon `0.6` ;
plantes à `(-4.2, -2.9)`, `(4.4, -4.3)`, `(1.35, -3.42)` ; murs à `x = ±5`, `z = -5`.

```js
const W = {
  DOOR:      [ 4.85, 0,  0.60],   /* la porte, hors du champ du plan gameplay */
  OUTSIDE:   [ 5.90, 0,  0.60],   /* point de despawn, derrière le mur */
  ENTRY:     [ 3.90, 0,  0.20],
  AISLE_R:   [ 3.60, 0, -1.90],
  QUEUE:     [ 3.30, 0, -2.85],
  COUNTER:   [ 2.90, 0, -2.98],   /* devant le comptoir, face nord */
  MID:       [ 1.30, 0, -1.60],
  AISLE_L:   [-1.60, 0, -1.70],
  CONV_A:    [-1.10, 0, -3.40],
  CONV_B:    [ 1.55, 0, -2.35],
  SEAT_L:    [-2.70, 0, -3.10],   /* chaise existante, index.html:909 */
  SEAT_L2:   [-3.50, 0, -2.40],   /* chaise existante, index.html:909 */
  SEAT_R:    [ 3.00, 0, -1.60],   /* chaise existante, index.html:910 */
  WINDOW:    [-4.10, 0, -1.20],
  BACK_L:    [-3.60, 0, -4.30],
  BAR_BACK:  [ 2.55, 0, -4.30]    /* zone barista, derrière le comptoir */
};

/* arêtes bidirectionnelles, contournant les meubles */
const EDGES = {
  OUTSIDE: ['DOOR'],
  DOOR:    ['OUTSIDE', 'ENTRY'],
  ENTRY:   ['DOOR', 'AISLE_R', 'MID'],
  AISLE_R: ['ENTRY', 'QUEUE', 'SEAT_R', 'MID'],
  QUEUE:   ['AISLE_R', 'COUNTER'],
  COUNTER: ['QUEUE', 'CONV_B', 'BAR_BACK'],
  MID:     ['ENTRY', 'AISLE_R', 'AISLE_L', 'CONV_B'],
  AISLE_L: ['MID', 'WINDOW', 'CONV_A', 'SEAT_L2'],
  CONV_A:  ['AISLE_L', 'BACK_L', 'SEAT_L'],
  CONV_B:  ['MID', 'COUNTER'],
  SEAT_L:  ['CONV_A'],
  SEAT_L2: ['AISLE_L'],
  SEAT_R:  ['AISLE_R'],
  WINDOW:  ['AISLE_L'],
  BACK_L:  ['CONV_A'],
  BAR_BACK:['COUNTER']
};

/* BFS : le graphe a 16 nœuds, un Dijkstra serait de la sur-ingénierie */
function findPath(from, to){
  if (from === to) return [to];
  const prev = { }, q = [from], seen = { };
  seen[from] = true;
  while (q.length){
    const cur = q.shift();
    const ns = EDGES[cur] || [];
    for (let i = 0; i < ns.length; i++){
      const n = ns[i];
      if (seen[n]) continue;
      seen[n] = true; prev[n] = cur;
      if (n === to){
        const path = [n];
        let c = n;
        while (prev[c]){ c = prev[c]; path.unshift(c); }
        return path.slice(1);          /* on est déjà sur `from` */
      }
      q.push(n);
    }
  }
  return null;
}
```

#### Steering

```js
const SEP_R = 0.55;                    /* rayon de séparation */
const _s1 = new THREE.Vector3();

function tickWalkTo(a, dtT){
  if (a.onEnter && a.path && a.path.length) a.wpIdx = 0;
  if (!a.path || a.wpIdx >= a.path.length){ a.onArrive(a); return; }

  const wp = W[a.path[a.wpIdx]];
  const dx = wp[0] - a.pos.x, dz = wp[2] - a.pos.z;
  const d  = Math.hypot(dx, dz);

  /* arrivée : ralentit sur les 45 derniers cm */
  const arriveMul = Math.min(1, d / 0.45);
  let vx = (dx / (d || 1)) * a.speed * arriveMul;
  let vz = (dz / (d || 1)) * a.speed * arriveMul;

  /* séparation : évite les autres agents */
  for (let i = 0; i < agents.length; i++){
    const o = agents[i];
    if (o === a || o.lod === 3) continue;
    const ox = a.pos.x - o.pos.x, oz = a.pos.z - o.pos.z;
    const od = Math.hypot(ox, oz);
    if (od > 1e-3 && od < SEP_R){
      const push = (SEP_R - od) / SEP_R;
      vx += (ox / od) * push * a.speed * 1.4;
      vz += (oz / od) * push * a.speed * 1.4;
    }
  }
  /* et les meubles : répulsion par cercle */
  for (let i = 0; i < OBSTACLES.length; i++){
    const ob = OBSTACLES[i];
    const ox = a.pos.x - ob[0], oz = a.pos.z - ob[1];
    const od = Math.hypot(ox, oz);
    const lim = ob[2] + 0.32;
    if (od > 1e-3 && od < lim){
      const push = (lim - od) / lim;
      vx += (ox / od) * push * a.speed * 2.2;
      vz += (oz / od) * push * a.speed * 2.2;
    }
  }

  a.vel.set(vx, 0, vz);
  a.pos.x += vx * dtT;
  a.pos.z += vz * dtT;

  /* orientation : tourne PROGRESSIVEMENT vers la direction de marche */
  const wantYaw = Math.atan2(vx, vz);
  a.yaw = angleDamp(a.yaw, wantYaw, 0.14, dtT);

  if (d < 0.22){ a.wpIdx++; }
}

/* cercles englobants (x, z, rayon) des meubles à ne pas traverser */
const OBSTACLES = [
  [ 0.00, -0.15, 0.95],   /* table Simon */
  [ 0.00, -1.08, 0.30],   /* la chaise de Simon */
  [-2.70, -2.40, 0.70],   /* table gauche */
  [ 2.30, -1.60, 0.60],   /* table droite */
  [ 1.60, -3.60, 0.55],   /* comptoir, gauche */
  [ 2.70, -3.60, 0.55],   /* comptoir, centre */
  [ 3.80, -3.60, 0.55],   /* comptoir, droite */
  [-4.20, -2.90, 0.30],   /* plante 1 */
  [ 4.40, -4.30, 0.26],   /* plante 2 */
  [ 1.35, -3.42, 0.16]    /* plante 3 */
];

/* interpolation d'angle par le plus court chemin */
function angleDamp(cur, target, k, dt){
  let d = target - cur;
  while (d >  Math.PI) d -= Math.PI * 2;
  while (d < -Math.PI) d += Math.PI * 2;
  return cur + d * (1 - Math.pow(1 - k, dt * 60));
}
```

#### L'interdiction du demi-tour

`index.html:1444` et `:1448` font `w.dir *= -1` : l'agent pivote de 180° au milieu de la
pièce et repart. **C'est interdit.** Un agent qui a fini son parcours :

1. passe en `LEAVE`,
2. calcule un chemin vers `DOOR` puis `OUTSIDE`,
3. franchit la porte (à `x = 4.85`, hors du cadre des plans `gameplay` et `closeup`),
4. `DESPAWN`, retour au pool,
5. réapparaît plus tard avec une **autre apparence** (§6.9).

Le seul demi-tour autorisé est celui qui s'étale sur au moins 1,2 s **et** qui se
produit derrière un meuble ou hors du cadre.

### 6.9 — Pool, spawn, variation

```js
const PALETTES = {
  shirt: [0x8a5540, 0x51606e, 0x35543f, 0x6e4a63, 0xc9973c, 0x2c4a6e,
          0x7d3b3b, 0x46524a, 0xa86b4a, 0x3f4a63],
  pants: [0x2e2e38, 0x3a3230, 0x23232b, 0x453b33, 0x2a3038],
  skin:  [0xe8b58c, 0xd9a578, 0xeac39a, 0xe0af83, 0xc48a5e, 0x8d5a3b, 0xf0cba8],
  hair:  [0x1d1d24, 0x4a3524, 0x2c2018, 0x14100c, 0x3a2c1c, 0x6b5340, 0x8a8a8a]
};
function pick(arr){ return arr[(Math.random() * arr.length) | 0]; }

const MAX_AGENTS = { high: 7, medium: 5, low: 3 };
const agents = [], groups = [];
let pool = [];

function acquireAgent(){
  const a = pool.pop();
  if (a){ a.rig.root.visible = true; return a; }
  return null;                          /* le pool est pré-alloué, jamais vide */
}

function reskin(a){
  const o = a.rig.opts;
  o.shirt = pick(PALETTES.shirt); o.pants = pick(PALETTES.pants);
  o.skin  = pick(PALETTES.skin);  o.hair  = pick(PALETTES.hair);
  /* les matériaux sont partagés (§4.9) : on les RÉ-ASSIGNE, on n'en crée pas */
  a.rig.root.traverse(m => {
    if (!m.isMesh || !m.userData.slot) return;
    m.material = stdMat(o[m.userData.slot], MAT_ROUGH[m.userData.slot], 0,
                        MAT_ENV[m.userData.slot]);
  });
  a.rig.root.scale.setScalar(0.96 + Math.random() * 0.08);   /* ±4 % */
  a.speed = 0.42 + Math.random() * 0.16;                     /* ±15 % */
  a.rateMul = 0.90 + Math.random() * 0.20;                   /* §6.10 */
  a.seed = Math.random() * 100;
}
```

> **Marque chaque mesh avec `userData.slot`** (`'shirt'`, `'pants'`, `'skin'`, `'hair'`)
> dans `buildPerson`, sinon `reskin` ne peut pas savoir quoi recolorer.
>
> **Jamais de `new` en cours de jeu.** Le pool est alloué une fois au chargement avec
> `MAX_AGENTS.high` agents ; les paliers inférieurs en gardent simplement moins de
> visibles.

### 6.10 — Anti-synchronisation

**La règle d'or de cette section.** Toute boucle partagée reçoit un **décalage de
phase** ET un **multiplicateur de fréquence** propres à l'agent. Sans ça, cinq
personnages deviennent cinq clones et l'illusion tombe instantanément.

```js
/* Chaque agent porte son horloge propre. On ne lit JAMAIS le `t` global
   dans une couche d'animation d'agent. */
function agentClock(a, dt){
  a.clock += dt * a.rateMul;
  return a.clock;
}
```

À l'initialisation : `a.clock = Math.random() * 100; a.rateMul = 0.90 + Math.random() * 0.20;`

Audit à faire sur ton propre code : **cherche toute occurrence de `Math.sin(t` dans une
fonction qui anime un agent.** Il ne doit en rester aucune. Le `t` global n'est légitime
que pour la caméra, les lumières, la vapeur et la poussière.

### 6.11 — Respiration universelle

Coût nul, gain disproportionné. Tous les agents, tout le temps, y compris Simon, y
compris assis, y compris pendant une autre animation.

```js
function breathLayer(a, buf, ac){
  const b = Math.sin(ac * 1.55 + a.seed);            /* ~0,25 Hz */
  addPose(buf, {
    chest: { x: b * 0.012 },
    spine: { x: b * 0.006 }
  }, 1);
  /* le mesh torse enfle légèrement : c'est ça qu'on voit vraiment */
  a.rig.torso.scale.set(1 + b * 0.014, 1 + b * 0.006, 1 + b * 0.014);
}
```

### 6.12 — Verrouillage des pieds

Sans IK, les pieds glissent — le tell le plus visible d'une marche procédurale. Solution
sans solveur : on **plante** le pied quand sa vitesse projetée au sol est faible, et on
compense sur la hanche.

```js
/* dans la couche de locomotion, pour chaque jambe */
function footLock(a, side, cyclePhase, buf){
  const S = side;
  /* phase de contact : 0 → 0.5 du cycle pour la jambe gauche */
  const contact = (cyclePhase % 1) < 0.5;
  const key = 'lock' + S;

  if (contact){
    if (!a[key]){
      /* on vient de poser : mémorise la position monde du pied */
      a[key] = new THREE.Vector3();
      a.rig.J['ankle' + S].getWorldPosition(a[key]);
    }
    /* écart entre où le pied EST et où il devrait rester */
    a.rig.J['ankle' + S].getWorldPosition(_s1);
    const slipZ = _s1.z - a[key].z;
    const slipX = _s1.x - a[key].x;
    const slip = Math.hypot(slipX, slipZ);
    /* on corrige en fléchissant la hanche à contre-sens, plafonné */
    const corr = THREE.MathUtils.clamp(slip * 0.9, 0, 0.28);
    addPose(buf, { ['hip' + S]: { x: -corr } }, 1);
  } else {
    a[key] = null;
  }
}
```

> Ce n'est pas de l'IK exacte : ça réduit le glissement perçu de 70 à 80 %, ce qui
> suffit largement pour des agents vus à 3 m derrière un sujet net. N'implémente pas de
> vrai solveur à deux os ici : le rapport coût/bénéfice est mauvais.

### 6.13 — LOD comportemental

```js
const _fr = new THREE.Frustum();
const _pm = new THREE.Matrix4();
const _sp = new THREE.Sphere(new THREE.Vector3(), 1.1);

function updateLOD(){
  _pm.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  _fr.setFromProjectionMatrix(_pm);
  for (let i = 0; i < agents.length; i++){
    const a = agents[i];
    _sp.center.set(a.pos.x, 1.0, a.pos.z);
    const visible = _fr.intersectsSphere(_sp);
    const d = camera.position.distanceTo(_sp.center);
    a.distToSimon = Math.hypot(a.pos.x, a.pos.z + 1.08);
    if (!visible)      a.lod = 3;
    else if (d < 3.0)  a.lod = 0;
    else if (d < 6.0)  a.lod = 1;
    else               a.lod = 2;
  }
}
```

| LOD | Condition | Couches actives | Tick |
|---|---|---|---|
| **0** | visible, < 3 m | Toutes : posture, locomotion, geste, regard complet, micro-saccades, respiration, clignement, verrouillage des pieds | 10 Hz |
| **1** | visible, 3–6 m | Idem sans micro-saccades ni verrouillage des pieds | 10 Hz |
| **2** | visible, > 6 m | Posture, locomotion, respiration. Regard réduit à la tête (pas d'yeux). Pas de geste. | 5 Hz |
| **3** | hors frustum | **Aucune.** `behaviourTick` saute l'agent, `root.visible` reste `true` (le culling de three s'en charge). Seule la position continue d'être intégrée pour que l'agent ne se téléporte pas en revenant. | — |

> Appelle `updateLOD()` **une fois par frame**, avant `behaviourTick`, et jamais dans une
> boucle par agent : `setFromProjectionMatrix` est coûteux.
>
> `camera.matrixWorldInverse` est tenu à jour par three au rendu. Si tu appelles
> `updateLOD()` avant le premier `render`, force `camera.updateMatrixWorld()`.

### 6.14 — Paliers de qualité

| Palier | Agents visibles | `TICK_HZ` | Groupes | LOD 0 max |
|---|---|---|---|---|
| `high` | 7 | 10 | 2 | 3 agents |
| `medium` | 5 | 10 | 1 | 2 agents |
| `low` | 3 | 6 | 1 | 1 agent |

**`prefers-reduced-motion`** : les agents restent **présents et animés** — un café
figé serait plus déstabilisant qu'un café qui bouge. On coupe seulement :
- la locomotion (tout le monde reste en place, en `IDLE` / `SEATED` / `CONVERSE`),
- les micro-saccades,
- le clignement rapide (on passe à un clignement lent, 6 s),
- les gestes one-shot (on garde la respiration et le regard lent).

### 6.15 — Instrumentation

Tu n'as pas d'yeux : il te faut une console.

```js
window.__agents = () => agents.map(a => ({
  id: a.id,
  state: Object.keys(ST).find(k => ST[k] === a.state),
  lod: a.lod,
  pos: [ +a.pos.x.toFixed(2), +a.pos.z.toFixed(2) ],
  yaw: +a.yaw.toFixed(2),
  speed: +a.speed.toFixed(2),
  clock: +a.clock.toFixed(1),
  rateMul: +a.rateMul.toFixed(3),
  group: a.group ? groups.indexOf(a.group) : -1,
  speaking: !!(a.group && a.group.speaker === a),
  gaze: a.gaze ? (a.gaze.obj ? a.gaze.obj.name || 'obj' : 'pos') : null
}));

window.__groups = () => groups.map(g => ({
  center: g.center,
  members: g.members.length,
  speaker: g.speaker ? g.speaker.id : null,
  turn: +g.turnT.toFixed(1) + '/' + g.turnDur.toFixed(1),
  laughing: +g.laughing.toFixed(2)
}));

/* aides visuelles, activées par #agents */
let debugHelpers = null;
function toggleAgentDebug(on){
  if (on && !debugHelpers){
    debugHelpers = new THREE.Group();
    agents.forEach(a => {
      const arrow = new THREE.ArrowHelper(
        new THREE.Vector3(0, 0, 1), new THREE.Vector3(), 0.6, 0xff4488);
      arrow.userData.agent = a;
      debugHelpers.add(arrow);
    });
    scene.add(debugHelpers);
  }
  if (debugHelpers) debugHelpers.visible = on;
}
/* dans animate() : orienter chaque flèche vers la cible de regard de son agent */
```

### Critères d'acceptation

- [ ] `person()` (ancien) n'existe plus. Les 6 agents et Simon sont construits par
      `buildPerson`.
- [ ] `rig.J` contient exactement les 15 articulations nommées de `JOINT_NAMES`.
- [ ] `__agents()` renvoie un tableau où **aucun `rateMul` n'est identique** et
      **aucun `clock` n'est identique** — c'est le test d'anti-synchronisation.
- [ ] `grep 'Math.sin(t' ` dans les fonctions d'animation d'agents ne renvoie
      **aucune** occurrence.
- [ ] Le tick comportemental s'exécute à 10 Hz : compte les appels à `behaviourTick`
      sur 10 secondes, tu dois en avoir **100 ± 3**, quel que soit le framerate.
- [ ] Aucun agent ne fait un demi-tour de plus de 90° en moins de 1 s dans le cadre :
      log `a.yaw` sur 60 s et vérifie la dérivée max.
- [ ] Aucun agent ne traverse un meuble : log la distance minimale à chaque
      `OBSTACLES[i]` sur 3 minutes, elle doit rester **> rayon**.
- [ ] `__groups()` montre un `speaker` qui change toutes les 3 à 9 s, et **jamais deux
      tours consécutifs pour le même membre**.
- [ ] Les deux groupes sont **visibles dans le cadre** du plan `gameplay` : vérifie par
      capture.
- [ ] La paupière descend par rotation (`lid.rotation.x`) et aucun code ne touche à
      `eg.scale.y`.
- [ ] Les yeux atteignent une nouvelle cible avant la tête : log `a.eyeY` et `a.headY`
      lors d'un changement de fixation, l'œil doit converger ~6× plus vite.
- [ ] Un agent sorti par la porte réapparaît avec une couleur de chemise différente.
- [ ] `renderer.info.memory.geometries` et `.textures` sont **stables** après 5 minutes
      de fonctionnement (pas de `new` dans les ticks).

---

## 7. Catalogue de comportements et animation procédurale

Le §6 fournit le rig, la FSM, le regard, les groupes et la navigation. Cette section
écrit **ce que les agents font** — c'est elle qui produit littéralement « ils
discutent, ils travaillent ».

### 7.1 — Vocabulaire d'animation

Le principe qui manque totalement au fichier actuel : **anticipation → action →
récupération**. Aucun mouvement réel ne démarre à vitesse maximale. Avant de saisir une
tasse, la main recule de 2 cm ; après l'avoir posée, elle dépasse légèrement puis
revient. C'est le premier principe de l'animation Disney et c'est ce qui sépare un
geste d'une translation.

```js
/* ---------------- ANIM TOOLKIT ---------------- */
function easeInOut(x){ return x * x * (3 - 2 * x); }                  /* smoothstep */
function pulse(x){ return Math.sin(Math.min(1, Math.max(0, x)) * Math.PI); }

/* courbe one-shot avec anticipation et overshoot :
   0 → -antAmp (recul) → 1+ovAmp (dépassement) → 1 (repos) */
function shot(x, antAmp, ovAmp){
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  if (x < 0.18) return -antAmp * pulse(x / 0.18);                    /* anticipation */
  const y = (x - 0.18) / 0.82;
  return easeInOut(y) * (1 + ovAmp * Math.sin(Math.min(1, y * 1.6) * Math.PI));
}

/* ressort amorti : pour les réactions (sursaut, rire, hochement sec) */
function makeSpring(freq, damping){
  return { v: 0, x: 0, f: freq, d: damping,
    tick(target, dt){
      const k = this.f * this.f;
      this.v += (k * (target - this.x) - 2 * this.d * this.f * this.v) * dt;
      this.x += this.v * dt;
      return this.x;
    } };
}

/* Un OneShot = une animation jouée une fois, pilotée par le tick 60 Hz.
   `apply(k, buf, a)` reçoit la progression 0→1 et écrit dans le tampon de pose. */
function playShot(a, dur, apply){
  a.shots.push({ t: 0, dur: dur, apply: apply });
}
function shotsLayer(a, buf, dt){
  for (let i = a.shots.length - 1; i >= 0; i--){
    const s = a.shots[i];
    s.t += dt;
    const k = Math.min(1, s.t / s.dur);
    s.apply(k, buf, a);
    if (k >= 1) a.shots.splice(i, 1);
  }
}
```

`a.shots = []` à l'initialisation de chaque agent. **Maximum 2 one-shots simultanés par
agent** — au-delà, ignore la demande : des gestes empilés produisent du bruit, pas de
la vie.

### 7.2 — Gestes de parole (beat gestures)

Quand un agent est `group.speaker`, ses mains battent la mesure. Huit gestes, chacun
une fonction `(k, buf, a)` :

```js
/* amplitude générale des gestes, modulée par le babil (§7.10) */
const GESTURES = [
  /* 1. main droite qui présente, paume ouverte */
  { dur: 1.4, fn: (k, b) => { const p = pulse(k);
      addPose(b, { shoulderR: { x: -0.85 * p, z: 0.35 * p },
                   elbowR: { x: -0.50 * p }, wristR: { z: 0.4 * p } }, 1); } },
  /* 2. index qui ponctue : trois petits coups */
  { dur: 1.1, fn: (k, b) => { const p = pulse(k) * Math.abs(Math.sin(k * 9.42));
      addPose(b, { shoulderR: { x: -0.95 * pulse(k) },
                   elbowR: { x: -0.9 * pulse(k) + p * 0.25 } }, 1); } },
  /* 3. les deux mains qui écartent (« voilà le truc ») */
  { dur: 1.6, fn: (k, b) => { const p = pulse(k);
      addPose(b, { shoulderL: { x: -0.7 * p, z: -0.45 * p },
                   shoulderR: { x: -0.7 * p, z:  0.45 * p },
                   elbowL: { x: -0.35 * p }, elbowR: { x: -0.35 * p } }, 1); } },
  /* 4. haussement d'épaules */
  { dur: 1.2, fn: (k, b) => { const p = pulse(k);
      addPose(b, { chest: { y: 0 }, shoulderL: { z: -0.22 * p },
                   shoulderR: { z: 0.22 * p }, head: { z: 0.10 * p } }, 1); } },
  /* 5. main sur la poitrine (« moi, personnellement ») */
  { dur: 1.5, fn: (k, b) => { const p = pulse(k);
      addPose(b, { shoulderR: { x: -1.15 * p, z: -0.30 * p },
                   elbowR: { x: -1.45 * p } }, 1); } },
  /* 6. main qui balaie latéralement */
  { dur: 1.3, fn: (k, b) => { const p = pulse(k);
      addPose(b, { shoulderR: { x: -0.8 * p, y: 0.6 * Math.sin(k * Math.PI * 2) * p },
                   elbowR: { x: -0.4 * p } }, 1); } },
  /* 7. compter sur ses doigts : coude haut, poignet qui marque 3 temps */
  { dur: 1.8, fn: (k, b) => { const p = pulse(k);
      const beat = Math.abs(Math.sin(k * 9.42)) * p;
      addPose(b, { shoulderL: { x: -1.0 * p }, elbowL: { x: -1.2 * p },
                   wristL: { x: -0.3 * beat } }, 1); } },
  /* 8. tête qui s'incline avec la main qui tourne (« tu vois ? ») */
  { dur: 1.2, fn: (k, b) => { const p = pulse(k);
      addPose(b, { head: { z: 0.14 * p },
                   shoulderR: { x: -0.7 * p }, elbowR: { x: -0.6 * p },
                   wristR: { y: 1.2 * Math.sin(k * Math.PI * 2) * p } }, 1); } }
];

function queueSpeechGesture(a){
  let gi = (Math.random() * GESTURES.length) | 0;
  if (gi === a.lastGesture) gi = (gi + 1) % GESTURES.length;   /* jamais 2× le même */
  a.lastGesture = gi;
  const g = GESTURES[gi];
  playShot(a, jit(g.dur, 0.25), (k, buf) => g.fn(k, buf, a));
}

/* dans tickConverse() : le locuteur gesticule toutes les 1,8 à 4 s */
function tickConverse(a, dtT, t){
  if (a.gestureQueue){ a.gestureQueue = false; queueSpeechGesture(a); }
  if (a.group && a.group.speaker === a){
    a.gestureT -= dtT;
    if (a.gestureT <= 0){ queueSpeechGesture(a); a.gestureT = jit(2.8, 0.45); }
  }
}
```

### 7.3 — Écoute active

Les auditeurs d'un groupe ne sont pas immobiles :

```js
function listenerLayer(a, buf, ac, dtT){
  if (!a.group || a.group.speaker === a) return;

  /* hochements : déclenchés pendant les pauses du locuteur (gapT > 0)
     ou aléatoirement toutes les 4 à 9 s */
  a.nodT -= dtT;
  if ((a.group.gapT > 0 && Math.random() < 0.5) || a.nodT <= 0){
    playShot(a, 0.9, (k, b) => {
      const p = pulse(k) * Math.abs(Math.sin(k * 6.28));
      addPose(b, { head: { x: 0.11 * p }, neck: { x: 0.05 * p } }, 1);
    });
    a.nodT = jit(6.0, 0.45);
  }

  /* changement de posture toutes les 8 à 20 s : report de poids,
     bras croisés, penché en avant */
  a.postureT -= dtT;
  if (a.postureT <= 0){
    a.postureT = jit(13, 0.5);
    a.posture = (a.posture + 1 + ((Math.random() * 2) | 0)) % 3;
  }
  /* les trois postures d'écoute, mélangées en douceur */
  a.postureK = damp(a.postureK === undefined ? 0 : a.postureK, 1, 0.05, dtT);
  const P = LISTEN_POSTURES[a.posture];
  addPose(buf, P, a.postureK);
}
const LISTEN_POSTURES = [
  /* poids sur une jambe, bassin décalé */
  { pelvis: { z: 0.05 }, chest: { z: -0.04 }, hipL: { x: 0.06 } },
  /* bras croisés (approximation : coudes très fléchis, épaules internes) */
  { shoulderL: { x: -0.55, z: 0.55 }, shoulderR: { x: -0.55, z: -0.55 },
    elbowL: { x: -1.55 }, elbowR: { x: -1.55 }, chest: { x: 0.03 } },
  /* penché vers le locuteur, tête légèrement inclinée */
  { chest: { x: 0.08 }, spine: { x: 0.05 }, head: { z: 0.08 } }
];
```

Quand `a.posture` change, remets `a.postureK = 0` pour que la nouvelle posture s'installe
en fondu (~1 s), pas d'un coup.

**Le rire collectif** (branché sur `group.laughing` de §6.7) :

```js
function laughLayer(a, buf, ac){
  const L = a.group ? a.group.laughing : 0;
  if (L <= 0) return;
  /* chaque agent rit avec SA phase : le rire est synchronisé à ±300 ms, pas exact */
  const lp = Math.max(0, L - a.seed % 0.3);
  const sh = Math.sin(ac * 14) * lp;
  addPose(buf, {
    chest: { x: 0.10 * lp + sh * 0.02 },
    head:  { x: -0.14 * lp },
    shoulderL: { z: -0.06 * lp }, shoulderR: { z: 0.06 * lp }
  }, 1);
}
```

### 7.4 — Auto-contact

Une fois toutes les 15 à 40 s, un agent se touche : nuque, lunettes, cheveux, mains
frottées, tasse tournée. Gain de crédibilité énorme pour un coût minime. Le modèle
complet — les autres suivent le même patron :

```js
/* se gratter la nuque : LE geste d'auto-contact modèle */
function scratchNeck(a){
  playShot(a, 2.2, (k, buf) => {
    if (k < 0.25){                        /* lever la main vers la nuque */
      const p = easeInOut(k / 0.25);
      addPose(buf, { shoulderR: { x: -2.15 * p, z: 0.55 * p },
                     elbowR: { x: -2.35 * p },
                     head: { z: 0.06 * p, x: 0.05 * p } }, 1);
    } else if (k < 0.75){                 /* gratter : 3 petits mouvements */
      const s = Math.sin((k - 0.25) * 18.85);
      addPose(buf, { shoulderR: { x: -2.15, z: 0.55 },
                     elbowR: { x: -2.35 + s * 0.10 },
                     head: { z: 0.06, x: 0.05 } }, 1);
    } else {                              /* redescendre, avec un léger overshoot */
      const p = 1 - easeInOut((k - 0.75) / 0.25);
      addPose(buf, { shoulderR: { x: -2.15 * p, z: 0.55 * p },
                     elbowR: { x: -2.35 * p },
                     head: { z: 0.06 * p, x: 0.05 * p } }, 1);
    }
  });
}

const SELF_TOUCH = [scratchNeck, adjustGlasses, rubHands, turnCup, fixHair];
function selfTouchTick(a, dtT){
  a.selfT -= dtT;
  if (a.selfT > 0) return;
  a.selfT = jit(26, 0.5);                       /* 13 à 39 s */
  if (a.shots.length === 0)                     /* jamais par-dessus un autre geste */
    SELF_TOUCH[(Math.random() * SELF_TOUCH.length) | 0](a);
}
```

Écris `adjustGlasses` (main vers le visage, 1,4 s — réservé aux agents qui ont des
lunettes), `rubHands` (les deux mains se rejoignent devant le torse et se frottent,
1,8 s), `turnCup` (assis seulement : la main pivote la tasse d'un quart de tour sur la
table, 1,6 s), `fixHair` (main qui remonte le long de la tempe, 1,3 s) sur ce même
patron trois-phases : approche 25 % / action 50 % / retour 25 %.

### 7.5 — ★ Le barista qui travaille

`index.html:992-998` — aujourd'hui deux sinus (`:1460-1462`). On remplace par une
**boucle de travail lisible** : le spectateur doit pouvoir dire ce que fait le barista
depuis l'autre bout de la pièce.

#### Props nécessaires (positions cohérentes avec le comptoir à `(2.7, 1.09, -3.6)`)

| Prop | Position | Géométrie |
|---|---|---|
| Moulin | `(2.05, 1.30, -3.72)` | Cylindre 0.09 + trémie conique |
| Porte-filtre | dans la main, sinon `(2.30, 1.14, -3.60)` | Cylindre plat 0.045 + poignée |
| Tamper | `(2.30, 1.16, -3.42)` | Cylindre 0.03 + pommeau |
| Machine (existante) | `(3.5, 1.34, -3.65)` | inchangée |
| Chiffon | `(2.42, 1.13, -3.38)` | `bevelBox(.14,.02,.10)` |
| Tasse en cours | `(3.30, 1.16, -3.45)` | comme les mugs existants |

Le barista est **derrière** le comptoir, à `(2.55, 0, -4.30)` (position existante),
face au sud (`yaw ≈ π`).

#### La boucle en 5 temps

```js
const BARISTA = { GRIND:0, TAMP:1, PULL:2, SERVE:3, IDLE:4 };

function tickWork(a, dtT, t){
  if (a.onEnter){ a.wPhase = BARISTA.GRIND; a.wT = 0; a.wDur = jit(4.5, 0.2); }
  a.wT += dtT;
  const done = a.wT >= a.wDur;

  switch (a.wPhase){
    case BARISTA.GRIND:
      /* penché vers le moulin, le bras droit oscille (il verse / tasse le grain) */
      a.gaze = { pos: [2.05, 1.35, -3.72] };
      if (done) next(BARISTA.TAMP, jit(2.6, 0.2));
      break;
    case BARISTA.TAMP:
      /* 2 pressions verticales franches, AVEC anticipation */
      if (a.onPhaseEnter){
        /* deux pressions dans UN one-shot : coup à k∈[0,0.45], pause, coup à k∈[0.55,1] */
        playShot(a, 2.2, (k, buf) => {
          const kk = k < 0.45 ? k / 0.45 : k < 0.55 ? 0 : (k - 0.55) / 0.45;
          const press = kk > 0 ? shot(kk, 0.35, 0.15) : 0;   /* recul puis impact */
          addPose(buf, { shoulderR: { x: -1.1 - press * 0.5 },
                         elbowR: { x: -0.6 + press * 0.45 },
                         chest: { x: press * 0.10 } }, 1);
        });
      }
      a.gaze = { pos: [2.30, 1.10, -3.42] };
      if (done) next(BARISTA.PULL, jit(15, 0.2));  /* l'extraction prend 12-18 s */
      break;
    case BARISTA.PULL:
      /* la machine travaille : le barista se redresse, regarde la salle,
         essuie le comptoir — c'est SA fenêtre de comportements libres */
      if (a.wT < 2){ a.gaze = { pos: [3.5, 1.4, -3.65] }; }
      else {
        /* essuyage : un one-shot circulaire toutes les ~5 s */
        a.wipeT = (a.wipeT || 0) - dtT;
        if (a.wipeT <= 0){
          a.wipeT = jit(5.5, 0.4);
          playShot(a, 2.4, (k, buf) => {
            const p = pulse(k);
            addPose(buf, { chest: { x: 0.14 * p },
                           shoulderR: { x: -0.9 * p,
                                        y: Math.sin(k * 12.5) * 0.35 * p },
                           elbowR: { x: -0.5 * p } }, 1);
          });
        }
        /* sinon : regard libre vers la salle (le système de gaze fait le reste) */
      }
      if (done) next(BARISTA.SERVE, jit(3.2, 0.2));
      break;
    case BARISTA.SERVE:
      /* se tourne vers le comptoir client, fait glisser la tasse, un hochement */
      if (a.onPhaseEnter){
        playShot(a, 2.6, (k, buf) => {
          if (k < 0.4){ const p = easeInOut(k / 0.4);
            addPose(buf, { chest: { y: -0.5 * p },
                           shoulderR: { x: -0.85 * p }, elbowR: { x: -0.3 * p } }, 1);
          } else if (k < 0.7){                       /* la glissade de la tasse */
            const p = (k - 0.4) / 0.3;
            addPose(buf, { chest: { y: -0.5 },
                           shoulderR: { x: -0.85, y: -0.5 * p },
                           elbowR: { x: -0.3 } }, 1);
            if (a.serveCup) a.serveCup.position.x = 3.30 - p * 0.55;
          } else { const p = 1 - easeInOut((k - 0.7) / 0.3);
            addPose(buf, { chest: { y: -0.5 * p },
                           shoulderR: { x: -0.85 * p } }, 1);
            addPose(buf, { head: { x: 0.08 * pulse((k - 0.7) / 0.3) } }, 1); /* hochement */
          }
        });
      }
      if (done) next(BARISTA.IDLE, jit(6, 0.6));
      break;
    case BARISTA.IDLE:
      /* interstitiels : ranger des tasses, consulter le téléphone, saluer.
         Un au hasard, puis retour au début de la boucle. */
      if (a.onPhaseEnter){
        const r = Math.random();
        if (r < 0.4)      stackCups(a);
        else if (r < 0.7) checkPhone(a);
        else              waveAtDoor(a);
      }
      if (done) next(BARISTA.GRIND, jit(4.5, 0.2));
      break;
  }
  a.onPhaseEnter = false;
  function next(ph, dur){ a.wPhase = ph; a.wT = 0; a.wDur = dur; a.onPhaseEnter = true; }
}
```

**Posture de base du barista pendant `GRIND`** (couche L0, pas un one-shot) : penché de
12° vers le moulin, bras droit à −0,9 rad, le bras oscille à `fbm1(ac, 2.1, seed) * 0.15`
— jamais un sinus nu.

Écris `stackCups` (3 allers-retours main droite entre `(2.05, 1.16, -3.45)` et une pile
qui monte), `checkPhone` (main gauche à hauteur du sternum, tête baissée dessus, 4 s),
`waveAtDoor` (bras levé bref + regard vers `W.DOOR`, 1,2 s) sur le patron du §7.4.

### 7.6 — ★ Le client qui travaille sur son portable

L'archétype « en train de travailler » demandé. Assis à la table gauche
(`W.SEAT_L2`, la chaise à `(-3.5, -2.4)` face à la fenêtre), un laptop devant lui.

#### Le prop laptop

```js
function makeLaptop(x, y, z, ry){
  const g = new THREE.Group();
  const base = new THREE.Mesh(bevelBox(.30, .012, .21, .003),
    stdMat(0x2a2c30, 0.5, 0.6, 1.1));
  g.add(base);
  const lid = new THREE.Mesh(bevelBox(.30, .20, .008, .003),
    stdMat(0x2a2c30, 0.5, 0.6, 1.1));
  lid.position.set(0, .10, -.105); lid.rotation.x = -0.32;
  g.add(lid);
  /* écran émissif : nourrit le bloom ET éclaire le visage */
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(.27, .17),
    new THREE.MeshStandardMaterial({ color: 0x0a0c10,
      emissive: 0xbfd8ff, emissiveIntensity: 1.6, roughness: 1 }));
  screen.position.set(0, .10, -.099); screen.rotation.x = -0.32;
  g.add(screen);
  /* la lueur sur le visage : un PointLight faible, portée courte.
     (RectAreaLight est INTERDIT ici — cf. §0.6 : pas d'UniformsLib en r134.) */
  const glow = new THREE.PointLight(0xbfd8ff, 0.30, 0.9, 2);
  glow.position.set(0, .16, .12);
  g.add(glow);
  g.position.set(x, y, z); g.rotation.y = ry;
  scene.add(g);
  return g;
}
/* sur le bord de la table gauche (centre (-2.7,-2.4), r 0.7, plateau y≈0.80),
   face à la chaise existante à (-3.5,-2.4) qui regarde vers +x */
const laptop = makeLaptop(-3.22, 0.815, -2.40, -Math.PI / 2);
```

#### Le comportement

```js
const WORKER = { TYPE:0, THINK:1, SCROLL:2, SIP:3, STRETCH:4 };

function tickLaptopWork(a, dtT){
  if (a.onEnter){ a.kPhase = WORKER.TYPE; a.kT = 0; a.kDur = jit(9, 0.4); }
  a.kT += dtT;

  switch (a.kPhase){
    case WORKER.TYPE:
      a.typing = true;
      a.gaze = { obj: a.laptop };
      if (a.kT >= a.kDur){
        a.typing = false;
        const r = Math.random();
        nextK(a, r < 0.35 ? WORKER.THINK : r < 0.6 ? WORKER.SCROLL :
                 r < 0.85 ? WORKER.SIP : WORKER.STRETCH);
      }
      break;
    case WORKER.THINK:
      /* main au menton, regard qui monte en haut à gauche — le cliché est
         un cliché parce qu'il est vrai */
      if (a.onPhaseEnter){
        playShot(a, 1.2, (k, buf) => {
          const p = easeInOut(Math.min(1, k * 2));
          addPose(buf, { shoulderR: { x: -1.7 * p }, elbowR: { x: -1.9 * p },
                         head: { z: -0.06 * p } }, 1);
        });
        a.gaze = { pos: [-4.5, 2.4, -3.4] };       /* en haut à gauche */
      }
      if (a.kT >= a.kDur) nextK(a, WORKER.TYPE);
      break;
    case WORKER.SCROLL:
      /* un seul avant-bras actif, petits mouvements du poignet */
      a.gaze = { obj: a.laptop };
      if (a.kT >= a.kDur) nextK(a, WORKER.TYPE);
      break;
    case WORKER.SIP:  sipCycle(a); if (a.kT >= a.kDur) nextK(a, WORKER.TYPE); break;
    case WORKER.STRETCH:
      if (a.onPhaseEnter){
        playShot(a, 2.8, (k, buf) => {
          const p = pulse(k);
          addPose(buf, { chest: { x: -0.16 * p },
                         shoulderL: { x: -2.6 * p, z: -0.3 * p },
                         shoulderR: { x: -2.6 * p, z: 0.3 * p },
                         head: { x: -0.2 * p } }, 1);
        });
        /* le soupir : le torse enfle puis retombe, via la couche respiration */
        a.sigh = 1.5;
      }
      if (a.kT >= a.kDur) nextK(a, WORKER.TYPE);
      break;
  }
  a.onPhaseEnter = false;
}
function nextK(a, ph){
  a.kPhase = ph; a.kT = 0; a.onPhaseEnter = true;
  a.kDur = ph === WORKER.TYPE ? jit(9, 0.4) :
           ph === WORKER.THINK ? jit(4, 0.4) :
           ph === WORKER.SCROLL ? jit(5, 0.4) :
           ph === WORKER.SIP ? 3.4 : 3.0;
}

/* la frappe : couche continue, PAS un one-shot */
function typingLayer(a, buf, ac){
  if (!a.typing) return;
  /* avant-bras posés, quasi immobiles ; seuls les poignets vibrent,
     à deux fréquences différentes (les deux mains ne tapent pas ensemble) */
  addPose(buf, {
    shoulderL: { x: -0.62 }, shoulderR: { x: -0.62 },
    elbowL: { x: -0.95 },    elbowR: { x: -0.95 },
    wristL: { x: -0.12 + Math.sin(ac * 21.7) * 0.055 },
    wristR: { x: -0.12 + Math.sin(ac * 24.3 + 1.3) * 0.055 },
    chest: { x: 0.09 },      head: { x: 0.14 }
  }, 1);
  /* pauses de frappe : 1 seconde sur 6 environ, les poignets s'arrêtent */
  if (Math.sin(ac * 0.9) > 0.86){ /* les mains s'immobilisent naturellement
     parce que le sinus des poignets est multiplié par 0 — implémente via un
     facteur: */ }
}
```

> Implémente la pause de frappe proprement : un facteur
> `typeAmp = smoothstep(Math.sin(ac * 0.9) < 0.86)` qui multiplie les deux termes
> `Math.sin(ac * 21.x)`. Pendant la pause, la tête se relève légèrement (+0,06 rad).
> C'est le micro-comportement qui fait « il réfléchit à sa phrase ».

### 7.7 — ★ Les groupes qui discutent

Mise en scène des deux groupes définis en §6.7, avec leurs rôles :

**`G_STAND`** — 3 personnes debout à `(-1.10, 0, -3.40)` :

| Membre | Archétype | Particularité |
|---|---|---|
| A | Le raconteur | `rateMul` haut (0.95–1.10), gestes amples (×1.2), parle 45 % du temps (pondère le tirage du speaker en sa faveur ×1.8). |
| B | L'approbateur | Hoche 2× plus souvent (`nodT` base 3 s), bras croisés (posture 1 dominante). |
| C | Le distrait | Regarde ailleurs 30 % du temps (poids `AMBIENT` ×3), consulte son téléphone une fois par minute (one-shot `checkPhone`). |

**`G_TABLE`** — 2 personnes assises à la table de droite `(2.3, -1.6)` :
l'une est **la personne qui boit** existante (déplacée ici), l'autre **le lecteur**
existant — qui lève les yeux de son livre quand l'autre parle (le gaze `SPEAKER` fait
ça tout seul), et tourne une page toutes les ~40 s (§7.8).

L'événement de rire (§6.7) touche les deux groupes indépendamment. Pendant un rire de
`G_STAND`, si la caméra est en plan `gameplay` et qu'aucune parole de Simon n'est en
cours, c'est le **moment idéal pour un plan `reaction`** de 1,5 s (§5.2) — mais
uniquement si `speaking` est faux : ne coupe jamais la cinématique de Simon pour un
PNJ.

### 7.8 — Les autres comportements

**Le cycle de gorgée** — remplace le sinus de `index.html:1463-1465`. Quatre phases,
jamais une oscillation :

```js
function sipCycle(a){
  if (a.shots.length) return;
  playShot(a, 3.4, (k, buf) => {
    if (k < 0.22){          /* saisir : la main descend vers la tasse */
      const p = easeInOut(k / 0.22);
      addPose(buf, { shoulderR: { x: -0.55 * p }, elbowR: { x: -0.45 * p } }, 1);
      if (a.cup && p > 0.9) a.cupHeld = true;
    } else if (k < 0.45){   /* porter : la tasse monte aux lèvres */
      const p = easeInOut((k - 0.22) / 0.23);
      addPose(buf, { shoulderR: { x: -0.55 - 0.75 * p },
                     elbowR: { x: -0.45 - 1.15 * p },
                     head: { x: 0.06 * p } }, 1);
    } else if (k < 0.62){   /* boire : immobile, la tête bascule à peine */
      addPose(buf, { shoulderR: { x: -1.30 }, elbowR: { x: -1.60 },
                     head: { x: 0.10 } }, 1);
    } else {                /* reposer, avec un overshoot léger */
      const p = 1 - easeInOut((k - 0.62) / 0.38);
      addPose(buf, { shoulderR: { x: -1.30 * p + (p > 0.9 ? 0.04 : 0) },
                     elbowR: { x: -1.60 * p }, head: { x: 0.10 * p } }, 1);
      if (a.cupHeld && p < 0.1){ a.cupHeld = false; }
    }
    /* la tasse suit la main pendant cupHeld */
    if (a.cup && a.cupHeld){
      a.rig.J.wristR.getWorldPosition(a.cup.position);
      a.cup.position.y -= 0.03;
    }
  });
}
```

**Tourner une page** (le lecteur) : toutes les 30–55 s, la main gauche traverse le
livre en 0,9 s avec une petite rotation du poignet, et le mesh `pages`
(`index.html:1019-1021`) fait un flip de `rotation.y` sur 0,25 s au moment du passage.

**Commander au comptoir** (`ORDER`) : l'agent arrive à `W.COUNTER`, regarde le tableau
de menu **au-dessus du comptoir** (`gaze = {pos: [2.7, 2.42, -4.96]}`) pendant 3 à 5 s
— détail hyper-crédible — puis regarde le barista, un geste de parole court, attend en
micro-balancements (`fbm1` sur `pelvis.z`, amplitude 0,02), reçoit un hochement du
barista, repart.

**Entrer et chercher une place** : à l'entrée (`SPAWN` → `WALK_TO ENTRY`), l'agent
marque une pause de 1,5 s en `IDLE` avec trois fixations successives (table gauche,
comptoir, table droite) avant de choisir sa destination. C'est un one-shot de regard
pur qui « vend » l'intentionnalité.

### 7.9 — La marche

Remplace `index.html:1453-1458` dans le cadre du nouveau rig.

**La règle qui empêche le glissement** : vitesse, longueur et fréquence de pas sont
couplées. `fréquence = vitesse / longueur_de_pas`. Ne les fixe jamais indépendamment.

```js
function walkLayer(a, buf, ac, dt){
  const v = a.vel.length();
  const walkK = damp(a.walkK || 0, Math.min(1, v / 0.25), 0.12, dt);
  a.walkK = walkK;
  if (walkK < 0.02) return;

  const stepLen = 0.52 * (a.rig.root.scale.x);        /* m par pas */
  a.walkPhase = (a.walkPhase || 0) + (v / stepLen) * dt * Math.PI;
  const p = a.walkPhase;

  const s  = Math.sin(p), c = Math.cos(p);
  addPose(buf, {
    hipL:  { x:  s * 0.50 }, hipR:  { x: -s * 0.50 },
    /* le genou se plie en phase de passage, jamais en contact */
    kneeL: { x: Math.max(0, -c) * 0.75 }, kneeR: { x: Math.max(0, c) * 0.75 },
    /* contre-rotation épaules vs bassin */
    pelvis:{ y:  s * 0.08 },
    chest: { y: -s * 0.12 },
    shoulderL: { x: -s * 0.35 }, shoulderR: { x: s * 0.35 },
    elbowL: { x: -0.25 - Math.max(0, s) * 0.25 },
    elbowR: { x: -0.25 + Math.min(0, s) * 0.25 },
    /* léger tangage de tête, COMPENSÉ : le regard reste stable */
    head:  { z: s * 0.025, y: 0 }
  }, walkK);

  /* rebond vertical à 2× la fréquence des pas */
  a.rig.root.position.y = Math.abs(Math.sin(p)) * 0.022 * walkK;

  footLock(a, 'L', p / (Math.PI * 2), buf);           /* §6.12 */
  footLock(a, 'R', p / (Math.PI * 2) + 0.5, buf);
}
```

Le tangage de tête compensé (`head.z` faible + regard stable via la couche gaze qui
vient APRÈS et corrige) reproduit la stabilisation vestibulo-oculaire : les humains
stabilisent leur regard en marchant, leur tête tangue mais leurs yeux non.

### 7.10 — ★ Babil audio spatialisé

Le son des conversations de fond. Vérifié en r134 : `THREE.AudioListener`,
`THREE.PositionalAudio`, `THREE.Audio`, `THREE.AudioLoader` sont tous dans le build.

#### Architecture

```js
/* Le listener sur la caméra — créé mais PAS branché avant le geste utilisateur */
const audioListener = new THREE.AudioListener();
camera.add(audioListener);

const audioLoader = new THREE.AudioLoader();
let roomTone = null;
const babbles = [];

function startAmbience(){
  /* room tone : lit stéréo global, pas positionnel */
  roomTone = new THREE.Audio(audioListener);
  audioLoader.load('audio/amb/roomtone.mp3', buf => {
    roomTone.setBuffer(buf); roomTone.setLoop(true);
    roomTone.setVolume(0.16); roomTone.play();
  });
  /* un babil positionnel par groupe */
  groups.forEach((g, i) => {
    const pa = new THREE.PositionalAudio(audioListener);
    audioLoader.load('audio/amb/babble' + (i % 2 + 1) + '.mp3', buf => {
      pa.setBuffer(buf); pa.setLoop(true);
      pa.setRefDistance(1.1);        /* volume plein à 1,1 m */
      pa.setRolloffFactor(2.2);      /* décroît vite : on ne comprend pas les mots */
      pa.setVolume(0.55);
      pa.play();
    });
    const anchor = new THREE.Object3D();
    anchor.position.set(g.center[0], 1.45, g.center[2]);
    anchor.add(pa);
    scene.add(anchor);
    babbles.push({ pa: pa, group: g, analyser: null });
  });
}
```

**Geste utilisateur** : `AudioContext` exige une interaction. Le clic « Take a seat »
(`index.html:1415-1421`) est le point d'entrée — appelle `startAmbience()` dedans,
après le `speak(...)` existant. `THREE.AudioListener` crée son propre contexte
(`listener.context`) ; s'il est `suspended`, fais `audioListener.context.resume()` dans
ce même handler.

#### Ducking : le babil s'efface quand Simon parle

```js
function updateAmbienceDucking(dt){
  /* -18 dB ≈ ×0.125 */
  const duckTarget = speaking ? 0.125 : 1.0;
  ambDuck = damp(ambDuck === undefined ? 1 : ambDuck, duckTarget, 0.10, dt);
  if (roomTone && roomTone.isPlaying) roomTone.setVolume(0.16 * ambDuck);
  for (let i = 0; i < babbles.length; i++){
    if (babbles[i].pa.isPlaying) babbles[i].pa.setVolume(0.55 * ambDuck);
  }
}
```

#### L'astuce forte : l'amplitude du babil pilote la gestuelle

Audio et animation corrélés gratuitement — le locuteur du groupe gesticule **sur** le
babil qu'on entend :

```js
/* un AnalyserNode par babil, branché une fois le buffer chargé */
function attachBabbleAnalyser(b){
  const ctx = audioListener.context;
  b.analyser = ctx.createAnalyser();
  b.analyser.fftSize = 64;
  b.data = new Uint8Array(b.analyser.frequencyBinCount);
  /* PositionalAudio expose son gain via getOutput() */
  b.pa.getOutput().connect(b.analyser);
}
function babbleAmplitude(b){
  if (!b.analyser) return 0.5;
  b.analyser.getByteFrequencyData(b.data);
  let s = 0;
  for (let i = 1; i < 12; i++) s += b.data[i];
  return Math.min(1, s / (11 * 140));
}
/* dans la couche de gestes du speaker : multiplier l'amplitude des poses
   par 0.5 + babbleAmplitude(groupBabble) * 0.8 */
```

#### Fichiers

| Fichier | Contenu | Durée | Poids cible |
|---|---|---|---|
| `audio/amb/roomtone.mp3` | Fond de salle neutre (vaisselle lointaine, frigo) | 30–45 s en boucle | ≤ 300 Ko |
| `audio/amb/babble1.mp3` | Murmure de conversation à 2-3 voix, **inintelligible** | 25–40 s | ≤ 300 Ko |
| `audio/amb/babble2.mp3` | Variante, timbres différents | 25–40 s | ≤ 300 Ko |
| `audio/amb/machine.mp3` | Sifflement de percolateur | 4 s, one-shot | ≤ 80 Ko |

**Budget total ambiance : ≤ 1 Mo.** Chargés uniquement via `AudioLoader` **après** le
clic d'entrée — donc zéro impact sur le chargement initial. Le commanditaire fournit
les fichiers ; s'ils n'existent pas au moment de l'implémentation, le code doit
**dégrader en silence** (test `onError` du loader, pas d'exception).

Le sifflement `machine.mp3` se joue en `PositionalAudio` à la position de la machine,
déclenché par la phase `PULL` du barista (§7.5) : le son et l'animation racontent la
même chose — c'est exactement le genre de cohérence qui fait « vrai lieu ».

### 7.11 — Table récapitulative du casting

| Agent | Archétype | Position initiale | État initial | Boucle | LOD priorité |
|---|---|---|---|---|---|
| Barista | Travailleur fixe | `(2.55, 0, -4.30)` | `WORK` | Moudre → tasser → extraire → servir → interstitiel | Haute (toujours visible) |
| Laptop worker | Travailleur assis | chaise `(-3.5, 0, -2.4)` | `SEATED` + laptop | Frapper → réfléchir → scroller → gorgée → étirement | Haute |
| Raconteur (A) | Debout, `G_STAND` | slot 0 du groupe | `CONVERSE` | Parle beaucoup, gestes amples | Moyenne |
| Approbateur (B) | Debout, `G_STAND` | slot 1 | `CONVERSE` | Hoche, bras croisés | Moyenne |
| Distrait (C) | Debout, `G_STAND` | slot 2 | `CONVERSE` | Regarde ailleurs, téléphone | Moyenne |
| Buveuse | Assise, `G_TABLE` | chaise `(3.0, 0, -1.6)` | `CONVERSE` | Gorgées + écoute | Haute (près du cadre) |
| Lecteur | Assis, `G_TABLE` | 2e position table droite | `CONVERSE` | Lit, lève les yeux, tourne les pages | Haute |
| Passant (pool ×2) | Client de passage | `OUTSIDE` | `SPAWN` différé (45–120 s) | Entre → cherche → commande → repart | Basse |

Le passant est ce qui remplace les deux « walkers » actuels : au lieu de deux rails
permanents, des **visites** épisodiques avec un but lisible.

### 7.12 — Anti-patterns — la liste noire

L'IA d'implémentation doit vérifier son propre code contre cette liste. Chaque entrée
est un bug, même si « ça a l'air de marcher » :

1. **Un sinus nu sur `t` global** dans une animation d'agent. → `agentClock` + fbm.
2. **Deux agents avec la même phase ou la même fréquence.** → §6.10.
3. **Un demi-tour sur place.** → `LEAVE` par la porte, §6.8.
4. **Des pieds qui glissent** pendant la marche. → couplage vitesse/fréquence §7.9 + footLock §6.12.
5. **Un regard fixe droit devant** pendant plus de 5 s. → le gaze réévalue toutes les 1,4–5 s.
6. **Des mains figées** pendant que l'agent parle. → beat gestures §7.2.
7. **Une boucle parfaitement périodique** (la même durée deux fois de suite). → `jit()` partout.
8. **Un agent qui traverse un meuble.** → `OBSTACLES` §6.8.
9. **Un geste qui démarre à vitesse max.** → `shot()` avec anticipation §7.1.
10. **Un rire parfaitement synchronisé** dans un groupe. → offset par `a.seed`, §7.3.
11. **Une tasse qui flotte** pendant la gorgée. → `cupHeld` + suivi du poignet, §7.8.
12. **Un `new` dans un tick.** → pool + scratch vectors préalloués.

### Critères d'acceptation

- [ ] Le barista exécute la boucle complète en 30–40 s et chaque phase est
      **identifiable à l'œil** sur une capture d'écran par phase (penché-moulin /
      pression verticale / redressé-essuie / glisse la tasse / interstitiel).
- [ ] Le sifflement machine (si le fichier existe) part **pendant** la phase `PULL`.
- [ ] Le laptop worker a un cycle où la frappe **s'interrompt** (pauses visibles des
      poignets) et où il lève la tête pendant `THINK`.
- [ ] L'écran du laptop éclaire le visage : vérifie que le `PointLight` du laptop
      change la luminance du mesh crâne (capture avec/sans).
- [ ] Dans `G_STAND`, le raconteur gesticule quand `__groups()[0].speaker` est lui, et
      les deux autres hochent la tête dans les 2 s qui suivent un changement de tour.
- [ ] Un éclat de rire visible se produit dans chaque groupe au moins une fois par
      minute, et les trois têtes ne basculent **pas** exactement en même temps.
- [ ] La gorgée est un cycle en 4 phases : sur un enregistrement de 10 s, la tasse
      monte, s'immobilise aux lèvres, redescend — jamais d'oscillation.
- [ ] La tasse suit la main pendant la gorgée (distance poignet-tasse < 6 cm durant
      toute la phase portée).
- [ ] Le passant, quand il apparaît : pause à l'entrée avec 3 fixations, file
      d'attente, regard au menu **puis** au barista, sortie par la porte. Jamais de
      demi-tour dans le cadre.
- [ ] Le babil est inaudible pendant que Simon parle (`ambDuck < 0.15` en 1 s) et
      revient après (`> 0.9` en 2 s).
- [ ] Fichiers audio absents → aucune exception, la scène tourne en silence.
- [ ] Les 12 anti-patterns de §7.12 sont vérifiés un par un, avec la méthode indiquée
      dans chaque section référencée.

---

## 8. HUD, voix de Simon, performance et recette

### 8.1 — Refonte du HUD

**Ce qui dégage** — tout le chrome « web app 2024 » :

| Élément | Ligne | Problème |
|---|---|---|
| `.pill` / `.lang` en pilules + `backdrop-filter` | `72-85` | `border-radius: 999px` + blur = vocabulaire SaaS, pas jeu. |
| `.sign` en Caveat penchée | `59-64` | Enseigne mignonne — remplacée par un carton de mission (§8.5). |
| `.howto` carte modale, 6 emoji | `125-136`, `161-163` | Mur de texte. Remplacé §8.3. |
| `.prompt` flottant en Caveat | `120-123` | Remplacé par un prompt d'action condensé. |

**Ce qui arrive** — typo condensée capitales, ombre dure 1 px, aucun conteneur :

```css
/* ---------------- HUD AAA ---------------- */
.hud-txt{font-family:"Archivo Narrow","Space Grotesk",sans-serif;
  text-transform:uppercase;letter-spacing:.12em;
  color:#fff;text-shadow:1px 1px 0 #000;}

.tools{position:fixed;top:calc(16px + env(safe-area-inset-top));
  right:calc(16px + env(safe-area-inset-right));z-index:70;
  display:flex;gap:18px;align-items:center;}
.hbtn{background:none;border:0;padding:4px 2px;cursor:pointer;
  font:600 13px/1 "Archivo Narrow","Space Grotesk",sans-serif;
  text-transform:uppercase;letter-spacing:.14em;
  color:rgba(255,255,255,.72);text-shadow:1px 1px 0 #000;transition:color .15s;}
.hbtn:hover,.hbtn.active{color:#f4b740;}
.hbtn:focus-visible{outline:2px solid #f4b740;outline-offset:3px;}
.hsep{width:1px;height:14px;background:rgba(255,255,255,.35);}

.prompt{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));
  transform:translateX(-50%);z-index:20;pointer-events:none;
  font:600 14px/1 "Archivo Narrow","Space Grotesk",sans-serif;
  text-transform:uppercase;letter-spacing:.16em;
  color:#fff;text-shadow:1px 1px 0 #000;white-space:nowrap;animation:none;}
.prompt b{color:#f4b740;font-weight:600;}
```

```html
<div class="tools">
  <button class="hbtn" id="cvBtn" aria-expanded="false" aria-controls="cv-text">Text résumé</button>
  <span class="hsep"></span>
  <button class="hbtn active" id="lang-en" lang="en">EN</button>
  <button class="hbtn" id="lang-fr" lang="fr">FR</button>
</div>
<div class="prompt" id="prompt"><b>[CLIC]</b>&nbsp; Examiner le CV</div>
```

> Le JS de `VC` (`index.html:353-373`) manipule `classList 'active'` sur `#lang-en` /
> `#lang-fr` et le texte de `#cvBtn` : les ids et les classes ci-dessus sont
> **compatibles tels quels**. Ne touche pas au JS de `VC`. Vérifie visuellement le
> focus clavier après la refonte : les `outline` remplacent les anneaux des pilules.

Le prompt devient contextuel :

| Contexte | Texte (EN) |
|---|---|
| Rien de survolé | `[HOVER] examine the résumé` |
| Feuille survolée, zone active | `[CLICK] listen — work experience` |
| Simon survolé | `[CLICK] off the record 🍺` → sans emoji : `[CLICK] off the record` |
| Cinématique | *(masqué par `body.cine`)* |

### 8.2 — Typographie et note de conformité

**Une seule famille ajoutée** : **Archivo Narrow** (SIL OFL) — condensée, neutre,
excellente en capitales, 2 graisses suffisent (400, 600). Alternative acceptable :
**Barlow Condensed** (OFL aussi). À télécharger en `.woff2` latin + latin-ext, déposer
dans `fonts/`, déclarer dans `fonts.css` sur le modèle des trois familles existantes,
et précharger la graisse 600 dans le `<head>` comme les autres
(`index.html:42-44`).

**Interdictions strictes** — cette page publique et indexée porte le nom réel d'une
personne et sert à la faire embaucher ; le *trade dress* de Rockstar est protégé et
activement défendu :

- La police **Pricedown** (le logo GTA) et tout clone (« Pricedown Bl », etc.).
- La minimap avec le **tracé GPS rose/violet** caractéristique.
- Les **étoiles de recherche** en bandeau.
- Les écrans **WASTED / BUSTED** — la formulation ET le traitement (zoom + noir et
  blanc + texte serif étiré).
- Le logo, le mot-marque « GTA », les noms de lieux (Los Santos, Vinewood, Del Perro…).

**Autorisé sans réserve** : la *grammaire* — étalonnage, objectif, letterbox,
sous-titres sans fond, cartons de mission, minimap générique, pourcentage de
complétion, typo condensée. Personne ne possède un langage formel. La cible est « on
dirait un jeu AAA moderne », jamais « c'est GTA ». Un recruteur qui reconnaît
l'inspiration sourit ; un recruteur qui voit une contrefaçon s'interroge sur le
jugement du candidat.

### 8.3 — Onboarding diégétique

La modale `.howto` (`index.html:161-163`, rendue par `renderHowto()` `:1407-1413`)
est un mur de texte. On la remplace par un onboarding joué :

1. **Écran d'entrée minimal** : fond noir, titre `VIRTUAL COFFEE` (Archivo Narrow 600,
   64 px, capitales), sous-titre `un café avec Simon Goffin`, un seul bouton
   `PRENDRE PLACE`. Pas de liste d'instructions.
2. **Au clic** : le bouton disparaît, la caméra joue une **poussée d'entrée** de 2,5 s
   (de `(1.9, 1.74, 2.34)` — le plan `wide` — vers le plan `gameplay`, en fondu
   `damp`), pendant que Simon dit son `welcome` existant.
3. **Le geste s'apprend par l'action** : à la fin de la poussée, le prompt contextuel
   (§8.1) s'affiche. Premier survol de la feuille → le rack focus (§5.7) attire l'œil.
   Aucune explication écrite n'est nécessaire : la MAP fait le tutoriel.
4. La ligne `📄 In a hurry?` survit sous forme d'un lien discret sous le bouton
   d'entrée : `— pressé ? version texte —` qui appelle `openCV()`.

> ⚠️ **Le clic sur `#enterBtn` est le geste utilisateur qui débloque l'audio**
> (`index.html:1415-1421` : il appelle `speak(...)`, et §7.10 y ajoute
> `startAmbience()`). Le nouveau bouton `PRENDRE PLACE` doit conserver **le même id**
> `enterBtn` et le même handler. Ne déplace pas cette responsabilité sur un autre
> événement — un `pointermove` ne compte pas comme geste pour l'AudioContext.

`renderHowto()` et l'objet `HOWTO` (`index.html:1375-1406`) se simplifient : garde
`title`, `btn`, `welcome` ; supprime `steps` / `stepsTouch`.

### 8.4 — Minimap fonctionnelle

Un canvas 2D de 180 px, bas-gauche, plan du café vu de dessus. **Cliquable** : chaque
blip de section déclenche `selectSection(key)` — un élément de HUD parodique qui rend
un vrai service de navigation.

```html
<canvas id="minimap" width="180" height="180"></canvas>
```

```css
#minimap{position:fixed;left:calc(16px + env(safe-area-inset-left));
  bottom:calc(16px + env(safe-area-inset-bottom));z-index:21;
  width:140px;height:140px;border-radius:50%;
  border:2px solid rgba(255,255,255,.55);cursor:pointer;
  background:rgba(10,14,18,.78);}
body.cine #minimap{opacity:0;transition:opacity .3s;}
@media(max-width:640px){ #minimap{width:104px;height:104px;} }
```

```js
/* ---------------- MINIMAP ---------------- */
const mmCanvas = document.getElementById('minimap');
const mmCtx = mmCanvas.getContext('2d');
/* Blips : les 7 sections + about, disposés en arc autour de Simon */
const MM_BLIPS = [
  { key:'intro',          a: -1.9 }, { key:'experience',     a: -1.25 },
  { key:'education',      a: -0.6 }, { key:'skills',         a:  0.05 },
  { key:'certifications', a:  0.7 }, { key:'languages',      a:  1.35 },
  { key:'contact',        a:  2.0 }, { key:'about',          a:  2.75 }
];
const heard = new Set(JSON.parse(localStorage.getItem('vc:heard') || '[]'));

function worldToMap(x, z, out){
  /* la pièce visible : x ∈ [-5, 5], z ∈ [-5, 1.8] → canvas 180×180 */
  out[0] = (x + 5) / 10 * 180;
  out[1] = (z + 5) / 6.8 * 180;
}
const _mp = [0, 0];
function drawMinimap(){
  const c = mmCtx;
  c.clearRect(0, 0, 180, 180);
  c.save();
  /* rotation avec le yaw caméra : le haut de la carte = devant la caméra */
  c.translate(90, 90);
  const camYaw = Math.atan2(
    camLook.x - camera.position.x, camLook.z - camera.position.z);
  c.rotate(camYaw + Math.PI);
  c.translate(-90, -90);

  /* murs */
  c.strokeStyle = 'rgba(255,255,255,.35)'; c.lineWidth = 2;
  c.strokeRect(8, 8, 164, 148);
  /* comptoir */
  c.fillStyle = 'rgba(255,255,255,.18)';
  worldToMap(1.1, -3.98, _mp); c.fillRect(_mp[0], _mp[1], 58, 12);
  /* tables : 3 cercles */
  [[0, -0.15, 16], [-2.7, -2.4, 12], [2.3, -1.6, 10]].forEach(tb => {
    worldToMap(tb[0], tb[1], _mp);
    c.beginPath(); c.arc(_mp[0], _mp[1], tb[2], 0, 7); c.stroke();
  });
  /* agents : points blancs */
  c.fillStyle = 'rgba(255,255,255,.8)';
  agents.forEach(a => {
    if (a.lod === 3) return;
    worldToMap(a.pos.x, a.pos.z, _mp);
    c.beginPath(); c.arc(_mp[0], _mp[1], 2.4, 0, 7); c.fill();
  });
  /* Simon : le point jaune central */
  worldToMap(0, -1.08, _mp);
  c.fillStyle = '#f4b740';
  c.beginPath(); c.arc(_mp[0], _mp[1], 5, 0, 7); c.fill();
  /* le visiteur */
  worldToMap(camera.position.x, camera.position.z, _mp);
  c.fillStyle = '#fff';
  c.beginPath(); c.arc(_mp[0], _mp[1], 3.5, 0, 7); c.fill();

  /* blips de section : losanges autour de Simon */
  MM_BLIPS.forEach(b => {
    const bx = 90 + Math.cos(b.a) * 62, by = 78 + Math.sin(b.a) * 58;
    b._x = bx; b._y = by;                     /* mémorisé pour le hit-test */
    c.save(); c.translate(bx, by); c.rotate(Math.PI / 4);
    c.fillStyle = b.key === current ? '#f4b740'
                : heard.has(b.key) ? 'rgba(120,220,160,.9)'
                : 'rgba(255,255,255,.85)';
    c.fillRect(-4, -4, 8, 8);
    c.restore();
  });
  c.restore();
}
/* hit-test : inverse la rotation, cherche le blip le plus proche */
mmCanvas.addEventListener('click', e => {
  const r = mmCanvas.getBoundingClientRect();
  const scale = 180 / r.width;
  let mx = (e.clientX - r.left) * scale, my = (e.clientY - r.top) * scale;
  const camYaw = Math.atan2(
    camLook.x - camera.position.x, camLook.z - camera.position.z) + Math.PI;
  const dx = mx - 90, dy = my - 90;
  mx = 90 + dx * Math.cos(-camYaw) - dy * Math.sin(-camYaw);
  my = 90 + dx * Math.sin(-camYaw) + dy * Math.cos(-camYaw);
  let best = null, bd = 18 * 18;
  MM_BLIPS.forEach(b => {
    const d = (b._x - mx) ** 2 + (b._y - my) ** 2;
    if (d < bd){ bd = d; best = b; }
  });
  if (best){
    if (best.key === 'about') selectAbout();
    else selectSection(best.key);
  }
});
```

Redessine la minimap **à 10 Hz** (dans `behaviourTick`), pas à 60 : un canvas 2D
redessiné à chaque frame coûte plus cher que tout le reste du HUD.

### 8.5 — Progression

La boucle de feedback absente : rien ne dit aujourd'hui au visiteur ce qu'il a écouté
ni ce qui reste.

```css
.mission{position:fixed;left:0;top:22vh;z-index:23;pointer-events:none;
  transform:translateX(-110%);transition:transform .55s cubic-bezier(.16,1,.3,1);
  padding:10px 26px 10px calc(18px + env(safe-area-inset-left));
  background:linear-gradient(90deg,rgba(0,0,0,.88),rgba(0,0,0,0));}
.mission.on{transform:translateX(0);}
.mission .m1{font:600 12px/1 "Archivo Narrow",sans-serif;letter-spacing:.22em;
  text-transform:uppercase;color:#f4b740;text-shadow:1px 1px 0 #000;}
.mission .m2{font:600 26px/1.15 "Archivo Narrow",sans-serif;letter-spacing:.06em;
  text-transform:uppercase;color:#fff;text-shadow:1px 1px 0 #000;margin-top:4px;}
.mission .m3{font:400 13px/1.3 "Archivo Narrow",sans-serif;color:rgba(255,255,255,.75);
  text-shadow:1px 1px 0 #000;margin-top:3px;}
```

```js
const missionEl = /* div.mission injectée au chargement */
function toast(kicker, title, sub, ms){
  missionEl.querySelector('.m1').textContent = kicker;
  missionEl.querySelector('.m2').textContent = title;
  missionEl.querySelector('.m3').textContent = sub || '';
  missionEl.classList.add('on');
  clearTimeout(missionEl._t);
  missionEl._t = setTimeout(() => missionEl.classList.remove('on'), ms || 3200);
}

/* à l'entrée (fin de la poussée caméra §8.3) */
toast('Nouvelle mission', 'Café virtuel', 'Écoutez les 8 sections du CV', 4200);

/* à la fin de chaque section : dans endSpeech(), si un `current` était actif */
function onSectionDone(key){
  if (!key || heard.has(key)) return;
  heard.add(key);
  localStorage.setItem('vc:heard', JSON.stringify([...heard]));
  const pct = Math.round(heard.size / 8 * 100);
  toast('Section terminée', DATA[lang].labels[key] || key, 'Complétion ' + pct + ' %');
  if (heard.size === 8) setTimeout(showCompletion, 2600);
}
```

**À 100 %** : un panneau plein écran sobre — `COMPLÉTION 100 %`, la liste des 8
sections cochées, et **le CTA** : « On prend un vrai café ? » + mailto. Un recruteur
qui atteint 100 % est un recruteur intéressé ; c'est exactement le moment de lui tendre
le contact. Fermeture par clic ou Échap.

### 8.6 — Navigation clavier

`Échap` est déjà pris par le CV texte (`index.html:392-394`). On ajoute :

```js
const KEY_SECTIONS = { '1':'intro', '2':'experience', '3':'education', '4':'skills',
                       '5':'certifications', '6':'languages', '7':'contact',
                       '8':'about', '0':'outro' };
addEventListener('keydown', e => {
  if (!entered) return;
  if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
  if (!document.getElementById('cv-text').hidden) return;   /* le CV texte a la main */
  if (e.key === ' '){ e.preventDefault(); stopSpeaking(); showCue(''); return; }
  const k = KEY_SECTIONS[e.key];
  if (k === 'about') selectAbout();
  else if (k === 'outro') selectSection('outro');
  else if (k) selectSection(k);
});
```

Affiche le mapping dans le HUD : une ligne discrète en bas à droite,
`1-7 sections · 8 off the record · espace silence`, même style `.hud-txt`, masquée en
`body.cine` et sur mobile.

### 8.7 — La bouche de Simon pilotée par l'audio

`index.html:1475-1486` : la bouche bat sur `|sin(t·14)|`, complètement décorrélée de la
voix. L'œil le détecte en une seconde.

**Les deux pièges, avant le code :**

1. `createMediaElementSource(el)` ne peut être appelé qu'**une seule fois par élément**.
   Or `speak()` fait `new Audio(f)` à chaque appel (`index.html:1337`) → un nouvel
   élément à chaque fois, donc pas de conflit. **Ne « réutilise » jamais un audioEl.**
2. L'`AudioContext` doit être créé/repris après un geste utilisateur. Le clic
   `#enterBtn` (§8.3) est ce geste. Toute lecture avant ce clic est impossible de toute
   façon (le how-to couvre l'écran).

```js
/* ---------------- LIPSYNC ---------------- */
let lipCtx = null, lipAnalyser = null, lipData = null, jawOpen = 0;

function attachAnalyser(el){
  if (!lipCtx) lipCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (lipCtx.state === 'suspended') lipCtx.resume();
  const src = lipCtx.createMediaElementSource(el);   /* 1 fois par élément — OK */
  lipAnalyser = lipCtx.createAnalyser();
  lipAnalyser.fftSize = 256;
  lipAnalyser.smoothingTimeConstant = 0.55;
  lipData = new Uint8Array(lipAnalyser.frequencyBinCount);
  src.connect(lipAnalyser);
  lipAnalyser.connect(lipCtx.destination);
}
/* speak() l'appelle déjà via §5.9.a : try { attachAnalyser(audioEl) } catch(_){} */
```

> Si tu utilises aussi `THREE.AudioListener` (§7.10), il crée SON propre contexte.
> Deux contextes coexistent sans problème (limite navigateur ≈ 6). **Le bus de Simon
> reste ce `lipCtx` séparé** ; l'ambiance vit dans `audioListener.context`. Ne fusionne
> pas les deux : `createMediaElementSource` et les buffers positionnels n'ont rien à se
> dire, et la séparation simplifie le ducking (§7.10 lit juste le booléen `speaking`).

```js
/* dans animate(), remplace les lignes 1475-1486 */
let jawTarget = 0;
if (speaking && audioEl && lipAnalyser){
  lipAnalyser.getByteFrequencyData(lipData);
  let s = 0;
  for (let i = 2; i < 26; i++) s += lipData[i];   /* ~90 Hz – 1,1 kHz : la mâchoire */
  jawTarget = Math.min(1, (s / 24) / 105);
} else if (speaking){
  /* repli TTS : pas d'élément média à analyser.
     onboundary (§5.9.b) fournit le rythme des phrases ; entre deux boundaries,
     une pseudo-énergie par caractères fait l'affaire. */
  jawTarget = 0.25 + Math.abs(Math.sin(t * 9.3)) * 0.45;
}
jawOpen += (jawTarget - jawOpen) * Math.min(1, dt * 20);
mouthMesh.scale.y = 1 + jawOpen * 3.2;
mouthMesh.scale.x = 1 - jawOpen * 0.15;          /* la bouche se pince en s'ouvrant */
```

### 8.8 — Expressions de Simon

Simon est le sujet du plan `closeup` (§5.2) : il doit tenir un cadrage serré.

| Expression | Déclencheur | Implémentation |
|---|---|---|
| Sourcils levés | Fin de phrase (nouveau cue de sous-titre, §5.9) | Les deux meshes sourcils (`index.html:1076-1080`) montent de 0,012 en 0,18 s puis redescendent en 0,5 s (petit spring). |
| Sourire au repos | `!speaking` | `mouthMesh.scale.x = 1.25`, `position.y` +0,004 — la bouche au repos remonte légèrement. |
| Acquiescement en parlant | Toutes les 4–7 s pendant `speaking` (jitter) | One-shot 0,8 s : `simonHead.rotation.x` +0,08 en pulse. Remplace l'actuel `sin(t*3.2)*.05` (`index.html:1476`) — un hochement périodique permanent lit comme un bobblehead. |
| Clignement corrélé | Réutilise `blinkLayer` §6.6 avec les paupières du nouveau rig | Supprime le clignement modulo fixe (`t % 3.7`, `index.html:1472-1474`) : il est parfaitement périodique ET écrase les sphères. |
| Regard au visiteur | En parlant : 80 % caméra, 20 % la feuille ou sa tasse | Simon passe dans le système de gaze de §6.6 comme les autres agents, avec des poids spécifiques : `CAMERA w:8` pendant `speaking`. |

**Simon rejoint le système d'agents** pour le regard, le clignement et la respiration
(§6.11) — mais **pas** pour la FSM ni la navigation : il reste assis, piloté par
`speaking`. Concrètement : un agent `simon` avec `state: ST.SEATED` permanent,
`lod: 0` forcé, exclu du pool et des groupes.

### 8.9 — Radio et ambiance : qui possède quel bus

Deux systèmes audio cohabitent. La règle de propriété, pour ne pas empiler deux
duckings concurrents :

| Bus | Contexte | Contenu | Ducking |
|---|---|---|---|
| **Voix de Simon** | `lipCtx` (§8.7) | mp3 des sections + TTS | Jamais ducké. C'est LA priorité. |
| **Monde** | `audioListener.context` (§7.10) | room tone, babils, machine, radio | Ducké à ×0.125 quand `speaking`. |

La radio est un `THREE.Audio` (global, pas positionnel) sur le bus monde :

```js
const STATIONS = [
  { name: 'LOFI.FM',      file: 'audio/amb/radio_lofi.mp3' },
  { name: 'JAZZ CAFÉ',    file: 'audio/amb/radio_jazz.mp3' },
  { name: 'SCRUM FM',     file: 'audio/amb/radio_talk.mp3' },   /* la blague maison */
  { name: 'OFF',          file: null }
];
let radioIdx = 0, radio = null;
function setStation(i){
  radioIdx = i % STATIONS.length;
  if (radio){ radio.stop(); radio = null; }
  const st = STATIONS[radioIdx];
  updateRadioHUD(st.name);
  if (!st.file) return;
  radio = new THREE.Audio(audioListener);
  audioLoader.load(st.file, buf => {
    radio.setBuffer(buf); radio.setLoop(true);
    radio.setVolume(0.14 * ambDuck); radio.play();
  }, undefined, () => { radio = null; });        /* fichier absent : silence */
}
```

Un bouton `.hbtn` « RADIO » dans `.tools` cycle les stations. Le nom de la station
s'affiche 2 s en toast (§8.5, kicker `RADIO`). Le sifflement machine et le room tone
sont déjà spécifiés en §7.10. **Budget total ambiance + radio : ≤ 1,6 Mo, tout chargé
après le clic d'entrée, `AudioLoader` uniquement.**

### 8.10 — Paliers de qualité et sonde

```js
/* ---------------- QUALITY ---------------- */
const QUALITY = (function(){
  const dpr = Math.min(devicePixelRatio || 1, 2);
  const coarse = matchMedia('(pointer: coarse)').matches;
  const small  = Math.min(innerWidth, innerHeight) < 700;
  const gl2    = renderer.capabilities.isWebGL2;
  if (coarse || small || !CAN_DEPTH_TEX)
       return { name:'low',    dpr:1.0,          shadows:1024, bloom:2, dof:false,
                ssao:false, fxaa:true,  agents:3, transmission:false };
  if (!gl2 || dpr < 1.5)
       return { name:'medium', dpr:dpr,          shadows:2048, bloom:3, dof:true,
                ssao:false, fxaa:true,  agents:5, transmission:false };
  return { name:'high',   dpr:dpr,          shadows:2048, bloom:4, dof:true,
                ssao:true,  fxaa:true,  agents:7, transmission:true };
})();
renderer.setPixelRatio(QUALITY.dpr);

/* sonde d'auto-dégradation : FPS moyen sur les 90 frames après l'entrée */
let probeFrames = 0, probeAcc = 0, probed = false;
function fpsProbe(dt){
  if (probed || !entered) return;
  probeFrames++; probeAcc += dt;
  if (probeFrames >= 90){
    probed = true;
    const fps = probeFrames / probeAcc;
    if (fps < 45) degradeOneStep();      /* silencieux : pas de message utilisateur */
  }
}
function degradeOneStep(){
  if (QUALITY.ssao){ QUALITY.ssao = false; return; }
  if (QUALITY.dof){ QUALITY.dof = false; return; }
  if (QUALITY.dpr > 1){ QUALITY.dpr = 1; renderer.setPixelRatio(1); allocTargets(); return; }
  if (QUALITY.bloom > 2){ QUALITY.bloom = 2; return; }
}
```

| Palier | DPR | Ombres | Bloom (mips) | DOF | SSAO | Agents | Transmission |
|---|---|---|---|---|---|---|---|
| `high` | natif ≤ 2 | 2048 | 4 | ✅ | ✅ | 7 | ✅ |
| `medium` | natif | 2048 | 3 | ✅ | ✗ (blobs) | 5 | ✗ |
| `low` | 1.0 | 1024 | 2 | ✗ | ✗ (blobs) | 3 | ✗ |

### 8.11 — Toggle « Réduire les effets »

Bloom + grain + aberration chromatique + DOF déclenchent des gênes réelles (migraines,
photosensibilité) chez une partie du public. Sur un site dont l'unique métier est
« qu'un recruteur lise mon CV », le toggle est **non négociable**.

```js
let fxReduced = localStorage.getItem('vc:fx') === 'off';
function applyFxToggle(){
  const u = compMat.uniforms;
  if (fxReduced){
    u.uGrain.value = 0; u.uCA.value = 0; u.uBarrel.value = 0;
    u.uVig.value = Math.min(u.uVig.value, 0.25);
    QUALITY.dof = false; QUALITY.bloom = Math.min(QUALITY.bloom, 2);
  } else {
    applyGrade(currentGrade);          /* restaure les valeurs du preset */
    /* dof/bloom reviennent au palier détecté */
  }
  localStorage.setItem('vc:fx', fxReduced ? 'off' : 'on');
}
```

Un `.hbtn` « FX » dans `.tools`, état visible (`.active`), persisté. Il s'ajoute à
`prefers-reduced-motion` (§5.11) — les deux sont indépendants : `RM` coupe le
*mouvement*, ce toggle coupe le *traitement d'image*.

### 8.12 — Budget

| Poste | Actuel | Après chantier | Note |
|---|---|---|---|
| `three.min.js` | 615 Ko | 615 Ko | inchangé |
| `index.html` | 86 Ko | ~145 Ko | tout le code ajouté est inline |
| Polices | ~180 Ko | ~230 Ko | +Archivo Narrow 400/600 |
| Voix (mp3) | 4,6 Mo | 4,6 Mo | déjà `new Audio()` à la demande — **rien n'est préchargé** avant le clic |
| Ambiance + radio | 0 | ≤ 1,6 Mo | `AudioLoader` après le clic d'entrée uniquement |
| `og.jpg` | 122 Ko | ~130 Ko | re-rendu §8.14 |
| **Total à l'arrivée sur la page** | | **≤ 1,1 Mo** | html + three + fonts + favicon |
| **Total absolu** | ~5,4 Mo | **≤ 7,3 Mo** | sous le plafond de 8 Mo |

Cibles de chargement : **LCP < 2,5 s en 4G** (c'est le how-to screen, du texte), scène
interactive < 4 s. Les textures procédurales se génèrent en < 350 ms au chargement ;
les normal maps partent en `requestIdleCallback` (§4.2).

### 8.13 — RECETTE DE VALIDATION

La partie la plus importante pour une IA sans yeux. Chaque test donne la commande et le
critère chiffré. Exécute le bloc du lot que tu viens de finir (§9), plus **R0 et R1 à
chaque fois**.

**R0 — Le site fonctionne encore.**
```js
/* console */
!!document.getElementById('cv-text') && typeof VC.textOnly === 'function'
```
Critère : `true`. Puis : ouvrir la page avec `?webgl=off` simulé — dans la console,
`VC.textOnly('test')` → le CV texte devient la page, la bascule EN/FR fonctionne
encore (cliquer FR change les blocs `[data-cvlang]`).

**R1 — Pas de fuite.**
```js
/* console, après 2 min de fonctionnement */
JSON.stringify(renderer.info.memory)   /* noter */
for (let i = 0; i < 50; i++) onResize();
JSON.stringify(renderer.info.memory)   /* re-noter */
```
Critère : `textures` et `geometries` identiques à ±2 avant/après.

**R2 — Passthrough (après L0).** Capture avant modification, capture après avec le
preset `neutral` et tous les effets à zéro. Critère : diff pixel < 1 % (compression
JPEG mise à part). Symptômes de l'échec : image délavée = double gamma ; image sombre
et saturée = encodage manquant.

**R3 — Draw calls (après L4 et L5).**
```js
renderer.info.render.calls
```
Critère : ≤ 260 après L4 ; **≤ 230** après L5 (le hoisting et l'instancing compensent
les props ajoutés).

**R4 — Framerate.**
```js
/* console : moyenne sur 300 frames */
let n=0, t0=performance.now();
const id=setInterval(()=>{ if(++n===300){ clearInterval(id);
  console.log(300000/(performance.now()-t0), 'fps'); } }, 0);
```
Critère : ≥ 55 fps sur le palier détecté, fenêtre 1280×720. Si < 45, la sonde (§8.10)
doit avoir déjà dégradé — vérifie `QUALITY`.

**R5 — Bascule EN/FR en cours de lecture.** Lancer `experience`, attendre 3 s, cliquer
FR. Critère : l'audio s'arrête, aucun sous-titre orphelin (`.subs` vide), le CV 3D
se redessine en FR, aucune exception console.

**R6 — `prefers-reduced-motion`.** Émuler dans le navigateur (DevTools → Rendering).
Critère : caméra immobile (log `camera.position.x` sur 5 s : écart-type < 1e-6), pas
de letterbox, pas de coupes, agents sans locomotion mais **avec** regard lent et
respiration.

**R7 — Mobile portrait.** Viewport 375×812, `pointer: coarse` émulé. Critère : palier
`low`, la feuille se lève au premier tap (`paperLifted`), les sections répondent au
deuxième, minimap réduite, prompts adaptés (`promptTouch`), pas de débordement
horizontal (`document.documentElement.scrollWidth === 375`).

**R8 — Non-synchronisation (après L6).**
```js
const A = __agents();
new Set(A.map(a => a.rateMul)).size === A.length          /* → true */
new Set(A.map(a => Math.round(a.clock * 10))).size === A.length   /* → true */
```
Et le test visuel : capture à t et t+30 s — les postures du groupe `G_STAND` doivent
différer.

**R9 — Le tour de parole.**
```js
/* logger 60 s de __groups()[0].speaker : */
```
Critère : ≥ 8 changements de locuteur en 60 s, jamais deux tours consécutifs du même
membre, `laughing > 0` observé au moins une fois.

**R10 — Audio duck.** Lancer une section pendant que le babil tourne. Critère :
`ambDuck < 0.15` en une seconde, retour `> 0.9` dans les 2 s après `endSpeech()`.

**R11 — Lipsync.** Pendant `experience.mp3` : logger `jawOpen` à 10 Hz sur 10 s.
Critère : variance > 0.02 (ça bouge), ET corrélation temporelle grossière — pendant un
silence de l'enregistrement (il y en a un vers la fin de chaque phrase), `jawOpen`
doit descendre sous 0.15.

**R12 — Progression.** Écouter 2 sections, recharger la page. Critère :
`localStorage['vc:heard']` contient les 2 clés, la minimap les affiche en vert.

**R13 — Clavier.** `1` → `intro` se lance ; `espace` → silence ; `8` → mode bière.
Avec le CV texte ouvert, les chiffres ne doivent PAS déclencher de section.

### 8.14 — Re-rendu de `og.jpg`

Après le changement de DA, l'image de partage actuelle (rendu cartoon, `og.jpg`,
1200×630) ne correspond plus à la page. C'est la **seule** image que verront LinkedIn,
Slack et les aperçus de lien — si elle ne matche pas, l'effet de surprise est perdu au
moment précis où il compte.

Procédure : fenêtre 1200×630, plan `gameplay`, preset `losSantosDay`, letterbox
désactivé, prompt masqué, `renderer.domElement.toDataURL('image/jpeg', 0.85)` depuis la
console, remplacer le fichier. Garder la composition actuelle (Simon centré, CV
visible) : elle fonctionne.

### Critères d'acceptation

- [ ] Plus aucun `border-radius: 999px` ni `backdrop-filter` dans le CSS.
- [ ] `#cvBtn`, `#lang-en`, `#lang-fr` conservent leurs ids et la classe `active` —
      `VC` fonctionne sans modification.
- [ ] Archivo Narrow (ou Barlow Condensed) est auto-hébergée, préchargée, et *aucune*
      règle CSS ne référence Pricedown ni un domaine de fonts externe.
- [ ] Le bouton d'entrée conserve l'id `enterBtn` et déclenche : `entered = true`,
      `speak(welcome)`, `startAmbience()`, la poussée caméra.
- [ ] La minimap est cliquable : un clic sur le blip `experience` lance la section, y
      compris quand la carte a tourné avec la caméra.
- [ ] La recette R0–R13 passe intégralement, chaque test avec son critère chiffré.
- [ ] `og.jpg` re-rendu et poussé avec le reste.

---

## 9. Plan d'exécution global

### 9.1 — Les huit lots

Chaque lot est livrable seul, testable seul, et laisse le site en état de marche. Ne
commence jamais un lot sans avoir validé la recette du précédent (§8.13).

| Lot | Contenu | Sections | Effet attendu à l'écran |
|---|---|---|---|
| **L0** | Socle post-traitement en **passthrough** : RT HDR, quad plein écran, composite qui ne fait que réencoder. Suppression de `.vig` et `.grade`. | §2.3, §2.4, §2.13 | **Image inchangée.** C'est le test. |
| **L1** | Étalonnage + vignettage + grain + dithering dans le composite. | §2.9, §2.10 | Premier choc visuel. |
| **L2** | IBL (`scene.environment`) + `envMapIntensity` par matériau + `clearcoat` sur la table. | §3.4, §3.5, §3.6 | Le plastique disparaît. Deuxième choc. |
| **L3** | Rig de lumière refroidi + ombres retaillées + `normalBias` + brouillard + néon. | §3.2, §3.7–3.10 | Le contraste chaud/froid apparaît. |
| **L4** | Bloom + FXAA + DOF + rack focus + SSAO ou blobs. | §2.5–2.8 | Profondeur et « objectif ». |
| **L5** | Normal/roughness maps, refonte des textures, chanfreins, crasse, fenêtre-portail, props, optimisations. | §4 | Le décor devient matière. |
| **L6** | **Vie de fond** : rig, FSM, regard, groupes, navigation, comportements, babil. | §6, §7 | Le café s'anime. **Le lot le plus visible.** |
| **L7** | Caméra cinématique, letterbox, sous-titres, lipsync, HUD, minimap, progression, radio, paliers, toggle FX. | §5, §8 | La mise en forme finale. |

### 9.2 — Ordre imposé et pourquoi

- **L0 avant tout.** Si le passthrough n'est pas pixel-identique, tu as un problème
  d'espace colorimétrique et **tous** les réglages suivants seront faux. C'est le seul
  test bloquant absolu.
- **L2 avant L3.** Refroidir l'éclairage sans IBL rend la scène terne et tu croiras
  t'être trompé de valeurs.
- **L4 après L2/L3.** Le bloom se règle sur des valeurs HDR : l'éclairage doit être
  définitif, sinon tu règleras le seuil deux fois.
- **L5 après L4.** Les normal maps se jugent sous la lumière finale et avec la DOF.
- **L6 peut se faire en parallèle de L1→L5.** Le système de vie ne dépend d'aucune
  décision de rendu. Si tu travailles en plusieurs passes, c'est le lot à isoler.
- **L7 en dernier.** Le HUD se dessine par-dessus une image finie ; le régler avant,
  c'est le régler deux fois. Exception : le lipsync (§8.7) peut accompagner L6.

### 9.3 — Points d'arrêt obligatoires

1. Après **L0** — R2 (passthrough). Bloquant.
2. Après **L2** — capture : la machine à café a cessé d'être un bloc gris.
3. Après **L4** — R3 (draw calls) et R4 (framerate) par palier.
4. Après **L6** — R8 (non-synchronisation) et R9 (tour de parole).
5. Après **L7** — recette complète R0–R13, y compris R0 (repli sans WebGL), R7
   (mobile portrait) et R6 (`prefers-reduced-motion`).

### 9.4 — Ce qu'il ne faut pas faire

| Interdit | Raison |
|---|---|
| Vendoriser `EffectComposer` et ses passes | Chaque passe est un blit plein écran ; le composite fusionné de §2.9 fait mieux, plus vite, et se règle en un seul endroit. |
| Importer un avatar riggé (`GLTFLoader`) | +4 à 8 Mo, incohérence avec les PNJ procéduraux, rig facial à animer. Hors budget et hors stratégie (§1.3). |
| Un moteur physique | Zéro apport, +200 Ko. La navigation §6.8 se fait au steering. |
| `RectAreaLight` | Inutilisable sans `RectAreaLightUniformsLib` (absent du build, §0.6). |
| Pousser bloom / grain / CA « pour que ça se voie » | Règle : monte jusqu'à ce que l'effet devienne perceptible, puis divise par deux. |
| Reproduire le trade dress Rockstar | §8.2. |
| Régénérer `#cv-text` depuis `DATA` | Le markup statique est ce qu'indexe un robot sans JS 3D. Délibéré (`README.md`). |
| Rendre le CV moins lisible au nom de la DA | DOF sur la feuille, grain sur le texte, letterbox qui rogne : à chaque effet, revérifie la lisibilité. C'est l'unique métier de cette page. |
| Mélanger ancien et nouveau rig de personnage | §6.2. Tout ou rien. |
| Un deuxième système de ducking audio | §8.9 : un seul propriétaire par bus. |

---

## Annexe A — Cartographie de `index.html`

| Plage | Contenu |
|---|---|
| `1-45` | `<head>`, métadonnées de partage, préchargement des polices |
| `46-154` | CSS complet (overlays, enseigne, outils, CV texte, prompt, how-to, media queries) |
| `156-172` | Conteneurs : `#app`, overlays, how-to, enseigne, outils, prompt |
| `174-302` | CV texte statique, EN puis FR |
| `304-420` | Shell `VC` : sonde WebGL, `fontsReady`, langue, panneau CV, `textOnly()` |
| `422` | `<script src="three.min.js">` |
| `424-439` | Ouverture de l'IIFE de la scène et gardes de repli |
| `440-507` | `DATA` (contenu bilingue) et `AUDIO` (chemins mp3) |
| `509-514` | État global : `lang`, `current`, `hoverKey`, `speaking`, `RM`, `TOUCH`, `paperLifted`, `stagingReady` |
| `515-543` | Renderer, scène, caméra, `onResize` |
| `545-722` | Textures procédurales : `ctex`, `speckle`, sol, brique, plâtre, table, vue, menu, tapis, art, glow, shaft |
| `724-765` | Lumières et pendants |
| `767-832` | Pièce : sol, plafond, poutres, murs, plinthes, fenêtre, shafts, poussière, tableaux |
| `834-876` | Zone comptoir : comptoir, plateau, menu, machine, tasses, tabourets |
| `878-928` | Tables, chaises, tapis, plantes |
| `930-1022` | Fabrique `person()` et les cinq PNJ |
| `1024-1175` | Simon : corps, tête, cheveux, lunettes, yeux, bouche, hitbox, tasse, bières, stylo, croissant |
| `1177-1258` | Feuille de CV : canvas, `drawResume()`, zones cliquables, mesh, poses repos/levé |
| `1260-1298` | Raycasting, survol, clic |
| `1300-1356` | Sélection de section, TTS, lecture des mp3 |
| `1358-1372` | Bascule de langue |
| `1374-1421` | Overlay how-to et entrée dans la scène |
| `1423-1521` | Boucle d'animation et fermeture de l'IIFE |

## Annexe B — Symboles existants à ne pas casser

| Symbole | Ligne | Rôle |
|---|---|---|
| `VC` | `316` | Shell hors scène : langue, CV texte, sonde WebGL, `fontsReady`. Survit à l'échec de la 3D. |
| `VC.textOnly(reason)` | `398` | Bascule en mode CV texte seul. Doit rester fonctionnel. |
| `VC.onLang(fn)` / `VC.onOpenCV` | `415-416` | Points d'abonnement de la scène. |
| `DATA` | `441` | Contenu bilingue. Doit rester en phase avec `#cv-text`. |
| `AUDIO` | `494` | Chemins mp3. Clé manquante → TTS : comportement voulu. |
| `RM` / `TOUCH` | `510-511` | Préférences mouvement réduit / pointeur grossier. |
| `maxAniso` | `536` | Anisotropie max, à propager à toute nouvelle texture. |
| `ctex` / `speckle` | `546` / `553` | Fabriques de textures partagées. |
| `speaking` | `509` | Déclencheur de la cinématique (§5) et du lipsync (§8.7). |
| `paperHover` / `paperLifted` | `1263` / `512` | État de la feuille : pilote le rack focus (§5.7). |
| `entered` | `1261` | Passe à `true` au clic d'entrée — le geste qui débloque l'`AudioContext` (§8.3). |
| `applyStaging()` | `1426` | Recadrage portrait/paysage. Doit gérer tous les plans après §5.10. |
| `drawResume()` / `ZONES` | `1187` / `1182` | Redessin de la feuille + zones cliquables. Le picking (`:1283`) en dépend. |
| `selectSection()` / `selectAbout()` | `1302` / `1308` | Points d'entrée des sections — la minimap (§8.4) et le clavier (§8.6) les appellent. |
| `simonHead` / `mouthMesh` | `1054` / `1108` | Remplacés par le rig §6.2 — mais les références dans `pick()` et la boucle doivent être migrées, pas orphelines. |

## Annexe C — Vérification d'API : la méthode

Avant d'utiliser une classe, une propriété ou une constante de three.js :

```bash
grep -c 'NomExact' three.min.js
```

Une occurrence ≥ 1 sur un nom de classe ou de propriété publique signifie qu'elle
existe dans ce build. Zéro occurrence signifie qu'elle n'existe pas — quelle que soit
ta certitude. Le tableau §0.6 couvre les cas déjà audités.

Rappel : r134 date de novembre 2021. Noms r134 à utiliser — et leurs successeurs à ne
**pas** utiliser :

| r134 (correct ici) | Renommé plus tard en (ne pas utiliser) |
|---|---|
| `renderer.outputEncoding` | `outputColorSpace` |
| `THREE.sRGBEncoding` / `LinearEncoding` | `SRGBColorSpace` / `LinearSRGBColorSpace` |
| `renderer.physicallyCorrectLights` | `useLegacyLights` (inversé) |
| `WebGLMultisampleRenderTarget` | option `samples` de `WebGLRenderTarget` |
| `texture.encoding` | `texture.colorSpace` |

Et les classes **absentes** de r134 rencontrées dans ce brief : `CapsuleGeometry`
(r136+), `RoomEnvironment` (examples), `RectAreaLightUniformsLib` (examples),
`EffectComposer` et toutes les passes (examples), `GLTFLoader` (examples).

---

*Brief rédigé à partir d'une lecture intégrale de `index.html` (1 524 lignes), d'une
observation du rendu en cours d'exécution, et d'un audit par grep du contenu réel de
`three.min.js` r134 (§0.6). Document amont : `ART_DIRECTION_GTA5.md`.*




