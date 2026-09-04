import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page (si ce code est le fichier principal)
# st.set_page_config(page_title="Simulateur Transfert PTZ", layout="centered")

# =================================================================
# MODULE : TRANSFERT DU PRÊT À TAUX ZÉRO (ANTICIPATION REVENTE)
# =================================================================

st.markdown('<div class="header-style">🔄 Anticipation : Transfert de votre Prêt à Taux Zéro (PTZ)</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Que se passe-t-il si vous revendez votre bien dans quelques années pour en acheter un nouveau ? Découvrez comment conserver votre PTZ actuel et l'impact direct sur votre futur pouvoir d'achat.</p>", unsafe_allow_html=True)

# --- A. ENCADRÉ PÉDAGOGIQUE (LÉGISLATION) ---
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
    <strong style="color: #9333EA; font-size: 14px;">💡 Bon à savoir</strong>
    <ul style="font-size: 13px; color: #475569; margin-top: 5px;">
    <li>Vos revenus actuels ne sont plus contrôlés, et vous n'avez plus besoin d'être primo-accédant.</li>
    </ul>
    </div>""", unsafe_allow_html=True)

st.write("---")

# --- B. SAISIE DES DONNÉES PAR LE CLIENT ---
st.markdown("### 📝 Étape 1 : Votre Prêt à Taux Zéro (PTZ) actuel")
st.info("💡 Munissez-vous du tableau d'amortissement de votre Prêt à Taux Zéro actuel. Nous n'avons besoin que des données de ce prêt (votre prêt principal sera, lui, soldé lors de la vente).")

is_constant = st.radio(
    "Les mensualités de votre prêt à taux zéro sont-elles constantes (identiques) du premier au dernier mois ?",
    ("Oui, la mensualité est toujours la même", "Non, il y a des paliers (la mensualité change avec le temps)")
)

ptz_flow_total = []

if is_constant.startswith("Oui"):
    col1, col2 = st.columns(2)
    with col1:
        mens_ptz = st.number_input("Mensualité hors assurance (€)", min_value=0.0, step=10.0, value=150.0)
    with col2:
        duree_ptz = st.number_input("Durée totale du prêt (en mois)", min_value=1, step=12, value=300)
    
    # Création du tableau d'amortissement simplifié (0% = que du capital)
    ptz_flow_total = [mens_ptz] * int(duree_ptz)

else:
    st.markdown("<p style='color: #db2777; font-weight: bold;'>Saisie des paliers de votre PTZ</p>", unsafe_allow_html=True)
    st.write("Indiquez les différentes phases de remboursement. (Exemple : Palier 1 = 180 mois à 0€ / Palier 2 = 120 mois à 300€).")
    
    nb_paliers = st.number_input("Combien de paliers comporte votre PTZ ?", min_value=2, max_value=6, value=2)
    
    for i in range(int(nb_paliers)):
        st.markdown(f"**Palier {i+1}**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            duree_p = st.number_input(f"Durée du palier (en mois)", min_value=1, step=12, value=120, key=f"dur_{i}")
        with col_p2:
            mens_p = st.number_input(f"Mensualité hors assurance (€)", min_value=0.0, step=10.0, value=0.0 if i==0 else 200.0, key=f"mens_{i}")
        
        # Ajout des mensualités à la ligne de temps globale
        ptz_flow_total.extend([mens_p] * int(duree_p))

st.write("---")

# --- C. LE FUTUR PROJET (LA REVENTE) ---
st.markdown("### 🎯 Étape 2 : Votre futur projet")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    annee_revente = st.slider("Revente dans combien d'années ?", min_value=1, max_value=25, value=7)
with col_t2:
    mens_cible_future = st.number_input("Mensualité globale souhaitée (€)", min_value=100, value=1200, step=50, help="Combien voulez-vous payer par mois au total pour le nouveau projet ?")
with col_t3:
    taux_futur = st.number_input("Taux du futur crédit classique (%)", min_value=0.5, value=4.0, step=0.10)

# --- D. CALCULS DU TRANSFERT ET DU LISSAGE ---
mois_revente = annee_revente * 12

# Vérification si le PTZ est déjà fini à la date de revente
if mois_revente >= len(ptz_flow_total):
    st.warning(f"⚠️ Dans {annee_revente} ans, votre Prêt à Taux Zéro sera déjà intégralement remboursé. Il n'y aura donc rien à transférer.")
else:
    # 1. Extraction de ce qu'il reste à payer du PTZ après la revente
    ptz_flow_futur = ptz_flow_total[mois_revente:]
    
    # 2. Le Capital Restant Dû (CRD) d'un PTZ, c'est simplement la somme des mensualités restantes (car taux à 0%)
    crd_ptz_transfert = sum(ptz_flow_futur)
    
    if crd_ptz_transfert <= 0:
        st.warning("Le capital restant dû de votre PTZ sera de 0 €. Le transfert est sans objet.")
    else:
        # Standard : le nouveau prêt se fera sur 25 ans (300 mois)
        duree_nouveau_pret_mois = 300 
        tm_futur = taux_futur / 100 / 12
        
        # --- SCÉNARIO 1 : SANS TRANSFERT (On solde tout, on refait un crédit simple) ---
        if tm_futur > 0:
            capacite_sans_transfert = mens_cible_future * ((1 - (1+tm_futur)**(-duree_nouveau_pret_mois)) / tm_futur)
        else:
            capacite_sans_transfert = mens_cible_future * duree_nouveau_pret_mois
            
        # --- SCÉNARIO 2 : AVEC TRANSFERT (Nouveau prêt lissé autour du vieux PTZ) ---
        # On s'assure que le tableau du PTZ futur a la même taille que le nouveau prêt pour le calcul (on comble avec des 0)
        ptz_flow_futur_padded = ptz_flow_futur + [0] * (duree_nouveau_pret_mois - len(ptz_flow_futur)) if len(ptz_flow_futur) < duree_nouveau_pret_mois else ptz_flow_futur[:duree_nouveau_pret_mois]
        
        max_ptz_flow = max(ptz_flow_futur_padded)
        
        if mens_cible_future <= max_ptz_flow:
            st.error(f"❌ Votre mensualité cible ({mens_cible_future} €) est trop faible. À un moment donné, votre PTZ seul vous coûtera {max_ptz_flow:.0f} €/mois. Veuillez augmenter la mensualité souhaitée pour permettre un nouveau financement.")
        else:
            # Calcul de la capacité d'emprunt du nouveau prêt (Lissage inversé : on actualise le disponible mensuel)
            pv_nouveau_pret = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret += disponible_mensuel / ((1+tm_futur)**m)
            
            # Capacité Totale = L'argent prêté par la banque (Nouveau prêt) + Le capital du PTZ qu'on conserve
            capacite_avec_transfert = pv_nouveau_pret + crd_ptz_transfert
            gain_transfert = capacite_avec_transfert - capacite_sans_transfert

            # --- E. AFFICHAGE DES RÉSULTATS (KPI) ---
            st.markdown("### 🏆 Résultats de l'optimisation")
            
            html_kpi_1 = f"""
            <div style="display: flex; gap: 15px; margin-top: 10px;">
                <div style="flex: 1; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #64748B !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Capital PTZ préservé à {annee_revente} ans</div>
                    <div style="color: #0F172A !important; font-size: 24px; font-weight: 900; margin: 0;">{crd_ptz_transfert:,.0f} €</div>
                    <div style="color: #475569 !important; font-size: 11px; margin-top: 5px;">(C'est l'argent gratuit que vous ne rendez pas à la banque)</div>
                </div>
            </div>
            """.replace(',', ' ')
            st.markdown(html_kpi_1, unsafe_allow_html=True)
            
            html_kpi_2 = f"""
            <div style="display: flex; gap: 15px; margin-top: 15px;">
                <div style="flex: 1; background-color: #FFF1F2; border: 1px solid #FECDD3; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #9F1239 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">1. Si vous soldez tout</div>
                    <div style="color: #E11D48 !important; font-size: 22px; font-weight: 900; margin: 0;">{capacite_sans_transfert:,.0f} €</div>
                    <div style="color: #9F1239 !important; font-size: 11px; margin-top: 5px;">Enveloppe pour {mens_cible_future}€/m à {taux_futur}%</div>
                </div>
                <div style="flex: 1; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 15px; text-align: center; position: relative;">
                    <div style="position: absolute; top: -10px; right: 10px; background-color: #10B981; color: #FFFFFF !important; font-size: 10px; font-weight: bold; padding: 3px 8px; border-radius: 12px;">CONSEILLÉ</div>
                    <div style="color: #065F46 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">2. Avec Transfert PTZ</div>
                    <div style="color: #059669 !important; font-size: 22px; font-weight: 900; margin: 0;">{capacite_avec_transfert:,.0f} €</div>
                    <div style="color: #065F46 !important; font-size: 11px; margin-top: 5px;">Le nouveau prêt classique s'emboîte sur le PTZ</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; background-color: #F0FDF4; border: 2px dashed #10B981; padding: 15px; border-radius: 8px;">
                <div style="margin: 0; font-size: 20px; font-weight: 900; color: #047857 !important;">🚀 Gain sur votre pouvoir d'achat : + {gain_transfert:,.0f} €</div>
                <div style="margin: 5px 0 0 0; font-size: 13px; font-weight: 600; color: #065F46 !important;">Pour la MÊME mensualité de {mens_cible_future} €, vous achetez plus grand grâce au lissage !</div>
            </div>
            """.replace(',', ' ')
            st.markdown(html_kpi_2, unsafe_allow_html=True)
            
            # --- F. GRAPHIQUE PÉDAGOGIQUE DU LISSAGE ---
            st.markdown("#### 📊 Comment fonctionne le lissage ?")
            st.write("Le graphique ci-dessous montre comment la banque va adapter les mensualités de votre nouveau prêt (en bleu) pour qu'elles s'emboîtent parfaitement autour de votre ancien PTZ (en rose). Le total fera toujours la mensualité souhaitée.")
            
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
