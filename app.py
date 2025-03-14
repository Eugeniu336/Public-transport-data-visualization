import mysql.connector
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt




# Connect to the database
connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    database='test1',
    port=3306
)
cursor = connection.cursor(dictionary=True)

# Function to fetch data from the database
def fetch_data(query):
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    return df

# Streamlit App
st.title("Public Transport Dashboard")


# Table Selection
selected_table = st.selectbox("Select a table", ["routes", "trips", "public_vehicle", "stops", "stop_times", "bimbim"])

# Data Loading
st.subheader(f"{selected_table.capitalize()} Data")
if selected_table!="bimbim":
    table_query = f"SELECT * FROM {selected_table}"
    table_df = fetch_data(table_query)
    st.write(table_df)

# Data Analysis and Visualization
st.header("Data Analysis and Visualization")

# Example: Show Visualization based on the selected table
if selected_table == "routes":
    # Example: Route Type Distribution
    route_type_distribution = table_df['route_type'].value_counts()
    st.subheader("Route Type Distribution")
    st.bar_chart(route_type_distribution)

elif selected_table == "public_vehicle":
    # Example: Number of Vehicles per Route
    vehicles_per_route = table_df.groupby('route_id').size().reset_index(name='num_vehicles')
    st.subheader("Number of Vehicles per Route")
    st.bar_chart(vehicles_per_route.set_index('route_id'))

elif selected_table == "trips":
    # Example: Trips Heatmap
    st.subheader("Trips Heatmap")
    fig = px.scatter_mapbox(table_df, lat=table_df['geo_lat'], lon=table_df['geo_lon'],
                            color=table_df['route_id'], size_max=15, zoom=10,
                            mapbox_style="stamen-terrain")

    st.plotly_chart(fig)
elif selected_table == "stops":
    # Example: Display Stop Locations on Map
    st.subheader("Stop Locations on Map")
    fig = px.scatter_mapbox(table_df, lat=table_df['geo_lat'], lon=table_df['geo_lon'],
                            color=table_df['stop_name'], size_max=15, zoom=10,
                            mapbox_style="stamen-terrain")
    st.plotly_chart(fig)

elif selected_table=="bimbim":
    cursor.execute("SELECT s.stop_name, r.route_number, COUNT(pv.vehicle_id) AS vehicle_count FROM stops s JOIN stop_times st ON s.stop_id = st.stop_id JOIN public_vehicle pv ON st.trip_id = pv.trip_id JOIN routes r ON pv.route_id = r.route_id JOIN trips t ON pv.trip_id = t.trip_id WHERE t.trip_headsign = s.stop_name GROUP BY s.stop_name, r.route_number")
    result_table=cursor.fetchall()

    st.write("Query result:")
    st.table(result_table)

elif selected_table == "stop_times":

    # Example: Stop Times Distribution
    st.subheader("Stop Times Distribution")

    # Fetch data for stop times
    stop_times_query = f"SELECT * FROM stop_times"
    stop_times_df = fetch_data(stop_times_query)

    # Fetch data for stops
    stops_query = f"SELECT * FROM stops"
    stops_df = fetch_data(stops_query)

    # Merge stop_times_df with stops_df on stop_id
    merged_df = pd.merge(stop_times_df, stops_df, on='stop_id', how='left')

    # Verifică dacă 'stop_name' există în DataFrame
    if 'stop_name' in merged_df.columns:
        # Iterate over each station and create a visualization
        for station in merged_df['stop_name'].unique():
            st.subheader(f"Stop Times Distribution for {station}")

            # Filter data for the current station
            station_df = merged_df[merged_df['stop_name'] == station]

            # Create a histogram for stop times at the current station
            fig, ax = plt.subplots()
            station_df['stop_sequence'].hist(ax=ax, bins=20, edgecolor='black')
            ax.set_xlabel('Stop Sequence')
            ax.set_ylabel('Frequency')
            st.pyplot(fig)


        # Fetch data for stop times
        stop_times_query = f"SELECT * FROM stop_times"
        stop_times_df = fetch_data(stop_times_query)

        # Fetch data for stops
        stops_query = f"SELECT * FROM stops"
        stops_df = fetch_data(stops_query)

        # Merge stop_times_df with stops_df on stop_id
        merged_df = pd.merge(stop_times_df, stops_df, on='stop_id', how='left')

        # Dropdown for station selection
        selected_station = st.selectbox("Select a station", merged_df['stop_name'].unique())

        # Filter data for the selected station
        station_df = merged_df[merged_df['stop_name'] == selected_station]

        # Display selected station name
        st.subheader(f"Stop Times Distribution for {selected_station}")

        # Create a histogram for stop times at the selected station
        fig, ax = plt.subplots()
        station_df['stop_sequence'].hist(ax=ax, bins=20, edgecolor='black')
        ax.set_xlabel('Stop Sequence')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)





# Close the database connection
cursor.close()
connection.close()
