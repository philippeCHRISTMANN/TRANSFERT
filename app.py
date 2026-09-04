import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ & Relais", layout="wide")

# =================================================================
# MODULE : TRANSFERT DU PRÊT À TAUX ZÉRO (ANTICIPATION REVENTE)
# =================================================================

st.markdown('<div class="header-style" style="font-size: 24px; font-weight: bold; color: #1E3A8A;">🔄 Anticipation : Transfert de PTZ & Prêt Relais</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Que se passe-t-il si vous revendez votre bien dans quelques années pour en acheter un nouveau ? Découvrez comment la conservation de votre PTZ booste votre Prêt Relais et votre futur pouvoir d'achat.</p>", unsafe_allow_html=True)

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
st.markdown("### 📝 Étape 1 : La vente de votre bien et vos crédits en cours")
st.info("💡 Placez-vous dans la situation estimée à **aujourd'hui + 3 mois** (date habituelle de signature chez le notaire). Prenez vos tableaux d'amortissement actuels à cette date.")

# 1. Estimation du bien
col_v1, col_v2 = st.columns(2)
with col_v1:
    val_estimee = st.number_input("Moyenne basse de 2 estimations de votre bien actuel (€)", min_value=0.0, step=5000.0, value=250000.0)
with col_v2:
    sans_reserves = st.radio("L'acheteur a-t-il déjà obtenu son financement SANS réserves (ou paie comptant) ?", ("Non", "Oui"))
    quotite_relais = 1.0 if sans_reserves == "Oui" else 0.70

st.write("")

# 2. Saisie des crédits
col_ptz, col_pp = st.columns(2)

# ----- LE PRÊT À TAUX ZÉRO -----
with col_ptz:
    st.markdown("#### 🟣 Votre Prêt à Taux Zéro (PTZ)")
    crd_ptz = st.number_input("Capital Restant Dû PTZ (à +3 mois) en €", min_value=0.0, step=1000.0, value=40000.0)
    
    is_constant_ptz = st.radio(
        "Les mensualités RESTANTES du PTZ sont-elles constantes ?",
        ("Oui, toujours la même", "Non, il y a des paliers"),
        key="radio_ptz"
    )
    
    ptz_flow_total = []
    
    if is_constant_ptz.startswith("Oui"):
        duree_ptz = st.number_input("Mensualités RESTANTES du PTZ", min_value=1, step=12, value=204)
        mens_ptz = crd_ptz / duree_ptz if duree_ptz > 0 else 0
        st.info(f"Mensualité calculée : **{mens_ptz:.2f} € / mois**")
        ptz_flow_total = [mens_ptz] * int(duree_ptz)
    else:
        nb_paliers_ptz = st.number_input("Nombre de paliers RESTANTS du PTZ", min_value=1, max_value=6, value=2, key="nb_pal_ptz")
        for i in range(int(nb_paliers_ptz)):
            c1, c2 = st.columns(2)
            with c1:
                dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=120 if i==0 else 84, key=f"ptz_dur_{i}")
            with c2:
                men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=0.0 if i==0 else 200.0, key=f"ptz_mens_{i}")
            ptz_flow_total.extend([men_p] * int(dur_p))

# ----- LE PRÊT PRINCIPAL -----
with col_pp:
    st.markdown("#### 🔵 Votre Prêt Principal")
    crd_pp = st.number_input("Capital Restant Dû Prêt Principal (à +3 mois) en €", min_value=0.0, step=1000.0, value=150000.0)
    
    is_constant_pp = st.radio(
        "Les mensualités RESTANTES du Prêt Principal sont-elles constantes ?",
        ("Oui, toujours la même", "Non, il y a des paliers"),
        key="radio_pp"
    )
    
    pp_flow_total = []
    
    if is_constant_pp.startswith("Oui"):
        mens_pp = st.number_input("Mensualité hors assurance Prêt Principal (€)", min_value=0.0, step=10.0, value=850.0)
        duree_pp = st.number_input("Mensualités RESTANTES Prêt Principal", min_value=1, step=12, value=204)
        pp_flow_total = [mens_pp] * int(duree_pp)
    else:
        nb_paliers_pp = st.number_input("Nombre de paliers RESTANTS du Prêt Principal", min_value=1, max_value=6, value=2, key="nb_pal_pp")
        for i in range(int(nb_paliers_pp)):
            c1, c2 = st.columns(2)
            with c1:
                dur_p = st.number_input(f"Durée Palier {i+1} (mois)", min_value=1, step=12, value=120 if i==0 else 84, key=f"pp_dur_{i}")
            with c2:
                men_p = st.number_input(f"Mensualité Palier {i+1} (€)", min_value=0.0, step=10.0, value=1000.0 if i==0 else 800.0, key=f"pp_mens_{i}")
            pp_flow_total.extend([men_p] * int(dur_p))

# --- CALCUL DES APPORTS (PRÊT RELAIS) ---
max_len_actuel = max(len(ptz_flow_total), len(pp_flow_total))
ptz_padded_actuel = ptz_flow_total + [0] * (max_len_actuel - len(ptz_flow_total))
pp_padded_actuel = pp_flow_total + [0] * (max_len_actuel - len(pp_flow_total))

total_mensualite_actuelle = [p + m for p, m in zip(ptz_padded_actuel, pp_padded_actuel)]
mensualite_lisse_moyenne = int(max(total_mensualite_actuelle)) if total_mensualite_actuelle else 1000

apport_banque_classique = max(0, (val_estimee * quotite_relais) - crd_pp - crd_ptz)
apport_banque_transfert = max(0, (val_estimee * quotite_relais) - crd_pp)
gain_apport_relais = apport_banque_transfert - apport_banque_classique

st.markdown(f"""
<div style="margin-top: 20px; padding: 15px; border-radius: 8px; background-color: #F0F9FF; border-left: 4px solid #0284C7;">
    <h4 style="color: #0369A1; margin-top: 0; font-size: 16px;">💡 La magie du Transfert sur votre Prêt Relais</h4>
    <p style="font-size: 13px; color: #334155; margin-bottom: 15px;">
        Pour se protéger, la banque ne retient que <b>{int(quotite_relais*100)}%</b> de la valeur de votre bien. Habituellement, elle déduit de cette somme <b>tous</b> vos crédits en cours pour calculer votre apport. <b>Mais en transférant le PTZ, vous n'avez pas à le solder !</b>
    </p>
    <table style="width: 100%; border-collapse: collapse; font-size: 13px; background-color: white; border: 1px solid #E2E8F0;">
        <tr style="background-color: #F8FAFC; border-bottom: 2px solid #E2E8F0;">
            <th style="padding: 10px; width: 33%; color: #475569; text-align: left;">Calcul de la Banque</th>
            <th style="padding: 10px; width: 33%; color: #9F1239; text-align: center;">Si vous soldez tout (Classique)</th>
            <th style="padding: 10px; width: 33%; color: #065F46; text-align: center;">Si vous transférez le PTZ</th>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #64748B;">Valeur retenue ({int(quotite_relais*100)}%)</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #334155; text-align: center;">{val_estimee * quotite_relais:,.0f} €</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #334155; text-align: center;">{val_estimee * quotite_relais:,.0f} €</td>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #64748B;">Solder le Prêt Principal</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #E11D48; text-align: center;">- {crd_pp:,.0f} €</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #E11D48; text-align: center;">- {crd_pp:,.0f} €</td>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #64748B;">Solder le PTZ</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #E11D48; text-align: center;">- {crd_ptz:,.0f} €</td>
            <td style="padding: 10px; border-bottom: 1px solid #F1F5F9; color: #059669; font-weight: bold; text-align: center;">0 € (Conservé !)</td>
        </tr>
        <tr style="background-color: #F8FAFC;">
            <td style="padding: 10px; font-weight: bold; color: #0EA5E9;">Apport généré (Prêt Relais)</td>
            <td style="padding: 10px; font-weight: bold; color: #9F1239; text-align: center; font-size: 16px;">{apport_banque_classique:,.0f} €</td>
            <td style="padding: 10px; font-weight: bold; color: #059669; text-align: center; font-size: 16px;">{apport_banque_transfert:,.0f} €</td>
        </tr>
    </table>
    <div style="text-align: center; margin-top: 15px; color: #0284C7; font-weight: bold;">
        🚀 Le transfert génère instantanément + {gain_apport_relais:,.0f} € d'apport mobilisable pour votre achat !
    </div>
</div>
""".replace(',', ' '), unsafe_allow_html=True)

st.write("---")

# --- C. LE FUTUR PROJET (LA REVENTE) ---
st.markdown("### 🎯 Étape 2 : Votre futur projet (Achat)")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    annee_revente = st.slider("Décalage de la revente (0 = projet immédiat)", min_value=0, max_value=25, value=0, help="0 signifie que la vente se fait à +3 mois comme estimé au-dessus.")
with col_t2:
    mens_cible_future = st.number_input("Mensualité cible pour le futur projet (€)", min_value=100, value=mensualite_lisse_moyenne, step=50, help="Nous reprenons par défaut votre mensualité globale actuelle.")
with col_t3:
    taux_futur = st.number_input("Taux estimé du futur crédit classique (%)", min_value=0.5, value=4.0, step=0.10)

# --- D. CALCULS DU TRANSFERT ET DU NOUVEAU LISSAGE ---
mois_revente = annee_revente * 12

if mois_revente >= len(ptz_flow_total) and len(ptz_flow_total) > 0:
    st.warning(f"⚠️ Dans {annee_revente} ans, votre Prêt à Taux Zéro sera déjà intégralement remboursé. Il n'y aura donc rien à transférer.")
else:
    # 1. Ce qu'il reste du PTZ à la date de revente
    ptz_flow_futur = ptz_flow_total[mois_revente:]
    crd_ptz_transfert = sum(ptz_flow_futur)
    
    if crd_ptz_transfert <= 0:
        st.warning("Le capital restant dû de votre PTZ sera de 0 €. Le transfert est sans objet.")
    else:
        duree_nouveau_pret_mois = 300 # Prêt classique futur sur 25 ans
        tm_futur = taux_futur / 100 / 12
        
        # SCÉNARIO 1 : SANS TRANSFERT (Classique)
        if tm_futur > 0:
            capacite_nouveau_pret_classique = mens_cible_future * ((1 - (1+tm_futur)**(-duree_nouveau_pret_mois)) / tm_futur)
        else:
            capacite_nouveau_pret_classique = mens_cible_future * duree_nouveau_pret_mois
            
        enveloppe_totale_classique = apport_banque_classique + capacite_nouveau_pret_classique
            
        # SCÉNARIO 2 : AVEC TRANSFERT ET NOUVEAU LISSAGE
        ptz_flow_futur_padded = ptz_flow_futur + [0] * (duree_nouveau_pret_mois - len(ptz_flow_futur)) if len(ptz_flow_futur) < duree_nouveau_pret_mois else ptz_flow_futur[:duree_nouveau_pret_mois]
        max_ptz_flow = max(ptz_flow_futur_padded)
        
        if mens_cible_future <= max_ptz_flow:
            st.error(f"❌ Votre mensualité cible ({mens_cible_future} €) est trop faible pour absorber l'échéance du PTZ conservé ({max_ptz_flow:.0f} €/m). Augmentez votre mensualité cible.")
        else:
            pv_nouveau_pret_lisse = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret_lisse += disponible_mensuel / ((1+tm_futur)**m)
            else:
                pv_nouveau_pret_lisse = sum((mens_cible_future - p) for p in ptz_flow_futur_padded)
            
            # Enveloppe avec transfert = Apport Boosté + Capacité Nouveau Prêt (Lissé) + Capital PTZ Conservé
            # (Note: Le capital PTZ est une dette transférée, il vient abonder la capacité d'achat car la banque n'a pas à le prêter)
            enveloppe_totale_transfert = apport_banque_transfert + pv_nouveau_pret_lisse + crd_ptz_transfert
            gain_transfert = enveloppe_totale_transfert - enveloppe_totale_classique

            # --- E. AFFICHAGE DES RÉSULTATS ---
            st.markdown("### 🏆 Résultats : Votre budget d'achat global")
            
            html_kpi_2 = f"""
            <div style="display: flex; gap: 15px; margin-top: 15px;">
                <div style="flex: 1; background-color: #FFF1F2; border: 1px solid #FECDD3; border-radius: 8px; padding: 15px; text-align: center;">
                    <div style="color: #9F1239 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Si vous soldez tout (Classique)</div>
                    <div style="color: #E11D48 !important; font-size: 24px; font-weight: 900; margin: 0;">{enveloppe_totale_classique:,.0f} €</div>
                    <div style="color: #9F1239 !important; font-size: 11px; margin-top: 5px;">Apport Relais ({apport_banque_classique:,.0f}€) + Nouveau Prêt</div>
                </div>
                <div style="flex: 1; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 15px; text-align: center; position: relative;">
                    <div style="position: absolute; top: -10px; right: 10px; background-color: #10B981; color: #FFFFFF !important; font-size: 10px; font-weight: bold; padding: 3px 8px; border-radius: 12px;">AVANTAGEUX</div>
                    <div style="color: #065F46 !important; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;">Avec Transfert du PTZ</div>
                    <div style="color: #059669 !important; font-size: 24px; font-weight: 900; margin: 0;">{enveloppe_totale_transfert:,.0f} €</div>
                    <div style="color: #065F46 !important; font-size: 11px; margin-top: 5px;">Apport Relais Boosté ({apport_banque_transfert:,.0f}€) + Prêt Lissé + PTZ Conservé</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; background-color: #F0FDF4; border: 2px dashed #10B981; padding: 15px; border-radius: 8px;">
                <div style="margin: 0; font-size: 20px; font-weight: 900; color: #047857 !important;">🚀 Budget immobilier supplémentaire : + {gain_transfert:,.0f} €</div>
                <div style="margin: 5px 0 0 0; font-size: 13px; font-weight: 600; color: #065F46 !important;">Pour la même mensualité de {mens_cible_future} €/mois, le transfert décuple votre pouvoir d'achat !</div>
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
