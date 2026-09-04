import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ", layout="wide")

# =================================================================
# MODULE : TRANSFERT DU PRÊT À TAUX ZÉRO (ANTICIPATION REVENTE)
# =================================================================

st.markdown('<div class="header-style" style="font-size: 24px; font-weight: bold; color: #1E3A8A;">🔄 Anticipation : Transfert de votre Prêt à Taux Zéro (PTZ)</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Que se passe-t-il si vous revendez votre bien dans quelques années pour en acheter un nouveau ? Découvrez comment conserver votre PTZ actuel et l'impact direct sur votre futur pouvoir d'achat.</p>", unsafe_allow_html=True)

# --- A. ENCADRÉ PÉDAGOGIQUE ---
with st.expander("📚 Rappel : Les règles du transfert de PTZ", expanded=False):
    st.markdown("""<div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 15px;">
    <p style="font-size: 13px; color: #334155; margin-bottom: 10px;">La loi vous permet de conserver votre PTZ en cours si vous revendez pour acheter une <b>nouvelle résidence principale</b>.</p>
    <strong style="color: #1E3A8A; font-size: 14px;">⏳ Revente MOINS de 6 ans après le versement</strong>
    <ul style="font-size: 13px; color: #475569; margin-top: 5px;">
    <li>Le nouveau bien doit respecter les conditions du PTZ actuel (ex: Neuf, ou Ancien avec 25% de travaux en zone B2/C).</li>
    </ul>
    <strong style="color: #10B981; font-size: 14px;">⌛ Revente PLUS de 6 ans après le versement</strong>
    <ul style="font-size: 13px; color: #475569; margin-top: 5px; margin-bottom: 15px;">
    <li><b>Aucune condition !</b> Vous pouvez acheter de l'ancien sans travaux, où vous voulez.</li>
    </ul>
    </div>""", unsafe_allow_html=True)

st.write("---")

# --- B. SAISIE DES DONNÉES ACTUELLES PAR LE CLIENT ---
st.markdown("### 📝 Étape 1 : Vos crédits actuels")

# Saisie de la donnée globale du projet
col_g1, col_g2 = st.columns(2)
with col_g1:
    mensualite_globale_actuelle = st.number_input("Quelle est votre mensualité globale actuelle ? (Tous prêts confondus, en €)", min_value=100.0, value=1000.0, step=50.0, help="Regardez combien vous êtes prélevé chaque mois par la banque au total.")
with col_g2:
    duree_totale_globale = st.number_input("Durée totale de votre financement (en mois)", min_value=12, value=300, step=12)

st.write("")
st.markdown("#### 🟣 Reconstitution de votre Prêt à Taux Zéro (PTZ)")
st.info("💡 Saisissez le montant de votre PTZ. Nous allons calculer automatiquement les paliers restants pour vous éviter les erreurs de saisie !")

col_p1, col_p2 = st.columns(2)
with col_p1:
    capital_ptz = st.number_input("Montant total emprunté sur le PTZ (€)", min_value=1000.0, value=60000.0, step=1000.0)
with col_p2:
    duree_ptz = st.number_input("Durée de votre PTZ (en mois)", min_value=12, value=300, step=12)

is_constant_ptz = st.radio(
    "Les mensualités du PTZ sont-elles constantes ?",
    ("Oui, toujours la même mensualité", "Non, il y a des paliers (ex: 0€ pendant X mois, puis Y€)"),
    key="radio_ptz"
)

ptz_flow_total = []

if is_constant_ptz.startswith("Oui"):
    mens_ptz = capital_ptz / duree_ptz
    st.success(f"✨ **Calcul automatique :** Votre mensualité de PTZ est de **{mens_ptz:.2f} € / mois**.")
    ptz_flow_total = [mens_ptz] * int(duree_ptz)
else:
    nb_paliers_ptz = st.number_input("Combien de paliers comporte votre PTZ ?", min_value=2, max_value=4, value=2, key="nb_pal_ptz")
    
    duree_cumulee = 0
    capital_rembourse = 0
    
    for i in range(int(nb_paliers_ptz)):
        # Pour tous les paliers SAUF le dernier : l'utilisateur saisit
        if i < int(nb_paliers_ptz) - 1:
            st.markdown(f"**Palier {i+1}**")
            c1, c2 = st.columns(2)
            with c1:
                dur_p = st.number_input(f"Durée du Palier {i+1} (en mois)", min_value=1, step=12, value=180 if i==0 else 120, key=f"ptz_dur_{i}")
            with c2:
                men_p = st.number_input(f"Mensualité du Palier {i+1} (€)", min_value=0.0, step=10.0, value=0.0 if i==0 else 200.0, key=f"ptz_mens_{i}")
            
            ptz_flow_total.extend([men_p] * int(dur_p))
            duree_cumulee += dur_p
            capital_rembourse += (men_p * dur_p)
            
        # Pour le DERNIER palier : le robot calcule tout seul
        else:
            st.markdown(f"**Palier {i+1} (Calculé automatiquement)**")
            dur_restante = duree_ptz - duree_cumulee
            capital_restant = capital_ptz - capital_rembourse
            
            if dur_restante <= 0:
                st.error("⚠️ Attention, la somme des durées de vos premiers paliers dépasse ou annule la durée totale de votre prêt.")
            elif capital_restant < 0:
                st.error("⚠️ Attention, vous avez saisi des mensualités trop élevées : le capital est déjà totalement remboursé avant le dernier palier.")
            else:
                men_p = capital_restant / dur_restante
                st.success(f"✨ **Dernier palier déduit :** Il vous restera **{int(dur_restante)} mois** à payer **{men_p:.2f} € / mois**.")
                ptz_flow_total.extend([men_p] * int(dur_restante))

# --- DÉDUCTION DU PRÊT PRINCIPAL ---
st.markdown("#### 🔵 Votre Prêt Principal")
st.info("🪄 **Magie du Lissage :** Inutile de saisir les données complexes de votre Prêt Principal ! Puisque votre financement initial est lissé, notre outil déduit mathématiquement les paliers de votre Prêt Principal en soustrayant le PTZ de votre mensualité globale.")

# On allonge le tableau PTZ avec des zéros si la durée globale est plus longue que le PTZ
if len(ptz_flow_total) < duree_totale_globale:
    ptz_flow_total.extend([0] * (int(duree_totale_globale) - len(ptz_flow_total)))

# Calcul du flux du prêt principal
pp_flow_total = [max(0, mensualite_globale_actuelle - p) for p in ptz_flow_total]

st.write("---")

# --- C. LE FUTUR PROJET (LA REVENTE) ---
st.markdown("### 🎯 Étape 2 : Votre futur projet (Revente & Rachat)")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    annee_revente = st.slider("Revente dans combien d'années ?", min_value=1, max_value=25, value=7)
with col_t2:
    mens_cible_future = st.number_input("Mensualité cible du futur projet (€)", min_value=100.0, value=float(mensualite_globale_actuelle), step=50.0, help="Nous reprenons par défaut votre mensualité actuelle pour comparer à effort égal.")
with col_t3:
    taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=4.0, step=0.10)

# --- D. CALCULS DU TRANSFERT ET DU NOUVEAU LISSAGE ---
mois_revente = annee_revente * 12

if mois_revente >= len(ptz_flow_total):
    st.warning(f"⚠️ Dans {annee_revente} ans, votre Prêt à Taux Zéro sera déjà intégralement remboursé. Il n'y aura donc rien à transférer.")
else:
    # 1. Ce qu'il reste du PTZ à la date de revente
    ptz_flow_futur = ptz_flow_total[mois_revente:]
    crd_ptz_transfert = sum(ptz_flow_futur)
    
    if crd_ptz_transfert <= 0:
        st.warning("Le capital restant dû de votre PTZ sera de 0 €. Le transfert est sans objet.")
    else:
        duree_nouveau_pret_mois = 300 # Prêt classique futur sur 25 ans standard
        tm_futur = taux_futur / 100 / 12
        
        # SCÉNARIO 1 : SANS TRANSFERT
        if tm_futur > 0:
            capacite_sans_transfert = mens_cible_future * ((1 - (1+tm_futur)**(-duree_nouveau_pret_mois)) / tm_futur)
        else:
            capacite_sans_transfert = mens_cible_future * duree_nouveau_pret_mois
            
        # SCÉNARIO 2 : AVEC TRANSFERT ET NOUVEAU LISSAGE
        ptz_flow_futur_padded = ptz_flow_futur + [0] * (duree_nouveau_pret_mois - len(ptz_flow_futur)) if len(ptz_flow_futur) < duree_nouveau_pret_mois else ptz_flow_futur[:duree_nouveau_pret_mois]
        max_ptz_flow = max(ptz_flow_futur_padded)
        
        if mens_cible_future <= max_ptz_flow:
            st.error(f"❌ Votre mensualité cible ({mens_cible_future} €) est trop faible pour absorber l'échéance du PTZ qu'il vous restera à rembourser ({max_ptz_flow:.0f} €/m). Augmentez votre mensualité cible.")
        else:
            pv_nouveau_pret = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret += disponible_mensuel / ((1+tm_futur)**m)
            
            capacite_avec_transfert = pv_nouveau_pret + crd_ptz_transfert
            gain_transfert = capacite_avec_transfert - capacite_sans_transfert

            # --- E. AFFICHAGE DES RÉSULTATS ---
            st.markdown("### 🏆 Résultats : Votre gain de pouvoir d'achat")
            
            html_kpi_1 = f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 15px;">
                <div style="color: #64748B !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Capital PTZ transféré (à {annee_revente} ans)</div>
                <div style="color: #0F172A !important; font-size: 24px; font-weight: 900; margin: 0;">{crd_ptz_transfert:,.0f} €</div>
                <div style="color: #475569 !important; font-size: 12px; margin-top: 5px;">(C'est l'argent à 0% que vous ne rendez pas à la banque lors de la vente)</div>
            </div>
            """.replace(',', ' ')
            st.markdown(html_kpi_1, unsafe_allow_html=True)
            
            html_kpi_2 = f"""
            <div style="display: flex; gap: 15px; margin-top: 15px;">
                <div style="flex: 1; background-color: #FFF1F2; border: 1px solid #FECDD3; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #9F1239 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Si vous soldez tout (Classique)</div>
                    <div style="color: #E11D48 !important; font-size: 22px; font-weight: 900; margin: 0;">{capacite_sans_transfert:,.0f} €</div>
                </div>
                <div style="flex: 1; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 15px; text-align: center; position: relative;">
                    <div style="position: absolute; top: -10px; right: 10px; background-color: #10B981; color: #FFFFFF !important; font-size: 10px; font-weight: bold; padding: 3px 8px; border-radius: 12px;">AVANTAGEUX</div>
                    <div style="color: #065F46 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Avec Transfert du PTZ</div>
                    <div style="color: #059669 !important; font-size: 22px; font-weight: 900; margin: 0;">{capacite_avec_transfert:,.0f} €</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; background-color: #F0FDF4; border: 2px dashed #10B981; padding: 15px; border-radius: 8px;">
                <div style="margin: 0; font-size: 20px; font-weight: 900; color: #047857 !important;">🚀 Budget supplémentaire : + {gain_transfert:,.0f} €</div>
                <div style="margin: 5px 0 0 0; font-size: 13px; font-weight: 600; color: #065F46 !important;">Pour la même mensualité de {mens_cible_future} €/mois, voici ce que vous gagnez en transférant !</div>
            </div>
            """.replace(',', ' ')
            st.markdown(html_kpi_2, unsafe_allow_html=True)
            
            # --- F. GRAPHIQUE PÉDAGOGIQUE DU NOUVEAU LISSAGE ---
            st.markdown("#### 📊 Le nouveau plan de financement")
            
            months_array = np.arange(1, duree_nouveau_pret_mois + 1)
            y_ptz_flow = np.array(ptz_flow_futur_padded)
            y_nouveau_pret = mens_cible_future - y_ptz_flow
            
            fig_transf = go.Figure()
            fig_transf.add_trace(go.Scatter(x=months_array/12, y=y_ptz_flow, mode='lines', name='PTZ Conservé', stackgroup='one', line=dict(width=0, color="#db2777"), fillcolor="#db2777"))
            fig_transf.add_trace(go.Scatter(x=months_array/12, y=y_nouveau_pret, mode='lines', name=f'Nouveau Prêt Principal ({taux_futur}%)', stackgroup='one', line=dict(width=0, color="#1e3a8a"), fillcolor="#1e3a8a"))
            
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
