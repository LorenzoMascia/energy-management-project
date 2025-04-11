import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_wind(Z, alpha, AG, Pe, speed_power, K):
    # Read the file skipping the first 17 rows
    data_file = 'wind_speed.csv'  # Replace with the correct file name
    output_pct_file = 'wind_speed_pct.csv'

    # Load the CSV file
    col_names = ["time(UTC)", "T2m", "RH", "G(h)", "Gb(n)", "Gd(h)", "IR(h)", "WS10m", "WD10m", "SP"]
    df = pd.read_csv(data_file, skiprows=18, names=col_names)

    # Remove the last 10 rows
    df = df[:-10]

    # Keep only the required columns: time(UTC), WS10m
    df = df[["time(UTC)", "WS10m"]]

    # Rename WS10m column to WS
    df = df.rename(columns={'WS10m': 'WS'})

    # Format the time(UTC) column as day-month hour:minute
    df["time(UTC)"] = pd.to_datetime(df["time(UTC)"], format='%Y%m%d:%H%M').dt.strftime('%d-%m %H:%M')

    # Apply the adjustment formula to WS
    df["WS"] = df["WS"] * (Z / 10) ** alpha

    # Round WS and calculate frequency
    if not df.empty:
        df["WS"] = df["WS"].round().astype(int)
        total_hours = len(df)

        # Calculate percentage of occurrences
        wind_speed_pct = (df["WS"].value_counts(normalize=True) * 100).reset_index()
        wind_speed_pct.columns = ["WS", "%_h"]

        # Save the percentage file
        wind_speed_pct.to_csv(output_pct_file, index=False)
        print(f"Percentage file saved as: {output_pct_file}")

        # Plot the distribution graph
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Histogram of wind speed distribution
        ax1.bar(wind_speed_pct["WS"], wind_speed_pct["%_h"], color='skyblue', label='Wind Speed Distribution')
        ax1.set_xlabel(f"Wind Speed (WS{Z}m)")
        ax1.set_ylabel("% of Hours", color='blue')
        ax1.grid(axis='y', linestyle='--', alpha=0.6)
        ax1.tick_params(axis='y', labelcolor='blue')

        # Title and legend
        plt.title("Wind Speed Distribution")
        fig.tight_layout()
        plt.savefig('wind_speed_pct.png')

        speed_power_df = pd.DataFrame(speed_power, columns=["Speed", "Power"])

        # Add the power curve line on a second y-axis
        ax2 = ax1.twinx()
        ax2.plot(speed_power_df["Speed"], speed_power_df["Power"], color='orange', marker='o', linestyle='-', label='Speed-Power Curve')
        ax2.set_ylabel("Power", color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        # Title and legend
        fig.tight_layout()
        plt.savefig('wind_speed_pct_power_curve.png')
        plt.show()

        # Linear interpolation for power
        speed_values = speed_power_df["Speed"].values
        power_values = speed_power_df["Power"].values
        power_interpolator = np.interp

        # Calculation of total produced power
        total_power = 0
        hours_per_year = 8760

        for _, row in wind_speed_pct.iterrows():
            speed = row["WS"]
            pct_hours = row["%_h"] / 100
            interpolated_power = power_interpolator(speed, speed_values, power_values)
            total_power += interpolated_power * pct_hours * hours_per_year

        # Revenue calculation
        f1_buy = 0.169
        f2_buy = 0.174
        f3_buy = 0.163

        f1_sell = 0.137
        f2_sell = 0.142
        f3_sell = 0.131

        df["Wind Power"] = 0.0
        df2 = pd.read_csv("load_preproc_net_cog.csv")
        df2.rename(columns={
            'Tempo': 'time(UTC)',
            'Potenza Elettrica': 'Electric Power',
            'Fascia Oraria': 'Time Band'
        }, inplace=True)

        df2 = df2[['time(UTC)', 'Electric Power', 'Time Band']]
        df = pd.merge(df[['time(UTC)', 'WS', 'Wind Power']], df2, on='time(UTC)', how='inner')
        df['Wind Power'] = df['WS'].apply(lambda ws: power_interpolator(ws, speed_values, power_values))

        Revenue = AG
        energy_sold_to_grid = 0  # Variabile per accumulare l'energia venduta alla rete

        for _, row in df.iterrows():
            wp = row['Wind Power']
            lp = row['Electric Power']
            surplus = wp - lp

            if surplus < 0:
                if row['Time Band'] == "F1":
                    Revenue += wp * f1_buy
                elif row['Time Band'] == "F2":
                    Revenue += wp * f2_buy
                elif row['Time Band'] == "F3":
                    Revenue += wp * f3_buy
            else:
                if row['Time Band'] == "F1":
                    Revenue += wp * f1_buy + surplus * f1_sell
                    energy_sold_to_grid += surplus  # Accumula l'energia venduta alla rete
                elif row['Time Band'] == "F2":
                    Revenue += wp * f2_buy + surplus * f2_sell
                    energy_sold_to_grid += surplus  # Accumula l'energia venduta alla rete
                elif row['Time Band'] == "F3":
                    Revenue += wp * f3_buy + surplus * f3_sell
                    energy_sold_to_grid += surplus  # Accumula l'energia venduta alla rete

        df.to_csv("wind_speed_h.csv", index=False)

        print(f"Total produced Energy: {total_power:.2f} kWh")
        print(f"Total Energy Sold to Grid: {energy_sold_to_grid:.2f} kWh")  # Stampa l'energia venduta alla rete

        # **Salvare i dati in un CSV**
        df_wind = pd.DataFrame({
            "Fonte": ["Eolico"],
            "Energia Venduta (kWh)": [energy_sold_to_grid]
        })
        df_wind.to_csv("Wind_energy_sold.csv", index=False)

        # (Opzionale) Messaggio di conferma
        print("Dati salvati in Wind_energy_sold.csv")


        Ee = total_power * K
        H_eq = Ee / Pe

        print(f"Heq.: {H_eq:.2f}")

        I_Pe = 1500  # Installation Cost per Power
        I = I_Pe * Pe  # Total Installation Cost
        m = 0.03  # Annual Maintenance Cost
        AF = 12.5  # Capital Recovery Factor, CRF

        Cue = (I * (1 + m) / Pe) / (AF * H_eq)

        Annual_Maintenance = I * m
        Pay_Back = I / (Revenue - Annual_Maintenance)

        print(f"Unit Energy Cost: {Cue:.2f} €/kWh")
        print(f"Total Revenue: {Revenue:.2f} €")
        print(f"Installation Cost: {I:.2f} €")
        print(f"Annual Maintenance: {Annual_Maintenance:.2f} €")
        print(f"Pay Back: {Pay_Back:.1f} Years")

    else:
        print("The dataset does not contain usable data.")



# alpha 
# Unstable air above open water surface 0.06
# Neutral air above open water surface 0.10
# Unstable air above flat open coast 0.11
# Neutral air above flat open coast 0.16
# Stable air above open water surface 0.27
# Unstable air above human inhabited areas 0.27
# Neutral air above human inhabited areas 0.34
# Stable air above flat open coast 0.40
# Stable air above human inhabited areas 0.60

# V100/2000
# Z = 120         # High of the turbine
# alpha = 0.34    # Location Factor 
# AG = 0          # Aid Governative
# Pe = 4000       # Wind Turbine Electric Power
# speed_power =   [[0, 0], [4, 42], [5, 144], [6, 380], [7, 736],[8,1226],[9,1526],[10,1833], [11,1980],[12,2000],[25,2000]]   # Wind Speed / Power
# K  = .85        # availability factor

# Vestas > V112/3450
# Z = 80          # High of the turbine
# alpha = 0.34    # Location Factor 
# AG = 0          # Aid Governative
# Pe = 3500       # Wind Turbine Electric Power
# speed_power =   [[0, 0], [4, 42], [5, 144], [6, 380], [7, 736],[8,1226],[9,1894],[10,2719], [11,3306],[12,3442],[25,3450]]   # Wind Speed / Power
# K  = .85        # availability factor

# Default Values From vesta V117/4000-4200
#
Z = 90          # High of the turbine
alpha = 0.34    # Location Factor 
AG = 0          # Aid Governative
Pe = 4000       # Wind Turbine Electric Power
speed_power =   [[0, 0],[1,0],[2,0],[3, 25],[4,159],[5, 356], [6, 645], [7, 1051],[8,1859],[9,2273],[10,3016], [11,3646],[12,3971],[25,4000]]   # Wind Speed / Power
K  = .85        # availability factor

# Function to request input with a default value
def input_with_default(prompt, default, type_cast=float):
    user_input = input(f"{prompt} (default: {default}): ")
    return type_cast(user_input) if user_input else default

# Default values
default_Z = 90
default_alpha = 0.34
default_AG = 0
default_Pe = 4000
default_speed_power = [[0, 0], [1, 0], [2, 0], [3, 25], [4, 159], [5, 356], [6, 645], [7, 1051], [8, 1859], [9, 2273], [10, 3016], [11, 3646], [12, 3971], [25, 4000]]
default_K = 0.85

# Ask for user input with default values
Z = input_with_default("Enter the height of the turbine (Z) in meters", default_Z, int)
alpha = input_with_default("Enter the location factor (alpha)", default_alpha)
AG = input_with_default("Enter the government aid (AG) in €", default_AG)
Pe = input_with_default("Enter the wind turbine electric power (Pe) in kW", default_Pe, int)
K = input_with_default("Enter the availability factor (K)", default_K)

# For speed_power, we need to handle a list of lists
print("\nEnter the speed-power curve as a list of lists [wind_speed,power]  (e.g., [[0, 0], [1, 0], [2, 0], ...]).")
print(f"Default speed-power curve: {default_speed_power}")
speed_power_input = input("Enter the speed-power curve (leave blank to use default): ")
speed_power = eval(speed_power_input) if speed_power_input.strip() else default_speed_power

# Call the function with the provided or default values
calculate_wind(Z, alpha, AG, Pe, speed_power, K)

