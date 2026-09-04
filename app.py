import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Transfert PTZ & Stratégie Revente", layout="wide")

# =================================================================
# MODULE : TRANSFERT DE PTZ & STRATÉGIE DE REVENTE
# =================================================================

st.markdown('<div class="header-style" style="font-size: 24px; font-weight: bold; color: #1E3A8A;">🔄 Anticipation : Transfert de PTZ & Stratégie de Revente</div>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px;'>Découvrez comment la conservation de votre Prêt à Taux Zéro (PTZ) booste votre prochain achat, et comparez l'impact financier entre un <b>Prêt Relais</b> et une <b>Vente préalable</b>.</p>", unsafe_allow_html=True)

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
st.markdown("### 📝 Étape 1 : Votre bien actuel et vos crédits en cours")
st.info("💡 Placez-vous dans la situation de votre future vente. Indiquez la valeur du bien et copiez les données de vos tableaux d'amortissement à cette date de revente.")

val_estimee = st.number_input("Valeur nette vendeuse estimée de votre bien actuel (€)", min_value=0.0, step=5000.0, value=250000.0)

st.write("")

col_ptz, col_pp = st.columns(2)

# ----- LE PRÊT À TAUX ZÉRO -----
with col_ptz:
    st.markdown("#### 🟣 Votre Prêt à Taux Zéro (PTZ)")
    crd_ptz = st.number_input("Capital Restant Dû PTZ en €", min_value=0.0, step=1000.0, value=40000.0)
    
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
    crd_pp = st.number_input("Capital Restant Dû Prêt Principal en €", min_value=0.0, step=1000.0, value=150000.0)
    
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

# --- C. LE FUTUR PROJET ---
st.write("---")
st.markdown("### 🎯 Étape 2 : Votre futur projet")

# Calcul de la mensualité cible par défaut
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

# --- D. CALCULS DES SCÉNARIOS (RELAIS vs VENTE 100%) ---
if len(ptz_flow_total) == 0:
    st.warning("⚠️ Vous n'avez pas saisi de durée ou de mensualité pour le PTZ. Les calculs ne peuvent pas aboutir.")
else:
    crd_ptz_transfert = sum(ptz_flow_total)
    
    if crd_ptz_transfert <= 0:
        st.warning("Le capital restant dû de votre PTZ sera de 0 €. Le transfert est sans objet.")
    else:
        # CALCUL DES APPORTS (Puisqu'on transfère le PTZ, on ne le solde pas à la vente !)
        # Scénario 1: Vente sécurisée (100% de la valeur - prêt principal)
        apport_100 = max(0, val_estimee - crd_pp)
        # Scénario 2: Prêt Relais (70% de la valeur - prêt principal)
        apport_70 = max(0, (val_estimee * 0.70) - crd_pp)
        
        # CALCUL DE LA CAPACITÉ DU NOUVEAU PRÊT (Lissé avec le PTZ conservé)
        duree_nouveau_pret_mois = 300 # 25 ans
        tm_futur = taux_futur / 100 / 12
        
        ptz_flow_futur_padded = ptz_flow_total + [0] * (duree_nouveau_pret_mois - len(ptz_flow_total)) if len(ptz_flow_total) < duree_nouveau_pret_mois else ptz_flow_total[:duree_nouveau_pret_mois]
        max_ptz_flow = max(ptz_flow_futur_padded)
        
        if mens_cible_future <= max_ptz_flow:
            st.error(f"❌ Votre mensualité cible ({mens_cible_future} €) est trop faible pour absorber l'échéance du PTZ conservé ({max_ptz_flow:.0f} €/m). Veuillez l'augmenter.")
        else:
            pv_nouveau_pret_lisse = 0
            if tm_futur > 0:
                for m in range(1, duree_nouveau_pret_mois + 1):
                    disponible_mensuel = mens_cible_future - ptz_flow_futur_padded[m-1]
                    pv_nouveau_pret_lisse += disponible_mensuel / ((1+tm_futur)**m)
            else:
                pv_nouveau_pret_lisse = sum((mens_cible_future - p) for p in ptz_flow_futur_padded)
            
            # Enveloppes totales
            enveloppe_vente_100 = apport_100 + pv_nouveau_pret_lisse + crd_ptz_transfert
            enveloppe_relais_70 = apport_70 + pv_nouveau_pret_lisse + crd_ptz_transfert
            
            gain_location = enveloppe_vente_100 - enveloppe_relais_70

            # --- E. AFFICHAGE STRATÉGIQUE (CÔTE À CÔTE) ---
            st.write("---")
            st.markdown("### 🏆 Comparatif Stratégique : Vendre d'abord ou Prêt Relais ?")
            st.markdown(f"<p style='color: #475569; font-size: 14px;'>Dans les deux cas, le transfert de votre PTZ est validé (Vous ne le remboursez pas à la vente, ce qui <b>booste votre apport de {crd_ptz_transfert:,.0f} €</b>). Voici l'impact de la décote du prêt relais sur votre enveloppe finale :</p>", unsafe_allow_html=True)
            
            col_res1, col_res2 = st.columns(2)
            
            # SCÉNARIO 1 : VENTE SÉCURISÉE / FERME
            with col_res1:
                st.markdown(f"""
                <div style="background-color: #ECFDF5; border: 2px solid #10B981; border-radius: 8px; padding: 20px; height: 100%; position: relative;">
                    <div style="position: absolute; top: -12px; right: 20px; background-color: #10B981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;">+ BUDGET MAXIMAL</div>
                    <h4 style="color: #065F46; margin-top: 0;">1️⃣ Vendre d'abord</h4>
                    <p style="color: #047857; font-size: 13px; margin-top: -10px;">L'acheteur n'a pas de clause (ou vous vendez et louez temporairement). Vous encaissez <b>100%</b> de la vente.</p>
                    
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="font-size: 12px; color: #065F46; text-transform: uppercase; font-weight: bold;">Budget d'Achat Global</div>
                        <div style="font-size: 32px; font-weight: 900; color: #059669;">{enveloppe_vente_100:,.0f} €</div>
                    </div>
                    
                    <div style="background-color: white; border-radius: 6px; padding: 12px; border: 1px solid #A7F3D0;">
                        <div style="font-weight: bold; color: #065F46; margin-bottom: 8px; border-bottom: 1px dashed #A7F3D0; padding-bottom: 4px;">Plan de financement :</div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 4px;">
                            <span>Apport (Fruit de la vente) :</span> <strong>{apport_100:,.0f} €</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 4px;">
                            <span>PTZ Transféré (Dette reprise) :</span> <strong>{crd_ptz_transfert:,.0f} €</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #1E3A8A;">
                            <span>Nouveau Prêt Bancaire (Lissé) :</span> <strong>{pv_nouveau_pret_lisse:,.0f} €</strong>
                        </div>
                    </div>
                </div>
                """.replace(',', ' '), unsafe_allow_html=True)
                
            # SCÉNARIO 2 : PRÊT RELAIS
            with col_res2:
                st.markdown(f"""
                <div style="background-color: #FFFBEB; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; height: 100%;">
                    <h4 style="color: #92400E; margin-top: 0;">2️⃣ Prêt Relais (Achat avant vente)</h4>
                    <p style="color: #B45309; font-size: 13px; margin-top: -10px;">La banque retient 30% de marge de sécurité en cas de vente difficile. Vous n'encaissez que <b>70%</b>.</p>
                    
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="font-size: 12px; color: #92400E; text-transform: uppercase; font-weight: bold;">Budget d'Achat Global</div>
                        <div style="font-size: 32px; font-weight: 900; color: #D97706;">{enveloppe_relais_70:,.0f} €</div>
                    </div>
                    
                    <div style="background-color: white; border-radius: 6px; padding: 12px; border: 1px solid #FDE68A;">
                        <div style="font-weight: bold; color: #92400E; margin-bottom: 8px; border-bottom: 1px dashed #FDE68A; padding-bottom: 4px;">Plan de financement :</div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 4px;">
                            <span>Apport (Avance Relais à 70%) :</span> <strong>{apport_70:,.0f} €</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #DB2777; margin-bottom: 4px;">
                            <span>PTZ Transféré (Dette reprise) :</span> <strong>{crd_ptz_transfert:,.0f} €</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #1E3A8A;">
                            <span>Nouveau Prêt Bancaire (Lissé) :</span> <strong>{pv_nouveau_pret_lisse:,.0f} €</strong>
                        </div>
                    </div>
                </div>
                """.replace(',', ' '), unsafe_allow_html=True)
                
            # --- CONCLUSION PÉDAGOGIQUE ---
            st.markdown(f"""
            <div style="text-align: center; margin-top: 20px; background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 15px; border-radius: 8px;">
                <div style="margin: 0; font-size: 18px; font-weight: 800; color: #0F172A;">💡 Bilan de l'opération</div>
                <div style="margin: 5px 0 0 0; font-size: 14px; color: #334155;">
                    S'engager sur un prêt relais ampute immédiatement votre budget d'achat de <b>{gain_location:,.0f} €</b> par rapport à une vente ferme. 
                    <br><i>Posez-vous la question : Cette somme justifie-t-elle de louer un logement de transition pendant quelques mois pour sécuriser la vente ?</i>
                </div>
            </div>
            """.replace(',', ' '), unsafe_allow_html=True)

            # --- F. GRAPHIQUE PÉDAGOGIQUE DU NOUVEAU LISSAGE ---
            st.write("---")
            st.markdown("#### 📊 Fonctionnement de votre futur crédit (Identique aux 2 scénarios)")
            st.write(f"Quel que soit votre choix, voici comment la banque va construire votre nouvelle mensualité de {mens_cible_future} € : le nouveau prêt (en bleu) viendra parfaitement combler les trous laissés par les paliers de votre vieux PTZ transféré (en rose).")
            
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
