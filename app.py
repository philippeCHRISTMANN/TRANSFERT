

import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ", layout="wide")


# Fonction utilitaire pour formater les euros proprement sans casser le HTML
def fmt(n):
    return f"{n:,.0f}".replace(",", " ")

# Algorithme mathématique exact pour le Taux Moyen Lissé (TRI Actuariel)
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
# GESTION DES ÉTAPES (NAVIGATION)
# =================================================================
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# =================================================================
# HEADER GLOBAL
# =================================================================
st.markdown('<div style="font-size: 24px; font-weight: bold; color: #1E3A8A; border-bottom: 3px solid #E91E63; padding-bottom: 5px; margin-bottom: 20px;">🔄 Anticipation : Transfert de PTZ & Prêt Relais</div>', unsafe_allow_html=True)

# Barre de progression
progress_val = (st.session_state.step - 1) / 3.0
st.progress(progress_val)
st.write("---")

# --- BANNIÈRE AVEC IMAGE DE FOND ET TEXTE SUPERPOSÉ ---
# Remplacez l'URL par l'adresse de l'image que vous souhaitez utiliser.
url_image = "https://www.econopret.fr/" 

st.markdown(f"""
<style>
.hero-banner {{
    background-image: linear-gradient(rgba(0, 51, 102, 0.7), rgba(0, 51, 102, 0.4)), url('{url_image}');
    background-size: cover;
    background-position: center;
    border-radius: 12px;
    padding: 60px 40px;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}}
.hero-title {{
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 10px;
    line-height: 1.2;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
.hero-subtitle {{
    font-size: 20px;
    font-weight: 400;
    max-width: 700px;
    margin-top: 10px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}}
</style>

<div class="hero-banner">
    <div class="hero-title">Anticipation : Transfert de PTZ & Prêt Relais</div>
    <div class="hero-subtitle">
        Découvrez le gain généré par la conservation de votre Prêt à Taux Zéro (PTZ), 
        puis comparez la mécanique d'achat entre une <b>Vente préalable</b> et un <b>Prêt Relais</b>.
    </div>
</div>
""", unsafe_allow_html=True)

# =================================================================
# ÉTAPE 1 : RÈGLEMENTATION PTZ
# =================================================================
if st.session_state.step == 1:
    st.markdown("### 📚 Étape 1 : Les règles du transfert de PTZ")
    st.markdown("<p style='color: #64748B; font-size: 15px;'>Avant de commencer, voici un rappel de la réglementation en vigueur (Source : Service-Public.fr).</p>", unsafe_allow_html=True)
    
    html_regles = """
<div style="background-color: #F8FAFC; padding: 20px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 20px; border: 1px solid #E2E8F0;">
<p style="font-size: 14px; color: #334155; margin-bottom: 15px;">La loi vous permet de conserver les avantages de votre Prêt à Taux Zéro en cours si vous revendez votre logement pour acheter une <b>nouvelle résidence principale</b>. Le transfert ne concerne que le <b>Capital Restant Dû (CRD)</b>. Cependant, la date de revente change tout :</p>

<strong style="color: #1E3A8A; font-size: 15px;">⏳ Revente MOINS de 6 ans après le versement du PTZ</strong>
<ul style="font-size: 14px; color: #475569; margin-top: 5px; margin-bottom: 15px;">
<li>Votre nouveau logement <b>doit respecter les conditions d'éligibilité au PTZ en vigueur à la date du transfert</b>.</li>
<li><i>Exemple :</i> Pour transférer un PTZ vers un logement ancien avant 6 ans, la nouvelle maison devra impérativement se situer en zone détendue (B2 ou C), et vous devrez y réaliser au moins 25% de travaux d'amélioration. Si vous visez de l'ancien sans travaux, le transfert sera refusé.</li>
</ul>

<strong style="color: #10B981; font-size: 15px;">⌛ Revente PLUS de 6 ans après le versement du PTZ</strong>
<ul style="font-size: 14px; color: #475569; margin-top: 5px; margin-bottom: 15px;">
<li><b>Aucune condition d'éligibilité n'est exigée sur la typologie du nouveau logement !</b></li>
<li><i>Exemple :</i> Vous pouvez acheter n'importe quel logement ancien, où vous voulez, avec ou sans travaux, et transférer votre PTZ à 0% dessus.</li>
</ul>

<strong style="color: #9333EA; font-size: 15px;">💡 Ce qui n'est PLUS contrôlé (Revenus et Primo-accession)</strong>
<ul style="font-size: 14px; color: #475569; margin-top: 5px;">
<li>Lors d'un transfert, <b>les plafonds de revenus (RFR) ne sont pas recalculés</b>. Même si votre salaire a fortement augmenté, vous conservez votre PTZ.</li>
<li>La condition de <b>primo-accédant</b> n'est plus exigée non plus (logique, puisque vous revendez un bien !).</li>
</ul>

<div style="background-color: #FEF2F2; padding: 12px; border-radius: 6px; border: 1px solid #FCA5A5; font-size: 13px; color: #991B1B; margin-top: 20px;">
<b>⚠️ Accord Bancaire :</b> Dans tous les cas, le transfert n'est pas automatique. La banque refusera l'opération si elle estime que vos nouvelles capacités de remboursement ou la garantie du nouveau bien sont insuffisantes pour absorber le nouveau prêt complémentaire.
</div>
</div>
"""
    st.markdown(html_regles, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        st.button("J'ai compris, suivant ➡️", on_click=next_step, type="primary", use_container_width=True)

# =================================================================
# ÉTAPE 2 : LE PTZ EN COURS
# =================================================================
elif st.session_state.step == 2:
    st.markdown("### 🟣 Étape 2 : Votre Prêt à Taux Zéro en cours")
    st.info("💡 Placez-vous à la date estimée de votre future vente (ex: dans 3 ou 6 mois). Prenez votre tableau d'amortissement actuel à cette date.")

    crd_ptz = st.number_input("Capital Restant Dû sur le PTZ (€)", min_value=0.0, step=1000.0, value=st.session_state.get('crd_ptz', 40000.0))
    is_constant_ptz = st.radio("Mensualités RESTANTES du PTZ :", ("Oui, constantes", "Non, avec paliers"), index=st.session_state.get('idx_rad_ptz', 1))
    
    ptz_flow_total = []
    if is_constant_ptz.startswith("Oui"):
        duree_ptz = st.number_input("Mensualités RESTANTES PTZ", min_value=1, step=12, value=st.session_state.get('dur_ptz_const', 204))
        mens_ptz = crd_ptz / duree_ptz if duree_ptz > 0 else 0
        st.success(f"Mensualité calculée : **{mens_ptz:.2f} € / mois**")
        ptz_flow_total = [mens_ptz] * int(duree_ptz)
        
        # Sauvegardes
        st.session_state['idx_rad_ptz'] = 0
        st.session_state['dur_ptz_const'] = duree_ptz
    else:
        st.session_state['idx_rad_ptz'] = 1
        nb_paliers_ptz = st.number_input("Nombre de paliers RESTANTS", min_value=2, max_value=6, value=st.session_state.get('nb_pal_ptz', 2))
        st.session_state['nb_pal_ptz'] = nb_paliers_ptz
        
        capital_rembourse = 0
        for i in range(int(nb_paliers_ptz)):
            c1, c2 = st.columns(2)
            with c1: 
                dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=st.session_state.get(f"ptz_dur_{i}", 60 if i==0 else 180), key=f"ptz_dur_{i}")
            
            # Saisie manuelle pour tous SAUF le dernier
            if i < int(nb_paliers_ptz) - 1:
                with c2: 
                    men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=st.session_state.get(f"ptz_mens_{i}", 0.0 if i==0 else 787.50), key=f"ptz_mens_{i}")
                capital_rembourse += (men_p * dur_p)
                ptz_flow_total.extend([men_p] * int(dur_p))
            
            # Calcul auto pour le dernier palier
            else:
                crd_restant = crd_ptz - capital_rembourse
                men_p = crd_restant / dur_p if (dur_p > 0 and crd_restant > 0) else 0
                with c2:
                    st.text_input(f"Mensualité Palier {i+1} (€)", value=f"{men_p:.2f} (Calcul auto)", disabled=True)
                
                if crd_restant < 0:
                    st.error("⚠️ Les mensualités des paliers précédents remboursent déjà plus que votre Capital Restant Dû !")
                
                ptz_flow_total.extend([men_p] * int(dur_p))

    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("⬅️ Précédent", on_click=prev_step, use_container_width=True)
    with col3:
        if st.button("Suivant ➡️", type="primary", use_container_width=True):
            # Sauvegarde des données PTZ avant de changer d'étape
            st.session_state['crd_ptz'] = crd_ptz
            st.session_state['ptz_flow_total'] = ptz_flow_total
            next_step()
            st.rerun()

# =================================================================
# ÉTAPE 3 : PRÊT PRINCIPAL ET VENTE
# =================================================================
elif st.session_state.step == 3:
    st.markdown("### 🔵 Étape 3 : Le Prêt Principal et la Vente")
    st.info("💡 Continuez à vous projeter à la date de revente. Indiquez la valeur du bien et le prêt principal en cours.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        val_estimee = st.number_input("Valeur nette vendeuse estimée de votre bien actuel (€)", min_value=0.0, step=5000.0, value=st.session_state.get('val_estimee', 250000.0))
    with col_v2:
        epargne_perso = st.number_input("Épargne personnelle ajoutée au projet (€)", min_value=0.0, step=1000.0, value=st.session_state.get('epargne_perso', 10000.0))

    st.write("")
    
    crd_pp = st.number_input("Capital Restant Dû sur le Prêt Principal (€)", min_value=0.0, step=1000.0, value=st.session_state.get('crd_pp', 150000.0))
    is_constant_pp = st.radio("Mensualités RESTANTES du Prêt Principal :", ("Oui, constantes", "Non, avec paliers"), index=st.session_state.get('idx_rad_pp', 0))
    
    pp_flow_total = []
    if is_constant_pp.startswith("Oui"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            mens_pp = st.number_input("Mensualité Prêt Principal (€)", min_value=0.0, step=10.0, value=st.session_state.get('mens_pp_const', 850.0))
        with col_c2:
            duree_pp = st.number_input("Mensualités RESTANTES Prêt Principal", min_value=1, step=12, value=st.session_state.get('dur_pp_const', 204))
        pp_flow_total = [mens_pp] * int(duree_pp)
        
        st.session_state['idx_rad_pp'] = 0
        st.session_state['mens_pp_const'] = mens_pp
        st.session_state['dur_pp_const'] = duree_pp
    else:
        st.session_state['idx_rad_pp'] = 1
        nb_paliers_pp = st.number_input("Nombre de paliers RESTANTS", min_value=1, max_value=6, value=st.session_state.get('nb_pal_pp', 2))
        st.session_state['nb_pal_pp'] = nb_paliers_pp
        for i in range(int(nb_paliers_pp)):
            c1, c2 = st.columns(2)
            with c1: 
                dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=st.session_state.get(f"pp_dur_{i}", 120 if i==0 else 84), key=f"pp_dur_{i}")
            with c2: 
                men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=st.session_state.get(f"pp_mens_{i}", 1000.0 if i==0 else 800.0), key=f"pp_mens_{i}")
            pp_flow_total.extend([men_p] * int(dur_p))

    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("⬅️ Précédent", on_click=prev_step, use_container_width=True)
    with col3:
        if st.button("Suivant ➡️", type="primary", use_container_width=True):
            st.session_state['val_estimee'] = val_estimee
            st.session_state['epargne_perso'] = epargne_perso
            st.session_state['crd_pp'] = crd_pp
            st.session_state['pp_flow_total'] = pp_flow_total
            next_step()
            st.rerun()

# =================================================================
# ÉTAPE 4 : LE FUTUR PROJET & RÉSULTATS
# =================================================================
elif st.session_state.step == 4:
    st.markdown("### 🎯 Étape 4 : Le futur projet et les résultats")
    
    html_disclaimer = """
<div style="background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
<strong style="color: #B45309; font-size: 14px;">⚠️ Précision importante sur l'objectif de cet outil :</strong>
<p style="color: #92400E; font-size: 13px; margin-top: 5px; margin-bottom: 0;">
L'objectif de ce simulateur n'est <b>pas</b> de calculer votre capacité d'achat personnalisée (il ne tient pas compte de vos revenus, de votre taux d'endettement maximum autorisé, ni de vos crédits conso ou LOA en cours). Son but est <b>uniquement de mesurer l'impact mathématique et financier d'un transfert de PTZ</b> sur votre enveloppe budgétaire, à effort équivalent.
</p>
</div>
"""
    st.markdown(html_disclaimer, unsafe_allow_html=True)

    # Récupération des données mémorisées
    ptz_flow_total = st.session_state.get('ptz_flow_total', [])
    pp_flow_total = st.session_state.get('pp_flow_total', [])
    val_estimee = st.session_state.get('val_estimee', 0)
    epargne_perso = st.session_state.get('epargne_perso', 0)
    crd_ptz = st.session_state.get('crd_ptz', 0)
    crd_pp = st.session_state.get('crd_pp', 0)

    # Mensualité actuelle indicative pour pré-remplir la cible
    max_len_actuel = max(len(ptz_flow_total), len(pp_flow_total))
    ptz_padded_actuel = ptz_flow_total + [0] * (max_len_actuel - len(ptz_flow_total))
    pp_padded_actuel = pp_flow_total + [0] * (max_len_actuel - len(pp_flow_total))
    total_mensualite_actuelle = [p + m for p, m in zip(ptz_padded_actuel, pp_padded_actuel)]
    mensualite_lisse_moyenne = int(max(total_mensualite_actuelle)) if total_mensualite_actuelle else 1000

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        mens_cible_future = st.number_input("Mensualité cible de référence (€)", min_value=100, value=mensualite_lisse_moyenne, step=50, help="Nous reprenons par défaut la mensualité maximale que vous payez actuellement pour faire une comparaison équitable.")
    with col_t2:
        taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=3.60, step=0.10)

    if len(ptz_flow_total) == 0:
        st.error("Aucune donnée de PTZ trouvée en mémoire. Veuillez recommencer l'étape 2.")
    else:
        crd_ptz_transfert = sum(ptz_flow_total)
        
        if crd_ptz_transfert <= 0:
            st.warning("Le capital restant dû de votre PTZ est de 0 €. Le transfert n'a pas d'impact.")
        else:
            duree_nouveau_pret_mois = 300 # 25 ans
            tm_futur = taux_futur / 100 / 12
            
            # --- SCÉNARIO A : ON SOLDE TOUT ---
            cash_soldetout = val_estimee - crd_pp - crd_ptz_transfert
            apport_soldetout = cash_soldetout + epargne_perso
            
            if tm_futur > 0:
                capa_bancaire_soldetout = mens_cible_future * ((1 - (1+tm_futur)**-duree_nouveau_pret_mois) / tm_futur)
            else:
                capa_bancaire_soldetout = mens_cible_future * duree_nouveau_pret_mois
                
            budget_achat_soldetout = apport_soldetout + capa_bancaire_soldetout
            
            # --- SCÉNARIO B : TRANSFERT DU PTZ ---
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
                
                cash_transfert = val_estimee - crd_pp
                apport_transfert = cash_transfert + epargne_perso
                budget_achat_transfert = apport_transfert + pv_nouveau_pret_lisse
                
                gain_transfert_budget = budget_achat_transfert - budget_achat_soldetout
                
                dette_totale_en_cours = crd_ptz_transfert + pv_nouveau_pret_lisse
                taux_moyen_transfert = calc_taux_moyen(dette_totale_en_cours, mens_cible_future, duree_nouveau_pret_mois) * 100

                # ==========================================
                # RÉSULTATS : L'AVANTAGE DU TRANSFERT 
                # ==========================================
                st.write("---")
                st.markdown("### 🏆 Faut-il conserver votre PTZ ?")
                
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
                # RÉSULTATS : LOGISTIQUE (VENTE VS RELAIS)
                # ==========================================
                st.write("---")
                st.markdown("### ⚖️ Comment gérer la transition (Logistique)")
                st.markdown(f"<p style='color: #475569; font-size: 14px;'>Sachant que vous transférez le PTZ (Budget d'achat ciblé : <b>{fmt(budget_achat_transfert)} €</b>), comment allez-vous acheter le nouveau bien ? Voici la logistique de transition.</p>", unsafe_allow_html=True)
                
                # --- Calculs Prêt Relais Exacts ---
                avance_relais = max(0, (val_estimee * 0.70) - crd_pp)
                apport_initial_relais = avance_relais + epargne_perso
                pret_principal_temporaire = budget_achat_transfert - apport_initial_relais
                solde_recupere_revente = cash_transfert - avance_relais 
                
                col_r1, col_r2 = st.columns(2)
                
                # SCÉNARIO 1 : VENTE D'ABORD
                html_s1_log = f"""
<div style='background-color: #F8FAFC; border: 2px solid #94A3B8; border-radius: 8px; padding: 20px; height: 100%;'>
<h4 style='color: #334155; margin-top: 0; font-size: 18px;'>1️⃣ Vendre d'abord (Location de transition)</h4>
<p style='color: #475569; font-size: 13px; margin-bottom: 20px;'>Vous vendez avant d'acheter. Vous encaissez directement le fruit de la vente. Le plan de financement est définitif dès le 1er jour.</p>

<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #E2E8F0;'>
<div style='color: #334155; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #E2E8F0; padding-bottom: 5px;'>Montage financier au jour de l'achat :</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #475569; margin-bottom: 5px;'>
<span>Apport (Vente 100% encaissée + Épargne)</span> <strong>{fmt(apport_transfert)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #0284C7; margin-bottom: 10px;'>
<span>Nouveau Prêt Bancaire (Définitif)</span> <strong>{fmt(pv_nouveau_pret_lisse)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 15px; color: #0F172A; font-weight: 900; border-top: 2px solid #E2E8F0; padding-top: 5px;'>
<span>BUDGET D'ACHAT ATTEINT</span> <span>{fmt(budget_achat_transfert)} €</span>
</div>
<div style='font-size: 11px; color: #DB2777; margin-top: 8px; padding-top: 6px; border-top: 1px solid #FBCFE8;'>
<i>* Votre ancien PTZ ({fmt(crd_ptz_transfert)} €) est rattaché à ce nouveau bien en garantie.</i>
</div>
</div>

<div style='margin-top: 20px; text-align: center; background-color: #F1F5F9; padding: 10px; border-radius: 6px;'>
<div style='font-size: 12px; color: #475569; font-weight: bold;'>Mensualité immédiate et définitive</div>
<div style='font-size: 22px; font-weight: 900; color: #1E293B;'>{fmt(mens_cible_future)} € / mois</div>
<div style='font-size: 10px; color: #64748B;'>(PTZ transféré + Nouveau Prêt Lissé)</div>
</div>
</div>
"""
                with col_r1:
                    st.markdown(html_s1_log, unsafe_allow_html=True)
                    
                # SCÉNARIO 2 : PRÊT RELAIS
                html_s2_log = f"""
<div style='background-color: #FFFBEB; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; height: 100%;'>
<h4 style='color: #92400E; margin-top: 0; font-size: 18px;'>2️⃣ Prêt Relais (Acheter avant de vendre)</h4>
<p style='color: #B45309; font-size: 13px; margin-bottom: 20px;'>La banque applique sa décote (70%). Pour combler l'apport manquant à l'achat, le <b>prêt principal est gonflé temporairement</b>.</p>

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
<i>* Votre ancien PTZ ({fmt(crd_ptz_transfert)} €) est rattaché à ce nouveau bien en garantie.</i>
</div>
</div>
"""
                with col_r2:
                    st.markdown(html_s2_log, unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-top: 15px; border-top: 1px dashed #FDE68A; padding-top: 10px;'>", unsafe_allow_html=True)
                    st.markdown("<strong style='color:#92400E; font-size:13px;'>⚙️ Alléger la trésorerie avant la revente :</strong>", unsafe_allow_html=True)
                    choix_relais = st.radio("Paiement de l'avance Relais :", ["Différé PARTIEL (Payer les intérêts)", "Différé TOTAL (0€, intérêts capitalisés)"])
                    choix_pp = st.radio("Paiement du Prêt Principal temporaire :", ["Différé PARTIEL (Payer les intérêts)", "Amortissement IMMÉDIAT (Pleine mensualité)"], index=0)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    mens_ptz_actuelle = ptz_flow_futur_padded[0]
                    int_relais = avance_relais * ((taux_futur + 0.20) / 100 / 12)
                    mens_relais_phase1 = int_relais if "PARTIEL" in choix_relais else 0
                    
                    int_pp_tempo = pret_principal_temporaire * tm_futur
                    mens_pp_pleine = pret_principal_temporaire * tm_futur / (1 - (1+tm_futur)**-300) if tm_futur > 0 else pret_principal_temporaire / 300
                    mens_pp_phase1 = mens_pp_pleine if "IMMÉDIAT" in choix_pp else int_pp_tempo
                    
                    mens_totale_phase_relais = mens_ptz_actuelle + mens_relais_phase1 + mens_pp_phase1

                    html_s2_footer = f"""
<div style='background-color: #FEF2F2; padding: 10px; border-radius: 6px; border: 1px dashed #EF4444; margin-top: 15px; text-align: center;'>
<div style='font-size: 12px; color: #B91C1C; font-weight: bold;'>Effort de trésorerie pendant la vente</div>
<div style='font-size: 22px; font-weight: 900; color: #9F1239;'>{fmt(mens_totale_phase_relais)} € / mois</div>
<div style='font-size: 10px; color: #7F1D1D;'>(PTZ Transféré + Relais + Prêt Gonflé)</div>
</div>

<div style='background-color: white; border-radius: 6px; padding: 15px; border: 1px solid #A7F3D0; margin-top: 15px;'>
<div style='color: #065F46; font-weight: bold; margin-bottom: 10px; border-bottom: 1px dashed #A7F3D0; padding-bottom: 5px;'>Phase 2 : À la revente de l'ancien bien</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>
<span>Encaissement du solde (Les 30% restants)</span> <strong style='color: #10B981;'>+ {fmt(solde_recupere_revente)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 5px;'>
<span>Remboursement Anticipé sur Prêt Principal</span> <strong style='color: #E11D48;'>- {fmt(solde_recupere_revente)} €</strong>
</div>
<div style='display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; color: #065F46; margin-top: 10px; padding-top: 5px; border-top: 1px solid #E2E8F0;'>
<span>La mensualité retombe à la cible :</span> <span>{fmt(mens_cible_future)} € / mois</span>
</div>
</div>
</div>
"""
                    st.markdown(html_s2_footer, unsafe_allow_html=True)


            # --- GRAPHIQUE ---
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

    st.write("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("⬅️ Précédent", on_click=prev_step, use_container_width=True)

# --- MENTIONS LÉGALES & AVERTISSEMENTS ---
st.write("---")
st.markdown("""
<div style="background-color: #F1F5F9; padding: 20px; border-radius: 8px; font-size: 11px; color: #64748B; text-align: justify; border: 1px solid #E2E8F0;">
<strong style="color: #334155; font-size: 12px;">Mentions légales & Avertissements réglementaires :</strong><br><br>
<b>« Un crédit vous engage et doit être remboursé. Vérifiez vos capacités de remboursement avant de vous engager. »</b><br><br>
<b>« Aucun versement de quelque nature que ce soit ne peut être exigé d'un particulier avant l'obtention d'un ou plusieurs prêts d'argent. »</b><br><br>
<i>Clause de non-responsabilité :</i> Ce simulateur est un outil pédagogique fourni à titre strictement indicatif. Les résultats calculés dépendent des données saisies par l'utilisateur et ne constituent en <b>aucun cas une offre de prêt, un accord de principe ou un engagement contractuel</b> de la part de notre entreprise, d'un partenaire bancaire ou d'un courtier. Les conditions définitives de financement (taux, assurance, garanties, acceptation du dossier) seront établies uniquement par l'établissement prêteur après étude complète des justificatifs.
</div>
""", unsafe_allow_html=True)
