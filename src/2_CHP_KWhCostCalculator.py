def kwh_chp_cost_calculator(c_NG, tax, LH, eta_e, eta_t, eta_t_re, eta_e_CHP_re, M):  
    """  
    Calculates the cost per kWh produced by a combined heat and power (CHP) system.  

    Args:  
        c_NG (float): Cost of natural gas for the CHP system (€/m³).  
        tax (float): Tax on natural gas (€/m³).  
        LH (float): Lower heating value (LHV) of natural gas (kWh/m³).  
        eta_e (float): Effective electrical efficiency of the CHP system.  
        eta_t (float): Effective thermal efficiency of the CHP system.  
        eta_t_re (float): Reference thermal efficiency for comparison.  
        eta_e_CHP_re (float): Reference electrical efficiency for tax exemption calculation (default: 0.474).  
        M (float): Maintenance costs (€/kWh).  

    Returns:  
        float: Cost per kWh produced by the CHP system (€/kWh).  
    """  

    # Formula to compute the cost per kWh produced by CHP
    c_kWh_CH = (1 / (eta_e * LH)) * (c_NG + (1 - eta_e / eta_e_CHP_re) * tax - (eta_t / eta_t_re) * (c_NG + tax)) + M  
    return c_kWh_CH  

# Function to request input with a default value
def input_with_deafult(prompt, default):
    user_input = input(f"{prompt} (default: {default}): ")
    return float(user_input) if user_input else default

# Input variables with default values
print("CHP Data:")
eta_e = input_with_deafult("Enter the electrical efficiency (eta_e)", 0.39)
eta_t = input_with_deafult("Enter the thermal efficiency (eta_t)", 0.473)
print("Calculation Data:")
c_NG = input_with_deafult("Enter the cost of natural gas (€/m³)", 0.60)
tax = input_with_deafult("Enter the natural gas tax (€/m³)", 0.0187)
LH = input_with_deafult("Enter the lower heating value of natural gas (kWh/m³)", 9.59)
eta_t_re = input_with_deafult("Enter the reference system thermal efficiency", 0.90)
eta_e_CHP_re = input_with_deafult("Enter the reference electrical efficiency", 0.474)
M = input_with_deafult("Enter the maintenance costs (€/kWh)", 0.015)

# Calculate the cost per kWh produced by CHP
kwh_cost = kwh_chp_cost_calculator(c_NG, tax, LH, eta_e, eta_t, eta_t_re, eta_e_CHP_re, M)  

print("-------------------------------------------------------")
print(f"Cost per kWh produced by the CHP: {kwh_cost:.3f} €/kWh")
print("-------------------------------------------------------")