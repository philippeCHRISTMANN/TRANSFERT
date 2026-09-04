import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Simulateur Transfert PTZ & Stratégie Revente", layout="wide")

def fmt(n):
    return f"{n:,.0f}".replace(",", " ")

# =================================================================
# MODULE : TRANSFERT DE PTZ & STRATÉGIE DE REVENTE
# =================================================================

st.markdown('<div style="font-size: 24px; font-weight: bold; color: #1E3A8A; border-bottom: 3px solid #E91E63; padding-bottom: 5px; margin-bottom: 20px;">🔄 Anticipation : Transfert de PTZ & Prêt Relais</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Découvrez le gain généré par la conservation de votre Prêt à Taux Zéro (PTZ) et comparez le déroulement financier entre une <b>Vente préalable</b> et un <b>Prêt Relais</b>.</p>", unsafe_allow_html=True)

st.write("---")

# --- A. SAISIE DES DONNÉES ---
st.markdown("### 📝 Étape 1 : La vente de votre bien et vos crédits en cours")
st.info("💡 Placez-vous dans la situation estimée à la date de votre future vente (ex: dans 3 ou 6 mois). Indiquez la valeur du bien et les capitaux restants dus à cette date.")

col_v1, col_v2 = st.columns(2)
with col_v1:
    val_estimee = st.number_input("Valeur nette vendeuse estimée de votre bien actuel (€)", min_value=0.0, step=5000.0, value=250000.0)
with col_v2:
    epargne_perso = st.number_input("Épargne personnelle ajoutée au projet (€)", min_value=0.0, step=1000.0, value=10000.0, help="Vos économies personnelles que vous injecterez en plus de la revente.")

st.write("")
col_ptz, col_pp = st.columns(2)

# PTZ
with col_ptz:
    st.markdown("#### 🟣 Votre Prêt à Taux Zéro (PTZ)")
    crd_ptz = st.number_input("Capital Restant Dû PTZ en €", min_value=0.0, step=1000.0, value=40000.0)
    is_constant_ptz = st.radio("Mensualités RESTANTES du PTZ :", ("Oui, constantes", "Non, avec paliers"), key="rad_ptz")
    
    ptz_flow_total = []
    if is_constant_ptz.startswith("Oui"):
        duree_ptz = st.number_input("Mensualités RESTANTES PTZ", min_value=1, step=12, value=204)
        mens_ptz = crd_ptz / duree_ptz if duree_ptz > 0 else 0
        st.info(f"Mensualité : **{mens_ptz:.2f} € / mois**")
        ptz_flow_total = [mens_ptz] * int(duree_ptz)
    else:
        nb_paliers_ptz = st.number_input("Nombre de paliers RESTANTS", min_value=1, max_value=6, value=2, key="nb_pal_ptz")
        for i in range(int(nb_paliers_ptz)):
            c1, c2 = st.columns(2)
            with c1: dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=120 if i==0 else 84, key=f"ptz_dur_{i}")
            with c2: men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=0.0 if i==0 else 200.0, key=f"ptz_mens_{i}")
            ptz_flow_total.extend([men_p] * int(dur_p))

# PRET PRINCIPAL
with col_pp:
    st.markdown("#### 🔵 Votre Prêt Principal")
    crd_pp = st.number_input("Capital Restant Dû Prêt Principal en €", min_value=0.0, step=1000.0, value=150000.0)
    is_constant_pp = st.radio("Mensualités RESTANTES du Prêt Principal :", ("Oui, constantes", "Non, avec paliers"), key="rad_pp")
    
    pp_flow_total = []
    if is_constant_pp.startswith("Oui"):
        mens_pp = st.number_input("Mensualité Prêt Principal (€)", min_value=0.0, step=10.0, value=850.0)
        duree_pp = st.number_input("Mensualités RESTANTES Prêt Principal", min_value=1, step=12, value=204)
        pp_flow_total = [mens_pp] * int(duree_pp)
    else:
        nb_paliers_pp = st.number_input("Nombre de paliers RESTANTS", min_value=1, max_value=6, value=2, key="nb_pal_pp")
        for i in range(int(nb_paliers_pp)):
            c1, c2 = st.columns(2)
            with c1: dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=120 if i==0 else 84, key=f"pp_dur_{i}")
            with c2: men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=1000.0 if i==0 else 800.0, key=f"pp_mens_{i}")
            pp_flow_total.extend([men_p] * int(dur_p))

st.write("---")

# --- B. LE FUTUR PROJET ---
st.markdown("### 🎯 Étape 2 : Votre futur projet (Achat)")

# Mensualité actuelle indicative
max_len_actuel = max(len(ptz_flow_total), len(pp_flow_total))
ptz_padded_actuel = ptz_flow_total + [0] * (max_len_actuel - len(ptz_flow_total))
pp_padded_actuel = pp_flow_total + [0] * (max_len_actuel - len(pp_flow_total))
total_mensualite_actuelle = [p + m for p, m in zip(ptz_padded_actuel, pp_padded_actuel)]
mensualite_lisse_moyenne = int(max(total_mensualite_actuelle)) if total_mensualite_actuelle else 1000

col_t1, col_t2 = st.columns(2)
with col_t1:
    mens_cible_future = st.number_input("Mensualité cible pour le futur projet (€)", min_value=100, value=mensualite_lisse_moyenne, step=50, help="Nous reprenons par défaut la mensualité maximale que vous payez actuellement.")
with col_t2:
    taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=4.0, step=0.10)

# --- C. CALCULS MATHÉMATIQUES EXPERTS ---
if len(ptz_flow_total) > 0:
    crd_ptz_transfert = sum(ptz_flow_total)
    
    if crd_ptz_transfert > 0:
        duree_nouveau_pret_mois = 300 # 25 ans
        tm_futur = taux_futur / 100 / 12
        
        # Lissage du nouveau prêt autour du PTZ
        ptz_flow_futur_padded = ptz_flow_total + [0] * (duree_nouveau_pret_mois - len(ptz_flow_total)) if len(ptz_flow_total) < duree_nouveau_pret_mois else ptz_flow_total[:duree_nouveau_pret_mois]
        
        if mens_cible_future <= max(ptz_flow_futur_padded):
            st.error(f"❌ Mensualité cible ({mens_cible_future} €) trop faible pour absorber l'échéance du PTZ.")
        else:
            # Calcul capacité nouveau prêt
            pv_nouveau_pret_lisse = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret_lisse += disponible_mensuel / ((1+tm_futur)**m)
            else:
                pv_nouveau_pret_lisse = sum((mens_cible_future - p) for p in ptz_flow_futur_padded)
            
            # -------------------------------------------------------------
            # VRAIS CALCULS DES SCÉNARIOS (VENTE VS RELAIS)
            # -------------------------------------------------------------
            # Scénario 1 : Vente d'abord
            cash_vente_secu = max(0, val_estimee - crd_pp) # PTZ conservé donc pas remboursé
            apport_total_secu = cash_vente_secu + epargne_perso
            budget_achat_global = apport_total_secu + pv_nouveau_pret_lisse
            
            # Scénario 2 : Relais (La banque retient 70%)
            avance_relais = max(0, (val_estimee * 0.70) - crd_pp)
            apport_initial_relais = avance_relais + epargne_perso
            
            # Pour atteindre le même budget d'achat, on gonfle le prêt principal temporaire !
            pret_principal_temporaire = budget_achat_global - apport_initial_relais
            
            # À la revente : récupération du solde (30%)
            solde_recupere_revente = cash_vente_secu - avance_relais
            
            # Mensualités pendant la phase relais (Avant revente)
            mens_ptz_actuelle = ptz_flow_futur_padded[0]
            mens_int_relais = avance_relais * ((taux_futur + 0.20) / 100 / 12)
            mens_pret_tempo = pret_principal_temporaire * tm_futur / (1 - (1+tm_futur)**-300) if tm_futur > 0 else pret_principal_temporaire / 300
            
            mens_totale_phase_relais = mens_ptz_actuelle + mens_int_relais + mens_pret_tempo

            # --- D. AFFICHAGE DES RÉSULTATS PÉDAGOGIQUES ---
            st.write("---")
            st.markdown("### 🏆 Bilan : Comment se déroule votre financement ?")
            st.write(f"En conservant votre PTZ, votre budget d'achat s'élève à **{fmt(budget_achat_global)} €**. Voici comment ce montage se déroule selon la stratégie choisie :")

            col_r1, col_r2 = st.columns(2)
            
            # SCÉNARIO 1 : VENTE D'ABORD
            html_s1 = f"""
<div style="background-color: #F8FAFC; border: 2px solid #3B82F6; border-radius: 8px; padding: 20px; height: 100%;">
<h4 style="color: #1E3A8A; margin-top: 0; font-size: 18px;">1️⃣ Vente préalable (Acheter après avoir vendu)</h4>
<p style="color: #334155; font-size: 13px; margin-bottom: 20px;">Vous encaissez directement 100% de la vente. Le plan de financement est définitif dès la signature.</p>

<div style="background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #BFDBFE;">
<div style="color: #1E3A8A; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #BFDBFE; padding-bottom: 5px;">Plan de financement :</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;">
<span>Apport (Fruit de vente {fmt(cash_vente_secu)}€ + Épargne {fmt(epargne_perso)}€)</span> <strong>{fmt(apport_total_secu)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 5px;">
<span>PTZ (Dette transférée, non soldée)</span> <strong>{fmt(crd_ptz_transfert)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #0284C7; margin-bottom: 10px;">
<span>Nouveau Prêt Bancaire (Lissé)</span> <strong>{fmt(pv_nouveau_pret_lisse)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;">
<span>TOTAL BUDGET ACHAT</span> <span style="color: #0284C7;">{fmt(budget_achat_global)} €</span>
</div>
</div>

<div style="margin-top: 20px; text-align: center; background-color: #F0F9FF; padding: 10px; border-radius: 6px; border: 1px dashed #3B82F6;">
<div style="font-size: 12px; color: #0284C7; font-weight: bold;">Mensualité immédiate et définitive</div>
<div style="font-size: 22px; font-weight: 900; color: #1E3A8A;">{fmt(mens_cible_future)} € / mois</div>
</div>
</div>
"""
            with col_r1:
                st.markdown(html_s1, unsafe_allow_html=True)
                
            # SCÉNARIO 2 : PRÊT RELAIS (La vraie mécanique)
            html_s2 = f"""
<div style="background-color: #FFFBEB; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; height: 100%;">
<h4 style="color: #92400E; margin-top: 0; font-size: 18px;">2️⃣ Prêt Relais (Acheter avant de vendre)</h4>
<p style="color: #B45309; font-size: 13px; margin-bottom: 20px;">La banque retient 30% de marge de sécurité. Pour combler l'apport manquant, elle "gonfle" votre prêt principal temporairement.</p>

<div style="background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #FDE68A;">
<div style="color: #92400E; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #FDE68A; padding-bottom: 5px;">Phase 1 : L'Achat (Avant la revente)</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;">
<span>Avance Relais (70%) + Épargne</span> <strong>{fmt(apport_initial_relais)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 5px;">
<span>PTZ (Dette transférée)</span> <strong>{fmt(crd_ptz_transfert)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #E11D48; margin-bottom: 5px;">
<span>Prêt Principal "Gonflé" temporairement</span> <strong>{fmt(pret_principal_temporaire)} €</strong>
</div>
</div>

<div style="background-color: #FEF2F2; padding: 10px; border-radius: 6px; border: 1px dashed #EF4444; margin-top: 10px; text-align: center;">
<div style="font-size: 12px; color: #B91C1C; font-weight: bold;">Effort de trésorerie pendant la vente</div>
<div style="font-size: 22px; font-weight: 900; color: #9F1239;">{fmt(mens_totale_phase_relais)} € / mois</div>
<div style="font-size: 10px; color: #7F1D1D;">(PTZ + Intérêts Relais + Prêt Gonflé)</div>
</div>

<div style="background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #A7F3D0; margin-top: 15px;">
<div style="color: #065F46; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #A7F3D0; padding-bottom: 5px;">Phase 2 : La Revente de l'ancien bien</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;">
<span>Encaissement du solde de la vente (30%)</span> <strong style="color: #10B981;">+ {fmt(solde_recupere_revente)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;">
<span>Remboursement Anticipé sur Prêt Gonflé</span> <strong style="color: #E11D48;">- {fmt(solde_recupere_revente)} €</strong>
</div>
<div style="display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; color: #065F46; margin-top: 10px; padding-top: 5px; border-top: 1px solid #E2E8F0;">
<span>La mensualité retombe à la cible :</span> <span>{fmt(mens_cible_future)} € / mois</span>
</div>
</div>
</div>
"""
            with col_res2:
                st.markdown(html_s2, unsafe_allow_html=True)

            # --- CONCLUSION PÉDAGOGIQUE ---
            html_conclusion = f"""
<div style="text-align: center; margin-top: 20px; background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 15px; border-radius: 8px;">
<div style="margin: 0; font-size: 16px; font-weight: bold; color: #0F172A;">💡 Le conseil de l'Expert</div>
<div style="margin: 5px 0 0 0; font-size: 14px; color: #334155;">
Le prêt relais est tout à fait viable car il préserve votre PTZ. Cependant, soyez vigilant sur <b>l'effort de trésorerie transitoire ({fmt(mens_totale_phase_relais)} €/mois)</b> exigé par la banque jusqu'à la revente définitive.
</div>
</div>
"""
            st.markdown(html_conclusion, unsafe_allow_html=True)
            
            # --- GRAPHIQUE PÉDAGOGIQUE DU LISSAGE FINAL ---
            st.write("---")
            st.markdown("#### 📊 Fonctionnement de votre crédit définitif (Après la revente)")
            st.write(f"Une fois le Remboursement Anticipé effectué, voici comment la banque calibrera votre nouvelle mensualité de {mens_cible_future} € : le prêt classique (en bleu) viendra parfaitement s'emboîter autour des paliers de votre PTZ conservé (en rose).")
            
            months_array = np.arange(1, duree_nouveau_pret_mois + 1)
            y_ptz_flow = np.array(ptz_flow_futur_padded)
            y_nouveau_pret = mens_cible_future - y_ptz_flow
            
            fig_transf = go.Figure()
            fig_transf.add_trace(go.Scatter(x=months_array/12, y=y_ptz_flow, mode='lines', name='Votre PTZ conservé', stackgroup='one', line=dict(width=0, color="#db2777"), fillcolor="#db2777"))
            fig_transf.add_trace(go.Scatter(x=months_array/12, y=y_nouveau_pret, mode='lines', name=f'Nouveau Prêt ({taux_futur}%)', stackgroup='one', line=dict(width=0, color="#1e3a8a"), fillcolor="#1e3a8a"))
            
            fig_transf.update_layout(
                xaxis=dict(title="Années après la nouvelle acquisition", tickmode="linear", dtick=2),
                yaxis=dict(title="Mensualité (€ / mois)", showgrid=True, gridcolor='#e2e8f0'),
                hovermode="x unified",
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(orientation="h", y=-0.2),
                plot_bgcolor="white"
            )
            st.plotly_chart(fig_transf, use_container_width=True, config={'displayModeBar': False})
