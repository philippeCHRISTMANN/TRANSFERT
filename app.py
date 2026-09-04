import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ & Stratégie Revente", layout="wide")

# Fonction utilitaire pour formater les euros proprement (sans erreur d'affichage Streamlit)
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

# Mensualité actuelle indicative pour pré-remplir la cible
max_len_actuel = max(len(ptz_flow_total), len(pp_flow_total))
ptz_padded_actuel = ptz_flow_total + [0] * (max_len_actuel - len(ptz_flow_total))
pp_padded_actuel = pp_flow_total + [0] * (max_len_actuel - len(pp_flow_total))
total_mensualite_actuelle = [p + m for p, m in zip(ptz_padded_actuel, pp_padded_actuel)]
mensualite_lisse_moyenne = int(max(total_mensualite_actuelle)) if total_mensualite_actuelle else 1000

col_t1, col_t2 = st.columns(2)
with col_t1:
    mens_cible_future = st.number_input("Mensualité cible pour le futur projet (€)", min_value=100, value=mensualite_lisse_moyenne, step=50)
with col_t2:
    taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=4.0, step=0.10)

# --- C. CALCULS MATHÉMATIQUES EXPERTS ---
if len(ptz_flow_total) > 0:
    crd_ptz_transfert = sum(ptz_flow_total)
    
    if crd_ptz_transfert > 0:
        duree_nouveau_pret_mois = 300 # 25 ans
        tm_futur = taux_futur / 100 / 12
        
        # 1. SCÉNARIO : ON SOLDE TOUT (Classique)
        apport_soldetout = max(0, val_estimee - crd_pp - crd_ptz_transfert) + epargne_perso
        if tm_futur > 0:
            capa_bancaire_soldetout = mens_cible_future * ((1 - (1+tm_futur)**-duree_nouveau_pret_mois) / tm_futur)
        else:
            capa_bancaire_soldetout = mens_cible_future * duree_nouveau_pret_mois
        budget_achat_soldetout = apport_soldetout + capa_bancaire_soldetout
        
        # 2. SCÉNARIO : TRANSFERT DU PTZ
        ptz_flow_futur_padded = ptz_flow_total + [0] * (duree_nouveau_pret_mois - len(ptz_flow_total)) if len(ptz_flow_total) < duree_nouveau_pret_mois else ptz_flow_total[:duree_nouveau_pret_mois]
        
        if mens_cible_future <= max(ptz_flow_futur_padded):
            st.error(f"❌ Mensualité cible ({mens_cible_future} €) trop faible pour absorber l'échéance du PTZ conservé.")
        else:
            # Calcul capacité nouveau prêt lissé
            pv_nouveau_pret_lisse = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    pv_nouveau_pret_lisse += (mens_cible_future - ptz_flow_futur_padded[m-1]) / ((1+tm_futur)**m)
            else:
                pv_nouveau_pret_lisse = sum((mens_cible_future - p) for p in ptz_flow_futur_padded)
            
            # --- CALCUL DU TAUX MOYEN PONDÉRÉ DU NOUVEAU FINANCEMENT ---
            total_emprunte_transfert = crd_ptz_transfert + pv_nouveau_pret_lisse
            if total_emprunte_transfert > 0:
                taux_moyen_transfert = (pv_nouveau_pret_lisse * taux_futur) / total_emprunte_transfert
            else:
                taux_moyen_transfert = 0
            
            # --- CALCULS VENTE vs RELAIS (Avec Transfert PTZ) ---
            
            # Cas A : Vente préalable
            cash_vente_secu = max(0, val_estimee - crd_pp) # PTZ conservé !
            apport_total_secu = cash_vente_secu + epargne_perso
            budget_achat_transfert = apport_total_secu + pv_nouveau_pret_lisse + crd_ptz_transfert
            
            # Cas B : Prêt Relais (70% retenu)
            avance_relais = max(0, (val_estimee * 0.70) - crd_pp)
            apport_initial_relais = avance_relais + epargne_perso
            # On gonfle le prêt principal pour atteindre le même budget d'achat
            pret_principal_temporaire = budget_achat_transfert - apport_initial_relais - crd_ptz_transfert
            solde_recupere_revente = cash_vente_secu - avance_relais # Ce qui servira à faire le remboursement anticipé
            
            # --- LE GAIN DU TRANSFERT ---
            gain_transfert_budget = budget_achat_transfert - budget_achat_soldetout

            st.write("---")
            
            # ==========================================
            # 🏆 ENCADRÉ : LE GAIN DU TRANSFERT DE PTZ
            # ==========================================
            html_gain = (
                f"<div style='text-align: center; margin-top: 10px; margin-bottom: 25px; background-color: #F0FDF4; border: 2px dashed #10B981; padding: 20px; border-radius: 8px;'>"
                f"<div style='margin: 0; font-size: 14px; font-weight: 700; color: #065F46; text-transform: uppercase;'>Le pouvoir de la conservation de votre PTZ</div>"
                f"<div style='margin: 5px 0; font-size: 28px; font-weight: 900; color: #047857;'>+ {fmt(gain_transfert_budget)} € de budget d'achat !</div>"
                f"<div style='font-size: 13px; color: #065F46; margin-bottom: 12px;'>"
                f"Par rapport à une situation où vous solderiez tous vos crédits pour repartir de zéro, le simple fait de <b>transférer votre PTZ</b> (taux à 0%) sur le nouveau bien vous offre cette enveloppe supplémentaire pour la <b>même mensualité de {mens_cible_future} €</b>."
                f"</div>"
                f"<div style='display: inline-block; background-color: #D1FAE5; padding: 8px 15px; border-radius: 20px; font-size: 13px; color: #065F46; font-weight: bold; border: 1px solid #34D399;'>"
                f"📉 Taux moyen de votre nouveau financement : {taux_moyen_transfert:.2f} % (au lieu de {taux_futur:.2f} %)"
                f"</div>"
                f"</div>"
            )
            st.markdown(html_gain, unsafe_allow_html=True)

            # ==========================================
            # ⚖️ COMPARATIF STRATÉGIQUE (VENTE VS RELAIS)
            # ==========================================
            st.markdown("### ⚖️ Comment financer cette acquisition ?")
            st.markdown(f"<p style='color: #475569; font-size: 14px;'>Votre budget d'achat avec PTZ transféré s'élève à <b>{fmt(budget_achat_transfert)} €</b>. Voici comment se déroule le plan de financement selon que vous vendez avant, ou après.</p>", unsafe_allow_html=True)
            
            col_res1, col_res2 = st.columns(2)
            
            # --- SCÉNARIO 1 : VENTE D'ABORD ---
            html_s1 = (
                f"<div style='background-color: #F8FAFC; border: 2px solid #3B82F6; border-radius: 8px; padding: 20px; height: 100%;'>"
                f"<h4 style='color: #1E3A8A; margin-top: 0; font-size: 18px;'>1️⃣ Vendre d'abord</h4>"
                f"<p style='color: #334155; font-size: 13px; margin-bottom: 20px;'>Vous encaissez directement 100% de la vente. Le plan de financement est définitif dès la signature.</p>"
                f"<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #BFDBFE;'>"
                f"<div style='color: #1E3A8A; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #BFDBFE; padding-bottom: 5px;'>Plan de financement du projet :</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>"
                f"<span>Fruit de la vente encaissé</span> <strong>{fmt(cash_vente_secu)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>"
                f"<span>Épargne personnelle</span> <strong>{fmt(epargne_perso)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 5px;'>"
                f"<span>PTZ Conservé (Garantie transférée)</span> <strong>{fmt(crd_ptz_transfert)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #0284C7; margin-bottom: 10px;'>"
                f"<span>Nouveau Prêt Bancaire (Lissé)</span> <strong>{fmt(pv_nouveau_pret_lisse)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;'>"
                f"<span>TOTAL BUDGET</span> <span style='color: #0284C7;'>{fmt(budget_achat_transfert)} €</span>"
                f"</div>"
                f"</div>"
                f"<div style='margin-top: 20px; text-align: center; background-color: #F0F9FF; padding: 10px; border-radius: 6px; border: 1px dashed #3B82F6;'>"
                f"<div style='font-size: 12px; color: #0284C7; font-weight: bold;'>Mensualité immédiate et définitive</div>"
                f"<div style='font-size: 22px; font-weight: 900; color: #1E3A8A;'>{fmt(mens_cible_future)} € / mois</div>"
                f"</div>"
                f"</div>"
            )
            with col_res1:
                st.markdown(html_s1, unsafe_allow_html=True)
                
            # --- SCÉNARIO 2 : PRÊT RELAIS ---
            html_s2 = (
                f"<div style='background-color: #FFFBEB; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; height: 100%;'>"
                f"<h4 style='color: #92400E; margin-top: 0; font-size: 18px;'>2️⃣ Prêt Relais (Acheter avant de vendre)</h4>"
                f"<p style='color: #B45309; font-size: 13px; margin-bottom: 20px;'>La banque retient 30% de marge de sécurité. Pour combler l'apport manquant, elle <b>gonfle temporairement le prêt principal</b>.</p>"
                f"<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #FDE68A;'>"
                f"<div style='color: #92400E; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #FDE68A; padding-bottom: 5px;'>Plan de financement temporaire (à l'Achat) :</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>"
                f"<span>Avance Relais (70%)</span> <strong>{fmt(avance_relais)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>"
                f"<span>Épargne personnelle</span> <strong>{fmt(epargne_perso)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 5px;'>"
                f"<span>PTZ Conservé (Garantie transférée)</span> <strong>{fmt(crd_ptz_transfert)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #E11D48; margin-bottom: 10px;' title='Sera réduit lors de la revente.'>"
                f"<span>Nouveau Prêt Principal (Sur-gonflé)</span> <strong>{fmt(pret_principal_temporaire)} €</strong>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;'>"
                f"<span>TOTAL BUDGET</span> <span style='color: #D97706;'>{fmt(budget_achat_transfert)} €</span>"
                f"</div>"
                f"</div>"
            )
            
            with col_res2:
                # Affichage de la carte de base
                st.markdown(html_s2, unsafe_allow_html=True)
                
                # Ajout des réglages de trésorerie DANS la carte relais
                st.markdown("<div style='margin-top: 15px; border-top: 1px dashed #FDE68A; padding-top: 10px;'>", unsafe_allow_html=True)
                st.markdown("<strong style='color:#92400E; font-size:13px;'>⚙️ Alléger la trésorerie avant la revente :</strong>", unsafe_allow_html=True)
                choix_relais = st.radio("Paiement du Prêt Relais :", ["Différé PARTIEL (Intérêts payés)", "Différé TOTAL (0€, intérêts capitalisés)"])
                choix_pp = st.radio("Paiement du Nouveau Prêt :", ["Différé PARTIEL (Intérêts payés)", "Amortissement IMMÉDIAT (Pleine mensualité)"], index=0)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Calculs de la mensualité transitoire
                mens_ptz_actuelle = ptz_flow_futur_padded[0]
                int_relais = avance_relais * ((taux_futur + 0.20) / 100 / 12)
                mens_relais_phase1 = int_relais if "PARTIEL" in choix_relais else 0
                
                int_pp_tempo = pret_principal_temporaire * tm_futur
                mens_pp_pleine = pret_principal_temporaire * tm_futur / (1 - (1+tm_futur)**-300) if tm_futur > 0 else pret_principal_temporaire / 300
                
                mens_pp_phase1 = mens_pp_pleine if "IMMÉDIAT" in choix_pp else int_pp_tempo
                
                mens_totale_phase_relais = mens_ptz_actuelle + mens_relais_phase1 + mens_pp_phase1

                html_s2_footer = (
                    f"<div style='background-color: #FEF2F2; padding: 10px; border-radius: 6px; border: 1px dashed #EF4444; margin-top: 15px; text-align: center;'>"
                    f"<div style='font-size: 12px; color: #B91C1C; font-weight: bold;'>Effort de trésorerie pendant la vente</div>"
                    f"<div style='font-size: 22px; font-weight: 900; color: #9F1239;'>{fmt(mens_totale_phase_relais)} € / mois</div>"
                    f"<div style='font-size: 10px; color: #7F1D1D;'>(PTZ + Relais + Nouveau Prêt selon vos choix)</div>"
                    f"</div>"
                    f"<div style='background-color: white; border-radius: 6px; padding: 12px; border: 1px solid #A7F3D0; margin-top: 15px;'>"
                    f"<div style='color: #065F46; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #A7F3D0; padding-bottom: 5px;'>Phase 2 : À la revente de l'ancien bien</div>"
                    f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>"
                    f"<span>Encaissement du solde (Les 30% restants)</span> <strong style='color: #10B981;'>+ {fmt(solde_recupere_revente)} €</strong>"
                    f"</div>"
                    f"<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>"
                    f"<span>Remboursement Anticipé sur le Prêt Principal</span> <strong style='color: #E11D48;'>- {fmt(solde_recupere_revente)} €</strong>"
                    f"</div>"
                    f"<div style='display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; color: #065F46; margin-top: 10px; padding-top: 5px; border-top: 1px solid #E2E8F0;'>"
                    f"<span>La mensualité retombe à la cible :</span> <span>{fmt(mens_cible_future)} € / mois</span>"
                    f"</div>"
                    f"</div>"
                    f"</div>"
                )
                st.markdown(html_s2_footer, unsafe_allow_html=True)

            # --- F. GRAPHIQUE PÉDAGOGIQUE DU NOUVEAU LISSAGE ---
            st.write("---")
            st.markdown("#### 📊 Fonctionnement de votre crédit définitif (Après la revente)")
            st.write(f"Une fois le Remboursement Anticipé partiel effectué, le prêt principal se dégonfle. Voici comment la banque calibrera votre nouvelle mensualité cible de {mens_cible_future} € : le prêt classique (en bleu) viendra parfaitement s'emboîter autour des paliers de votre PTZ conservé (en rose).")
            
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
