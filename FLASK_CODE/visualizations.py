import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # For running matplotlib without the need for an X server
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from flask import current_app

# Ensure the directory for charts exists
if not os.path.exists('static/charts'):
    os.makedirs('static/charts')

# Helper function to load data from the database
def load_data(query):
    connection = current_app.config['SQLALCHEMY_ENGINE'].connect()
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Function to create the charts
def create_charts():
    charts = []
    scale_factor = 1_000_000  # For scaling large values (e.g., millions)

    def plot_and_save(data, x=None, y=None, kind=None, title=None, xlabel=None, ylabel=None, filepath=None, palette=None):
        if isinstance(filepath, str):  # Ensure filepath is a string
            plt.figure(figsize=(10, 6))
            if kind == "bar":
                sns.barplot(data=data, x=x, y=y, palette=palette)
            elif kind == "line":
                sns.lineplot(data=data, x=x, y=y, marker='o', color=palette)
            elif kind == "hist":
                sns.histplot(data[x], kde=True, color=palette)
            elif kind == "pie":
                plt.pie(data, autopct='%1.1f%%', labels=y, explode=(0.06, 0.05, 0.05, 0.07, 0.08, 0.05), 
                        shadow=True, colors=palette)
            elif kind == "count":
                sns.catplot(data=data, x=x, aspect=3, kind='count', palette=palette)
            elif kind == "box":
                sns.boxplot(data=data, x=x, y=y, palette=palette)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.xticks(rotation=45, ha='right', fontsize=10)  # Rotate x-axis labels for better readability
            plt.tight_layout()
            plt.savefig(filepath)
            charts.append(filepath)  # Appending the filepath
            plt.close()
        else:
            print(f"Error: Expected a string for 'filepath', but got {type(filepath)}")


    # Query 1: Crop production by state
    query1 = """
        SELECT state_name, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY state_name
        ORDER BY total_production DESC;
    """
    statewise_df = load_data(query1)
    if not statewise_df.empty:
        plot_and_save(
            statewise_df.head(10),
            x='state_name',
            y='total_production',
            kind="bar",
            title="Top 10 States by Crop Production",
            xlabel="State",
            ylabel="Total Production",
            filepath='static/charts/statewise_production.png',
            palette='viridis'
        )

    # Query 2: Crop production trends by year
    query2 = """
        SELECT crop_year, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY crop_year
        ORDER BY crop_year;
    """
    yearwise_df = load_data(query2)
    if not yearwise_df.empty:
        plot_and_save(
            yearwise_df,
            x='crop_year',
            y='total_production',
            kind="line",
            title="Crop Production Trends Over Years",
            xlabel="Year",
            ylabel="Total Production",
            filepath='static/charts/yearwise_production.png',
            palette='blue'
        )

    # Query 3: Crop production by season
    query3 = """
        SELECT season, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY season
        ORDER BY total_production DESC;
    """
    seasonwise_df = load_data(query3)
    if not seasonwise_df.empty:
        plot_and_save(
            seasonwise_df,
            x='season',
            y='total_production',
            kind="bar",
            title="Crop Production by Season",
            xlabel="Season",
            ylabel="Total Production",
            filepath='static/charts/seasonwise_production.png',
            palette='coolwarm'
        )

    # Additional visualizations

    # Pie chart for crop production by season
    query4 = """
        SELECT season, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY season;
    """
    season_pie_df = load_data(query4)
    if not season_pie_df.empty:
        plot_and_save(
            season_pie_df['total_production'],
            y=season_pie_df['season'],
            kind="pie",
            title="Crop Production Distribution by Season",
            xlabel="",
            ylabel="Season",
            filepath='static/charts/season_pie_chart.png',
            palette=['LightPink', 'LightBlue', 'LightGreen', 'Violet', 'honeydew', 'aquamarine']
        )

    # Count plot for crop production per crop year
    query5 = """
        SELECT crop_year, COUNT(*) AS count
        FROM src_schema.crop_production
        GROUP BY crop_year;
    """
    year_count_df = load_data(query5)
    if not year_count_df.empty:
        plot_and_save(
            year_count_df,
            x='crop_year',
            y='count',
            kind="bar",  # Changed from 'count' to 'bar'
            title="Crop Production Frequency by Crop Year",
            xlabel="Year",
            ylabel="Frequency",
            filepath='static/charts/yearwise_count.png',
            palette='viridis'
        )

    # Bar plot showing the sum of production for each crop year
    query6 = """
        SELECT crop_year, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY crop_year;
    """
    year_total_production_df = load_data(query6)
    if not year_total_production_df.empty:
        plot_and_save(
            year_total_production_df,
            x='crop_year',
            y='total_production',
            kind="bar",
            title="Total Crop Production per Year",
            xlabel="Year",
            ylabel="Total Production",
            filepath='static/charts/yearwise_total_production.png',
            palette='magma'
        )

    # Box plot for crop production distribution by crop type
    query7 = """
        SELECT crop, production
        FROM src_schema.crop_production;
    """
    crop_production_df = load_data(query7)
    if not crop_production_df.empty:
        plot_and_save(
            crop_production_df,
            x='crop',
            y='production',
            kind="box",
            title="Crop Production Distribution by Crop Type",
            xlabel="Crop Type",
            ylabel="Production",
            filepath='static/charts/crop_production_boxplot.png',
            palette='Set2'
        )

    # Bar plot for crop production by crop type
    query8 = """
        SELECT crop, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY crop;
    """
    cropwise_production_df = load_data(query8)
    if not cropwise_production_df.empty:
        plot_and_save(
            cropwise_production_df,
            x='crop',
            y='total_production',
            kind="bar",
            title="Total Crop Production by Crop Type",
            xlabel="Crop Type",
            ylabel="Total Production",
            filepath='static/charts/cropwise_production.png',
            palette='Paired'
        )

    # Grouped bar plot for production by crop and season
    query9 = """
        SELECT crop, season, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY crop, season;
    """
    crop_seasonwise_df = load_data(query9)
    if not crop_seasonwise_df.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(data=crop_seasonwise_df, x='crop', y='total_production', hue='season', palette='coolwarm')
        plt.title("Crop Production by Crop and Season")
        plt.xlabel("Crop Type")
        plt.ylabel("Total Production")
        plt.xticks(rotation=45, ha='right', fontsize=10)  # Rotate x-axis labels for better readability
        plt.tight_layout()
        plt.savefig('static/charts/crop_seasonwise_production.png')
        charts.append('static/charts/crop_seasonwise_production.png')
        plt.close()

    # Additional visualizations (Heatmap, Scatter, Treemap, etc.)

    # Heatmap for crop production by state and year
    query10 = """
        SELECT state_name, crop_year, SUM(production) AS total_production
        FROM src_schema.crop_production
        GROUP BY state_name, crop_year
        ORDER BY state_name, crop_year;
    """
    heatmap_df = load_data(query10)
    if not heatmap_df.empty:
        crop_state_year_df = heatmap_df.pivot_table(values='total_production', index='state_name', columns='crop_year', aggfunc='sum')
        plt.figure(figsize=(14, 8))
        sns.heatmap(crop_state_year_df, cmap='YlGnBu', annot=True, fmt='.1f', cbar_kws={'label': 'Production'})
        plt.title('Crop Production Heatmap by State and Year')
        plt.xlabel('Year')
        plt.ylabel('State')
        plt.tight_layout()
        plt.savefig('static/charts/state_year_heatmap.png')
        charts.append('static/charts/state_year_heatmap.png')
        plt.close()

    # Scatter plot for Area vs Production by Crop
    query11 = """
        SELECT area, production, crop
        FROM src_schema.crop_production;
    """
    scatter_df = load_data(query11)
    if not scatter_df.empty:
        plt.figure(figsize=(12, 8))
        sns.scatterplot(x='area', y='production', hue='crop', data=scatter_df, palette='tab20')
        plt.title('Scatter Plot of Area vs Production by Crop')
        plt.xlabel('Area (hectares)')
        plt.ylabel('Production (tons)')
        plt.tight_layout()
        plt.savefig('static/charts/area_vs_production.png')
        charts.append('static/charts/area_vs_production.png')
        plt.close()

    

    # Regression plot for Area vs Production
    query13 = """
        SELECT area, production
        FROM src_schema.crop_production;
    """
    regplot_df = load_data(query13)
    if not regplot_df.empty:
        plt.figure(figsize=(10, 6))
        sns.regplot(x='area', y='production', data=regplot_df, scatter_kws={'s': 10}, line_kws={'color': 'red'})
        plt.title('Production vs Area for Crops')
        plt.xlabel('Area (in hectares)')
        plt.ylabel('Production (in tons)')
        plt.tight_layout()
        plt.savefig('static/charts/production_vs_area.png')
        charts.append('static/charts/production_vs_area.png')
        plt.close()

    return charts
