import streamlit as st
import pandas as pd
import random
import json
import os
import math
import re
import qrcode
import socket
from datetime import datetime, timedelta

# --- 0. FORCER LE MODE NUIT & THÈME VERT AGP ---
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as f:
    f.write('[theme]\nbase="dark"\nprimaryColor="#ed7902"\nbackgroundColor="#051f0d"\nsecondaryBackgroundColor="#020b04"\ntextColor="#f4f7f6"\n')

# --- 1. CONFIGURATION & DESIGN CSS ---
st.set_page_config(page_title="Tournio Pro - AGP", page_icon="🏀", layout="wide", initial_sidebar_state="expanded")

def apply_pro_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700;900&display=swap');
    .stApp { background: radial-gradient(circle at top, #0c3d1b, #031207) !important; background-attachment: fixed !important; }
    [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
    .stDeployButton, [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    footer { display: none !important; }
    
    /* 💻 COMPORTEMENT SUR PC : BARRE VERROUILLÉE OUVERTE */
    [data-testid="stSidebar"] { background-color: #020b04 !important; border-right: 1px solid #0c3d1b !important; }
    @media (min-width: 768px) {
        [data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; transform: translateX(0px) !important; visibility: visible !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        [data-testid="stSidebarResizer"] { display: none !important; }
    }
    
    /* 📱 COMPORTEMENT SUR MOBILE : BARRE RÉTRACTABLE AVEC BOUTON ORANGE */
    @media (max-width: 767px) {
        [data-testid="stSidebarCollapseButton"] { color: #ed7902 !important; display: inline-flex !important; }
    }

    h1, h2, h3, h4, .terrain-badge, .convocation-header, .match-card div, .main-title, .main-date { font-family: 'Oswald', sans-serif !important; }
    .banner-container { background: linear-gradient(180deg, #020b04 0%, #0a3317 100%); border-bottom: 5px solid #ed7902; border-top: 5px solid #136d33; padding: 40px 20px; margin-bottom: 40px; border-radius: 12px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.8); }
    .main-title { font-size: 6vw !important; font-weight: 900 !important; background: linear-gradient(to right, #ffffff, #ed7902); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase; font-style: italic; letter-spacing: 0.15em !important; line-height: 1.1 !important; margin: 0 !important; padding: 0 !important; filter: drop-shadow(4px 4px 5px rgba(0,0,0,0.8)); }
    .main-date { font-size: 1.8vw !important; color: #829b8c !important; font-weight: 700 !important; letter-spacing: 0.5em !important; text-transform: uppercase; margin-top: 15px !important; margin-bottom: 0 !important; }
    .match-card { border-radius: 8px; padding: 20px; margin-bottom: 15px; border-left: 8px solid #ed7902; box-shadow: 0 10px 20px rgba(0,0,0,0.6); transition: transform 0.2s ease; }
    .terrain-badge { padding: 4px 12px; border-radius: 4px; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px; }
    .convocation-header { background: linear-gradient(90deg, #136d33, #0a3317); border-bottom: 4px solid #ed7902; text-transform: uppercase; letter-spacing: 2px; padding: 15px !important; }
    div.stButton > button[kind="primary"] { background-color: #ed7902 !important; color: white !important; border: 2px solid #ed7902 !important; font-family: 'Oswald', sans-serif !important; font-size: 1.2rem !important; letter-spacing: 2px; }
    .version-tag { text-align: right; color: #475569; font-family: 'Oswald', sans-serif; font-size: 0.85rem; opacity: 0.6; margin-top: 30px; padding-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ⚡ NOUVEAU SYSTÈME D'IMPRESSION (Zéro gaspillage)
def bouton_action_export(html_content_to_print, titre="Impression"):
    nom_t = st.session_state.get('nom_tournoi', 'TOURNOI')
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
        body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
        .btn {{ background-color: #ed7902; color: white; border: none; font-family: 'Oswald', sans-serif; font-size: 1.1rem; letter-spacing: 1px; padding: 8px; cursor: pointer; width: 100%; border-radius: 4px; text-transform: uppercase; font-weight: bold; transition: 0.2s; }}
        .btn:hover {{ background-color: #d66d02; }}
        .print-zone {{ display: none; }}
        @media print {{
            body {{ background: white; }}
            .btn {{ display: none; }}
            .print-zone {{ display: block; }}
            table {{ border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; font-size: 11pt; color: black; margin-bottom: 20px; page-break-inside: avoid; }}
            th, td {{ border: 1px solid black; padding: 6px; text-align: center; color: black; }}
            th {{ background-color: #e2e8f0; font-weight: bold; }}
            h2, h3, h4 {{ font-family: Arial, sans-serif; color: black; text-align: center; text-transform: uppercase; margin-top: 10px; margin-bottom: 10px; }}
        }}
    </style>
    </head>
    <body>
        <button class="btn" onclick="window.print()">🖨️ IMPRIMER</button>
        <div class="print-zone">
            <h2>{nom_t}</h2>
            <h3>{titre}</h3>
            {html_content_to_print}
        </div>
    </body>
    </html>
    """
    c1, c2 = st.columns([10, 2])
    with c2:
        st.components.v1.html(html_content, height=45)

apply_pro_theme()

# --- INITIALISATION MODE ADMIN ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
is_admin = st.session_state.is_admin

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close()
        return ip
    except: return "192.168.1.X"

# --- 2. PERSISTANCE & GESTION DES FICHIERS ---
SAVE_DIR = "sauvegardes"
os.makedirs(SAVE_DIR, exist_ok=True)

if "tournoi_id" not in st.session_state:
    st.session_state.tournoi_id = st.query_params.get("id", f"tournoi_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    st.query_params.id = st.session_state.tournoi_id

variables_defaut = { "nom_tournoi": "", "date_tournoi": datetime.now().strftime("%Y-%m-%d"), "nb_equipes": 8, "nb_poules": 2, "nb_terrains": 2, "duree_match": 15, "temps_transition": 5, "heure_debut": "09:00", "heure_pause": "12:00", "duree_pause": 60, "tours_phases_finales": 0, "tournoi_initialise": False, "matchs_poules": {}, "poules": {}, "tournoi_cloture": False, "page_actuelle": "📝 1. INFORMATIONS & ÉQUIPES", "etape1_validee": False }
for i in range(32): variables_defaut[f"n_{i}"] = f"Équipe {i+1}"; variables_defaut[f"j_{i}"] = 5

def charger_depuis_fichier():
    path = os.path.join(SAVE_DIR, f"{st.session_state.tournoi_id}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    if k not in ["is_admin", "page_actuelle"]: st.session_state[k] = v
        except: pass
    for k, v in variables_defaut.items():
        if k not in st.session_state: st.session_state[k] = v

if "init_ok" not in st.session_state:
    charger_depuis_fichier()
    st.session_state.init_ok = True

if not is_admin:
    charger_depuis_fichier()

def sauvegarder_donnees():
    if st.session_state.get("tournoi_initialise"):
        for p, matchs in st.session_state.matchs_poules.items():
            for i, m in enumerate(matchs):
                for suf, key in [("_a", "SA"), ("_b", "SB")]:
                    if f"s_{p}_{i}{suf}" in st.session_state: m[key] = st.session_state[f"s_{p}_{i}{suf}"]
                if f"c_{p}_{i}" in st.session_state: m["cloture"] = st.session_state[f"c_{p}_{i}"]
                if f"fp_{p}_{i}" in st.session_state: m["fairplay"] = st.session_state[f"fp_{p}_{i}"]
                if m.get("is_finale"):
                    for suf, key in [("a", "A"), ("b", "B")]:
                        if f"name_{suf}_{p}_{i}" in st.session_state: m[key] = st.session_state[f"name_{suf}_{p}_{i}"]
    
    data_to_save = {}
    for k, v in st.session_state.items():
        if not str(k).startswith("_") and k not in ["tournoi_id", "init_ok"] and not k.startswith(("lock_slot", "btn_", "print_", "nav_", "spec_", "filtre_", "input_", "hist_")):
            data_to_save[k] = v
            
    id_s = st.session_state.tournoi_id
    with open(os.path.join(SAVE_DIR, f"{id_s}.json"), "w", encoding="utf-8") as f: 
        json.dump(data_to_save, f, indent=4, ensure_ascii=False, default=str)

def generer_tournoi_sectorise():
    liste = [{"nom": st.session_state.get(f"n_{i}", f"Équipe {i+1}"), "joueurs": st.session_state.get(f"j_{i}", 5), "idx_origine": i} for i in range(st.session_state.nb_equipes)]
    random.shuffle(liste)
    poules = {f"Poule {i+1}": [] for i in range(st.session_state.nb_poules)}
    for i, eq in enumerate(liste): poules[f"Poule {(i % st.session_state.nb_poules) + 1}"].append(eq)
    nb_t, nb_p = st.session_state.nb_terrains, st.session_state.nb_poules
    t_p = min(max(1, nb_t // nb_p), 3)
    attr_t, curr_t = {}, 1
    for p in poules:
        fin_t = min(curr_t + t_p - 1, nb_t)
        attr_t[p] = list(range(curr_t, fin_t + 1))
        curr_t = curr_t + t_p if curr_t + t_p <= nb_t else max(1, nb_t - t_p + 1)
    matchs_l = {p: [] for p in poules}
    for p, eqs in poules.items():
        for i in range(len(eqs)):
            for j in range(i + 1, len(eqs)):
                matchs_l[p].append({"A": eqs[i]["nom"], "B": eqs[j]["nom"], "id_A": eqs[i]["idx_origine"], "id_B": eqs[j]["idx_origine"], "SA": 0, "SB": 0, "cloture": False, "poule": p, "attribue": False, "terrains_possibles": attr_t[p], "fairplay": "Aucune", "is_finale": False})
        random.shuffle(matchs_l[p])
    entrelaces = []
    for i in range(max((len(m) for m in matchs_l.values()), default=0)):
        for p in poules:
            if i < len(matchs_l[p]): entrelaces.append(matchs_l[p][i])
    vague, finalises = 0, []
    start_dt, pause_dt = datetime.strptime(st.session_state.heure_debut, "%H:%M"), datetime.strptime(st.session_state.heure_pause, "%H:%M")
    hist_v = {}
    while any(not m["attribue"] for m in entrelaces):
        occupees, terrains_o = set(), set()
        h = vague * (st.session_state.duree_match + st.session_state.temps_transition)
        h_v = start_dt + timedelta(minutes=h)
        if h_v >= pause_dt: h_v += timedelta(minutes=st.session_state.duree_pause)
        j1, j2 = hist_v.get(vague-1, set()), hist_v.get(vague-2, set())
        bannis = j1.intersection(j2)
        for m in entrelaces:
            if not m["attribue"] and m["A"] not in occupees and m["B"] not in occupees and m["A"] not in j1 and m["B"] not in j1:
                t_l = next((t for t in m["terrains_possibles"] if t not in terrains_o), None)
                if t_l: m.update({"attribue": True, "terrain": t_l, "heure": h_v.strftime("%H:%M")}); finalises.append(m); occupees.update([m["A"], m["B"]]); terrains_o.add(t_l)
        for m in entrelaces:
            if not m["attribue"] and m["A"] not in occupees and m["B"] not in occupees and m["A"] not in bannis and m["B"] not in bannis:
                t_l = next((t for t in m["terrains_possibles"] if t not in terrains_o), None)
                if t_l: m.update({"attribue": True, "terrain": t_l, "heure": h_v.strftime("%H:%M")}); finalises.append(m); occupees.update([m["A"], m["B"]]); terrains_o.add(t_l)
        hist_v[vague] = occupees; vague += 1
    st.session_state.matchs_poules = {p: [m for m in finalises if m["poule"] == p] for p in poules}
    matchs_f = {}
    for t in range(st.session_state.tours_phases_finales, 0, -1):
        nom = {4:"Huitièmes de Finale", 3:"Quarts de Finale", 2:"Demi-Finales", 1:"Finale"}.get(t, "Phase Finale")
        m_tour = [{"A": "À définir", "B": "À définir", "SA": 0, "SB": 0, "cloture": False, "poule": nom, "attribue": False, "fairplay": "Aucune", "is_finale": True} for _ in range(2**(t-1))]
        while any(not m["attribue"] for m in m_tour):
            to = set()
            h_v = start_dt + timedelta(minutes=vague * (st.session_state.duree_match + st.session_state.temps_transition))
            if h_v >= pause_dt: h_v += timedelta(minutes=st.session_state.duree_pause)
            for m in m_tour:
                if not m["attribue"]:
                    tl = next((tid for tid in range(1, nb_t + 1) if tid not in to), None)
                    if tl: m.update({"attribue": True, "terrain": tl, "heure": h_v.strftime("%H:%M")}); to.add(tl)
            vague += 1
        matchs_f[nom] = m_tour
    st.session_state.matchs_poules.update(matchs_f)
    st.session_state.poules = poules; st.session_state.tournoi_initialise = True; sauvegarder_donnees()

def changer_page(nouvelle_page): st.session_state.page_actuelle = nouvelle_page; sauvegarder_donnees()
def valider_etape1(): st.session_state.etape1_validee = True; changer_page("⚙️ 2. Logistique")
def generer_et_aller_vers_tournoi(): generer_tournoi_sectorise(); changer_page("🏆 3. Tournoi")

# --- UI ---
titre_affiche = st.session_state.get("nom_tournoi", "AGP TOURNAMENT")
if not titre_affiche.strip(): titre_affiche = "AGP TOURNAMENT"
d_format = datetime.strptime(st.session_state.get("date_tournoi", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").strftime("%d / %m / %Y")

st.markdown(f'''
<div class="banner-container">
    <div class="main-title">{titre_affiche}</div>
    <div class="main-date">
        <span style="color: #ffffff; text-shadow: 0px 0px 8px rgba(255,255,255,0.8); font-size: 0.9em; margin-right: 15px;">★ ★ ★</span>
        {d_format}
        <span style="color: #ffffff; text-shadow: 0px 0px 8px rgba(255,255,255,0.8); font-size: 0.9em; margin-left: 15px;">★ ★ ★</span>
    </div>
</div>
''', unsafe_allow_html=True)

etapes_globales = ["📝 1. INFORMATIONS & ÉQUIPES", "⚙️ 2. Logistique", "🏆 3. Tournoi", "📈 4. Statistiques"]
etapes_debloquees = ["📝 1. INFORMATIONS & ÉQUIPES"]
if st.session_state.get("etape1_validee") or st.session_state.get("tournoi_initialise"): etapes_debloquees.append("⚙️ 2. Logistique")
if st.session_state.get("tournoi_initialise"): etapes_debloquees.extend(["🏆 3. Tournoi", "📈 4. Statistiques"])

# Sécurité Spectateur
if not is_admin and st.session_state.get("page_actuelle") in ["📝 1. INFORMATIONS & ÉQUIPES", "⚙️ 2. Logistique"]: st.session_state.page_actuelle = "🏆 3. Tournoi"
if st.session_state.get("page_actuelle") not in etapes_debloquees: st.session_state.page_actuelle = etapes_debloquees[-1]

with st.sidebar:
    titre_actuel = st.session_state.get("nom_tournoi", "").lower()
    nom_logo = "Logo_AGP_enfant.png" if any(mot in titre_actuel for mot in ["u7", "u9", "u11", "u13", "enfant", "baby", "mini"]) else "Logo_AGP.png"
    chemin_logo = os.path.join("images", nom_logo)
    if not os.path.exists(chemin_logo): chemin_logo = os.path.join("images", "Logo_AGP.png")
    if os.path.exists(chemin_logo): st.image(chemin_logo, use_container_width=True)
    
    st.divider()
    if not is_admin:
        st.info("👁️ **MODE SPECTATEUR**\n\nScores en direct.")
        with st.expander("🔐 CONNEXION ADMIN"):
            mdp = st.text_input("Mot de passe", type="password", key="mdp_admin")
            if st.button("Déverrouiller", use_container_width=True):
                if mdp == "admin": 
                    st.session_state.is_admin = True
                    st.rerun()
                else: st.error("Mot de passe incorrect")
    else:
        st.success("👑 **MODE ADMIN ACTIF**\n\nContrôle total.")
        if st.button("🔒 Verrouiller", use_container_width=True): st.session_state.is_admin = False; st.rerun()
    st.divider()

    st.markdown("### 🗺️ NAVIGATION")
    for etape in etapes_globales:
        if etape in etapes_debloquees:
            if is_admin or etape in ["🏆 3. Tournoi", "📈 4. Statistiques"]:
                if st.button(etape, type="primary" if st.session_state.get("page_actuelle") == etape else "secondary", use_container_width=True, key=f"nav_{etape}"): changer_page(etape); st.rerun()
        else: 
            if is_admin: st.markdown(f"<div style='padding: 5px 15px; color: #475569; border-radius: 5px;'>🔒 {etape.split(' ', 1)[1]}</div>", unsafe_allow_html=True)
    
    if is_admin:
        st.divider()
        st.markdown("### 📱 LIVE STREAM")
        ip_detectee = get_local_ip()
        base_url_input = st.text_input("IP locale", value=f"http://{ip_detectee}:8501", label_visibility="collapsed")
        url_publique = f"{base_url_input.strip('/')}/?id={st.session_state.tournoi_id}"
        try: st.image(qrcode.make(url_publique).convert('RGB'), caption="Scannez ce QR Code !")
        except: pass
        st.divider()
        st.markdown(f'<a href="/?id=tournoi_{datetime.now().strftime("%Y%m%d_%H%M%S")}" target="_blank" style="display: block; text-align: center; background: linear-gradient(90deg, #136d33, #ed7902); color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 900; text-transform: uppercase; border: 1px solid #ed7902;">➕ NOUVEAU TOURNOI</a>', unsafe_allow_html=True)
        st.divider()
        
        st.markdown("### 📜 HISTORIQUE")
        fichiers = sorted([f for f in os.listdir(SAVE_DIR) if f.endswith(".json")], reverse=True)
        opts, lbls = [], {}
        for f in fichiers:
            fid = f.replace(".json", ""); opts.append(fid)
            try:
                with open(os.path.join(SAVE_DIR, f), "r", encoding="utf-8") as tmp:
                    d = json.load(tmp); lbls[fid] = f"{d.get('nom_tournoi', 'Sans nom')} ({d.get('date_tournoi', '')})"
            except: lbls[fid] = fid
        if st.session_state.tournoi_id not in opts: opts.insert(0, st.session_state.tournoi_id); lbls[st.session_state.tournoi_id] = f"✨ {st.session_state.get('nom_tournoi', 'Nouveau Tournoi') or 'Nouveau Tournoi'}"
        
        choix_historique = st.selectbox("Sélectionner :", options=opts, format_func=lambda x: lbls.get(x, x), index=opts.index(st.session_state.tournoi_id), key="hist_select_box", label_visibility="collapsed")
        
        if st.button("📂 Charger ce tournoi", use_container_width=True):
            if choix_historique != st.session_state.tournoi_id:
                st.query_params.id = choix_historique
                was_admin = st.session_state.is_admin
                st.session_state.clear()
                st.session_state.is_admin = was_admin
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        # --- LE BOUTON DE SUPPRESSION EST BIEN LÀ ! ---
        with st.expander("🗑️ Supprimer un tournoi"):
            st.error("⚠️ Cette action est irréversible.")
            if st.button("🚨 OUI, SUPPRIMER", key="btn_del_hist", use_container_width=True):
                chemin_fichier = os.path.join(SAVE_DIR, f"{choix_historique}.json")
                if os.path.exists(chemin_fichier):
                    try:
                        os.remove(chemin_fichier)
                    except: pass
                
                if choix_historique == st.session_state.tournoi_id:
                    was_admin = st.session_state.is_admin
                    st.session_state.clear()
                    st.session_state.is_admin = was_admin
                st.rerun()

verrouille, global_cloture, page_actuelle = st.session_state.get("tournoi_initialise"), st.session_state.get("tournoi_cloture"), st.session_state.get("page_actuelle")

# --- PAGE 1 : INSCRIPTION ---
if page_actuelle == "📝 1. INFORMATIONS & ÉQUIPES" and is_admin:
    st.subheader("📝 ÉTAPE 1 : INFORMATIONS & ÉQUIPES")
    c1, c2 = st.columns(2)
    
    # Petites fonctions silencieuses (Callbacks) pour sauvegarder sans faire planter l'écran
    def update_nom_tournoi():
        st.session_state["nom_tournoi"] = st.session_state["input_nom_tournoi"]
        sauvegarder_donnees()
        
    def update_date_tournoi():
        st.session_state["date_tournoi"] = st.session_state["input_date_tournoi"].strftime("%Y-%m-%d")
        sauvegarder_donnees()

    with c1: 
        st.text_input("Nom du Tournoi *", value=st.session_state.get("nom_tournoi", ""), placeholder="Ex: Tournoi AGP 2026", key="input_nom_tournoi", on_change=update_nom_tournoi)
            
    with c2: 
        d_val = datetime.strptime(st.session_state.get("date_tournoi", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").date()
        st.date_input("Date du Tournoi *", value=d_val, format="DD/MM/YYYY", key="input_date_tournoi", on_change=update_date_tournoi)
            
    st.divider(); st.subheader("👥 ROSTER (ÉQUIPES)")
    
    def update_nb_equipes():
        st.session_state["nb_equipes"] = st.session_state["input_nb_equipes"]
        sauvegarder_donnees()
        
    st.number_input("Nombre d'équipes", 4, 32, value=st.session_state.get("nb_equipes", 8), key="input_nb_equipes", disabled=verrouille, on_change=update_nb_equipes)
    
    # Callbacks pour les équipes
    def update_equipe(idx):
        st.session_state[f"n_{idx}"] = st.session_state[f"input_n_{idx}"]
        sauvegarder_donnees()
        
    def update_joueurs(idx):
        st.session_state[f"j_{idx}"] = st.session_state[f"input_j_{idx}"]
        sauvegarder_donnees()

    for i in range(0, st.session_state.nb_equipes, 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < st.session_state.nb_equipes:
                idx = i + j
                with cols[j]:
                    ca, cb = st.columns([3, 1])
                    ca.text_input(f"Équipe {idx+1}", value=st.session_state.get(f"n_{idx}", f"Équipe {idx+1}"), key=f"input_n_{idx}", on_change=update_equipe, args=(idx,))
                    cb.number_input("Joueurs", 1, 15, value=st.session_state.get(f"j_{idx}", 5), key=f"input_j_{idx}", on_change=update_joueurs, args=(idx,))
                    
    if not st.session_state.get("nom_tournoi", "").strip(): st.warning("⚠️ Renseignez le nom du tournoi.")
    else: st.button("➡️ RETOUR AU TOURNOI" if verrouille else "➡️ ÉTAPE SUIVANTE", type="primary", use_container_width=True, on_click=changer_page if verrouille else valider_etape1, args=("🏆 3. Tournoi",) if verrouille else ())

# --- PAGE 2 : LOGISTIQUE & ESTIMATION ---
elif page_actuelle == "⚙️ 2. Logistique" and is_admin:
    st.subheader("⚙️ ÉTAPE 2 : CONFIGURATION LOGISTIQUE")
    c1, c2 = st.columns(2)
    with c1:
        new_nbt = st.number_input("Terrains", 1, 12, value=st.session_state.get("nb_terrains", 2), key="input_nb_terrains", disabled=verrouille)
        if new_nbt != st.session_state.get("nb_terrains"): st.session_state["nb_terrains"] = new_nbt; sauvegarder_donnees(); st.rerun()
        
        op_p = [1, 2, 4, 8]
        new_nbp = st.selectbox("Poules", op_p, index=op_p.index(st.session_state.get("nb_poules", 2)) if st.session_state.get("nb_poules") in op_p else 1, key="input_nb_poules", disabled=verrouille)
        if new_nbp != st.session_state.get("nb_poules"): st.session_state["nb_poules"] = new_nbp; sauvegarder_donnees(); st.rerun()
        
        new_hd = st.time_input("Début", value=datetime.strptime(st.session_state.get("heure_debut", "09:00"), "%H:%M").time(), key="input_heure_debut", disabled=verrouille)
        if new_hd.strftime("%H:%M") != st.session_state.get("heure_debut"): st.session_state["heure_debut"] = new_hd.strftime("%H:%M"); sauvegarder_donnees(); st.rerun()
        
        of = {"Aucune": 0, "Finale": 1, "Demies+Finale": 2, "Quarts->Finale": 3, "Huitièmes->Finale": 4}
        new_tpf = of[st.selectbox("Phases Finales", list(of.keys()), index=list(of.values()).index(st.session_state.get("tours_phases_finales", 0)), key="input_phases_finales", disabled=verrouille)]
        if new_tpf != st.session_state.get("tours_phases_finales"): st.session_state["tours_phases_finales"] = new_tpf; sauvegarder_donnees(); st.rerun()
        
    with c2:
        new_dm = st.number_input("Match (min)", 5, 60, value=st.session_state.get("duree_match", 15), key="input_duree_match", disabled=verrouille)
        if new_dm != st.session_state.get("duree_match"): st.session_state["duree_match"] = new_dm; sauvegarder_donnees(); st.rerun()
        
        new_tt = st.number_input("Transition (min)", 0, 20, value=st.session_state.get("temps_transition", 5), key="input_temps_transition", disabled=verrouille)
        if new_tt != st.session_state.get("temps_transition"): st.session_state["temps_transition"] = new_tt; sauvegarder_donnees(); st.rerun()
        
        new_hp = st.time_input("Pause Midi", value=datetime.strptime(st.session_state.get("heure_pause", "12:00"), "%H:%M").time(), key="input_heure_pause", disabled=verrouille)
        if new_hp.strftime("%H:%M") != st.session_state.get("heure_pause"): st.session_state["heure_pause"] = new_hp.strftime("%H:%M"); sauvegarder_donnees(); st.rerun()
        
        new_dp = st.number_input("Durée Pause (min)", 0, 120, value=st.session_state.get("duree_pause", 60), key="input_duree_pause", disabled=verrouille)
        if new_dp != st.session_state.get("duree_pause"): st.session_state["duree_pause"] = new_dp; sauvegarder_donnees(); st.rerun()

    eq_p = math.ceil(st.session_state.nb_equipes / st.session_state.nb_poules)
    m_poule = (eq_p * (eq_p - 1)) / 2
    t_poule = max(1, st.session_state.nb_terrains // st.session_state.nb_poules)
    vagues_p = math.ceil(m_poule / t_poule)
    vagues_f = sum(math.ceil((2**(t-1)) / st.session_state.nb_terrains) for t in range(st.session_state.tours_phases_finales, 0, -1))
    vagues_total = vagues_p + vagues_f
    start_dt, pause_dt = datetime.strptime(st.session_state.heure_debut, "%H:%M"), datetime.strptime(st.session_state.heure_pause, "%H:%M")
    min_totaux = (vagues_total * st.session_state.duree_match) + ((vagues_total - 1) * st.session_state.temps_transition)
    fin_dt = start_dt + timedelta(minutes=min_totaux)
    if fin_dt > pause_dt: fin_dt += timedelta(minutes=st.session_state.duree_pause)
    
    st.info(f"⏱️ **ESTIMATION DU TEMPS :**\n- Poules : {vagues_p} créneaux\n- Finales : {vagues_f} créneaux\n🏆 **Fin prévue vers : {fin_dt.strftime('%H:%M')}**")
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn_retour, c_btn_suivant = st.columns(2)
    c_btn_retour.button("⬅️ RETOUR", use_container_width=True, on_click=changer_page, args=("📝 1. INFORMATIONS & ÉQUIPES",))
    c_btn_suivant.button("➡️ ALLER AU TOURNOI" if verrouille else "🚀 GÉNÉRER LE TOURNOI", type="primary", use_container_width=True, on_click=changer_page if verrouille else generer_et_aller_vers_tournoi, args=("🏆 3. Tournoi",) if verrouille else ())

# --- PAGE 3 : TOURNOI ---
elif page_actuelle == "🏆 3. Tournoi":
    if is_admin:
        if global_cloture:
            st.success("🏆 TOURNOI CLÔTURÉ !")
            if st.button("🔓 DÉVERROUILLER LE TOURNOI"): st.session_state.tournoi_cloture = False; sauvegarder_donnees(); st.rerun()
        else:
            if st.button("🏆 CLÔTURER LE TOURNOI", type="primary", use_container_width=True): st.session_state.tournoi_cloture = True; sauvegarder_donnees(); st.rerun()
        
        tbs = st.tabs(["📅 CALENDRIER", "📊 CLASSEMENTS", "📋 PLANNING", "🖨️ TERRAINS"])
        
        with tbs[0]:
            f = st.radio("Filtre", ["Poules", "Finales"], horizontal=True)
            all_m = sorted([m for sub in st.session_state.matchs_poules.values() for m in sub if (m.get("is_finale") if f=="Finales" else not m.get("is_finale"))], key=lambda x: (x['heure'], x['terrain']))
            
            # Génération du HTML simple pour l'impression
            html_cal = "<table><tr><th>Heure</th><th>Terrain</th><th>Phase</th><th>Équipe A</th><th>Score</th><th>Équipe B</th></tr>"
            for m in all_m:
                nA, nB = st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))
                sc = f"{m.get('SA',0)} - {m.get('SB',0)}" if (m.get('cloture') or m.get('SA',0)>0 or m.get('SB',0)>0) else " - "
                html_cal += f"<tr><td>{m['heure']}</td><td>T{m['terrain']}</td><td>{m['poule']}</td><td>{nA}</td><td>{sc}</td><td>{nB}</td></tr>"
            html_cal += "</table>"
            bouton_action_export(html_cal, f"Calendrier ({f})")
            
            # --- LE RETOUR DU VERROUILLAGE CHRONOLOGIQUE ---
            h_u = sorted(list(set(m['heure'] for m in all_m)))
            idx_nc = next((i for i, s in enumerate(h_u) if any(not m.get("cloture") for m in all_m if m['heure']==s)), len(h_u))
            
            curr_h = ""
            for m in all_m:
                if m['heure'] != curr_h:
                    curr_h = m['heure']
                    lock = h_u.index(curr_h) > idx_nc
                    
                    st.markdown(f"#### 🕒 {curr_h} {'<span style=\"color:#ef4444; font-size:0.6em;\">🔒 EN ATTENTE</span>' if lock else ''}", unsafe_allow_html=True)
                    cols = st.columns(st.session_state.nb_terrains)
                    
                with cols[m['terrain']-1]:
                    p_n, p_i = m["poule"], st.session_state.matchs_poules[m["poule"]].index(m)
                    nA, nB = st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))
                    cl, bg = m.get("cloture") or global_cloture, "#0a3317" if not m.get("cloture") else "#020b04"
                    st.markdown(f'<div class="match-card" style="background-color: {bg}; border-left-color: {"#ed7902" if not cl else "#0c3d1b"}; opacity: {1 if not cl else 0.5}; color: white;"><div style="display: flex; justify-content: space-between;"><div><span class="terrain-badge" style="background-color: #136d33;">T{m["terrain"]}</span> <small>{m["poule"]}</small></div><div>🕒 {m["heure"]}</div></div><div style="display: flex; align-items: center; margin-top: 10px;"><div style="flex: 1; text-align: center; font-weight: 900;">{nA}</div><div style="padding: 0 10px; color: #ed7902;">VS</div><div style="flex: 1; text-align: center; font-weight: 900;">{nB}</div></div></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    
                    old_sa = m.get("SA", 0)
                    new_sa = c1.number_input("A", 0, 200, value=old_sa, key=f"input_sa_{p_n}_{p_i}", label_visibility="collapsed", disabled=cl or lock)
                    if new_sa != old_sa: st.session_state[f"s_{p_n}_{p_i}_a"] = new_sa; sauvegarder_donnees(); st.rerun()
                    
                    old_sb = m.get("SB", 0)
                    new_sb = c2.number_input("B", 0, 200, value=old_sb, key=f"input_sb_{p_n}_{p_i}", label_visibility="collapsed", disabled=cl or lock)
                    if new_sb != old_sb: st.session_state[f"s_{p_n}_{p_i}_b"] = new_sb; sauvegarder_donnees(); st.rerun()
                    
                    if m.get("is_finale"):
                        teams = ["À définir"] + sorted([st.session_state.get(f"n_{i}") for i in range(st.session_state.nb_equipes)])
                        ca, cb = st.columns(2)
                        new_fA = ca.selectbox("A", teams, index=teams.index(m["A"]) if m["A"] in teams else 0, key=f"input_name_a_{p_n}_{p_i}", label_visibility="collapsed", disabled=cl or lock)
                        if new_fA != m["A"]: st.session_state[f"name_a_{p_n}_{p_i}"] = new_fA; sauvegarder_donnees(); st.rerun()
                        
                        new_fB = cb.selectbox("B", teams, index=teams.index(m["B"]) if m["B"] in teams else 0, key=f"input_name_b_{p_n}_{p_i}", label_visibility="collapsed", disabled=cl or lock)
                        if new_fB != m["B"]: st.session_state[f"name_b_{p_n}_{p_i}"] = new_fB; sauvegarder_donnees(); st.rerun()
                        
                    fp_o = ["Aucune", nA, nB]
                    new_fp = st.selectbox("🤝 Fair-Play", fp_o, index=fp_o.index(m.get("fairplay", "Aucune")) if m.get("fairplay") in fp_o else 0, key=f"input_fp_{p_n}_{p_i}", disabled=cl or lock)
                    if new_fp != m.get("fairplay", "Aucune"): st.session_state[f"fp_{p_n}_{p_i}"] = new_fp; sauvegarder_donnees(); st.rerun()
                    
                    new_cl = st.toggle("🔒 Clôturer", value=m.get("cloture"), key=f"input_c_{p_n}_{p_i}", disabled=global_cloture or lock)
                    if new_cl != m.get("cloture"): st.session_state[f"c_{p_n}_{p_i}"] = new_cl; sauvegarder_donnees(); st.rerun()

        with tbs[1]:
            html_clas = ""
            dfs = []
            for i, (p, eqs) in enumerate(st.session_state.poules.items()):
                sts = {st.session_state.get(f"n_{e['idx_origine']}"): {"Pts": 0, "Diff": 0, "J": 0, "🤝 FP": 0} for e in eqs}
                for m in st.session_state.matchs_poules.get(p, []):
                    nA, nB, sa, sb = st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), st.session_state.get(f"n_{m.get('id_B')}", m.get("B")), m.get("SA", 0), m.get("SB", 0)
                    if m.get("cloture") or sa > 0 or sb > 0:
                        sts[nA]["J"]+=1; sts[nB]["J"]+=1; sts[nA]["Diff"]+=(sa-sb); sts[nB]["Diff"]+=(sb-sa)
                        if sa > sb: sts[nA]["Pts"]+=3
                        elif sb > sa: sts[nB]["Pts"]+=3
                        else: sts[nA]["Pts"]+=1; sts[nB]["Pts"]+=1
                        if m.get("fairplay")==nA: sts[nA]["🤝 FP"]+=1
                        elif m.get("fairplay")==nB: sts[nB]["🤝 FP"]+=1
                df = pd.DataFrame.from_dict(sts, orient='index').reset_index().rename(columns={"index":"Équipe"}).sort_values(["Pts","Diff","🤝 FP"], ascending=False)
                df.index = range(1, len(df)+1)
                dfs.append((p, df))
                html_clas += f"<h4>{p}</h4>" + df.to_html(index=False)
                
            bouton_action_export(html_clas, "Classements des Poules")
            
            cols = st.columns(2)
            for i, (p, df) in enumerate(dfs):
                with cols[i%2]: st.markdown(f"<h4 style='color:#ed7902;'>{p}</h4>", unsafe_allow_html=True); st.table(df)

        with tbs[2]:
            st.markdown("### 📋 PLANNING")
            mode = st.radio("Affichage", ["Équipe", "Global"], horizontal=True)
            all_n = sorted([st.session_state.get(f"n_{i}") for i in range(st.session_state.nb_equipes)])
            if mode == "Équipe":
                choix = st.selectbox("Sélectionner une équipe", all_n)
                if choix:
                    m_eq = [{"Heure": m["heure"], "Terrain": f"T{m['terrain']}", "Phase": m["poule"], "Adversaire": st.session_state.get(f"n_{m.get('id_B')}", m.get("B")) if st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))==choix else st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))} for sub in st.session_state.matchs_poules.values() for m in sub if st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))==choix or st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))==choix]
                    df_plan = pd.DataFrame(m_eq).sort_values("Heure")
                    bouton_action_export(df_plan.to_html(index=False), f"Planning - {choix}")
                    st.markdown(f'<div class="convocation-header" style="color:white; text-align:center;"><h2>{choix}</h2></div>', unsafe_allow_html=True)
                    st.table(df_plan)
            else:
                lst = [{"Heure": m["heure"], "Terrain": f"T{m['terrain']}", "Phase": m["poule"], "Équipe 1": st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), "Équipe 2": st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))} for sub in st.session_state.matchs_poules.values() for m in sub if st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))!="À définir"]
                df_plan = pd.DataFrame(lst).sort_values(["Heure", "Terrain"])
                bouton_action_export(df_plan.to_html(index=False), "Planning Global")
                st.table(df_plan)

        with tbs[3]:
            st.markdown("### 🖨️ TERRAINS")
            opts_t = ["Tous les terrains"] + [f"Terrain {t}" for t in range(1, st.session_state.nb_terrains + 1)]
            choix_t = st.selectbox("Choisir :", opts_t)
            all_mt = sorted([m for sub in st.session_state.matchs_poules.values() for m in sub], key=lambda x: x['heure'])
            
            if choix_t == "Tous les terrains":
                html_ter = ""
                dfs_t = []
                for t in range(1, st.session_state.nb_terrains + 1):
                    mt = [{"Heure": m["heure"], "Phase": m["poule"], "Match": f"{st.session_state.get(f'n_{m.get('id_A')}', m.get('A'))} vs {st.session_state.get(f'n_{m.get('id_B')}', m.get('B'))}"} for m in all_mt if m['terrain']==t]
                    if mt:
                        df_t = pd.DataFrame(mt)
                        dfs_t.append((t, df_t))
                        html_ter += f"<h4>Terrain {t}</h4>" + df_t.to_html(index=False)
                bouton_action_export(html_ter, "Planning de Tous les Terrains")
                
                t_cols = st.columns(min(st.session_state.nb_terrains, 3))
                for idx, (t, df_t) in enumerate(dfs_t):
                    with t_cols[idx%len(t_cols)]: 
                        st.markdown(f"<div class='convocation-header' style='color:white; text-align:center;'><h4>T{t}</h4></div>", unsafe_allow_html=True)
                        st.table(df_t)
            else:
                tid = int(choix_t.split(" ")[1])
                mt = [{"Heure": m["heure"], "Phase": m["poule"], "Équipe 1": st.session_state.get(f'n_{m.get("id_A")}', m.get("A")), "Équipe 2": st.session_state.get(f'n_{m.get("id_B")}', m.get("B"))} for m in all_mt if m['terrain']==tid]
                
                df_t = pd.DataFrame(mt) if mt else pd.DataFrame()
                if not df_t.empty:
                    bouton_action_export(df_t.to_html(index=False), f"Planning {choix_t}")
                    st.markdown(f"<div class='convocation-header' style='color:white; text-align:center;'><h2>{choix_t}</h2></div>", unsafe_allow_html=True)
                    st.table(df_t)
                else:
                    st.info("Aucun match.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_btn_retour, c_btn_suivant = st.columns(2)
        c_btn_retour.button("⬅️ RETOUR", use_container_width=True, on_click=changer_page, args=("⚙️ 2. Logistique",))
        c_btn_suivant.button("➡️ ALLER AUX STATISTIQUES", type="primary", use_container_width=True, on_click=changer_page, args=("📈 4. Statistiques",))

    else:
        # ==========================================
        # VUE SPECTATEUR
        # ==========================================
        st.markdown("<h2 style='text-align:center; color:#ed7902;'>📱 LIVE SCORE & RÉSULTATS</h2>", unsafe_allow_html=True)
        
        if st.button("🔄 ACTUALISER LES DONNÉES", type="primary", use_container_width=True):
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        tbs_spec = st.tabs(["⏱️ MATCHS EN DIRECT", "📊 CLASSEMENTS", "📋 MON ÉQUIPE"])
        
        with tbs_spec[0]:
            f = st.radio("Filtre :", ["Période de Poules", "Phases Finales"], horizontal=True, key="filtre_spec")
            all_m = sorted([m for sub in st.session_state.matchs_poules.values() for m in sub if (m.get("is_finale") if f=="Phases Finales" else not m.get("is_finale"))], key=lambda x: (x['heure'], x['terrain']))
            curr_h = ""
            for m in all_m:
                if m['heure'] != curr_h:
                    curr_h = m['heure']
                    st.markdown(f"#### 🕒 {curr_h}", unsafe_allow_html=True)
                    cols = st.columns(st.session_state.nb_terrains)
                with cols[m['terrain']-1]:
                    nA = st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))
                    nB = st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))
                    sa, sb = m.get("SA", 0), m.get("SB", 0)
                    cl = m.get("cloture") or global_cloture
                    
                    bg = "#0a3317" if not cl else "#020b04"
                    opac = 1 if not cl else 0.7
                    
                    if cl or sa > 0 or sb > 0:
                        centre_html = f"<div style='padding: 2px 10px; font-weight: 900; font-size: 1.3em; color: #ffffff; background-color: #ed7902; border-radius: 6px;'>{sa} - {sb}</div>"
                    else:
                        centre_html = f"<div style='padding: 0 10px; font-weight: 900; color: #ed7902;'>VS</div>"

                    st.markdown(f'''
                    <div class="match-card" style="background-color: {bg}; border-left-color: #ed7902; opacity: {opac}; color: white; padding: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                            <div><span class="terrain-badge" style="background-color: #136d33; padding: 4px 8px; border-radius: 4px;">T{m["terrain"]}</span> <small style="margin-left: 5px; font-weight: bold; color: #829b8c;">{m["poule"]}</small></div>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="flex: 1; text-align: center; font-weight: 900; font-size: 1.1em; line-height: 1.2;">{nA}</div>
                            {centre_html}
                            <div style="flex: 1; text-align: center; font-weight: 900; font-size: 1.1em; line-height: 1.2;">{nB}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

        with tbs_spec[1]:
            cols = st.columns(2)
            for i, (p, eqs) in enumerate(st.session_state.poules.items()):
                sts = {st.session_state.get(f"n_{e['idx_origine']}"): {"Pts": 0, "Diff": 0, "J": 0} for e in eqs}
                for m in st.session_state.matchs_poules.get(p, []):
                    nA, nB, sa, sb = st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), st.session_state.get(f"n_{m.get('id_B')}", m.get("B")), m.get("SA", 0), m.get("SB", 0)
                    if m.get("cloture") or sa > 0 or sb > 0:
                        sts[nA]["J"]+=1; sts[nB]["J"]+=1; sts[nA]["Diff"]+=(sa-sb); sts[nB]["Diff"]+=(sb-sa)
                        if sa > sb: sts[nA]["Pts"]+=3
                        elif sb > sa: sts[nB]["Pts"]+=3
                        else: sts[nA]["Pts"]+=1; sts[nB]["Pts"]+=1
                df = pd.DataFrame.from_dict(sts, orient='index').reset_index().rename(columns={"index":"Équipe"}).sort_values(["Pts","Diff"], ascending=False)
                df.index = range(1, len(df)+1)
                with cols[i%2]: st.markdown(f"<h4 style='color:#ed7902;'>{p}</h4>", unsafe_allow_html=True); st.table(df)

        with tbs_spec[2]:
            st.markdown("### 📋 SUIVRE UNE ÉQUIPE")
            all_n = sorted([st.session_state.get(f"n_{i}") for i in range(st.session_state.nb_equipes)])
            choix = st.selectbox("Sélectionner votre équipe :", all_n, key="spec_eq")
            if choix:
                st.markdown(f'<div class="convocation-header" style="color:white; text-align:center; border-radius: 8px;"><h2>{choix}</h2></div>', unsafe_allow_html=True)
                m_eq = [{"Heure": m["heure"], "Terrain": f"T{m['terrain']}", "Phase": m["poule"], "Match": f"{st.session_state.get(f'n_{m.get('id_A')}', m.get('A'))} vs {st.session_state.get(f'n_{m.get('id_B')}', m.get('B'))}", "Résultat": f"{m.get('SA',0)} - {m.get('SB',0)}" if (m.get('cloture') or m.get('SA',0)>0 or m.get('SB',0)>0) else "À venir"} for sub in st.session_state.matchs_poules.values() for m in sub if st.session_state.get(f"n_{m.get('id_A')}", m.get("A"))==choix or st.session_state.get(f"n_{m.get('id_B')}", m.get("B"))==choix]
                st.table(pd.DataFrame(m_eq).sort_values("Heure"))
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("➡️ VOIR LES STATISTIQUES GLOBALES", type="primary", use_container_width=True, on_click=changer_page, args=("📈 4. Statistiques",))

# --- PAGE 4 : STATISTIQUES ---
elif page_actuelle == "📈 4. Statistiques":
    all_m = [m for sub in st.session_state.matchs_poules.values() for m in sub]
    joues = [m for m in all_m if m.get("SA", 0) > 0 or m.get("SB", 0) > 0 or m.get("cloture")]
    
    if joues:
        gst = {st.session_state.get(f"n_{i}"): {"Pts":0, "Diff":0, "J":0, "Enc":0} for i in range(st.session_state.nb_equipes)}
        v_f, p_f, max_e, b_m, min_e, c_m, max_t, p_m = None, None, 0, None, float('inf'), None, -1, None
        fp_totals = {}
        for m in joues:
            nA, nB, sa, sb = st.session_state.get(f"n_{m.get('id_A')}", m.get("A")), st.session_state.get(f"n_{m.get('id_B')}", m.get("B")), m.get("SA",0), m.get("SB",0)
            if nA in gst and nB in gst:
                gst[nA]["Diff"]+=(sa-sb); gst[nB]["Diff"]+=(sb-sa); gst[nA]["J"]+=1; gst[nB]["J"]+=1; gst[nA]["Enc"]+=sb; gst[nB]["Enc"]+=sa
                if sa > sb: gst[nA]["Pts"]+=3
                elif sb > sa: gst[nB]["Pts"]+=3
                else: gst[nA]["Pts"]+=1; gst[nB]["Pts"]+=1
                if m.get("poule")=="Finale" and (sa>0 or sb>0 or m.get("cloture")):
                    if sa>sb: v_f, p_f = nA, nB
                    elif sb>sa: v_f, p_f = nB, nA
                ec, tot = abs(sa-sb), sa+sb
                if ec > max_e: max_e=ec; b_m={"v": nA if sa>sb else nB, "p": nB if sa>sb else nA, "sv": max(sa,sb), "sp": min(sa,sb)}
                if 0 < ec < min_e: min_e=ec; c_m={"v": nA if sa>sb else nB, "p": nB if sa>sb else nA, "sv": max(sa,sb), "sp": min(sa,sb)}
                if tot > max_t: max_t=tot; p_m={"A":nA, "B":nB, "sa":sa, "sb":sb, "tot":tot}
                
                fp = m.get("fairplay", "Aucune")
                if fp in [nA, nB] and fp != "Aucune": fp_totals[fp] = fp_totals.get(fp, 0) + 1
                
        cl_g = sorted(gst.keys(), key=lambda x: (gst[x]["Pts"], gst[x]["Diff"]), reverse=True)
        if v_f:
            if v_f in cl_g: cl_g.remove(v_f); 
            if p_f in cl_g: cl_g.remove(p_f); 
            cl_g.insert(0, p_f); cl_g.insert(0, v_f)
            
        if global_cloture:
            st.markdown("<h2 style='text-align:center; color:#ed7902;'>🏆 HALL OF FAME</h2>", unsafe_allow_html=True)
            c2, c1, c3 = st.columns(3)
            c2.markdown(f"<div style='text-align:center; margin-top:50px;'><h3 style='color:#829b8c;'>RUNNER UP</h3><div style='background:linear-gradient(135deg,#cbd5e1,#94a3b8); padding:20px; border-radius:8px; color:#020b04; font-weight:900;'>🥈 {cl_g[1] if len(cl_g)>1 else '---'}</div></div>", unsafe_allow_html=True)
            c1.markdown(f"<div style='text-align:center;'><h2 style='color:#fbbf24;'>CHAMPION</h2><div style='background:linear-gradient(135deg,#fde047,#ed7902); padding:30px; border-radius:8px; color:white; font-weight:900; border:2px solid #fff;'>👑 {cl_g[0] if len(cl_g)>0 else '---'}</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='text-align:center; margin-top:70px;'><h4 style='color:#b45309;'>3RD PLACE</h4><div style='background:linear-gradient(135deg,#fcd34d,#b45309); padding:15px; border-radius:8px; color:#fff; font-weight:900;'>🥉 {cl_g[2] if len(cl_g)>2 else '---'}</div></div>", unsafe_allow_html=True)
            
            meilleur_fp = max(fp_totals, key=fp_totals.get) if fp_totals else "---"
            st.markdown(f"<div style='text-align:center; margin-top:40px;'><h3 style='color:#10b981;'>PRIX DU FAIR-PLAY</h3><div style='background:linear-gradient(135deg,#34d399,#047857); padding:15px; border-radius:8px; color:#fff; font-weight:900; display:inline-block; min-width:300px; border:2px solid #fff;'>🤝 {meilleur_fp}</div></div>", unsafe_allow_html=True)
            st.divider()
        else:
            st.info("🔒 Le Podium HALL OF FAME et le trophée du Fair-Play seront révélés ici une fois le tournoi officiellement clôturé !")
            st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("FRANCHISES", st.session_state.nb_equipes)
        c2.metric("JOUEURS", sum(st.session_state.get(f"j_{i}",5) for i in range(st.session_state.nb_equipes)))
        c3.metric("MATCHS JOUÉS", f"{len(joues)} / {len(all_m)}")
        c4.metric("PROGRESSION", f"{round((len(joues)/len(all_m))*100) if all_m else 0} %")
        
        st.markdown("<h3 style='color:#ed7902;'>🔥 RECORDS</h3>", unsafe_allow_html=True); c1, c2, c3 = st.columns(3)
        m_atk = max(gst, key=lambda x: gst[x]["Diff"]) if gst else None
        m_def = min([e for e in gst if gst[e]["J"]>0], key=lambda x: gst[x]["Enc"]/gst[x]["J"]) if joues else None
        if m_atk: c1.success(f"**⚡ BEST ATTACK :**\n\n**{m_atk}**")
        if m_def: c2.info(f"**🛡️ BEST DEFENSE :**\n\n**{m_def}**\n\n*{round(gst[m_def]['Enc']/gst[m_def]['J'],1)} pts/match*")
        if b_m: c3.error(f"**💥 BLOWOUT :**\n\n**{b_m['v']}** {b_m['sv']}-{b_m['sp']} {b_m['p']}")
        c1, c2, c3 = st.columns(3)
        if c_m: c1.warning(f"**🥶 NAIL-BITER :**\n\n**{c_m['v']}** {c_m['sv']}-{c_m['sp']} {c_m['p']}")
        if p_m: c2.error(f"**🔥 SCORING FEST :**\n\n**{p_m['A']}** vs **{p_m['B']}** ({p_m['tot']} pts)")
    else:
        st.info("Les statistiques apparaîtront ici dès que le premier match sera validé !")
        
    st.divider(); 
    if is_admin:
        st.button("⬅️ RETOUR", use_container_width=True, on_click=changer_page, args=("🏆 3. Tournoi",))

st.markdown('<div class="version-tag">Version 1.8</div>', unsafe_allow_html=True)