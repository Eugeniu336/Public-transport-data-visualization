from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import json
import requests


class TransportApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection = None
        self.cursor = None
        self.current_table = None
        self.update_interval = None

    def build(self):
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Database connection
        self.connect_to_database()

        # Table selection
        self.create_table_selector()

        # Data display area
        self.data_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.data_layout)

        # Start periodic updates
        self.update_interval = Clock.schedule_interval(self.update_data, 10)  # Update every 10 seconds

        return self.main_layout

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                database='test1',
                port=3306
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")

    def create_table_selector(self):
        # Create spinner for table selection
        self.table_spinner = Spinner(
            text='Select Table',
            values=('routes', 'trips', 'public_vehicle', 'stops', 'stop_times', 'bimbim'),
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': .5}
        )
        self.table_spinner.bind(text=self.on_table_select)
        self.main_layout.add_widget(self.table_spinner)

    def fetch_data(self, query):
        try:
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(data, columns=columns)
        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            return pd.DataFrame()

    def on_table_select(self, spinner, text):
        self.current_table = text
        self.update_data(None)

    def update_data(self, dt):
        if not self.current_table:
            return

        # Clear previous data display
        self.data_layout.clear_widgets()

        # Fetch and display data based on selected table
        if self.current_table != "bimbim":
            df = self.fetch_data(f"SELECT * FROM {self.current_table}")
            self.display_table_data(df)

            # Create visualization based on table
            if self.current_table == "routes":
                self.create_routes_visualization(df)
            elif self.current_table == "public_vehicle":
                self.create_vehicle_visualization(df)
            elif self.current_table == "stops":
                self.create_stops_visualization(df)

    def display_table_data(self, df):
        # Create scrollable grid for data display
        scroll = ScrollView(size_hint=(1, 0.7))
        grid = GridLayout(cols=len(df.columns), spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # Add headers
        for col in df.columns:
            grid.add_widget(Label(text=str(col), size_hint_y=None, height=30))

        # Add data
        for _, row in df.iterrows():
            for value in row:
                grid.add_widget(Label(text=str(value), size_hint_y=None, height=30))

        scroll.add_widget(grid)
        self.data_layout.add_widget(scroll)

    def create_routes_visualization(self, df):
        if 'route_type' in df.columns:
            plt.figure(figsize=(10, 6))
            df['route_type'].value_counts().plot(kind='bar')
            plt.title('Route Type Distribution')
            plt.xlabel('Route Type')
            plt.ylabel('Count')

            canvas = FigureCanvasKivyAgg(plt.gcf())
            self.data_layout.add_widget(canvas)

    def create_vehicle_visualization(self, df):
        if 'route_id' in df.columns:
            plt.figure(figsize=(10, 6))
            df.groupby('route_id').size().plot(kind='bar')
            plt.title('Vehicles per Route')
            plt.xlabel('Route ID')
            plt.ylabel('Number of Vehicles')

            canvas = FigureCanvasKivyAgg(plt.gcf())
            self.data_layout.add_widget(canvas)

    def create_stops_visualization(self, df):
        if 'geo_lat' in df.columns and 'geo_lon' in df.columns:
            plt.figure(figsize=(10, 6))
            plt.scatter(df['geo_lon'], df['geo_lat'])
            plt.title('Stop Locations')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')

            canvas = FigureCanvasKivyAgg(plt.gcf())
            self.data_layout.add_widget(canvas)

    def on_stop(self):
        # Clean up resources
        if self.update_interval:
            self.update_interval.cancel()
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == '__main__':
    TransportApp().run()