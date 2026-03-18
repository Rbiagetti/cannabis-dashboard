import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Config pagina
st.set_page_config(page_title="Cannabis Retail Dashboard", layout="wide", page_icon="🌿")

# CSS custom
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #00c896;
    }
</style>
""", unsafe_allow_html=True)

# Carica dati
@st.cache_data
def load_data():
    df = pd.read_csv("Cannabis_Retail_Sales_by_Week_Ending.csv")
    df['Week Ending'] = pd.to_datetime(df['Week Ending'])
    df = df.sort_values('Week Ending')
    return df

df = load_data()

# ── Helpers ────────────────────────────────────────────────────────────────────

def send_formspree(form_url, data):
    try:
        r = requests.post(form_url, json=data, headers={"Accept": "application/json"})
        return r.status_code == 200
    except:
        return False

def info_tooltip(label, spiegazione):
    with st.expander(f"ℹ️ Come leggere: {label}"):
        st.markdown(spiegazione)

def mostra_moduli():
    st.divider()
    st.subheader("📬 Aiutaci a migliorare")
    col_f, col_i = st.columns(2)

    with col_f:
        st.markdown("#### 💬 Invia Feedback")
        with st.form("form_feedback"):
            nome     = st.text_input("Nome")
            email    = st.text_input("Email")
            chart    = st.selectbox("Grafico di riferimento", [
                "Trend vendite", "Prodotti venduti", "Prezzo medio",
                "Split Adult-Use vs Medical", "Elasticità al prezzo", "Generale"
            ])
            voto     = st.slider("Quanto è utile questa dashboard?", 1, 5, 3,
                                 format="%d ⭐")
            messaggio = st.text_area("Il tuo feedback",
                                     placeholder="Cosa funziona bene? Cosa miglioreresti?",
                                     height=120)
            inviato  = st.form_submit_button("✉️ Invia feedback", use_container_width=True)
            if inviato:
                if not nome or not email or not messaggio:
                    st.warning("Compila tutti i campi prima di inviare.")
                else:
                    ok = send_formspree("https://formspree.io/f/xreyrynr", {
                        "tipo": "FEEDBACK",
                        "nome": nome,
                        "email": email,
                        "grafico": chart,
                        "voto": f"{voto}/5",
                        "messaggio": messaggio
                    })
                    if ok:
                        st.success("Feedback inviato, grazie! 🙏")
                    else:
                        st.error("Errore nell'invio, riprova.")

    with col_i:
        st.markdown("#### 🐛 Segnala un problema")
        with st.form("form_issue"):
            nome_i   = st.text_input("Nome")
            email_i  = st.text_input("Email")
            chart_i  = st.selectbox("Grafico con il problema", [
                "Trend vendite", "Prodotti venduti", "Prezzo medio",
                "Split Adult-Use vs Medical", "Elasticità al prezzo", "Generale"
            ])
            severita = st.select_slider("Severità del problema",
                                        options=["🟢 Bassa", "🟡 Media", "🟠 Alta", "🔴 Critica"])
            descrizione = st.text_area("Descrivi il problema",
                                       placeholder="Cosa hai visto? Cosa ti aspettavi?",
                                       height=80)
            riprodurre  = st.text_area("Come riprodurlo?",
                                       placeholder="Es: 1) seleziona solo Medical, 2) cambia il filtro data…",
                                       height=80)
            inviato_i = st.form_submit_button("🚨 Segnala problema", use_container_width=True)
            if inviato_i:
                if not nome_i or not email_i or not descrizione:
                    st.warning("Compila almeno nome, email e descrizione.")
                else:
                    ok = send_formspree("https://formspree.io/f/mjgajand", {
                        "tipo": "ISSUE",
                        "nome": nome_i,
                        "email": email_i,
                        "grafico": chart_i,
                        "severita": severita,
                        "descrizione": descrizione,
                        "come_riprodurre": riprodurre
                    })
                    if ok:
                        st.success("Problema segnalato! Lo esamineremo presto 🔧")
                    else:
                        st.error("Errore nell'invio, riprova.")

# ── Layout principale ──────────────────────────────────────────────────────────

st.title("🌿 Cannabis Retail Sales Dashboard")
st.markdown("**Dati settimanali · Adult-Use vs Medical · 2023–2024**")
st.divider()

# Sidebar filtri
st.sidebar.header("🔎 Filtri")
all_dates = df['Week Ending'].sort_values().unique()
date_labels = [pd.Timestamp(d).strftime("%b %Y") for d in all_dates]
min_idx = 0
max_idx = len(all_dates) - 1

idx_start, idx_end = st.sidebar.select_slider(
    "Periodo",
    options=list(range(len(all_dates))),
    value=(min_idx, max_idx),
    format_func=lambda i: date_labels[i]
)
date_range = (pd.Timestamp(all_dates[idx_start]), pd.Timestamp(all_dates[idx_end]))

categoria = st.sidebar.multiselect(
    "Categoria",
    ["Adult-Use", "Medical"],
    default=["Adult-Use", "Medical"]
)

# Filtra
mask = (df['Week Ending'] >= date_range[0]) & \
       (df['Week Ending'] <= date_range[1])
df_f = df[mask]

# ── KPI ────────────────────────────────────────────────────────────────────────
st.subheader("📊 Riepilogo periodo")
info_tooltip("KPI di riepilogo", """
- **Vendite totali** — somma di Adult-Use + Medical nel periodo selezionato
- **Prodotti venduti** — numero totale di unità vendute (non fatturato)
- **Prezzo medio Adult-Use / Medical** — media settimanale del prezzo per prodotto nelle due categorie
- Usa il filtro date nella sidebar per confrontare periodi diversi
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendite totali", f"${df_f['Total Adult-Use and Medical Sales'].sum()/1e6:.1f}M")
col2.metric("Prodotti venduti", f"{df_f['Total Products Sold'].sum():,}")
col3.metric("Prezzo medio Adult-Use", f"${df_f['Adult-Use Average Product Price'].mean():.2f}")
col4.metric("Prezzo medio Medical", f"${df_f['Medical Average Product Price'].mean():.2f}")

st.divider()

# ── Grafico 1 — Trend vendite ──────────────────────────────────────────────────
st.subheader("📈 Trend vendite nel tempo")
info_tooltip("Trend vendite", """
- **Linea verde** = vendite settimanali Adult-Use ($)
- **Linea rossa** = vendite settimanali Medical ($)
- **Picchi verso l'alto** → settimane eccezionali (festività, promozioni, nuove aperture)
- **Trend crescente** nel tempo indica espansione del mercato
- Passa il mouse sul grafico per vedere i valori esatti di ogni settimana
- Usa il filtro date nella sidebar per zoomare su un periodo specifico
""")

fig1 = go.Figure()
if "Adult-Use" in categoria:
    fig1.add_trace(go.Scatter(
        x=df_f['Week Ending'], y=df_f['Adult-Use Retail Sales'],
        name='Adult-Use', line=dict(color='#00c896', width=2),
        fill='tozeroy', fillcolor='rgba(0,200,150,0.1)'
    ))
if "Medical" in categoria:
    fig1.add_trace(go.Scatter(
        x=df_f['Week Ending'], y=df_f['Medical Marijuana Retail Sales'],
        name='Medical', line=dict(color='#ff6b6b', width=2),
        fill='tozeroy', fillcolor='rgba(255,107,107,0.1)'
    ))
fig1.update_layout(hovermode='x unified', height=350, margin=dict(t=20))
st.plotly_chart(fig1, use_container_width=True)

# ── Grafico 2 — Prodotti venduti ───────────────────────────────────────────────
st.subheader("📦 Prodotti venduti per settimana")
info_tooltip("Prodotti venduti", """
- **Barre verdi** = unità Adult-Use vendute ogni settimana
- **Barre rosse** = unità Medical vendute ogni settimana
- Confronta l'altezza delle barre per capire quale categoria muove più volume
- Un aumento di vendite senza aumento di fatturato può indicare calo del prezzo medio
- Un calo improvviso può segnalare problemi di stock o stagionalità
""")

fig2 = go.Figure()
if "Adult-Use" in categoria:
    fig2.add_trace(go.Bar(
        x=df_f['Week Ending'], y=df_f['Adult-Use Products Sold'],
        name='Adult-Use', marker_color='#00c896', opacity=0.8
    ))
if "Medical" in categoria:
    fig2.add_trace(go.Bar(
        x=df_f['Week Ending'], y=df_f['Medical Products Sold'],
        name='Medical', marker_color='#ff6b6b', opacity=0.8
    ))
fig2.update_layout(barmode='group', height=350, margin=dict(t=20))
st.plotly_chart(fig2, use_container_width=True)

# ── Grafici 3 e 4 affiancati ───────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("💰 Prezzo medio prodotto")
    info_tooltip("Prezzo medio prodotto", """
- Mostra l'andamento del **prezzo medio per unità** venduta ogni settimana
- **Adult-Use** tende ad avere prezzi più alti per via della leva commerciale
- **Medical** è spesso più stabile perché legato a prescrizioni e rimborsi
- Un calo del prezzo medio può indicare promozioni, cambio del mix prodotti o pressione competitiva
""")
    fig3 = go.Figure()
    if "Adult-Use" in categoria:
        fig3.add_trace(go.Scatter(
            x=df_f['Week Ending'], y=df_f['Adult-Use Average Product Price'],
            name='Adult-Use', line=dict(color='#00c896', width=2)
        ))
    if "Medical" in categoria:
        fig3.add_trace(go.Scatter(
            x=df_f['Week Ending'], y=df_f['Medical Average Product Price'],
            name='Medical', line=dict(color='#ff6b6b', width=2)
        ))
    fig3.update_layout(height=300, margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    st.subheader("🥧 Split Adult-Use vs Medical")
    info_tooltip("Split Adult-Use vs Medical", """
- Mostra la **quota di mercato in valore ($)** di ciascuna categoria nel periodo selezionato
- Una quota Medical > 50% indica un mercato ancora dominato dall'uso terapeutico
- Nel tempo, i mercati maturi tendono a spostare il peso verso l'Adult-Use
- Cambia il filtro date per vedere come lo split evolve nel tempo
""")
    totals = {
        'Adult-Use': df_f['Adult-Use Retail Sales'].sum(),
        'Medical': df_f['Medical Marijuana Retail Sales'].sum()
    }
    fig4 = px.pie(
        values=list(totals.values()),
        names=list(totals.keys()),
        color_discrete_sequence=['#00c896', '#ff6b6b'],
        hole=0.4
    )
    fig4.update_layout(height=300, margin=dict(t=20))
    st.plotly_chart(fig4, use_container_width=True)

# ── Elasticità al prezzo ───────────────────────────────────────────────────────
st.divider()
st.subheader("🔬 Elasticità al prezzo")
info_tooltip("Elasticità al prezzo", """
- **Elasticità = % variazione vendite ÷ % variazione prezzo** (settimana su settimana)
- **Valore < -1** → domanda **elastica**: un aumento del prezzo riduce significativamente le vendite
- **Valore tra -1 e 0** → domanda **anelastica**: le vendite resistono ai cambi di prezzo (tipico per prodotti medici o di prima necessità)
- **Valore > 0** → apparente anomalia: vendite e prezzo salgono insieme — spesso effetto stagionale o lancio di nuovi prodotti premium
- La **linea tratteggiata a -1** è la soglia di elasticità unitaria: sopra = anelastica, sotto = elastica
- Gli **spike estremi** (picchi molto alti o bassi) si verificano nelle settimane in cui la variazione di prezzo è minima (divisione per quasi-zero): da leggere con cautela
- **Scatter (sinistra)**: ogni punto è una settimana. La trendline mostra la direzione generale della relazione prezzo-vendite
""")

df_f = df_f.copy()
for cat, price_col, sales_col in [
    ("Adult-Use", "Adult-Use Average Product Price",    "Adult-Use Retail Sales"),
    ("Medical",   "Medical Average Product Price",      "Medical Marijuana Retail Sales")
]:
    df_f[f'{cat}_price_pct']  = df_f[price_col].pct_change() * 100
    df_f[f'{cat}_sales_pct']  = df_f[sales_col].pct_change() * 100
    df_f[f'{cat}_elasticity'] = df_f[f'{cat}_sales_pct'] / df_f[f'{cat}_price_pct']

df_elas = df_f.dropna()

col_e1, col_e2 = st.columns(2)

with col_e1:
    st.markdown("**Scatter: prezzo vs vendite**")
    fig_s = go.Figure()
    if "Adult-Use" in categoria:
        fig_s.add_trace(go.Scatter(
            x=df_f['Adult-Use Average Product Price'],
            y=df_f['Adult-Use Retail Sales'],
            mode='markers', name='Adult-Use',
            marker=dict(color='#00c896', size=8, opacity=0.7),
        ))
    if "Medical" in categoria:
        fig_s.add_trace(go.Scatter(
            x=df_f['Medical Average Product Price'],
            y=df_f['Medical Marijuana Retail Sales'],
            mode='markers', name='Medical',
            marker=dict(color='#ff6b6b', size=8, opacity=0.7),
        ))
    if "Adult-Use" in categoria:
        x = df_f['Adult-Use Average Product Price'].dropna()
        y = df_f['Adult-Use Retail Sales'].dropna()
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        fig_s.add_trace(go.Scatter(
            x=x_line, y=p(x_line), mode='lines', name='Trend Adult-Use',
            line=dict(color='#00c896', dash='dash', width=1)
        ))
    if "Medical" in categoria:
        x = df_f['Medical Average Product Price'].dropna()
        y = df_f['Medical Marijuana Retail Sales'].dropna()
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        fig_s.add_trace(go.Scatter(
            x=x_line, y=p(x_line), mode='lines', name='Trend Medical',
            line=dict(color='#ff6b6b', dash='dash', width=1)
        ))
    fig_s.update_layout(
        height=350, margin=dict(t=20),
        xaxis_title="Prezzo medio ($)",
        yaxis_title="Vendite ($)"
    )
    st.plotly_chart(fig_s, use_container_width=True)

with col_e2:
    st.markdown("**Elasticità settimana per settimana**")
    fig_e = go.Figure()
    if "Adult-Use" in categoria:
        fig_e.add_trace(go.Scatter(
            x=df_elas['Week Ending'],
            y=df_elas['Adult-Use_elasticity'].clip(-10, 10),
            name='Adult-Use', line=dict(color='#00c896', width=2),
            mode='lines+markers'
        ))
    if "Medical" in categoria:
        fig_e.add_trace(go.Scatter(
            x=df_elas['Week Ending'],
            y=df_elas['Medical_elasticity'].clip(-10, 10),
            name='Medical', line=dict(color='#ff6b6b', width=2),
            mode='lines+markers'
        ))
    fig_e.add_hline(y=0,  line_dash="dash", line_color="gray",  opacity=0.5)
    fig_e.add_hline(y=-1, line_dash="dot",  line_color="white", opacity=0.3,
                    annotation_text="elasticità unitaria",
                    annotation_position="bottom right")
    fig_e.update_layout(
        height=350, margin=dict(t=20),
        yaxis_title="Elasticità (% Δvendite / % Δprezzo)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_e, use_container_width=True)

st.markdown("**Elasticità media nel periodo selezionato**")
kpi1, kpi2 = st.columns(2)
if "Adult-Use" in categoria:
    e_au = df_elas['Adult-Use_elasticity'].clip(-10, 10).mean()
    kpi1.metric("Adult-Use", f"{e_au:.2f}",
                help="< -1 = elastica | -1 a 0 = anelastica | > 0 = anomala")
if "Medical" in categoria:
    e_med = df_elas['Medical_elasticity'].clip(-10, 10).mean()
    kpi2.metric("Medical", f"{e_med:.2f}",
                help="< -1 = elastica | -1 a 0 = anelastica | > 0 = anomala")

# ── Tabella dati grezzi ────────────────────────────────────────────────────────
st.divider()
st.subheader("🗂 Dati grezzi")
info_tooltip("Tabella dati grezzi", """
- Mostra i dati settimanali originali filtrati per il periodo selezionato
- Le colonne con **$** sono in dollari; le colonne **Products Sold** sono in unità
- Clicca sull'intestazione di una colonna per ordinare i dati
- Puoi scaricare la tabella come CSV cliccando sull'icona in alto a destra della tabella
""")

cols_to_format = {
    'Adult-Use Retail Sales':             '${:,.0f}',
    'Medical Marijuana Retail Sales':     '${:,.0f}',
    'Total Adult-Use and Medical Sales':  '${:,.0f}',
    'Adult-Use Average Product Price':    '${:.2f}',
    'Medical Average Product Price':      '${:.2f}',
}
display_cols = [c for c in cols_to_format if c in df_f.columns]
st.dataframe(
    df_f.style.format({c: cols_to_format[c] for c in display_cols}),
    use_container_width=True,
    height=300
)

# ── Moduli feedback / issue ────────────────────────────────────────────────────
mostra_moduli()