import json
import math
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Notation d'un projet éolien — 3D", page_icon="🌬️", layout="wide")

# ---------------------------------------------------------------------------
# Données de référence
# ---------------------------------------------------------------------------
PILLARS = [
    {"key": "env", "label": "Environnemental", "color": "#3f7a5c", "criteria": [
        {"id": "biodiversite", "label": "Biodiversité (faune, flore)"},
        {"id": "paysage", "label": "Paysage et patrimoine"},
        {"id": "nuisances", "label": "Nuisances (bruit, ombre)"},
    ]},
    {"key": "eco", "label": "Économique", "color": "#b8863b", "criteria": [
        {"id": "retombees", "label": "Retombées fiscales locales"},
        {"id": "emploi", "label": "Emploi et filière locale"},
        {"id": "rentabilite", "label": "Coût et rentabilité"},
    ]},
    {"key": "soc", "label": "Social", "color": "#3d6b8a", "criteria": [
        {"id": "acceptabilite", "label": "Acceptabilité locale"},
        {"id": "concertation", "label": "Concertation et gouvernance"},
        {"id": "cadre_vie", "label": "Cadre de vie et santé"},
    ]},
]
AXES = [(c["id"], c["label"], p["key"], p["color"]) for p in PILLARS for c in p["criteria"]]
N = len(AXES)
REFERENCE_SCORE = 6
REFERENCE_WEIGHT = 2

# ---------------------------------------------------------------------------
# État (session_state)
# ---------------------------------------------------------------------------
if "project_name" not in st.session_state:
    st.session_state.project_name = ""
for cid, _, _, _ in AXES:
    st.session_state.setdefault(f"score_{cid}", 5)
    st.session_state.setdefault(f"weight_{cid}", 2)
    st.session_state.setdefault(f"comment_{cid}", "")


def threshold_for(weight: int) -> int:
    return 3 + 2 * weight


def interpret(score: int, weight: int):
    t = threshold_for(weight)
    if score >= t:
        return "ok", "Acceptable"
    if score >= t - 2:
        return "watch", "À surveiller"
    return "block", "Point bloquant"


def wedge_volume(radii, heights):
    n = len(radii)
    delta = (2 * math.pi) / n
    total = 0.0
    for i in range(n):
        r1, r2 = radii[i], radii[(i + 1) % n]
        h1, h2 = heights[i], heights[(i + 1) % n]
        total += (0.5 * math.sin(delta) * r1 * r2) * ((h1 + h2) / 2)
    return total


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  .stApp { background:#f6f4ef; }
  h1, h2, h3 { color:#1c2321; }
  .pillar-env { color:#3f7a5c; font-weight:600; font-size:0.82rem; letter-spacing:0.03em; }
  .pillar-eco { color:#b8863b; font-weight:600; font-size:0.82rem; letter-spacing:0.03em; }
  .pillar-soc { color:#3d6b8a; font-weight:600; font-size:0.82rem; letter-spacing:0.03em; }
  .tag-ok { background:rgba(63,122,92,0.16); color:#3f7a5c; padding:2px 8px; border-radius:10px; font-size:0.75rem; }
  .tag-watch { background:rgba(184,134,59,0.18); color:#b8863b; padding:2px 8px; border-radius:10px; font-size:0.75rem; }
  .tag-block { background:rgba(179,58,58,0.16); color:#b33a3a; padding:2px 8px; border-radius:10px; font-size:0.75rem; }
  .synthesis-box { background:rgba(90,110,100,0.08); border:1px solid #dcd8cd; border-radius:6px; padding:12px 14px; }
  @media print {
    header[data-testid="stHeader"], .stToolbar, #MainMenu, footer, .stDownloadButton, .stButton { display:none !important; }
    iframe { border:none !important; }
    .stApp { background:#ffffff !important; }
  }
</style>
""", unsafe_allow_html=True)

st.title("Notation d'un projet éolien — vue 3D")
st.caption("Rayon = note du critère (0–10) · Hauteur (axe Z) = poids d'importance (1–3). "
           "Seuil d'acceptabilité : poids 1 → note ≥ 5 · poids 2 → note ≥ 7 · poids 3 → note ≥ 9.")

st.session_state.project_name = st.text_input("Nom du projet (facultatif)", value=st.session_state.project_name)

# ---------------------------------------------------------------------------
# Mise en page : scène 3D | curseurs
# ---------------------------------------------------------------------------
col_scene, col_sliders = st.columns([1.15, 1])

with col_sliders:
    for p in PILLARS:
        st.markdown(f'<p class="pillar-{p["key"]}">{p["label"]}</p>', unsafe_allow_html=True)
        for c in p["criteria"]:
            cid = c["id"]
            st.markdown(f"**{c['label']}**")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.session_state[f"score_{cid}"] = st.slider(
                    "Note", 0, 10, st.session_state[f"score_{cid}"], key=f"score_slider_{cid}", label_visibility="collapsed")
            with sc2:
                st.session_state[f"weight_{cid}"] = st.slider(
                    "Poids", 1, 3, st.session_state[f"weight_{cid}"], key=f"weight_slider_{cid}", label_visibility="collapsed")
            level, label = interpret(st.session_state[f"score_{cid}"], st.session_state[f"weight_{cid}"])
            st.markdown(f'<span class="tag-{level}">{label} (seuil {threshold_for(st.session_state[f"weight_{cid}"])})</span>',
                        unsafe_allow_html=True)
            st.session_state[f"comment_{cid}"] = st.text_area(
                "Commentaire", value=st.session_state[f"comment_{cid}"],
                key=f"comment_area_{cid}", placeholder="Justifier la note et la pondération…",
                height=68, label_visibility="collapsed")
            st.write("")
    if st.button("Réinitialiser les notes"):
        for cid, _, _, _ in AXES:
            st.session_state[f"score_{cid}"] = 5
            st.session_state[f"weight_{cid}"] = 2
        st.rerun()

# Données courantes
state = {cid: {"score": st.session_state[f"score_{cid}"], "weight": st.session_state[f"weight_{cid}"]} for cid, _, _, _ in AXES}
axes_payload = [{"id": cid, "label": label, "pillar": pillar, "color": color,
                  "score": state[cid]["score"], "weight": state[cid]["weight"]} for cid, label, pillar, color in AXES]

with col_scene:
    HTML_TEMPLATE = r"""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
  html,body{margin:0; padding:0; background:#ffffff;}
  #scene{width:100%; height:440px; display:block; touch-action:none; cursor:grab;}
  #scene:active{cursor:grabbing;}
  .legend{position:absolute; bottom:8px; left:8px; display:flex; gap:10px; font-family:-apple-system,Arial,sans-serif; font-size:11px; color:#5c655f;}
  .legend span{display:flex; align-items:center; gap:4px;}
  .dot{width:8px; height:8px; border-radius:50%; display:inline-block;}
  .wrap{position:relative;}
  #exportBtn{position:absolute; top:8px; right:8px; font-family:-apple-system,Arial,sans-serif; font-size:11px; color:#5c655f; background:#fff; border:1px solid #dcd8cd; border-radius:5px; padding:5px 10px; cursor:pointer;}
  #exportBtn:hover{color:#1c2321; border-color:#5c655f;}
</style></head>
<body>
<div class="wrap">
  <canvas id="scene"></canvas>
  <button id="exportBtn">Exporter l'image (PNG)</button>
  <div class="legend">
    <span><i class="dot" style="background:#3f7a5c"></i>Environnemental</span>
    <span><i class="dot" style="background:#b8863b"></i>Économique</span>
    <span><i class="dot" style="background:#3d6b8a"></i>Social</span>
    <span><i style="display:inline-block;width:14px;height:0;border-top:1.5px dashed #5c655f;"></i>Référence</span>
  </div>
</div>
<script>
const AXES = __AXES__;
const REFERENCE_SCORE = __REF_SCORE__, REFERENCE_WEIGHT = __REF_WEIGHT__;
const n = AXES.length;
const maxR = 90, maxH = 70;

function angleFor(i){ return -Math.PI/2 + (2*Math.PI*i)/n; }
function hexToInt(h){ return parseInt(h.replace('#',''),16); }

function makeTextSprite(text, color, scale){
  const canvas = document.createElement('canvas');
  canvas.width = 128; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  ctx.font = '600 30px -apple-system, Arial, sans-serif';
  ctx.fillStyle = color; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(text, 64, 34);
  const tex = new THREE.CanvasTexture(canvas); tex.minFilter = THREE.LinearFilter;
  const mat = new THREE.SpriteMaterial({ map:tex, transparent:true, depthTest:false });
  const spr = new THREE.Sprite(mat); spr.scale.set(scale, scale/2, 1);
  return spr;
}

function makeAxisLabel(text, color){
  const canvas = document.createElement('canvas');
  canvas.width = 220; canvas.height = 84;
  const ctx = canvas.getContext('2d');
  ctx.font = '600 21px -apple-system, Arial, sans-serif';
  ctx.fillStyle = color; ctx.textAlign='center'; ctx.textBaseline='middle';
  const words = text.split(' ');
  const lines = []; let cur = '';
  words.forEach(w=>{ if((cur+' '+w).trim().length>15){ lines.push(cur.trim()); cur=w; } else { cur=(cur+' '+w).trim(); } });
  if(cur) lines.push(cur);
  const startY = canvas.height/2 - (lines.length-1)*13;
  lines.forEach((ln,i)=> ctx.fillText(ln, canvas.width/2, startY + i*26));
  const tex = new THREE.CanvasTexture(canvas); tex.minFilter = THREE.LinearFilter;
  const mat = new THREE.SpriteMaterial({ map:tex, transparent:true, depthTest:false });
  const spr = new THREE.Sprite(mat); spr.scale.set(38, 38*(84/220), 1);
  return spr;
}

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true, preserveDrawingBuffer:true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42,1,1,2000);
scene.add(new THREE.AmbientLight(0xffffff,0.75));
const dl = new THREE.DirectionalLight(0xffffff,0.6); dl.position.set(120,180,120); scene.add(dl);
const group = new THREE.Group(); scene.add(group);

let radius=380, theta=Math.PI/3.2, phi=Math.PI/2.3;
const target = new THREE.Vector3(-15,20,0);

function resize(){
  const w = canvas.parentElement.clientWidth, h = 440;
  renderer.setSize(w,h,false); camera.aspect = w/h; camera.updateProjectionMatrix();
}
function updateCamera(){
  const x = target.x + radius*Math.sin(phi)*Math.cos(theta);
  const y = target.y + radius*Math.cos(phi);
  const z = target.z + radius*Math.sin(phi)*Math.sin(theta);
  camera.position.set(x,y,z); camera.lookAt(target);
}
resize(); window.addEventListener('resize', resize);

let dragging=false, lastX=0, lastY=0;
canvas.addEventListener('pointerdown', e=>{ dragging=true; lastX=e.clientX; lastY=e.clientY; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e=>{
  if(!dragging) return;
  const dx=e.clientX-lastX, dy=e.clientY-lastY; lastX=e.clientX; lastY=e.clientY;
  theta -= dx*0.006; phi = Math.min(Math.PI-0.15, Math.max(0.2, phi - dy*0.006));
  updateCamera();
});
canvas.addEventListener('pointerup', ()=>{ dragging=false; });
canvas.addEventListener('pointercancel', ()=>{ dragging=false; });
canvas.addEventListener('wheel', e=>{ e.preventDefault(); radius=Math.min(600,Math.max(120,radius+e.deltaY*0.4)); updateCamera(); }, {passive:false});

function rebuild(){
  while(group.children.length) group.remove(group.children[0]);

  for(let ring=1; ring<=5; ring++){
    const r=(maxR/5)*ring;
    const pts=[];
    for(let i=0;i<=n;i++){ const a=angleFor(i%n); pts.push(new THREE.Vector3(r*Math.cos(a),0,r*Math.sin(a))); }
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({color:0xcfc9ba, transparent:true, opacity:0.6})));
    const lbl = makeTextSprite(String(ring*2), '#5c655f', 10);
    lbl.position.set(r*Math.cos(angleFor(0))+6, 1.5, r*Math.sin(angleFor(0)));
    group.add(lbl);
  }
  const zeroLbl = makeTextSprite('0', '#5c655f', 10); zeroLbl.position.set(6,1.5,0); group.add(zeroLbl);

  const gx = -(maxR+30);
  group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(gx,0,0), new THREE.Vector3(gx,maxH,0)]), new THREE.LineBasicMaterial({color:0xcfc9ba, transparent:true, opacity:0.8})));
  [1,2,3].forEach(w=>{
    const h=(w/3)*maxH;
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(gx-4,h,0), new THREE.Vector3(gx+4,h,0)]), new THREE.LineBasicMaterial({color:0x5c655f})));
    const lbl = makeTextSprite(String(w), '#5c655f', 10); lbl.position.set(gx-12,h,0); group.add(lbl);
  });
  const zTitle = makeTextSprite('Poids', '#5c655f', 16); zTitle.position.set(gx, maxH+12, 0); group.add(zTitle);

  const topPts=[];
  AXES.forEach((a,i)=>{
    const ang=angleFor(i);
    const r=(a.score/10)*maxR, h=(a.weight/3)*maxH;
    const x=r*Math.cos(ang), z=r*Math.sin(ang);
    const color = hexToInt(a.color);

    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), new THREE.Vector3(maxR*Math.cos(ang),0,maxR*Math.sin(ang))]), new THREE.LineBasicMaterial({color:0xcfc9ba, transparent:true, opacity:0.6})));
    group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x,0,z), new THREE.Vector3(x,h,z)]), new THREE.LineBasicMaterial({color, linewidth:2})));

    const base = new THREE.Mesh(new THREE.SphereGeometry(2.2,12,12), new THREE.MeshBasicMaterial({color, transparent:true, opacity:0.5}));
    base.position.set(x,0,z); group.add(base);
    const top = new THREE.Mesh(new THREE.SphereGeometry(3.6,16,16), new THREE.MeshStandardMaterial({color, roughness:0.4, metalness:0.05}));
    top.position.set(x,h,z); group.add(top);
    topPts.push(new THREE.Vector3(x,h,z));

    const axisLbl = makeAxisLabel(a.label, a.color);
    axisLbl.position.set((maxR+36)*Math.cos(ang), 2, (maxR+36)*Math.sin(ang));
    group.add(axisLbl);
  });

  const loop = topPts.concat([topPts[0]]);
  group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(loop), new THREE.LineBasicMaterial({color:0x1c2321, transparent:true, opacity:0.55})));

  const refR=(REFERENCE_SCORE/10)*maxR, refH=(REFERENCE_WEIGHT/3)*maxH;
  const refPts=[];
  for(let i=0;i<n;i++){
    const ang=angleFor(i);
    const x=refR*Math.cos(ang), z=refR*Math.sin(ang);
    refPts.push(new THREE.Vector3(x,refH,z));
    const m=new THREE.Mesh(new THREE.SphereGeometry(2.2,10,10), new THREE.MeshBasicMaterial({color:0x8a8f89, transparent:true, opacity:0.65}));
    m.position.set(x,refH,z); group.add(m);
  }
  const refLoop = refPts.concat([refPts[0]]);
  const refMat = new THREE.LineDashedMaterial({color:0x5c655f, dashSize:4, gapSize:3, transparent:true, opacity:0.85});
  const refLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(refLoop), refMat);
  refLine.computeLineDistances(); group.add(refLine);

  const shape = new THREE.BufferGeometry();
  const positions=[];
  for(let i=0;i<n;i++){
    const a=topPts[i], b=topPts[(i+1)%n];
    const a0=new THREE.Vector3(a.x,0,a.z), b0=new THREE.Vector3(b.x,0,b.z);
    positions.push(a0.x,a0.y,a0.z, b0.x,b0.y,b0.z, a.x,a.y,a.z);
    positions.push(b0.x,b0.y,b0.z, b.x,b.y,b.z, a.x,a.y,a.z);
  }
  shape.setAttribute('position', new THREE.Float32BufferAttribute(positions,3));
  shape.computeVertexNormals();
  group.add(new THREE.Mesh(shape, new THREE.MeshBasicMaterial({color:0x5c6b62, transparent:true, opacity:0.10, side:THREE.DoubleSide})));

  updateCamera();
}

function animate(){ requestAnimationFrame(animate); renderer.render(scene, camera); }
rebuild(); animate();

document.getElementById('exportBtn').addEventListener('click', ()=>{
  renderer.render(scene, camera);
  canvas.toBlob(blob=>{
    if(!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'notation-eolien-3d.png';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 'image/png');
});
</script>
</body></html>
"""
    html = (HTML_TEMPLATE
            .replace("__AXES__", json.dumps(axes_payload))
            .replace("__REF_SCORE__", str(REFERENCE_SCORE))
            .replace("__REF_WEIGHT__", str(REFERENCE_WEIGHT)))
    components.html(html, height=460, scrolling=False)

# ---------------------------------------------------------------------------
# Résultats (sous le graphique, comme dans la version 2D)
# ---------------------------------------------------------------------------
st.markdown("---")

avg_cols = st.columns(len(PILLARS))
pillar_averages = {}
for col, p in zip(avg_cols, PILLARS):
    items = [state[c["id"]] for c in p["criteria"]]
    sum_w = sum(i["weight"] for i in items)
    w_avg = sum(i["score"] * i["weight"] for i in items) / sum_w
    pillar_averages[p["key"]] = w_avg
    col.metric(p["label"], f"{w_avg:.1f}/10 pondéré")

proj_radii = [state[cid]["score"] for cid, _, _, _ in AXES]
proj_heights = [state[cid]["weight"] for cid, _, _, _ in AXES]
ref_radii = [REFERENCE_SCORE] * N
ref_heights = [REFERENCE_WEIGHT] * N
vol_proj = wedge_volume(proj_radii, proj_heights)
vol_ref = wedge_volume(ref_radii, ref_heights)
pct = (vol_proj / vol_ref) * 100
diff = pct - 100
st.write(f"**Volume du projet vs référence : {pct:.0f}%** ({'+' if diff >= 0 else ''}{diff:.0f} pts)")

results = [interpret(state[cid]["score"], state[cid]["weight"]) for cid, _, _, _ in AXES]
weights = [state[cid]["weight"] for cid, _, _, _ in AXES]
blocking_critical = sum(1 for (lvl, _), w in zip(results, weights) if lvl == "block" and w == 3)
blocking_all = sum(1 for lvl, _ in results if lvl == "block")
watching = sum(1 for lvl, _ in results if lvl == "watch")

if blocking_critical > 0:
    msg = f"{blocking_critical} critère(s) déterminant(s) (poids 3) sous le seuil : à traiter en priorité avant de poursuivre le projet."
    box = st.error
elif blocking_all > 0:
    msg = f"{blocking_all} critère(s) en point bloquant sur des critères secondaires : à examiner et à sécuriser."
    box = st.warning
elif watching > 0:
    msg = f"Profil globalement acceptable, avec {watching} critère(s) à surveiller de près."
    box = st.info
else:
    msg = "Profil globalement acceptable sur l'ensemble des critères notés."
    box = st.success
box(msg)

# ---------------------------------------------------------------------------
# Export des résultats (texte)
# ---------------------------------------------------------------------------
lines = [f"Notation d'un projet éolien — vue 3D", f"Projet : {st.session_state.project_name or '(sans nom)'}", ""]
for p in PILLARS:
    lines.append(p["label"])
    for c in p["criteria"]:
        cid = c["id"]
        lvl, lbl = interpret(state[cid]["score"], state[cid]["weight"])
        lines.append(f"  - {c['label']} : note {state[cid]['score']}/10, poids {state[cid]['weight']}, "
                     f"seuil {threshold_for(state[cid]['weight'])} → {lbl}")
    lines.append("")
lines.append("Moyennes pondérées par pilier : " + ", ".join(f"{p['label']} {pillar_averages[p['key']]:.1f}/10" for p in PILLARS))
lines.append(f"Volume du projet vs référence : {pct:.0f}% ({'+' if diff >= 0 else ''}{diff:.0f} pts)")
lines.append("")
lines.append(msg)

for p in PILLARS:
    for c in p["criteria"]:
        cid = c["id"]
        cm = st.session_state.get(f"comment_{cid}", "").strip()
        if cm:
            lines.append(f"Commentaire — {c['label']} : {cm}")

col_dl, col_print = st.columns(2)
with col_dl:
    st.download_button(
        "Exporter les résultats (TXT)",
        data="\n".join(lines),
        file_name=f"{(st.session_state.project_name or 'projet-eolien-3d').strip().replace(' ', '-')}-resultats.txt",
        mime="text/plain",
        use_container_width=True,
    )
with col_print:
    components.html("""
        <div style="text-align:center;">
        <button id="printBtn" style="width:100%; font-family:-apple-system,Arial,sans-serif; font-size:14px;
          color:#5c655f; background:#fff; border:1px solid #dcd8cd; border-radius:5px; padding:9px 14px; cursor:pointer;">
          Exporter / imprimer tout (PDF)
        </button>
        </div>
        <script>
        document.getElementById('printBtn').addEventListener('click', function(){
          try { window.parent.print(); } catch(e) { window.print(); }
        });
        </script>
    """, height=46)
st.caption("L'impression (Ctrl/Cmd+P ou le bouton ci-dessus) ouvre la boîte de dialogue du navigateur : "
           "choisissez « Enregistrer au format PDF » pour exporter toute la page, curseurs, scène 3D et commentaires inclus.")
