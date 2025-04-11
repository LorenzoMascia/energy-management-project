import pandas as pd
import numpy as np
import numpy_financial as npf

# ===============================
# CHP + WIND INTEGRATION
# ===============================

Pe = 800

# Upload CHP and Wind data
df_chp = pd.read_csv("load_preproc.csv")
df_chp.rename(columns={'Potenza Elettrica': 'Electric Power', 'Tempo': 'Time', 'Fascia Oraria': 'Time Band'}, inplace=True)

df_chp["Time"] = pd.to_datetime(df_chp["Time"], errors='coerce').dt.strftime('%d-%m %H:%M')
df_wind = pd.read_csv("wind_speed_h.csv")

#delete Electri Power column
df_wind = df_wind.drop(columns=['WS','Electric Power','Time Band'])

# Rename columns to merge datasets
df_wind.rename(columns={'time(UTC)': 'Time'}, inplace=True)

# Join datasets on time column
df_combined = pd.merge(df_chp, df_wind, on='Time', how='inner')

# Calculate total CHP + Wind production
df_combined["Total Power"] =  Pe + df_combined["Wind Power"]
df_combined.set_index('Time')


# Calculating surplus and deficit
df_combined["Surplus"] = df_combined["Total Power"] - df_combined["Electric Power"]
df_combined["Grid Import"] = df_combined["Surplus"].apply(lambda x: -x if x < 0 else 0)
df_combined["Surplus"] = df_combined["Surplus"].apply(lambda x: x if x > 0 else 0)

# Save the updated file
df_combined.to_csv("combined_energy_balance.csv", index=False)
print("CHP + Wind")


# ===============================
# PRIMARY ENERGY SAVING (PES) CALCULATION
# ===============================

# Load the combined data
df_combined = pd.read_csv("combined_energy_balance.csv")

# Efficiencies of the reference system
eta_t_ref = 0.9   # Boiler efficiency
eta_e_ref = 0.46  # Power grid efficiency

# Energy required by the reference system 
E_term_ref = df_combined["Potenza Termica"].sum()
E_elec_ref = df_combined["Electric Power"].sum()

# Primary energy consumption of the reference system
primary_energy_consumption_ref = (E_term_ref / eta_t_ref) + (E_elec_ref / eta_e_ref)

# CHP Efficiencies
eta_e_chp = 0.390  
eta_t_chp = 0.473  

# Energy produced by the proposed system
E_elec_prop = df_combined["Total Power"].sum()
E_term_prop = df_combined["Potenza Termica"].sum()

# Primary consumption of the proposed system
primary_energy_consumption = (E_term_prop / eta_t_chp) + (E_elec_prop / eta_e_chp)

# PES Calculation
PES = (primary_energy_consumption_ref - primary_energy_consumption) / primary_energy_consumption_ref * 100
print(f"Primary Energy Saving (PES): {PES:.2f}%")


# ===============================
# CO₂ REDUCTION CALCULATION
# ===============================

CO2_factor_grid = 0.48   # kg CO2/kWh (rete)
CO2_factor_gas = 0.2     # kg CO2/kWh (CHP)

# Reference system emissions
co2_emission_ref = (E_term_ref / eta_t_ref) * CO2_factor_gas + (E_elec_ref / eta_e_ref) * CO2_factor_grid

# Emissions of the proposed system
co2_emission = (E_term_prop / eta_t_chp) * CO2_factor_gas + (E_elec_prop / eta_e_chp) * CO2_factor_grid

# CO₂ reduction
CO2_saving = co2_emission_ref - co2_emission
print(f"CO2 Reduction: {CO2_saving/1000:.2f} tons")


# ===============================
# ECONOMIC INDICATORS
# ===============================

# Investment costs

# Turbine
I = (1000.0 * 4000.0)  + (2.0 * (Pe / 1000.0 ) ** 0.868) * 1000000
print(f"Total installation Costs {I/1000000:.2f} M")


operating_cost_RS = 5.42 * 1000000
# Operating cost CHP
operating_cost_CHP = 4.28 * 1000000
# Operating cost Wind
operating_cost_wind = 180000

# Operating cost CHP_Wind
operating_cost_CHP_wind = operating_cost_CHP + operating_cost_wind 

# Annual savings
annual_savings = operating_cost_RS - operating_cost_CHP_wind
print(f"Annual Saving: {annual_savings/1000000:.2f} M")

# SPB (Simple Payback Period)
SPB = I / annual_savings 
print(f"Simple Payback Period (SPB): {SPB:.2f} anni")

# NPV (Net Present Value)
r = 0.05  # Tasso di sconto
years = 20  # Vita utile
NPV = sum(annual_savings / (1 + r) ** t for t in range(1, years + 1)) - I
print(f"Net Present Value (NPV): {NPV:.2f} €")

# PI (Profitability Index)
PI = (NPV + I) / I
print(f"Profitability Index (PI): {PI:.2f}")

# IRR (Internal Rate of Return)
cash_flows = [-I] + [annual_savings] * years
IRR = npf.irr(cash_flows)  
print(f"Internal Rate of Return (IRR): {IRR:.2%}")

# ===============================
# ENERGY SOLD TO GRID SUMMARY
# ===============================


# Carica i dati dai CSV
df_chp = pd.read_csv("CHP_energy_sold.csv")
df_wind = pd.read_csv("Wind_energy_sold.csv")

# Converte le energie vendute da kWh a MWh nel dataframe Wind (dividendo per 1000)
df_wind["Energia Venduta (MWh)"] = df_wind["Energia Venduta (kWh)"] / 1000

# Unisce i dati in un unico DataFrame
df_total = pd.concat([df_chp[["Fonte", "Energia Venduta (MWh)"]], df_wind[["Fonte", "Energia Venduta (MWh)"]]])

# Calcola il totale dell'energia venduta in MWh
total_energy_sold = df_total["Energia Venduta (MWh)"].sum()

# Aggiunge la riga del totale
df_total = pd.concat([df_total, pd.DataFrame([{"Fonte": "Totale", "Energia Venduta (MWh)": total_energy_sold}])], ignore_index=True)

# Salva la tabella riassuntiva in un CSV
df_total.to_csv("Total_energy_sold_MWh.csv", index=False)

# Stampa la tabella riassuntiva
print("------------------------------------------------------------------")
print("                      Energy Sold to Grid (MWh)                   ")
print("------------------------------------------------------------------")
print(df_total.to_string(index=False))
print("------------------------------------------------------------------")

print("Dati salvati in Total_energy_sold_MWh.csv")