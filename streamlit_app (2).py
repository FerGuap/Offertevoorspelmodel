
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Offerteconversie Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv", parse_dates=["Aanmaakdatum"])
    return df

df = load_data()

st.title("Offerteconversie Dashboard - REZ")
st.markdown("Overzicht van conversies, marges en verkoopkansen op basis van voorspeloutput.")

col1, col2, col3 = st.columns(3)
with col1:
    selected_verkoper = st.multiselect("Selecteer Verkoper", df["Verkoper"].unique(), default=df["Verkoper"].unique())
with col2:
    selected_klant = st.multiselect("Selecteer Klant", df["klant"].unique(), default=df["klant"].unique())
with col3:
    date_range = st.date_input("Periode", [df["Aanmaakdatum"].min().date(), df["Aanmaakdatum"].max().date()])

# Zet de datums om naar Timestamp
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

mask = (
    df["Verkoper"].isin(selected_verkoper) &
    df["klant"].isin(selected_klant) &
    df["Aanmaakdatum"].between(start_date, end_date)
)
filtered_df = df[mask]

total_offertes = len(filtered_df)
conversion_ratio = (filtered_df["voorspelling"] == "Conversie").mean()
avg_total = filtered_df["Totaal"].mean()
avg_confidence = filtered_df["zekerheid_conversie"].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Totaal aantal offertes", f"{total_offertes}")
kpi2.metric("Conversieratio", f"{conversion_ratio:.0%}")
kpi3.metric("Gemiddelde offertewaarde", f"€ {avg_total:,.2f}")
kpi4.metric("Gemiddelde kans op conversie", f"{avg_confidence:.0%}")

st.markdown("### Conversieratio per maand")
monthly = (
    filtered_df
    .groupby(pd.Grouper(key="Aanmaakdatum", freq="M"))
    .agg(conversieratio=("voorspelling", lambda x: (x == "Conversie").mean()))
    .reset_index()
)

line_chart = alt.Chart(monthly).mark_line(point=True).encode(
    x=alt.X("Aanmaakdatum:T", title="Maand"),
    y=alt.Y("conversieratio:Q", title="Conversieratio"),
    tooltip=["Aanmaakdatum", alt.Tooltip("conversieratio", format=".0%")]
).properties(width=700, height=300)

st.altair_chart(line_chart, use_container_width=True)

st.markdown("### Offertes: Marge % vs. Kans op conversie")
scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.6).encode(
    x=alt.X("marge_%:Q", title="Marge %"),
    y=alt.Y("zekerheid_conversie:Q", title="Kans op conversie"),
    color="Verkoper:N",
    tooltip=["klant", "Totaal", "marge_%", "zekerheid_conversie"]
).interactive().properties(width=700, height=400)

st.altair_chart(scatter, use_container_width=True)
