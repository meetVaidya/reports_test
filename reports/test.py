from database import setup_agent, load_query_repository
from query_utils import get_most_similar_query, result_to_dataframe
from visualization import optimize_for_plotting, create_plot
import pandas as pd
import matplotlib.pyplot as plt
from config import PROJECT_ID, DATASET_ID

def verify_bigquery_connection():
    """Verify BigQuery connection and print available tables"""
    from google.cloud import bigquery

    client = bigquery.Client()
    dataset_ref = client.dataset(DATASET_ID, project=PROJECT_ID)

    try:
        dataset = client.get_dataset(dataset_ref)
        print(f"Dataset '{DATASET_ID}' exists")

        # List all tables in the dataset
        print("\nAvailable tables:")
        tables = list(client.list_tables(dataset))
        for table in tables:
            print(f"- {table.table_id}")
        return True
    except Exception as e:
        print(f"Error accessing BigQuery: {str(e)}")
        return False

def analyze_query_and_visualization(user_query: str):
    """
    Analyze a query to show:
    1. Generated SQL query
    2. Raw query results
    3. Optimized data for plotting
    4. Visualization details
    """
    # Setup
    agent_executor, db = setup_agent()
    query_repo = load_query_repository()

    print("="*80)
    print(f"Analyzing query: '{user_query}'\n")

    try:
        # 1. Get the SQL query
        best_match = get_most_similar_query(user_query, query_repo, method="cosine")
        if best_match:
            sql_query = best_match["query"]
            print("1. Generated SQL Query:")
            print("-"*40)
            print(sql_query)
            print("\n")

            # 2. Run the query and get raw results
            try:
                result = db.run(sql_query)
                print("2. Raw Query Results:")
                print("-"*40)
                df = result_to_dataframe(result)
                print(df.head())
                print(f"\nTotal rows: {len(df)}")
                print(f"Columns: {', '.join(df.columns)}\n")

                # 3. Show optimized data for plotting
                plot_df, strategy = optimize_for_plotting(df, user_query)
                print("3. Optimized Data for Plotting:")
                print("-"*40)
                print(f"Optimization strategy: {strategy}")
                print("\nOptimized dataset:")
                print(plot_df)
                print("\n")

                # 4. Analyze visualization type
                print("4. Visualization Analysis:")
                print("-"*40)
                if len(plot_df.columns) >= 2:
                    print(f"X-axis (categorical): {plot_df.columns[0]}")
                    print(f"Y-axis (numerical): {plot_df.columns[1]}")
                    print("Graph type: Bar Chart (default visualization)")
                    print(f"Number of data points: {len(plot_df)}")

                    # Create and show the plot
                    plt.figure(figsize=(10, 6))
                    plot_title = f"Results for: {best_match['description']}"
                    img_data = create_plot(plot_df, plot_title, strategy)
                    if img_data:
                        print("✓ Plot generated successfully")
                    else:
                        print("✗ Could not generate plot")
                else:
                    print("Insufficient columns for visualization")

            except Exception as query_error:
                print(f"Error executing query: {str(query_error)}")
                print("\nPlease verify that:")
                print("1. The table exists in your dataset")
                print(f"2. You have access to project '{PROJECT_ID}'")
                print(f"3. You have access to dataset '{DATASET_ID}'")
                print("4. The SQL syntax is correct for BigQuery")

        else:
            print("No matching query found in repository")

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

    print("="*80)

def show_table_schema():
    """Show the schema of available tables"""
    from google.cloud import bigquery

    client = bigquery.Client()
    dataset_ref = client.dataset(DATASET_ID, project=PROJECT_ID)

    for table_id in ['audit-anomalynew', 'newdb']:
        try:
            table_ref = dataset_ref.table(table_id)
            table = client.get_table(table_ref)

            print(f"\nSchema for table '{table_id}':")
            print("-" * 40)
            for field in table.schema:
                print(f"{field.name}: {field.field_type}")
        except Exception as e:
            print(f"Error getting schema for {table_id}: {str(e)}")

# Example usage
if __name__ == "__main__":
    # First verify BigQuery connection and show available tables
    print("Verifying BigQuery Connection...")
    if verify_bigquery_connection():
        print("Examining table schemas...")
        show_table_schema()

        print("\nProcessing test queries...")

        # Test with queries that match your actual tables
        test_queries = [
            "Show me the daily sales trends",
            "Find orders with long delivery delays",
            "Show top customers by total spending",
            "Analyze order modifications"
        ]

        for query in test_queries:
            analyze_query_and_visualization(query)
            print("\n")
    else:
        print("Please fix BigQuery connection issues before continuing.")
