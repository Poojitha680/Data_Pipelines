"""
Sales Data Pipeline Project
A complete end-to-end solution for sales data integration, analysis, and visualization
Designed as a student project with clear, human-readable code and professional comments
"""

# Importing all the required libraries
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import json
import os
import subprocess
from typing import Dict, Optional

# Assigning the Configuration for the Class
class Config:
    """Central configuration for the sales pipeline"""
    #  For Database using the SQLite ..
    DB_FILE = "sales_database.db"
    
    # Providing the source paths for each required file..
    SALES_CSV_PATH = r"C:\Users\Dell\Desktop\Flipkart\sales_data.csv"   # Sales_Data (csv)
    PRODUCT_JSON_PATH = r"C:\Users\Dell\Desktop\Flipkart\product_metadata.json" #Products_Data(json)
    REGION_EXCEL_PATH = r"C:\Users\Dell\Desktop\Flipkart\region_info.xlsx" #Regions_Data(xlsx)
    
    # Output directories
    REPORT_DIR = r"C:\Users\Dell\Desktop\Flipkart\output\report.csv"
    VISUALIZATION_DIR = r"C:\Users\Dell\Desktop\Flipkart\output\visualizations"
    
    # Create output directories if they don't exist
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)

class SalesDataPipeline:   # Main class (Sales_Data_Pipeline)
    """Main class Logic"""
    
    def __init__(self):  # Intializing the Pipeline
        """Initializing the pipeline with configuration"""
        self.config = Config()
        self.sales_data = None
        self.product_data = None
        self.region_data = None
        self.merged_data = None
        
        # Setting up database connection
        self.db_conn = sqlite3.connect(self.config.DB_FILE)
        
        # Configure visualization style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)

    def run_pipeline(self):  # Running the Pipeline method
        """Executing the complete pipeline from start to finish"""
        print("Starting sales data pipeline...")
        
        # Step 1: Loading the Data from all sources
        print("\n=== Loading Data ===")
        self.load_all_data_sources() #calling the function load_all_data_sources()
        
        # Step 2: Processing the Data from all sources
        print("\n=== Processing Data ===")
        self.process_and_clean_data() # Calling the function process_and_clean_data()
        
        # Step 3: Storing the Data from all sources
        print("\n=== Storing Data ===")
        self.store_data_in_database()  # Calling the function store_data_in_database()
        
        # Step 4: Analyzing the Data from all sources
        print("\n=== Analyzing Data ===")
        self.perform_analysis()  # Calling the function perform_analysis()
        
        # Step 5: Visualizating the source files
        print("\n=== Generating Visualizations ===")
        self.generate_visualizations() # Calling the function generate_visualizations()
        
        print("\nPipeline completed successfully!")   # Pipeline is completed..
        self.db_conn.close()

    def load_all_data_sources(self): 
        """Load data from all available sources"""
        # Loads sales transaction data
        try:
            self.sales_data = pd.read_csv(self.config.SALES_CSV_PATH)
            print(f"Loaded {len(self.sales_data)} sales records")
        except Exception as e:
            print(f"Error loading sales data: {str(e)}")
        
        # Loads product information
        try:
            with open(self.config.PRODUCT_JSON_PATH) as f:
                product_json = json.load(f)
            self.product_data = pd.DataFrame(product_json)
            print(f"Loaded {len(self.product_data)} product records")
        except Exception as e:
            print(f"Error loading product data: {str(e)}")
        
        # Loads region information
        try:
            self.region_data = pd.read_excel(self.config.REGION_EXCEL_PATH)
            print(f"Loaded {len(self.region_data)} region records")
        except Exception as e:
            print(f"Error loading region data: {str(e)}")

    def process_and_clean_data(self):
        """Clean and transform raw data into analysis-ready format"""
        if self.sales_data is not None:
            # Converts date column to datetime
            self.sales_data['Date'] = pd.to_datetime(self.sales_data['Date'])
            
            # Handles the missing values in sales data
            self.sales_data['Units Sold'].fillna(0, inplace=True)
            self.sales_data['Revenue'].fillna(0, inplace=True)
            
            print("Processed sales data")
        
        if self.product_data is not None:
            # Standardize product names
            self.product_data['Product'] = self.product_data['Product'].str.strip()
            
            # Fill missing categories with 'Unknown'
            self.product_data['Category'].fillna('Unknown', inplace=True)
            
            print("Processed product data")
        
        if self.region_data is not None:
            # Clean region names
            self.region_data['Region'] = self.region_data['Region'].str.strip()
            self.region_data['Manager'] = self.region_data['Manager'].str.strip()
            
            print("Processed region data")
        
        # Merge all datasets if they exist
        if self.sales_data is not None and self.product_data is not None:
            self.merged_data = pd.merge(
                self.sales_data,
                self.product_data,
                on='Product',
                how='left'
            )
            
            if self.region_data is not None:
                self.merged_data = pd.merge(
                    self.merged_data,
                    self.region_data,
                    on='Region',
                    how='left'
                )
            
            print(f"Created merged dataset with {len(self.merged_data)} records")

    def store_data_in_database(self):
        """Store processed data in SQLite database"""
        try:
            if self.sales_data is not None:
                self.sales_data.to_sql('sales', self.db_conn, if_exists='replace', index=False)
                print("Stored sales data in database")
            
            if self.product_data is not None:
                self.product_data.to_sql('products', self.db_conn, if_exists='replace', index=False)
                print("Stored product data in database")
            
            if self.region_data is not None:
                self.region_data.to_sql('regions', self.db_conn, if_exists='replace', index=False)
                print("Stored region data in database")
            
            if self.merged_data is not None:
                self.merged_data.to_sql('merged_sales', self.db_conn, if_exists='replace', index=False)
                print("Stored merged dataset in database")
        except Exception as e:
            print(f"Error storing data in database: {str(e)}")

    def perform_analysis(self):
        """Run key sales analytics and save reports"""
        if self.merged_data is None:
            print("No merged data available for analysis")
            return
        
        print("\nRunning sales analysis...")
        
        # 1. Basic Sales Summary
        total_revenue = self.merged_data['Revenue'].sum()
        avg_revenue_per_sale = self.merged_data['Revenue'].mean()
        total_units_sold = self.merged_data['Units Sold'].sum()
        
        print(f"\nSales Summary:")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Average Revenue per Sale: ${avg_revenue_per_sale:,.2f}")
        print(f"Total Units Sold: {total_units_sold}")
        
        # 2. Time-based Analysis
        self.merged_data['month'] = self.merged_data['Date'].dt.to_period('M')
        monthly_sales = self.merged_data.groupby('month').agg({
            'Revenue': 'sum',
            'Units Sold': 'sum'
        })
        
        # 3. Product Performance
        product_performance = self.merged_data.groupby(['Product', 'Category']).agg({
            'Revenue': 'sum',
            'Units Sold': 'sum'
        }).sort_values('Revenue', ascending=False)
        
        # 4. Regional Performance
        regional_performance = self.merged_data.groupby(['Region', 'Manager']).agg({
            'Revenue': 'sum',
            'Units Sold': 'sum'
        }).sort_values('Revenue', ascending=False)
        
        # Save reports to files
        monthly_sales.to_csv(f"{self.config.REPORT_DIR}monthly_sales.csv")
        product_performance.to_csv(f"{self.config.REPORT_DIR}product_performance.csv")
        regional_performance.to_csv(f"{self.config.REPORT_DIR}regional_performance.csv")
        
        print("\nSaved analysis reports to output directory")   # Successfully Performed the Analysis...

    def generate_visualizations(self):      # This will generates the Visualizations
        """Create and save key visualizations from the data"""
        if self.merged_data is None:
            print("No data available for visualization")
            return
        
        print("\nCreating sales visualizations...")   # Created the visualizations for Sales..

        figures=[]       # Created the Figures list..
        
        # 1. Monthly Sales Trend
        fig1=plt.figure()   # Monthly Sales fig is loaded into the fig1...
        monthly_sales = self.merged_data.groupby(
            self.merged_data['Date'].dt.to_period('M')
        )['Revenue'].sum()
        monthly_sales.plot(kind='line', marker='o', color='royalblue')
        plt.title('Monthly Sales Trend')
        plt.ylabel('Total Revenue ($)')
        plt.xlabel('Month')
        plt.tight_layout()
        figures.append(fig1)
        plt.show(block=False)
        plt.pause(4)  # It will Display for 4 seconds
        plt.close()      # The Fig will closes down..
        
        # 2. Top Selling Products
        fig2=plt.figure()            # Selling Products fig is loaded into the fig2...
        top_products = self.merged_data.groupby('Product')['Units Sold'].sum().nlargest(10)
        top_products.plot(kind='barh', color='forestgreen')
        plt.title('Top 10 Products by Units Sold')
        plt.xlabel('Total Units Sold')
        plt.tight_layout()
        figures.append(fig2)
        plt.show(block=False)
        plt.pause(4)     # It will Display for 4 seconds
        plt.close()    # The Fig will closes down..
        
        # 3. Revenue by Product Category
        fig3=plt.figure()     # Product Category fig is loaded into the fig3...
        category_sales = self.merged_data.groupby('Category')['Revenue'].sum().sort_values()
        category_sales.plot(kind='bar', color='teal')
        plt.title('Revenue by Product Category')
        plt.ylabel('Total Revenue ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        figures.append(fig3)
        plt.show(block=False)
        plt.pause(4)  # It will Display for 4 seconds
        plt.close()    # The Fig will closes down..
        
        # 4. Regional Sales Breakdown
        fig4=plt.figure()       # Product Category fig is loaded into the fig3...
        regional_sales = self.merged_data.groupby('Region')['Revenue'].sum()
        regional_sales.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('Revenue Distribution by Region')
        plt.ylabel('')
        plt.tight_layout()
        figures.append(fig4)
        plt.show(block=False)
        plt.pause(4)       # It will Display for 4 seconds
        plt.close()       # The Fig will closes down..

        for fig in figures:
            plt.show(block=False)
        
        print("The Outputs will display automatically one after another...")

# Main execution
if __name__ == "__main__":
    pipeline = SalesDataPipeline()
    pipeline.run_pipeline()   # Completed the Task....
    