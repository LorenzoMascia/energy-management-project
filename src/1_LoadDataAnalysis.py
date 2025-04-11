import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def preprocess_load_file(file_path='load.csv'):
    
    # Read the CSV file
    output_file_df = 'load_preproc.csv'

    data = pd.read_csv(file_path, sep=";")

    # Check the file size
    if len(data) != 8760:
        raise ValueError("The CSV file must contain exactly 8760 rows to represent hourly consumption for one year.")

    # Add the 'Tempo' column with a datetime index
    data['Tempo'] = pd.date_range(start='2024-01-01', periods=8760, freq='H')
    data.set_index('Tempo', inplace=True)

    # Convert columns to numeric, replacing non-numeric values with NaN
    data['Potenza Termica'] = pd.to_numeric(data['Potenza Termica'], errors='coerce')
    data['Potenza Elettrica'] = pd.to_numeric(data['Potenza Elettrica'], errors='coerce')

    # Replace NaN values with 0
    data.fillna(0, inplace=True)

    # Round values to the nearest whole number
    data['Potenza Termica'] = data['Potenza Termica'].round()
    data['Potenza Elettrica'] = data['Potenza Elettrica'].round()

    # Add the 'Fascia Oraria' column based on time ranges
    def calculate_time_band(row):
        hour = row.name.hour
        day = row.name.weekday()  # 0=Monday, 6=Sunday
        if day == 6:  # Sunday
            return 'F3'
        elif hour in [1, 2, 3, 4, 5, 6, 23, 0]:  # F3 hours regardless of the day
            return 'F3'
        elif 7 <= hour < 19 and 0 <= day <= 4:  # F1: Monday-Friday, 7:00 AM to 7:00 PM
            return 'F1'
        else:  # All other cases
            return 'F2'

    data['Fascia Oraria'] = data.apply(calculate_time_band, axis=1)

    # Save the modified DataFrame to a CSV file
    data.to_csv(output_file_df)
    print(f"Modified DataFrame saved to '{output_file_df}'")



def plot_data_charts():
    # Use the Agg backend to save the plot instead of displaying it
    matplotlib.use('Agg')

    # Path for the modified CSV file
    input_file = 'load_preproc.csv'

    # Read the CSV file and parse dates as the index
    data = pd.read_csv(input_file, parse_dates=['Tempo'], index_col='Tempo')
    data = data.drop(columns=['Fascia Oraria'])

    # Compute daily averages
    daily_averages = data.resample('D').mean()

    # Plot daily average power
    plt.figure(figsize=(15, 8))
    plt.plot(
        daily_averages.index,
        daily_averages['Potenza Termica'],
        label='Thermal Power',
        color='red',
        linewidth=1.5
    )
    plt.plot(
        daily_averages.index,
        daily_averages['Potenza Elettrica'],
        label='Electrical Power',
        color='blue',
        linestyle='--',
        linewidth=1.5
    )

    plt.title('Daily Power Averages', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Average Power (kW)', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig('daily_mean_values.png', dpi=300)
    plt.close()

    # Compute daily maximum power
    daily_max = data.resample('D').max()

    # Plot daily maximum power
    plt.figure(figsize=(15, 8))
    plt.plot(
        daily_max.index,
        daily_max['Potenza Termica'],
        label='Thermal Power',
        color='red',
        linewidth=1.5
    )
    plt.plot(
        daily_max.index,
        daily_max['Potenza Elettrica'],
        label='Electrical Power',
        color='blue',
        linestyle='--',
        linewidth=1.5
    )

    # Configure the plot
    plt.title('Max Daily Power', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Max Power (kW)', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig("daily_max_values.png", dpi=300)
    plt.close()

    # Compute daily minimum power
    daily_min = data.resample('D').min()

    # Plot daily minimum power
    plt.figure(figsize=(15, 8))
    plt.plot(
        daily_min.index,
        daily_min['Potenza Termica'],
        label='Thermal Power',
        color='red',
        linewidth=1.5
    )
    plt.plot(
        daily_min.index,
        daily_min['Potenza Elettrica'],
        label='Electrical Power',
        color='blue',
        linestyle='--',
        linewidth=1.5
    )

    # Configure the plot
    plt.title('Min Daily Power', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Min Power (kW)', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig("daily_min_values.png", dpi=300)
    plt.close()

    # Read the CSV file
    input_file = 'load_preproc.csv'
    data = pd.read_csv(input_file, parse_dates=['Tempo'])

    # Sort the DataFrame by 'Potenza Elettrica' in descending order
    data = data.sort_values(by='Potenza Elettrica', ascending=False).reset_index(drop=True)

    # Add a counter as a new index column
    data['Index'] = range(1, len(data) + 1)

    # Filter data for each time band
    f1_data = data[data['Fascia Oraria'] == 'F1']
    f2_data = data[data['Fascia Oraria'] == 'F2']
    f3_data = data[data['Fascia Oraria'] == 'F3']

    # Create the bar plot for electrical power
    plt.figure(figsize=(14, 7))

    # Draw bars for each time band
    plt.bar(f1_data['Index'], f1_data['Potenza Elettrica'], color='blue', alpha=0.7, label='F1')
    plt.bar(f2_data['Index'], f2_data['Potenza Elettrica'], color='green', alpha=0.7, label='F2')
    plt.bar(f3_data['Index'], f3_data['Potenza Elettrica'], color='red', alpha=0.7, label='F3')

    # Configure the plot
    plt.title('Electric Power', fontsize=16)
    plt.xlabel('Index', fontsize=14)
    plt.ylabel('Electric Power', fontsize=14)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig('electric_load_chart.png', dpi=300)
    plt.close()

    # Create the bar plot for thermal power
    plt.figure(figsize=(14, 7))

    # Draw bars for thermal power
    plt.bar(data['Index'], data['Potenza Termica'], color='red', alpha=0.7, label='Thermal Power')

    # Configure the plot
    plt.title('Thermal Power', fontsize=16)
    plt.xlabel('Index (Counter)', fontsize=14)
    plt.ylabel('Thermal Power', fontsize=14)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig('thermal_load_chart.png', dpi=300)
    plt.close()



# Step 1
#
# This method preprocess the load csv file  
#    adds the DateTime column 
#    adds the Time Bande column 
#    rounds the powers
#    corces the invalid values
#
preprocess_load_file(file_path='load.csv')


# Step 2
#
# This method creates the following charts
# 
#   daily_mean_values.png
#   daily_min_values.png
#   daily_max_values.png
#   electric_load_chart.png
#   thermal_load_chart.png
#
plot_data_charts()

