import streamlit as st
import math

st.set_page_config(page_title="Ai-je besoin d'un courtier ?", page_icon="⚖️", layout="wide")

# --- CSS POUR REPRODUIRE LE DESIGN ---
st.markdown("""
<style>
    .kpi-box {
        background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px;
    }
    .score-high { background-color: #ecfdf5; border-left: 5px solid #10b981; padding: 15px; border-radius: 8px; }
    .score-mid { background-color: #fefce8; border-left: 5px solid #eab308; padding: 15px; border-radius: 8px; }
    .score-low { background-color: #f1f5f9; border-left: 5px solid #64748b; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE CALCUL ---
def pmt(capital, taux_annuel, duree_annees):
    if capital <= 0: return 0
    if taux_annuel == 0: return capital / (duree_annees * 12)
    t = taux_annuel / 100 / 12
    n = duree_annees * 12
    return (capital * t) / (1 - (1 + t)**-n)

def calc_crd(capital, taux_annuel, duree_annees, mois_ecoules):
    if capital <= 0: return 0
    if taux_annuel == 0: return max(0, capital - (capital * (mois_ecoules / (duree_annees * 12))))
    t = taux_annuel / 100 / 12
    n = duree_annees * 12
    p = mois_ecoules
    return capital * ((1 + t)**n - (1 + t)**p) / ((1 + t)**n - 1)

def calculer_garanties(lignes_prets):
    montant_total = sum(lignes_prets)
    if montant_total == 0:
        return {"CM": {"net": 0, "nom": "CMH"}, "CE_BP": {"net": 0, "nom": "SACCEF"}, "CA": {"net": 0, "nom": "CAMCA"}, "LCL": {"net": 0, "nom": "Crédit Logement"}}

    # CMH
    tx_cmh = 0.0032 if montant_total <= 99999 else (0.0034 if montant_total <= 299999 else 0.00354)
    net_cmh = 350 + (montant_total * tx_cmh)

    # SACCEF
    if montant_total <= 100000: r_saccef = 1.65
    elif montant_total <= 150000: r_saccef = 1.55
    elif montant_total <= 200000: r_saccef = 1.45
    elif montant_total <= 300000: r_saccef = 1.25
    else: r_saccef = 1.20
    net_saccef = montant_total * (r_saccef / 100) / (1 - (r_saccef / 100))

    # CAMCA
    tx_camca = 0.011 if montant_total <= 150000 else (0.008 if montant_total > 400000 else 0.01)
    net_camca = (montant_total / (1 - tx_camca)) - montant_total

    # Crédit Logement
    fmg_total, com_total = 0, 0
    for ligne in lignes_prets:
        if ligne > 0:
            fmg_total += (ligne * 0.0089) + 230
            com_total += max(150, min(650, ligne * 0.005))
    restitution = fmg_total * 0.70
    net_cl = (fmg_total + com_total) - restitution

    return {
        "CM": {"net": net_cmh, "nom": "CMH"},
        "CE_BP": {"net": net_saccef, "nom": "SACCEF"},
        "CA": {"net": net_camca, "nom": "CAMCA"},
        "LCL": {"net": net_cl, "nom": "Crédit Logement (Net)"}
    }

# --- INTERFACE ---
st.title("⚖️ Simulateur : Ai-je besoin d'un courtier ?")

col_form, col_res = st.columns([1, 1], gap="large")

with col_form:
    st.markdown("### 🎯 Vos priorités")
    poids_finance = st.slider("Gain Financier vs Accompagnement (%)", 0, 100, 70, step=5, format="%d%% de priorité Finance")
    poids_confort = 100 - poids_finance
    
    st.markdown("### 🏦 Votre Établissement Bancaire")
    liste_banques = {"CA": "Crédit Agricole", "CE_BP": "Caisse d'Épargne / BP", "LCL": "LCL / Autres", "CM": "Crédit Mutuel / CIC"}
    banque_actuelle = st.radio("Sélectionnez la banque :", list(liste_banques.keys()), format_func=lambda x: liste_banques[x], horizontal=True)

    st.markdown("### 💰 Lignes de Prêts")
    c1, c2, c3 = st.columns(3)
    mt_principal = c1.number_input("Prêt Principal (€)", value=200000, step=5000)
    mt_ptz = c2.number_input("PTZ (€)", value=50000, step=5000)
    mt_autres = c3.number_input("Autres Prêts (€)", value=0, step=5000)

    st.markdown("### ⚙️ Conditions du crédit")
    c4, c5 = st.columns(2)
    tx_banque = c4.number_input("Taux estimé Banque (%)", value=3.90, step=0.05)
    tx_courtier = c5.number_input("Taux estimé Courtier (%)", value=3.70, step=0.05)
    
    honoraires = st.number_input("Honoraires courtier estimés (€)", value=2500, step=100)
    
    c6, c7 = st.columns(2)
    duree_pret = c6.slider("Durée du prêt (ans)", 5, 30, 25)
    duree_detention = c7.slider("Revente estimée (ans)", 1, 30, 10, help="Durée avant revente du bien")

    st.markdown("### 🧩 Profil du projet")
    type_projet = st.selectbox("Type de projet", ["Ancien standard", "VEFA", "Construction", "Rénovation énergétique"])
    prets_externes = st.selectbox("Prêts externes (PTZ, Action Log...)", ["0", "1", "2 ou plus"])
    
    pret_relais = st.checkbox("Présence d'un prêt relais")
    risque_sante = st.checkbox("Craintes sur l'assurance emprunteur / Antécédents de santé")
    evo_famille = st.checkbox("Évolution familiale prévue (naissance...)")

# --- MOTEUR DE CALCUL ---
lignes_banque = [mt_principal, mt_ptz, mt_autres]
lignes_courtier = [mt_principal + honoraires, mt_ptz, mt_autres]
total_emprunte = mt_principal + mt_ptz + mt_autres

pmt_main_b = pmt(mt_principal, tx_banque, duree_pret)
pmt_main_c = pmt(mt_principal + honoraires, tx_courtier, duree_pret)
pmt_autres_b = pmt(mt_autres, tx_banque, duree_pret)
pmt_autres_c = pmt(mt_autres, tx_courtier, duree_pret)
pmt_ptz = mt_ptz / (duree_pret * 12) if mt_ptz > 0 else 0

mens_b = pmt_main_b + pmt_autres_b + pmt_ptz
mens_c = pmt_main_c + pmt_autres_c + pmt_ptz

mois_detention = min(duree_detention, duree_pret) * 12

int_main_b = (pmt_main_b * mois_detention) - (mt_principal - calc_crd(mt_principal, tx_banque, duree_pret, mois_detention))
int_main_c = (pmt_main_c * mois_detention) - ((mt_principal + honoraires) - calc_crd(mt_principal + honoraires, tx_courtier, duree_pret, mois_detention))
int_autres_b = (pmt_autres_b * mois_detention) - (mt_autres - calc_crd(mt_autres, tx_banque, duree_pret, mois_detention))
int_autres_c = (pmt_autres_c * mois_detention) - (mt_autres - calc_crd(mt_autres, tx_courtier, duree_pret, mois_detention))

int_b = int_main_b + int_autres_b
int_c = int_main_c + int_autres_c

# Garanties
garanties = calculer_garanties(lignes_banque)
gar_banque = garanties.get(banque_actuelle, {"net": 0, "nom": ""})

min_net = float('inf')
opti_nom = ""
for g in garanties.values():
    if g["net"] < min_net:
        min_net = g["net"]
        opti_nom = g["nom"]

eco_garantie = gar_banque["net"] - min_net

cout_tot_b = int_b + gar_banque["net"]
cout_tot_c = int_c + min_net + honoraires
eco_totale = cout_tot_b - cout_tot_c

pts_finance = min(poids_finance, max(0, int(eco_totale / 100)))

raw_proj = 10 if type_projet in ["Construction", "Rénovation énergétique"] else 0
raw_ext = 4 if prets_externes == "1" else (8 if prets_externes == "2 ou plus" else 0)
raw_rel = 5 if pret_relais else 0
raw_san = 9 if risque_sante else 0
raw_fam = 3 if evo_famille else 0

pts_proj = round((raw_proj / 35) * poids_confort)
pts_ext = round((raw_ext / 35) * poids_confort)
pts_rel = round((raw_rel / 35) * poids_confort)
pts_san = round((raw_san / 35) * poids_confort)
pts_fam = round((raw_fam / 35) * poids_confort)

pts_confort_total = min(poids_confort, pts_proj + pts_ext + pts_rel + pts_san + pts_fam)
score_total = pts_finance + pts_confort_total

# --- AFFICHAGE RÉSULTATS ---
with col_res:
    st.markdown("### 📊 Résultat du Scoring")
    
    if score_total >= 65:
        st.markdown(f"<div class='score-high'><h3 style='color:#065f46; margin:0;'>Score : {score_total}/100</h3>Recours indispensable : Enjeux financiers massifs et dossier complexe.</div>", unsafe_allow_html=True)
    elif score_total >= 35:
        st.markdown(f"<div class='score-mid'><h3 style='color:#854d0e; margin:0;'>Score : {score_total}/100</h3>Utile : Le gain justifie l'accompagnement d'un courtier.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='score-low'><h3 style='color:#334155; margin:0;'>Score : {score_total}/100</h3>Dossier simple : Vous pouvez probablement gérer ce projet seul.</div>", unsafe_allow_html=True)

    st.markdown("#### 1. Enjeu Financier")
    st.progress(pts_finance / 100 if poids_finance > 0 else 0.0)
    st.markdown(f"**Bénéfice global estimé : <span style='color:#16a34a;'>+{eco_totale:,.0f} €</span>**".replace(",", " "), unsafe_allow_html=True)
    
    if eco_garantie > 50:
        st.info(f"💡 **L'optimisation cachée de la garantie :** Votre banque propose {gar_banque['nom']}. Un courtier cherchera le dispositif le plus compétitif (ex: {opti_nom}), générant à lui seul +{eco_garantie:,.0f} € d'économie nette.".replace(",", " "))

    c_b, c_c = st.columns(2)
    with c_b:
        st.markdown("<div class='kpi-box'><b>🏦 Sans courtier</b><br>"
                    f"Taux : {tx_banque}%<br>"
                    f"Mensualité : {mens_b:,.0f} €<br>"
                    f"Coût Garantie : {gar_banque['net']:,.0f} €<br>"
                    f"<span style='color:#dc2626; font-weight:bold;'>Coût Global : {cout_tot_b:,.0f} €</span></div>".replace(",", " "), unsafe_allow_html=True)
    with c_c:
        st.markdown("<div class='kpi-box'><b>👔 Avec courtier</b><br>"
                    f"Taux : {tx_courtier}%<br>"
                    f"Mensualité : {mens_c:,.0f} €<br>"
                    f"Coût Garantie : {min_net:,.0f} €<br>"
                    f"<span style='color:#16a34a; font-weight:bold;'>Coût Global : {cout_tot_c:,.0f} €</span></div>".replace(",", " "), unsafe_allow_html=True)

    st.markdown("#### 2. Besoin d'Accompagnement (Confort & Sécurité)")
    st.progress(pts_confort_total / 100 if poids_confort > 0 else 0.0)
    
    if pts_proj > 0: st.write(f"- 🏗️ Complexité du projet : **+{pts_proj} pts**")
    if pts_ext > 0: st.write(f"- 🧩 Montage prêts externes : **+{pts_ext} pts**")
    if pts_rel > 0: st.write(f"- 🔄 Gestion Prêt relais : **+{pts_rel} pts**")
    if pts_san > 0: st.write(f"- 🏥 Enjeu Assurance/Santé : **+{pts_san} pts**")
