import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import yfinance as yf
import os

class FinancialAnalysis:
    def __init__(self, companies):
        """
        Initialize Financial Analysis class
        
        Parameters:
        companies (list): List of company stock codes, e.g., ['AAPL', 'MSFT', 'GOOGL']
        """
        self.companies = companies
        self.balance_sheets = {}
        self.ratios = {}
        
        # Get the directory path of main.py
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Create output directory
        self.output_dir = os.path.join(self.base_path, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create plots directory
        self.plots_dir = os.path.join(self.output_dir, 'plots')
        os.makedirs(self.plots_dir, exist_ok=True)
        
    def get_output_path(self, filename):
        """Get the full path for output files"""
        return os.path.join(self.output_dir, filename)
        
    def get_plot_path(self, filename):
        """Get the full path for plot files"""
        return os.path.join(self.plots_dir, filename)
        
    def fetch_data(self, period='5y'):
        """Fetch balance sheet data from Yahoo Finance"""
        for company in self.companies:
            try:
                stock = yf.Ticker(company)
                bs = stock.quarterly_balance_sheet  # Use quarterly data
                if bs.empty:
                    print(f"Warning: Unable to fetch data for {company}")
                    continue
                print(f"\n{company} Balance Sheet Available Items:")
                print(bs.index.tolist())
                self.balance_sheets[company] = bs
            except Exception as e:
                print(f"Error fetching data for {company}: {str(e)}")
                
    def calculate_financial_ratios(self):
        """Calculate key financial ratios"""
        for company, bs in self.balance_sheets.items():
            try:
                # Create DataFrame to store ratios
                ratios = pd.DataFrame(index=bs.columns)
                
                # Current Ratio = Current Assets / Current Liabilities
                current_assets = bs.loc['Current Assets']
                current_liabilities = bs.loc['Current Liabilities']
                ratios['Current_Ratio'] = current_assets / current_liabilities
                
                # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
                if 'Inventory' in bs.index:
                    inventory = bs.loc['Inventory']
                else:
                    inventory = 0  # Assume 0 if no inventory data
                ratios['Quick_Ratio'] = (current_assets - inventory) / current_liabilities
                
                # Debt to Assets Ratio = Total Liabilities / Total Assets
                total_assets = bs.loc['Total Assets']
                total_liabilities = bs.loc['Total Liabilities Net Minority Interest']
                ratios['Debt_to_Assets'] = total_liabilities / total_assets
                
                # Equity Multiplier = Total Assets / Stockholders Equity
                stockholders_equity = bs.loc['Stockholders Equity']
                ratios['Equity_Multiplier'] = total_assets / stockholders_equity
                
                self.ratios[company] = ratios
                print(f"Financial ratios calculation completed for {company}")
                
            except Exception as e:
                print(f"Error calculating ratios for {company}: {str(e)}")
                print("Available balance sheet items:")
                print(bs.index.tolist())
    
    def plot_current_ratio_comparison(self):
        """Plot current ratio comparison chart"""
        plt.figure(figsize=(12, 6))
        for company in self.companies:
            if company in self.ratios:
                # Convert date index to datetime format
                dates = pd.to_datetime(self.ratios[company].index)
                values = self.ratios[company]['Current_Ratio']
                plt.plot(dates, values, marker='o', label=company)
        
        plt.title('Current Ratio Comparison', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Current Ratio', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        plot_path = self.get_plot_path('current_ratio_comparison.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        return plot_path
        
    def plot_debt_ratio_radar(self):
        """Plot financial ratios radar chart"""
        available_companies = [company for company in self.companies if company in self.ratios]
        if not available_companies:
            print("No data available for radar chart")
            return None
            
        latest_date = self.ratios[available_companies[0]].index[0]
            
        categories = ['Debt to Assets', 'Current Ratio', 'Quick Ratio', 'Equity Multiplier']
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(available_companies)))
        
        for company, color in zip(available_companies, colors):
            values = [
                self.ratios[company]['Debt_to_Assets'][latest_date],
                self.ratios[company]['Current_Ratio'][latest_date],
                self.ratios[company]['Quick_Ratio'][latest_date],
                self.ratios[company]['Equity_Multiplier'][latest_date]
            ]
            values = np.concatenate((values, [values[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2, color=color, label=company)
            ax.fill(angles, values, alpha=0.25, color=color)
            
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.grid(True)
        
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.title('Financial Ratios Radar Chart', pad=20, fontsize=14)
        
        plt.tight_layout()
        
        plot_path = self.get_plot_path('debt_ratio_radar.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        return plot_path

    def plot_balance_sheet_composition(self, company):
        """Plot balance sheet composition charts"""
        if company not in self.balance_sheets:
            print(f"No data available for {company}")
            return None
            
        bs = self.balance_sheets[company]
        latest_date = bs.columns[0]  # Use the latest date
            
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
            
            # Assets composition
            total_assets = bs.loc['Total Assets'][latest_date]
            current_assets = bs.loc['Current Assets'][latest_date]
            non_current_assets = bs.loc['Total Non Current Assets'][latest_date]
            
            assets = {
                'Current Assets': current_assets,
                'Non-current Assets': non_current_assets
            }
            
            ax1.pie(assets.values(), labels=assets.keys(), autopct='%1.1f%%', 
                   colors=plt.cm.Pastel1(np.linspace(0, 1, len(assets))))
            ax1.set_title(f'{company} Assets Composition', pad=20)
            
            # Liabilities and Equity composition
            total_liabilities = bs.loc['Total Liabilities Net Minority Interest'][latest_date]
            current_liabilities = bs.loc['Current Liabilities'][latest_date]
            non_current_liabilities = bs.loc['Total Non Current Liabilities Net Minority Interest'][latest_date]
            equity = bs.loc['Stockholders Equity'][latest_date]
            
            liabilities_equity = {
                'Current Liabilities': current_liabilities,
                'Non-current Liabilities': non_current_liabilities,
                "Shareholders' Equity": equity
            }
            
            ax2.pie(liabilities_equity.values(), labels=liabilities_equity.keys(), 
                   autopct='%1.1f%%', colors=plt.cm.Pastel2(np.linspace(0, 1, len(liabilities_equity))))
            ax2.set_title(f'{company} Liabilities and Equity Composition', pad=20)
            
            plt.suptitle(f'{company} Balance Sheet Analysis ({latest_date.strftime("%Y-%m-%d")})', 
                        fontsize=14, y=1.05)
            
            plt.tight_layout()
            
            plot_path = self.get_plot_path(f'{company}_balance_sheet_composition.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            return plot_path
            
        except Exception as e:
            print(f"Error plotting balance sheet composition for {company}: {str(e)}")
            print("Available balance sheet items:")
            print(bs.index.tolist())
            return None

    def generate_analysis_report(self):
        """Generate analysis report"""
        report = "Financial Analysis Report\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for company in self.companies:
            if company not in self.ratios:
                continue
                
            report += f"{company} Company Analysis\n"
            report += "-" * 30 + "\n"
            
            latest_date = self.ratios[company].index[0]
            latest_ratios = self.ratios[company].loc[latest_date]
            
            report += f"Analysis Date: {latest_date}\n\n"
            
            # Add key ratios
            report += "Key Financial Ratios:\n"
            report += f"1. Current Ratio: {latest_ratios['Current_Ratio']:.2f}\n"
            report += "   - Measures short-term liquidity, 2:1 is generally considered reasonable\n"
            report += f"2. Quick Ratio: {latest_ratios['Quick_Ratio']:.2f}\n"
            report += "   - Measures immediate liquidity, 1:1 is generally considered reasonable\n"
            report += f"3. Debt to Assets Ratio: {latest_ratios['Debt_to_Assets']:.2%}\n"
            report += "   - Measures long-term solvency, below 70% is generally considered safe\n"
            report += f"4. Equity Multiplier: {latest_ratios['Equity_Multiplier']:.2f}\n"
            report += "   - Measures financial leverage, higher values indicate higher leverage\n\n"
            
            # Add trend analysis
            report += "Trend Analysis:\n"
            try:
                for ratio in ['Current_Ratio', 'Debt_to_Assets']:
                    trend = self.ratios[company][ratio].pct_change().mean()
                    report += f"{ratio} Average Change Rate: {trend:.2%}\n"
            except Exception as e:
                report += f"Unable to calculate trends: {str(e)}\n"
            
            report += "\n"
            
            # Add recommendations
            report += "Recommendations:\n"
            if latest_ratios['Current_Ratio'] < 2:
                report += "- Monitor short-term liquidity position\n"
            if latest_ratios['Debt_to_Assets'] > 0.7:
                report += "- High debt ratio, monitor long-term solvency risk\n"
            
            report += "\n" + "=" * 50 + "\n\n"
        
        return report

def main():
    # Set companies to analyze
    companies = ['AAPL', 'MSFT', 'GOOGL']  # Tech industry examples
    
    try:
        print("Initializing analyzer...")
        analysis = FinancialAnalysis(companies)
        
        print("\nFetching financial data...")
        analysis.fetch_data()
        
        print("\nCalculating financial ratios...")
        analysis.calculate_financial_ratios()
        
        print("\nGenerating visualizations...")
        
        print("- Generating current ratio comparison...")
        current_ratio_path = analysis.plot_current_ratio_comparison()
        if current_ratio_path:
            print(f"  Saved: {current_ratio_path}")
        
        print("- Generating financial ratios radar chart...")
        radar_path = analysis.plot_debt_ratio_radar()
        if radar_path:
            print(f"  Saved: {radar_path}")
        
        print("- Generating balance sheet composition charts...")
        for company in companies:
            composition_path = analysis.plot_balance_sheet_composition(company)
            if composition_path:
                print(f"  Saved {company} balance sheet composition: {composition_path}")
        
        print("\nGenerating analysis report...")
        report = analysis.generate_analysis_report()
        report_path = analysis.get_output_path('financial_analysis_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Saved analysis report: {report_path}")
        
        print("\nAnalysis complete! All files have been saved in the output directory.")
        
    except Exception as e:
        print(f"\nProgram error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()