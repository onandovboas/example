import streamlit as st
import pandas as pd
import pubchempy as pcp
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Supplier Form", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1RJu6e0Lt4Hj_Opz0LY0eZgve0OTN7Aa1akJOm1sxqeQ/edit?usp=sharing"

todos_os_paises = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

# ---- TÍTULO E INTRODUÇÃO ----
st.title("Request for Quotation")

st.markdown("""
**Dear Supplier/ Partner**,  
Your Company has been invited to send a quotation for the referred API. Kindly submit your details below. Fields marked with an asterisk (\*) are mandatory.
""")

st.divider()

# --- SEÇÃO 1: INFORMAÇÕES GERAIS ---
st.header("General Information")

# Função para buscar o nome do composto a partir do CAS Number usando PubChem (com cache para otimizar)
@st.cache_data
def buscar_pubchem(cas):
    try:
        resultados = pcp.get_compounds(cas, 'name')
        if resultados:
            composto = resultados[0]
            return composto.synonyms[0] if composto.synonyms else composto.iupac_name
        return "Not found"
    except Exception:
        return "Error"

col1, col2 = st.columns(2)

with col1:
    cas_number_input = st.text_input("CAS Number *", help="Example: 15687-27-1 (Ibuprofen)")
    
    api_encontrado = ""
    if cas_number_input:
        with st.spinner("Buscando na base mundial do PubChem..."):
            # Chamar a função com cache
            api_encontrado = buscar_pubchem(cas_number_input)
            
            if api_encontrado not in ["Not found", "Error"]:
                st.success(f"API Encontrado: **{api_encontrado}**")
            elif api_encontrado == "Not found":
                st.error("CAS Number não encontrado no PubChem.")
            else:
                st.error("Erro na busca. Verifique a internet ou tente novamente.")
            
    api = st.text_input("API", value=api_encontrado if api_encontrado not in ["Not found", "Error", ""] else "", disabled=True)

with col2:
    country = st.selectbox("Country of Origin *", todos_os_paises, index=None, placeholder="Select a country...")
    manufacturer = st.text_input("Manufacturer *")

st.divider()

# --- SEÇÃO 2: INFORMAÇÕES COMERCIAIS ---
st.header("Commercial Information")

st.subheader("Specifications")
specs = ["USP with FDA", "USP without FDA", "EP with CEP", "EP without CEP", "In house", "Other Markets"]
currencies = ["USD", "EUR", "BRL"]
incoterms_list = ["EXW", "FCA", "FOB", "CPT", "CIP", "CFR", "CIF", "Not Applicable"]

for spec in specs:
    with st.expander(f"Specification: {spec}", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.selectbox("Currency", currencies, key=f"curr_{spec}")
        with c2: st.number_input("Price for Development Phase (/ kg)", min_value=0.0, format="%.2f", key=f"dev_{spec}")
        with c3: st.number_input("Price for Commercial Phase (/ kg)", min_value=0.0, format="%.2f", key=f"com_{spec}")
        with c4: st.selectbox("Incoterm", incoterms_list, key=f"inco_spec_{spec}")

st.subheader("Part 2 - Operations")
direct_ent = st.radio("Does the manufacturer accept to negotiate and work directly with our enterprise?", ["Yes", "No"])

brazil_agent = ""
if direct_ent == "No":
    brazil_agent = st.text_input("If no, please inform the exclusive agent or representative in Brazil *")

exp_locations = st.multiselect("Does the manufacturer have experience working with which locations?", 
                               ["Brazil", "Mexico", "US", "Europe", "Other Markets"])

other_markets = []
if "Other Markets" in exp_locations:
    other_markets = st.multiselect("Please specify the other markets:", todos_os_paises)

st.markdown("#### Logistics & Commercial Terms")
c_a, c_b, c_c = st.columns(3)
with c_a: 
    lead_time_choice = st.radio("Production Lead Time After PO", ["Immediate", "Other"])
    if lead_time_choice == "Other":
        lead_time = st.number_input("Please inform (days)", min_value=0, step=1)
    else:
        lead_time = "Immediate"
with c_b: 
    transit_time = st.number_input("Transit Time (from origin to the final destiny) (days)", min_value=0, step=1)
with c_c: 
    incoterm_gen = st.selectbox("Incoterm (General)", incoterms_list)

c_d, c_e = st.columns(2)
with c_d: pay_term_dev = st.number_input("Payment terms for Development Phase (days)", min_value=0, step=1)
with c_e: moq = st.text_area("Minimum Order Quantity")

st.markdown("#### Regulatory & Stability")
reg1, reg2, reg3 = st.columns(3)
with reg1: 
    dmf_brazil = st.radio("Available DMF for Brazil?", ["Yes", "No"])

stability_opts = ["Yes", "No", "We will arrange once project is approved"]
with reg2: 
    photo_study = st.selectbox("Photostability Study", stability_opts)
with reg3: 
    zone_ivb = st.selectbox("Zone IVb Stability", stability_opts)

st.warning("Kindly note that our enterprise has a 120 days payment term policy for Commercial Phase.")
pay_acceptable = st.radio("Is that acceptable?", ["Yes", "No"])

pay_conditions = ""
if pay_acceptable == "No":
    pay_conditions = st.text_area("Please inform your conditions")

st.divider()

# --- SEÇÃO 3: TECHNICAL INFORMATION ---
st.header("Technical Information")
t1, t2 = st.columns(2)
with t1:
    opcoes_polimorfos = ["Amorphous", "Crystalline", "Form I", "Form II", "Form III", "Hydrate", "Solvate", "Other"]
    poly_form = st.selectbox("Polymorphic Form", opcoes_polimorfos)
    
    other_poly_form = ""
    if poly_form == "Other":
        other_poly_form = st.text_input("Please specify the Polymorphic Form:")

with t2:
    psd_std = st.text_input("Particle Size Distribution (Standard)")

psd_req = st.radio("Does the manufacturer have the PSD required?", ["Yes", "No"], 
         help="In case the specification was declared by e-mail")

st.divider()

# --- SEÇÃO 4: COMPLEMENTARY INFORMATION ---
st.header("Complementary Information")

st.subheader("Manufacturing Details")
st.caption("*(Shall be the same used and informed in DMF)*")
m_col1, m_col2 = st.columns(2)
with m_col1:
    manuf_country = st.selectbox("Manufacturing Country", todos_os_paises, key="m_country", index=None, placeholder="Select a country...")
with m_col2:
    manuf_city = st.text_input("Manufacturing City")
manuf_address = st.text_area("Manufacturing Street Address", help="Shall be the same used and informed in DMF")

st.subheader("Exporter Details")
exporter_name = st.text_input("Complete Exporter’s Name")
e_col1, e_col2 = st.columns(2)
with e_col1:
    exp_country = st.selectbox("Exporter Country", todos_os_paises, key="e_country", index=None, placeholder="Select a country...")
with e_col2:
    exp_city = st.text_input("Exporter City")
exp_address = st.text_area("Exporter Street Address")

st.subheader("Certifications & Capabilities")
comp1, comp2 = st.columns(2)
with comp1:
    capacity = st.text_input("Monthly Production Capacity")
with comp2:
    gmp = st.multiselect("Does the manufacturer has GMP? (Or any other valid certificate, please specify)", 
                         ["Brazil", "Mexico", "USA", "Europe", "Other"])
    other_gmp = []
    if "Other" in gmp:
        other_gmp = st.multiselect("Please specify other countries/certificates:", todos_os_paises)

st.write("Does the manufacturer has CADIFA?")
st.caption("More info: [https://coifaeng.anvisa.gov.br/cadifa.html](https://coifaeng.anvisa.gov.br/cadifa.html)")
cadifa = st.radio("CADIFA Status", 
                  ["Yes", "No. Is willing to (or has intention)", "No. Is not willing to (has no intention)"],
                  label_visibility="collapsed")

cadifa_num = ""
if cadifa == "Yes":
    cadifa_num = st.text_input("Please inform its number:")

st.divider()

# --- FINAL DETAILS ---
st.header("Final Details")
notes = st.text_area("Notes")

c_name, c_email = st.columns(2)
with c_name: rep_name = st.text_input("Your Name *")
with c_email: rep_email = st.text_input("Your E-mail *")


# --- LÓGICA DE SALVAR DADOS E VALIDAÇÃO ---
if st.button("Submit Form"):
    campos_faltantes = []
    
    if not cas_number_input: campos_faltantes.append("CAS Number")
    if not country: campos_faltantes.append("Country of Origin")
    if not manufacturer: campos_faltantes.append("Manufacturer")
    if not rep_name: campos_faltantes.append("Your Name")
    if not rep_email: campos_faltantes.append("Your E-mail")
        
    if len(campos_faltantes) > 0:
        st.error(f"⚠️ Please, fill in the required fields before submitting: **{', '.join(campos_faltantes)}**")
    else:
        data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Dicionário com todos os dados coletados no formulário.
        dados_fornecedor = {
            "Submission Date": data_hora_atual,
            "CAS Number": cas_number_input,
            "API Name": api,
            "Origin Country": country,
            "Manufacturer": manufacturer,
            "Direct Negotiate": direct_ent,
            "Brazil Agent": brazil_agent,
            "Exp Locations": ", ".join(exp_locations),
            "Other Markets": ", ".join(other_markets),
            "Lead Time": lead_time,
            "Transit Time (Days)": transit_time,            
            "Pay Term Dev": pay_term_dev,
            "MOQ": moq,
            "Incoterm Gen": incoterm_gen,
            "DMF Brazil": dmf_brazil,                       
            "Photostability Study": photo_study,            
            "Zone IVb Stability": zone_ivb,                 
            "120 Days Accept": pay_acceptable,
            "Pay Conditions": pay_conditions,
            "Poly Form": poly_form if poly_form != "Other" else other_poly_form,
            "PSD Std": psd_std,
            "PSD Req": psd_req,
            "Manuf Country": manuf_country,
            "Manuf City": manuf_city,
            "Manuf Address": manuf_address,
            "Exporter Name": exporter_name,
            "Exp Country": exp_country,
            "Exp City": exp_city,
            "Exp Address": exp_address,
            "Capacity": capacity,
            "GMP": ", ".join(gmp),
            "Other GMP": ", ".join(other_gmp),
            "CADIFA": cadifa,
            "CADIFA Num": cadifa_num,
            "Notes": notes,
            "Rep Name": rep_name,
            "Rep Email": rep_email
        }

        # Loop para adicionar dinamicamente os dados de cada especificação comercial
        for spec in specs:
            # Valores usando as chaves (keys) que foi definido no loop de exibição
            dados_fornecedor[f"{spec} - Currency"] = st.session_state[f"curr_{spec}"]
            dados_fornecedor[f"{spec} - Price Dev (/kg)"] = st.session_state[f"dev_{spec}"]
            dados_fornecedor[f"{spec} - Price Com (/kg)"] = st.session_state[f"com_{spec}"]
            dados_fornecedor[f"{spec} - Incoterm"] = st.session_state[f"inco_spec_{spec}"]

        # Transforma em tabela e salva
        df_novo = pd.DataFrame([dados_fornecedor])
        
        try:
            with st.spinner("A guardar os dados na nuvem..."):
                # Lê os dados existentes na folha "Sheet1"
                df_existente = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1")
                
                # Junta a linha nova aos dados antigos
                # Se o ficheiro estiver vazio, ignora o erro e cria as colunas
                if df_existente.empty:
                    df_atualizado = df_novo
                else:
                    # Limpa linhas vazias que o Google Sheets costuma criar
                    df_existente = df_existente.dropna(how="all") 
                    df_atualizado = pd.concat([df_existente, df_novo], ignore_index=True)
                
                # Atualiza a folha de cálculo
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=df_atualizado)
                
            st.success("Form submitted successfully!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error while saving to cloud: {e}")
