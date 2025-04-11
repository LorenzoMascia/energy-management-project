import pandas as pd

def process_energy_data(file_path, Pe, Pt, NumH, eta_e, eta_t):
    # Read CSV File
    df = pd.read_csv(file_path)

    # Sort by Electric Power Desc
    df_sorted = df.sort_values(by='Potenza Elettrica', ascending=False)

    # Get first NumH elements
    df_top = df_sorted.head(NumH)

    # Initialize results dictionary
    results = {
        'F1': {'surplus': 0, 'integration': 0, 'provided_by_chp': 0, 'self_consumption': 0, 'energy_sold_to_grid': 0, 'KWhs': .169, "KWha": .137},
        'F2': {'surplus': 0, 'integration': 0, 'provided_by_chp': 0, 'self_consumption': 0, 'energy_sold_to_grid': 0, 'KWhs': .174, "KWha": .142},
        'F3': {'surplus': 0, 'integration': 0, 'provided_by_chp': 0, 'self_consumption': 0, 'energy_sold_to_grid': 0, 'KWhs': .163, "KWha": .131}
    }

    # Initialize variables
    provided_by_chp_t = 0
    surplus_t = 0
    integration_t = 0
    hours = NumH

    tot_t = 0
    tot_e = 0
    F1 = 0  # ref system
    F2 = 0  # ref system
    F3 = 0  # ref system

    committed_power = 0
    committed_power_ref = 0

    # Process each row in the dataframe
    for _, row in df_top.iterrows():
        fascia_oraria = row['Fascia Oraria']
        potenza_elettrica = row['Potenza Elettrica']
        potenza_termica = row["Potenza Termica"]

        committed_power_ref = max(committed_power_ref, potenza_elettrica)

        tot_e += potenza_elettrica
        tot_t += potenza_termica

        if fascia_oraria == "F1":
            F1 += potenza_elettrica
        elif fascia_oraria == "F2":
            F2 += potenza_elettrica
        else:
            F3 += potenza_elettrica

        # Compute surplus, integration, and energy sold to grid
        if potenza_elettrica > Pe:
            integration = potenza_elettrica - Pe
            results[fascia_oraria]['integration'] += integration
            results[fascia_oraria]['self_consumption'] += Pe
            results[fascia_oraria]['energy_sold_to_grid'] += integration  # Energia venduta alla rete
            committed_power = max(committed_power, integration)
        else:
            surplus = Pe - potenza_elettrica
            results[fascia_oraria]['surplus'] += surplus
            results[fascia_oraria]['self_consumption'] += potenza_elettrica
            results[fascia_oraria]['energy_sold_to_grid'] += 0  # Nessuna energia venduta

        # Update provided_by_chp
        results[fascia_oraria]['provided_by_chp'] += Pe

        # Compute thermal surplus and integration
        if potenza_termica > Pt:
            integration_t += potenza_termica - Pt
            provided_by_chp_t += Pt
        else:
            surplus_t += Pt - potenza_termica
            provided_by_chp_t += potenza_termica

    # Calculate totals
    tot_supplied_by_chp = 0
    tot_self_consumption = 0
    tot_surplus = 0
    tot_integration = 0
    tot_energy_sold_to_grid = 0

    # Print Results for each Time Band
    for fascia, values in results.items():
        tot_supplied_by_chp += values['provided_by_chp']
        tot_self_consumption += values['self_consumption']
        tot_surplus += values['surplus']
        tot_integration += values['integration']
        tot_energy_sold_to_grid += values['energy_sold_to_grid']
        p = values['self_consumption'] / values['provided_by_chp']
        cKW = p * values['KWha'] + (1 - p) * values['KWhs']
        print(f"  CKW_heRef {fascia}: {cKW:.4f}")

    print()
    print()

    print("------------------------------------------------------------------")
    print(f"  Thermal Energy Provided By CHP: {provided_by_chp_t / 1000:.2f} MWh")
    print(f"  Thermal Surplus (Heat Waste): {surplus_t / 1000:.2f} MWh")
    print(f"  Boiler Integration: {integration_t / 1000:.2f} MWh")
    print("------------------------------------------------------------------")

    print()
    print()

    ## ENERGY ANALYSIS
    eta_t_ref = 0.9
    primary_energy_consumption_boiler = integration_t / eta_t_ref
    total_supplied_termal_energy = provided_by_chp_t + integration_t

    print("------------------------------------------------------------------")
    print("                     PROPOSED SYSTEM                              ")
    print("----------------- Thermal Energy Balance (MWh) -------------------")
    print("------------------------------------------------------------------")
    print("                 THERMAL ENERGY BALANCE (MWh)                     ")
    print("------------------------------------------------------------------")
    print("                        Supplyed Energy                           ")
    print("------------------------------------------------------------------")
    print(f" Recovered from CHP plant          : {provided_by_chp_t / 1E3:.2f} MWh")
    print(f" Supplyed by boiler                : {integration_t / 1E3:.2f} MWh")
    print(f" TOTAL                             : {total_supplied_termal_energy / 1E3:.2f} MWh")
    print("------------------------------------------------------------------")
    print(f" Primary Energy consumption boiler : {primary_energy_consumption_boiler / 1E3:.2f}")
    print("------------------------------------------------------------------")
    print("                      ELECTRICITY (MWh)                           ")
    print("------------------------------------------------------------------")
    print("                      Supplyed Electricity                        ")
    print("------------------------------------------------------------------")
    print("                     |    F1    |    F2    |    F3    |  TOTAL   |")

    f1 = results['F1']['provided_by_chp']
    f2 = results['F2']['provided_by_chp']
    f3 = results['F3']['provided_by_chp']
    print(f"Supplied by CHP      | {f1 / 1E3:8.2f} | {f2 / 1E3:8.2f} | {f3 / 1E3:8.2f} | {tot_supplied_by_chp / 1E3:8.2f} |")

    f1 = results['F1']['self_consumption']
    f2 = results['F2']['self_consumption']
    f3 = results['F3']['self_consumption']
    print(f"Self-consumption     | {f1 / 1E3:8.2f} | {f2 / 1E3:8.2f} | {f3 / 1E3:8.2f} | {tot_self_consumption / 1E3:8.2f} |")

    f1 = results['F1']['surplus']
    f2 = results['F2']['surplus']
    f3 = results['F3']['surplus']
    print(f"Surplus              | {f1 / 1E3:8.2f} | {f2 / 1E3:8.2f} | {f3 / 1E3:8.2f} | {tot_surplus / 1E3:8.2f} |")

    f1 = results['F1']['integration']
    f2 = results['F2']['integration']
    f3 = results['F3']['integration']
    print(f"Integration          | {f1 / 1E3:8.2f} | {f2 / 1E3:8.2f} | {f3 / 1E3:8.2f} | {tot_integration / 1E3:8.2f} |")

    supplied_to_user = tot_supplied_by_chp + tot_integration

    print("------------------------------------------------------------------")
    print(f"Supplied to user (E_CHP + Integration) : {supplied_to_user / 1E3:.2f} MWh")
    print("------------------------------------------------------------------")

    # Print Energy Sold to Grid
    print("------------------------------------------------------------------")
    print("                      Energy Sold to Grid (MWh)                   ")
    print("------------------------------------------------------------------")
    print("                     |    F1    |    F2    |    F3    |  TOTAL   |")
    f1_sold = results['F1']['energy_sold_to_grid'] / 1E3
    f2_sold = results['F2']['energy_sold_to_grid'] / 1E3
    f3_sold = results['F3']['energy_sold_to_grid'] / 1E3
    total_sold = f1_sold + f2_sold + f3_sold
    print(f"Energy Sold to Grid | {f1_sold:8.2f} | {f2_sold:8.2f} | {f3_sold:8.2f} | {total_sold:8.2f} |")
    print("------------------------------------------------------------------")

    # **Salvare i dati in un CSV**
    df = pd.DataFrame({
        "Fonte": ["F1", "F2", "F3", "Totale"],
        "Energia Venduta (MWh)": [f1_sold, f2_sold, f3_sold, total_sold]
    })
    df.to_csv("CHP_energy_sold.csv", index=False)

    # (Opzionale) Messaggio di conferma
    print("Dati salvati in CHP_energy_sold.csv")

    eta_e_ref = 0.46

    ep_chp = tot_supplied_by_chp / eta_e
    integration_from_national_grid = tot_integration / eta_e_ref

    total_primary_energy_consumption = ep_chp + integration_from_national_grid

    print("------------------------------------------------------------------")
    print("                  Primary Energy Consumption                      ")
    print("------------------------------------------------------------------")
    print(f" CHP plant                         : {ep_chp/1E3:.2f} MWh")                            #EpCHP
    print(f" Integration from national grid    : {integration_from_national_grid/1E3:.2f} MWh")
    print("------------------------------------------------------------------")
    print(f" TOTAL: {total_primary_energy_consumption/1E3:.2f} MWh")                              #C
    print("------------------------------------------------------------------")      


    supplied_energy = total_supplied_termal_energy + supplied_to_user 
    primary_energy_consumption = primary_energy_consumption_boiler + total_primary_energy_consumption
    total_fuel_efficiency = supplied_energy/primary_energy_consumption
    co2_emission = (primary_energy_consumption_boiler +  ep_chp)*0.2 + tot_integration*0.48 

    print("------------------------------------------------------------------")
    print("                  Overall Energy Balance                          ")
    print("------------------------------------------------------------------")
    print(f" Supplied energy (heat + electricity)       : {supplied_energy/1E3:.2f} MWh")                           
    print(f" Primary energy consumption                 : {primary_energy_consumption/1E3:.2f} MWh")
    print(f" Total fuel efficiency                      : {total_fuel_efficiency/1E3:.2f} MWh")
    print(f" C02 emissions (t)                          : {co2_emission:.2f}")
    print("------------------------------------------------------------------")
   
    print()
    print()

    boiler_primary_energy_consumption_ref = tot_t/eta_t_ref
    consumptio_of_reference_thermal_power_system =tot_e/eta_e_ref


    print("------------------------------------------------------------------")
    print("                     Reference System                             ")
    print("------------------------------------------------------------------")
    print("                   Thermal Energy Balance                         ")
    print("------------------------------------------------------------------")
    print("                       Supplied Energy                            ")
    print("------------------------------------------------------------------")
    print(f" Supplied by boiler: {tot_t/1E3:.2f}")    #1'
    print("------------------------------------------------------------------")
    print("                   Primary energy consmption                      ")
    print("------------------------------------------------------------------")
    print(f" Boiler primary energy consumption: {boiler_primary_energy_consumption_ref/1E3:.2f}"); #A'
    print("------------------------------------------------------------------")
    print("                      ELECTRICITY (MWh)                           ")
    print("------------------------------------------------------------------")
    print("                      Supplyed Electricity                        ")
    print("------------------------------------------------------------------")
    print("                     |    F1    |    F2    |    F3    |  TOTAL   |")
    print(f"                     | {F1/1E3:8.2f} | {F2/1E3:8.2f} | {F3/1E3:8.2f} | {tot_e/1E3:8.2f} |") 
    print("------------------------------------------------------------------")
    print(f" Supplied to user: {tot_t/1E3:.2f}")    #3'
    print("------------------------------------------------------------------")
    print("                   Primary energy consmption                      ")
    print("------------------------------------------------------------------")
    print(f" Consumptio of reference thermal-power system: {consumptio_of_reference_thermal_power_system/1E3:.2f}"); #C'

    supplied_energy_ref = tot_t + tot_e 
    primary_energy_consumption_ref = boiler_primary_energy_consumption_ref + consumptio_of_reference_thermal_power_system
    supplied_energy_surplus = supplied_energy_ref + surplus_t
    primary_energy_consumption_surplus_ref = boiler_primary_energy_consumption_ref + consumptio_of_reference_thermal_power_system + surplus_t/eta_e_ref
    total_fuel_efficiency_ref = supplied_energy_surplus/primary_energy_consumption_surplus_ref
    co2_emission_ref = boiler_primary_energy_consumption_ref*0.2 + tot_e*0.48 
 
    print("------------------------------------------------------------------")
    print("                  Overall Energy Balance                          ")
    print("------------------------------------------------------------------")
    print(f" Supplied energy (heat + electricity)       : {supplied_energy_ref/1E3:.2f} MWh")                           
    print(f" Primary energy consumption                 : {primary_energy_consumption_ref/1E3:.2f} MWh")
    print(f" Supplied energy + Surplus                  : {supplied_energy_surplus/1E3:.2f} MWh") 
    print(f" Primary energy consumption + surplus       : {primary_energy_consumption_surplus_ref/1E3:.2f} MWh") 
    print(f" Total fuel efficiency                      : {total_fuel_efficiency_ref:.2f}")
    print(f" C02 emissions (t)                          : {co2_emission_ref:.2f}")
    print("------------------------------------------------------------------")



    LHV = 9.59
    annual_gas_consumption = (primary_energy_consumption_boiler  + ep_chp) / LHV 
    
    unitary_tax = 0.0181 
    tax_regime_s = 'civile'
    tax_exemption_factor = 0
    free_tax_annual_consumption = 0
    raw_material_and_gas_network_use = 0.6 * annual_gas_consumption
    taxes = annual_gas_consumption * unitary_tax
    total_gas_natural_cost = raw_material_and_gas_network_use + taxes
    
    tr = ep_chp / tot_e * 100 
    # The energy produced by COG must be grater then the 10% of total energy
    if tr > 10:
        unitary_tax = 0.0187 
        tax_regime_s = 'industriale'
        # Gas excemption = Produced Energy (kWh) * 0,22 (Sm³/kWh).
        tax_exemption_factor = 0.22
        free_tax_annual_consumption = 0.22 * tot_supplied_by_chp
        raw_material_and_gas_network_use = 0.6 * annual_gas_consumption
        taxes = (annual_gas_consumption - free_tax_annual_consumption) * unitary_tax
        total_gas_natural_cost = raw_material_and_gas_network_use + taxes


    print()
    print()
    print()
    print()

    print("------------------------------------------------------------------")
    print("         PROPOSED SYSTEM: econimc analysis                         ")
    print("------------------------------------------------------------------")
    print("                 Natural Gas Costs                                ")
    print("------------------------------------------------------------------")
    print(f" Annual consumption (Sm3)                   : {annual_gas_consumption:.2f}")                           
    print(" Charge e/Sm3                               :" ,0.6)
    print(f" Tax regime                                 : {tax_regime_s}  {tr:.2f}%") 
    print(f" Tax exemption factor (Sm3/kEhe)            : {tax_exemption_factor:.2f}") 
    print(f" Free-tax annual consumption (Sm3)          : {free_tax_annual_consumption:.2f}")
    print(f" Raw material and gas network use           : {raw_material_and_gas_network_use/1E6:.4f} M")
    print(f" Taxes                                      : {taxes/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print(f" Total natural gas costs                    : {total_gas_natural_cost/1E6:.4f} M")
    print("------------------------------------------------------------------")


    annual_gas_consumption_ref = boiler_primary_energy_consumption_ref / LHV
    raw_material_and_gas_network_use_ref = 0.6 * annual_gas_consumption_ref
    taxes_ref = raw_material_and_gas_network_use_ref * 0.181
    total_gas_natural_cost_ref = taxes_ref + raw_material_and_gas_network_use_ref


    print()
    
    print("------------------------------------------------------------------")
    print("        Reference System: economic analysis                       ")
    print("------------------------------------------------------------------")
    print("                 Natural Gas Costs                                ")
    print("------------------------------------------------------------------")
    print(f" Annual consumption (Sm3)                   : {annual_gas_consumption_ref:.4f}")                          
    print(" Charge e/Sm3                               :" ,0.6)
    print(f" Tax regime                                 : civile") 
    print(f" Raw material and gas network use           : {raw_material_and_gas_network_use_ref/1E6:.4f} M")
    print(f" Taxes                                      : {taxes_ref/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print(f" Total natural gas costs                    : {total_gas_natural_cost_ref/1E6:.4f} M")
    print("------------------------------------------------------------------")


    maintenance_cost = tot_supplied_by_chp * 0.015
    energy_fee = results['F1']['integration']* 0.169 +  results['F2']['integration'] * 0.174 +  results['F3']['integration'] * 0.163  
    power_fee = committed_power * 2.65 * 12
    total_tax_fee = energy_fee + power_fee
    monthly_consumption = (F1 + F2 + F3) / 12

    total_tax = 0
    if monthly_consumption < 200000:
        total_tax = monthly_consumption * 0.0125
    elif  monthly_consumption < 1200000:
        total_tax = monthly_consumption * 0.0075
    else:
        total_tax = 4800 +  0.0125 * 200000

    total_electricity_costs = total_tax + total_tax_fee + maintenance_cost
    total_revenue =  results['F1']['surplus'] * 0.137 +  results['F2']['surplus'] * 0.142 +  results['F3']['surplus'] * 0.131  
    total_net_costs = total_electricity_costs - total_revenue + total_gas_natural_cost


    print("------------------------------------------------------------------")
    print("        PROPOSED SYSTEM: econimc analysis                         ")
    print("------------------------------------------------------------------")
    print("                 Electricity Costs                                ")
    print("------------------------------------------------------------------")    
    print(" Maintenence charge (e/kWh)                       :" ,0.015)
    print(f" Maintenence cost                                 : {maintenance_cost/1E6:.4f} M")
    print("------------------------------------------------------------------") 
    print("                 Integration Costs                                ")    
    print("------------------------------------------------------------------")    
    print(" F1 charge (e/kWh)                       :" ,0.169)
    print(" F2 cahrge (e/kWh)                       :" ,0.174)
    print(" F3 charge (e/kWh)                       :" ,0.163)
    print(" Energy fee                              :", energy_fee)
    print(f" Committed Power                         : {committed_power:.2f} kW")
    print(f" Power fee                               : {power_fee/1E6:.4f} M")
    print(f" Total Tax fee                           : {total_tax_fee/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print("                 Tax (self-consumption and integration)")
    print("------------------------------------------------------------------")
    print(f"  Monthly consumption (kWhe/month)       : {monthly_consumption:.2f}")
    print("  Tax Ee (e/kWh) 1                       :",0.0075)
    print("  Tax Ee (e/kWh) 2                       :",0.0125)
    print(f"  Total Tax                              : {total_tax/1E6:.4f} M")
    print(f"  TOTAL Electricity Costs                : {total_electricity_costs/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print("                 Sale of Electricity                              ")
    print("------------------------------------------------------------------")
    print(" F1 sell (e/kWh)                       :" ,0.137)
    print(" F2 sell (e/kWh)                       :" ,0.142)
    print(" F3 sell (e/kWh)                       :" ,0.131)
    print(f" Total revenu                          : {total_revenue/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print(f" TOTAL NET COSTS                       : {total_net_costs/1E6:.4f} M")
    print("------------------------------------------------------------------")


    energy_fee_ref = F1 * 0.169 +  F2 * 0.174 +  F3 * 0.163  
    power_fee_ref = committed_power_ref * 2.65 * 12
    total_tax_fee_ref = energy_fee_ref + power_fee_ref
    total_electricity_costs_ref = total_tax + total_tax_fee_ref 
    total_net_costs_ref = total_electricity_costs_ref + total_gas_natural_cost_ref


    print()

    print("------------------------------------------------------------------")
    print("        Reference System: econimc analysis                        ")
    print("------------------------------------------------------------------")
    print("                 Electricity Costs                                ")
    print("------------------------------------------------------------------")    
    print(" F1 charge (e/kWh)                       :" ,0.169)
    print(" F2 cahrge (e/kWh)                       :" ,0.174)
    print(" F3 charge (e/kWh)                       :" ,0.163)
    print(f" Energy fee                              : {energy_fee/1E6:.4f} M")
    print(f" Committed Power                         : {committed_power_ref:.2f} kW")
    print(f" Power fee                               : {power_fee_ref/1E6:.4f} M")
    print(f" Total Tax fee                           : {total_tax_fee_ref/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print(f"  Monthly consumption (kWhe/month)       : {monthly_consumption:.2f}")
    print("  Tax Ee (e/kWh) 1                       :",0.0075)
    print("  Tax Ee (e/kWh) 2                       :",0.0125)
    print(f"  Total Tax                              : {total_tax/1E6:.4f} M")
    print(f"  Total Electricity Costs                : {total_electricity_costs_ref/1E6:.4f} M")
    print("------------------------------------------------------------------")
    print(f" TOTAL NET COSTS                       : {total_net_costs_ref/1E6:.4f} M")
    print("------------------------------------------------------------------")
    

    VNboiler = primary_energy_consumption_boiler / LHV  # VNboiler is the natural gas volume consumed by the boiler, calculated in standard cubic meters (Sm³).
    VNCHP = ep_chp / LHV                                # VNCHP is the natural gas volume consumed by the CHP, calculated in standard cubic meters (Sm³).
    cu_N_tax_free = 0.6                                 # cu_N_tax_free is the natural gas cost without taxes in €/Sm³.
    ECHP = tot_supplied_by_chp                          # ECHP is the electrical energy produced by the CHP in kWh.
    Ein = tot_integration                               # Ein is the electrical energy integrated from the grid in kWh.
    Esel = tot_self_consumption                         # Esel is the self-consumed electrical energy in kWh.
    cu_in = 0.18                                        # cu_in is the cost of the integrated electrical energy from the grid in €/kWh.
    cu_sel = 0.135                                      # cu_sel is the selling price of the electrical energy surplus in €/kWh.
    Esur = tot_surplus                                  # Esur is the surplus electrical energy sold to the grid in kWh.
    M = 0.015                                           # M represents maintenance costs in €/kWh.
    TAXe = 0.0095                                       # TAXe is the tax on electrical energy in €/kWh.
    TAXuN = 0.0187                                      # TAXuN is the unit tax on natural gas in €/Sm³.


    operating_cost_CHP = (VNboiler + VNCHP) * cu_N_tax_free + (VNCHP - 0.22 * ECHP) * TAXuN + Ein * cu_in - Esur * cu_sel + M * ECHP + TAXe * (Ein + Esel)
    

    VNboiler_to = annual_gas_consumption_ref 
    Eto = F1 + F2 + F3
    cu_ref_tax_free = 0.18
    TAXe_ref = 0.0095   
    TAXuN = 0.0181  

    operating_cost_RS = VNboiler_to * (cu_N_tax_free + TAXuN) + Eto * (cu_ref_tax_free + TAXe_ref)

    print()
    print()

    print (f"  Primary Energy Consumption P.S. :{primary_energy_consumption:.2f}")
    print (f"  Primary Energy Consumption Ref. : {primary_energy_consumption_ref:.2f}")    
    diff = primary_energy_consumption-primary_energy_consumption_ref
    print (f"  Diff : {diff:.2f}") 

    print()

    print(f"  CO2 Emission P.S. : {co2_emission:.2f}")
    print(f"  CO2 Emission Ref. : {co2_emission_ref:.2f}")
    diff = co2_emission-co2_emission_ref
    print(f"  Diff : {diff:.2f}")

    print()

    print(f"  Operating Cost P.S. : {operating_cost_CHP/1000000:.2f} M")
    print(f"  Operating Cost Ref. : {operating_cost_RS/1000000:.2f} M")
    diff = operating_cost_CHP-operating_cost_RS
    print(f"  Diff : {diff/1000000:.2f} M")

    print()

    
    # Save a file for next calculation
    new_data_file = 'load_preproc_net_cog.csv'  
    df_power = pd.read_csv("load_preproc.csv")
    df_power["Potenza Elettrica"] = df_power["Potenza Elettrica"] - Pe
    df_power["Tempo"] = pd.to_datetime(df_power["Tempo"], errors='coerce').dt.strftime('%d-%m %H:%M')
    df_power.to_csv(new_data_file, index=False)



# Input parameters
file_path = 'load_preproc.csv'

# Enter the values for the variables
print("ENTER COG Parameters:")
Pe = float(input("Enter the Electric Power (Pe) in kW: "))
Pt = float(input("Enter the Thermal Power (Pt) in kW: "))
NumH = int(input("Enter the number of hours (NumH 0-8760): "))

eta_e = float(input("Enter the electric efficiency (eta_e): "))
eta_t = float(input("Enter the thermal efficiency (eta_t): "))

# Display the entered values
print("\nInput Summary:")
print(f"Threshold Electric Power (Pe): {Pe} W")
print(f"Threshold Thermal Power (Pt): {Pt} W (not used in calculation)")
print(f"Number of rows to process (NumH): {NumH}")
print(f"Electric efficiency (eta_e): {eta_e}")
print(f"Thermal efficiency (eta_t): {eta_t}")

# Process energy data
process_energy_data(file_path, Pe, Pt, NumH, eta_e, eta_t)