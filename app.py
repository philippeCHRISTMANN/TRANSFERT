import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ & Stratégie Revente", layout="wide")

# Fonction utilitaire pour formater les euros proprement sans casser le HTML
def fmt(n):
    return f"{n:,.0f}".replace(",", " ")

# Algorithme mathématique exact pour le Taux Moyen Lissé (TRI)
def calc_taux_moyen(capital_total, mensualite_constante, duree_mois):
    if capital_total <= 0 or mensualite_constante <= 0 or mensualite_constante * duree_mois <= capital_total:
        return 0.0
    low, high = 0.0, 15.0
    for _ in range(40):
        mid = (low + high) / 2
        tm = mid / 100 / 12
        pv = mensualite_constante * ((1 - (1+tm)**-duree_mois) / tm)
        if pv > capital_total:
            low = mid
        else:
            high = mid
    return (low + high) / 2

# =================================================================
# MODULE : TRANSFERT DE PTZ & STRATÉGIE DE REVENTE
# =================================================================

st.markdown('<div style="font-size: 24px; font-weight: bold; color: #1E3A8A; border-bottom: 3px solid #E91E63; padding-bottom: 5px; margin-bottom: 20px;">🔄 Anticipation : Transfert de PTZ & Prêt Relais</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Découvrez le gain généré par la conservation de votre Prêt à Taux Zéro (PTZ), puis comparez la mécanique financière entre une <b>Vente préalable</b> et un <b>Prêt Relais</b>.</p>", unsafe_allow_html=True)

st.write("---")

# --- A. SAISIE DES DONNÉES ---
st.markdown("### 📝 Étape 1 : La revente de votre bien et vos crédits en cours")
st.info("💡 Placez-vous à la date estimée de votre future vente (ex: dans 3 ou 6 mois). Indiquez la valeur du bien et les capitaux restants dus à cette date.")

col_v1, col_v2 = st.columns(2)
with col_v1:
    val_estimee = st.number_input("Valeur nette vendeuse estimée de votre bien actuel (€)", min_value=0.0, step=5000.0, value=250000.0)
with col_v2:
    epargne_perso = st.number_input("Épargne personnelle ajoutée au projet (€)", min_value=0.0, step=1000.0, value=10000.0)

st.write("")
col_ptz, col_pp = st.columns(2)

with col_ptz:
    st.markdown("#### 🟣 Votre Prêt à Taux Zéro (PTZ)")
    crd_ptz = st.number_input("Capital Restant Dû PTZ en €", min_value=0.0, step=1000.0, value=141750.0)
    is_constant_ptz = st.radio("Mensualités RESTANTES du PTZ :", ("Oui, constantes", "Non, avec paliers"), index=1, key="rad_ptz")
    
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
            with c1: dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=60 if i==0 else 180, key=f"ptz_dur_{i}")
            with c2: men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=0.0 if i==0 else 787.50, key=f"ptz_mens_{i}")
            ptz_flow_total.extend([men_p] * int(dur_p))

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
st.markdown("### 🎯 Étape 2 : Le futur projet (Acquisition)")

max_len_actuel = max(len(ptz_flow_total), len(pp_flow_total))
ptz_padded_actuel = ptz_flow_total + [0] * (max_len_actuel - len(ptz_flow_total))
pp_padded_actuel = pp_flow_total + [0] * (max_len_actuel - len(pp_flow_total))
total_mensualite_actuelle = [p + m for p, m in zip(ptz_padded_actuel, pp_padded_actuel)]
mensualite_lisse_moyenne = int(max(total_mensualite_actuelle)) if total_mensualite_actuelle else 1000

col_t1, col_t2 = st.columns(2)
with col_t1:
    mens_cible_future = st.number_input("Mensualité cible pour le futur projet (€)", min_value=100, value=1637, step=50, help="Nous reprenons par défaut la mensualité maximale que vous payez actuellement.")
with col_t2:
    taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=3.60, step=0.10)

# --- C. CALCULS MATHÉMATIQUES EXPERTS ---
if len(ptz_flow_total) == 0:
    st.warning("⚠️ Vous n'avez pas saisi de durée ou de mensualité pour le PTZ. Les calculs ne peuvent pas aboutir.")
else:
    crd_ptz_transfert = sum(ptz_flow_total)
    
    if crd_ptz_transfert <= 0:
        st.warning("Le capital restant dû de votre PTZ sera de 0 €. Le transfert est sans objet.")
    else:
        duree_nouveau_pret_mois = 300 # 25 ans
        tm_futur = taux_futur / 100 / 12
        
        # -------------------------------------------------------------
        # SCÉNARIO A : ON SOLDE TOUT ET ON REPART DE ZÉRO
        # -------------------------------------------------------------
        cash_soldetout = val_estimee - crd_pp - crd_ptz_transfert
        apport_soldetout = cash_soldetout + epargne_perso
        
        if tm_futur > 0:
            capa_bancaire_soldetout = mens_cible_future * ((1 - (1+tm_futur)**-duree_nouveau_pret_mois) / tm_futur)
        else:
            capa_bancaire_soldetout = mens_cible_future * duree_nouveau_pret_mois
            
        budget_achat_soldetout = apport_soldetout + capa_bancaire_soldetout
        
        # -------------------------------------------------------------
        # SCÉNARIO B : ON TRANSFÈRE LE PTZ (LISSAGE)
        # -------------------------------------------------------------
        ptz_flow_futur_padded = ptz_flow_total + [0] * (duree_nouveau_pret_mois - len(ptz_flow_total)) if len(ptz_flow_total) < duree_nouveau_pret_mois else ptz_flow_total[:duree_nouveau_pret_mois]
        
        if mens_cible_future <= max(ptz_flow_futur_padded):
            st.error(f"❌ Mensualité cible ({mens_cible_future} €) trop faible pour absorber l'échéance du PTZ conservé.")
        else:
            pv_nouveau_pret_lisse = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret_lisse += disponible_mensuel / ((1+tm_futur)**m)
            else:
                pv_nouveau_pret_lisse = sum((mens_cible_future - p) for p in ptz_flow_futur_padded)
            
            # Le cash net de la vente (On ne rembourse QUE le prêt principal)
            cash_transfert = val_estimee - crd_pp
            apport_transfert = cash_transfert + epargne_perso
            
            # Le Budget d'achat, c'est l'Apport (qui contient l'argent du PTZ !) + Le nouveau prêt lissé.
            budget_achat_transfert = apport_transfert + pv_nouveau_pret_lisse
            
            # --- LE GAIN PUR (Intérêts évités par le lissage) ---
            gain_transfert_budget = budget_achat_transfert - budget_achat_soldetout
            
            # --- CALCUL DU VRAI TAUX MOYEN PONDÉRÉ LISSÉ (TRI ACTUARIEL) ---
            dette_totale_en_cours = crd_ptz_transfert + pv_nouveau_pret_lisse
            taux_moyen_transfert = calc_taux_moyen(dette_totale_en_cours, mens_cible_future, duree_nouveau_pret_mois) * 100

            # ==========================================
            # PARTIE 1 : L'AVANTAGE DU TRANSFERT (LE BUDGET)
            # ==========================================
            st.write("---")
            st.markdown("### 🏆 Étape 3 : Faut-il conserver votre PTZ ?")
            st.markdown("<p style='color: #475569; font-size: 14px;'>Voici mathématiquement pourquoi le transfert de votre PTZ vous fait gagner de l'argent sur votre enveloppe immobilière par rapport à un rachat de crédit classique.</p>", unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            
            html_b1 = f"""
<div style='background-color: #FFF1F2; border: 2px solid #FECDD3; border-radius: 8px; padding: 20px; height: 100%;'>
<h4 style='color: #9F1239; margin-top: 0;'>❌ Si vous soldez tous vos crédits</h4>
<p style='color: #BE123C; font-size: 13px; margin-bottom: 20px;'>Vous remboursez le Prêt Principal ET le PTZ lors de la vente. Vous repartez avec un nouveau crédit unique à {taux_futur} %.</p>
<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #FECDD3;'>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Fruit de la vente (Net des 2 crédits)</span> <strong style="color:{'#E11D48' if cash_soldetout < 0 else '#475569'};">{fmt(cash_soldetout)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Épargne personnelle</span> <strong>{fmt(epargne_perso)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #E11D48; margin-bottom: 10px;'>
<span>Nouveau Prêt Bancaire à {taux_futur}%</span> <strong>{fmt(capa_bancaire_soldetout)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 15px; color: #9F1239; font-weight: 900; border-top: 2px solid #FECDD3; padding-top: 5px;'>
<span>BUDGET D'ACHAT MAXIMAL</span> <span>{fmt(budget_achat_soldetout)} €</span>
</div>
</div>
</div>
"""
            with col_b1:
                st.markdown(html_b1, unsafe_allow_html=True)
                
            html_b2 = f"""
<div style='background-color: #ECFDF5; border: 2px solid #10B981; border-radius: 8px; padding: 20px; height: 100%; position: relative;'>
<div style='position: absolute; top: -12px; right: 20px; background-color: #10B981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;'>LA BONNE STRATÉGIE</div>
<h4 style='color: #065F46; margin-top: 0;'>✅ Si vous transférez le PTZ</h4>
<p style='color: #047857; font-size: 13px; margin-bottom: 20px;'>Vous ne remboursez pas le PTZ au notaire. La banque crée un nouveau prêt qui s'emboîte autour de vos anciennes mensualités.</p>
<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #A7F3D0;'>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Fruit de la vente (Seul le prêt principal est soldé)</span> <strong style="color:{'#E11D48' if cash_transfert < 0 else '#475569'};">{fmt(cash_transfert)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Épargne personnelle</span> <strong>{fmt(epargne_perso)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #0284C7; margin-bottom: 10px;'>
<span>Nouveau Prêt Bancaire (Lissé) à {taux_futur}%</span> <strong>{fmt(pv_nouveau_pret_lisse)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 15px; color: #059669; font-weight: 900; border-top: 2px solid #A7F3D0; padding-top: 5px;'>
<span>BUDGET D'ACHAT MAXIMAL</span> <span>{fmt(budget_achat_transfert)} €</span>
</div>
</div>
</div>
"""
            with col_b2:
                st.markdown(html_b2, unsafe_allow_html=True)

            html_gain = f"""
<div style='text-align: center; margin-top: 20px; background-color: #F0F9FF; border: 2px dashed #0EA5E9; padding: 20px; border-radius: 8px;'>
<div style='margin: 0; font-size: 24px; font-weight: 900; color: #0284C7;'>🚀 Le transfert vous fait gagner {fmt(gain_transfert_budget)} € de budget d'achat !</div>
<div style='font-size: 13px; color: #0369A1; margin-top: 8px; margin-bottom: 15px; max-width: 800px; margin-left: auto; margin-right: auto;'>
En conservant {fmt(crd_ptz_transfert)} € à 0% au lieu de les emprunter au taux actuel, vous faites une économie d'intérêts massive. C'est du pur pouvoir d'achat récupéré pour la <b>même mensualité globale de {fmt(mens_cible_future)} €</b>.
</div>
<div style='display: inline-block; background-color: white; padding: 6px 15px; border-radius: 20px; font-size: 13px; color: #0284C7; font-weight: bold; border: 1px solid #BAE6FD;'>
📉 Taux moyen lissé de votre financement : {taux_moyen_transfert:.2f} % (au lieu de {taux_futur:.2f} %)
</div>
</div>
"""
            st.markdown(html_gain, unsafe_allow_html=True)


            # ==========================================
            # PARTIE 2 : LA LOGISTIQUE (VENTE VS RELAIS)
            # ==========================================
            st.write("---")
            st.markdown("### ⚖️ Étape 4 : Comment gérer la transition (Logistique)")
            st.markdown(f"<p style='color: #475569; font-size: 14px;'>Maintenant que nous avons validé le transfert du PTZ (Budget d'achat ciblé : <b>{fmt(budget_achat_transfert)} €</b>), comment allez-vous acheter le nouveau bien ? Voici la logistique.</p>", unsafe_allow_html=True)
            
            # --- Calculs Prêt Relais Exacts ---
            avance_relais = max(0, (val_estimee * 0.70) - crd_pp)
            apport_initial_relais = avance_relais + epargne_perso
            
            # Mécanique bancaire pure : on gonfle le prêt principal en attendant la revente !
            pret_principal_temporaire = budget_achat_transfert - apport_initial_relais
            solde_recupere_revente = cash_transfert - avance_relais 
            
            col_r1, col_r2 = st.columns(2)
            
            # SCÉNARIO 1 : VENTE D'ABORD
            html_s1_log = f"""
<div style='background-color: #F8FAFC; border: 2px solid #94A3B8; border-radius: 8px; padding: 20px; height: 100%;'>
<h4 style='color: #334155; margin-top: 0; font-size: 18px;'>1️⃣ Vendre d'abord (Location de transition)</h4>
<p style='color: #475569; font-size: 13px; margin-bottom: 20px;'>Vous vendez avant d'acheter. Vous encaissez directement le fruit de la vente. Le plan de financement est définitif dès le 1er jour.</p>

<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #E2E8F0;'>
<div style='color: #334155; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #E2E8F0; padding-bottom: 5px;'>Montage financier le jour de l'achat :</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Apport (Vente 100% + Épargne)</span> <strong>{fmt(apport_transfert)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #0284C7; margin-bottom: 10px;'>
<span>Nouveau Prêt Bancaire (Définitif)</span> <strong>{fmt(pv_nouveau_pret_lisse)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;'>
<span>BUDGET D'ACHAT ATTEINT</span> <span>{fmt(budget_achat_transfert)} €</span>
</div>
<div style='font-size: 11px; color: #DB2777; margin-top: 8px; padding-top: 6px; border-top: 1px solid #FBCFE8;'>
<i>* Votre ancien PTZ ({fmt(crd_ptz_transfert)} €) est rattaché à ce nouveau bien.</i>
</div>
</div>

<div style='margin-top: 20px; text-align: center; background-color: #F1F5F9; padding: 10px; border-radius: 6px;'>
<div style='font-size: 12px; color: #475569; font-weight: bold;'>Mensualité immédiate et définitive</div>
<div style='font-size: 22px; font-weight: 900; color: #1E293B;'>{fmt(mens_cible_future)} € / mois</div>
<div style='font-size: 10px; color: #64748B;'>(PTZ transféré + Nouveau Prêt)</div>
</div>
</div>
"""
            with col_r1:
                st.markdown(html_s1_log, unsafe_allow_html=True)
                
            # SCÉNARIO 2 : PRÊT RELAIS
            html_s2_log = f"""
<div style='background-color: #FFFBEB; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; height: 100%;'>
<h4 style='color: #92400E; margin-top: 0; font-size: 18px;'>2️⃣ Prêt Relais (Acheter avant de vendre)</h4>
<p style='color: #B45309; font-size: 13px; margin-bottom: 20px;'>La banque applique sa décote (70%). Pour combler le manque d'apport à l'achat, le <b>prêt principal est gonflé temporairement</b>.</p>

<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #FDE68A;'>
<div style='color: #92400E; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #FDE68A; padding-bottom: 5px;'>Phase 1 : L'Achat (Avant la revente)</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Avance Relais (70%) + Épargne</span> <strong>{fmt(apport_initial_relais)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #E11D48; margin-bottom: 10px;' title='Sera réduit lors de la revente.'>
<span>Nouveau Prêt Principal (Sur-gonflé)</span> <strong>{fmt(pret_principal_temporaire)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;'>
<span>BUDGET D'ACHAT ATTEINT</span> <span style='color: #D97706;'>{fmt(budget_achat_transfert)} €</span>
</div>
<div style='font-size: 11px; color: #DB2777; margin-top: 8px; padding-top: 6px; border-top: 1px solid #FBCFE8;'>
<i>* Votre ancien PTZ ({fmt(crd_ptz_transfert)} €) est rattaché à ce nouveau bien.</i>
</div>
</div>
"""
            with col_r2:
                # Affichage du haut de la carte
                st.markdown(html_s2_log, unsafe_allow_html=True)
                
                # Paramètres de trésorerie DANS la carte (Interactif)
                st.markdown("<div style='margin-top: 15px; border-top: 1px dashed #FDE68A; padding-top: 10px;'>", unsafe_allow_html=True)
                st.markdown("<strong style='color:#92400E; font-size:13px;'>⚙️ Alléger la trésorerie avant la revente :</strong>", unsafe_allow_html=True)
                choix_relais = st.radio("Paiement de l'avance Relais :", ["Différé PARTIEL (Payer les intérêts)", "Différé TOTAL (0€, intérêts capitalisés)"])
                choix_pp = st.radio("Paiement du Prêt Principal temporaire :", ["Différé PARTIEL (Payer les intérêts)", "Amortissement IMMÉDIAT (Pleine mensualité)"], index=0)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Calculs de la mensualité transitoire
                mens_ptz_actuelle = ptz_flow_futur_padded[0]
                int_relais = avance_relais * ((taux_futur + 0.20) / 100 / 12)
                mens_relais_phase1 = int_relais if "PARTIEL" in choix_relais else 0
                
                int_pp_tempo = pret_principal_temporaire * tm_futur
                mens_pp_pleine = pret_principal_temporaire * tm_futur / (1 - (1+tm_futur)**-300) if tm_futur > 0 else pret_principal_temporaire / 300
                mens_pp_phase1 = mens_pp_pleine if "IMMÉDIAT" in choix_pp else int_pp_tempo
                
                mens_totale_phase_relais = mens_ptz_actuelle + mens_relais_phase1 + mens_pp_phase1

                # Affichage du bas de la carte
                html_s2_footer = f"""
<div style='background-color: #FEF2F2; padding: 10px; border-radius: 6px; border: 1px dashed #EF4444; margin-top: 15px; text-align: center;'>
<div style='font-size: 12px; color: #B91C1C; font-weight: bold;'>Effort de trésorerie pendant la vente</div>
<div style='font-size: 22px; font-weight: 900; color: #9F1239;'>{fmt(mens_totale_phase_relais)} € / mois</div>
<div style='font-size: 10px; color: #7F1D1D;'>(PTZ Transféré + Relais + Prêt Gonflé)</div>
</div>

<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #A7F3D0; margin-top: 15px;'>
<div style='color: #065F46; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #A7F3D0; padding-bottom: 5px;'>Phase 2 : À la revente de l'ancien bien</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>
<span>Encaissement du solde restant</span> <strong style='color: #10B981;'>+ {fmt(solde_recupere_revente)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>
<span>Remb. Anticipé du Prêt Principal</span> <strong style='color: #E11D48;'>- {fmt(solde_recupere_revente)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; color: #065F46; margin-top: 10px; padding-top: 5px; border-top: 1px solid #E2E8F0;'>
<span>La mensualité retombe à la cible :</span> <span>{fmt(mens_cible_future)} € / mois</span>
</div>
</div>
</div>
"""
                st.markdown(html_s2_footer, unsafe_allow_html=True)


            # --- F. GRAPHIQUE PÉDAGOGIQUE DU NOUVEAU LISSAGE ---
            st.write("---")
            st.markdown("#### 📊 Fonctionnement de votre crédit définitif (Après la revente)")
            st.write(f"Une fois l'ancien bien vendu et le Remboursement Anticipé partiel effectué, le prêt principal se dégonfle. Voici comment la banque calibrera votre nouvelle mensualité cible de {mens_cible_future} € : le prêt classique (en bleu) viendra parfaitement s'emboîter autour des paliers de votre PTZ conservé (en rose).")
            
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
