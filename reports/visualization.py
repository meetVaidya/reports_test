import matplotlib.pyplot as plt
from io import BytesIO
from typing import Tuple, Optional
import pandas as pd

# === Data optimization and plotting functions ===
def optimize_for_plotting(df: pd.DataFrame, user_prompt: str, max_items: int = 10) -> Tuple[pd.DataFrame, str]:
    """
    Intelligently reduces dataset size for effective visualization
    """
    if len(df) <= max_items:
        return df, "All data shown (within visualization limits)"

    # Try to determine which columns to use based on the prompt
    # Simple strategy if dataset is too large: Sort by the second column (typically value column)
    # and take top N items
    try:
        if len(df.columns) >= 2 and df[df.columns[1]].dtype.kind in 'ifc':
            sorted_df = df.sort_values(df.columns[1], ascending=False).head(max_items)
            return sorted_df, f"Showing top {max_items} items sorted by {df.columns[1]}"
    except Exception as e:
        print(f"Error optimizing data for plotting: {str(e)}")

    # Fallback - just take the first N rows
    return df.head(max_items), f"Showing first {max_items} items"

def create_plot(df: pd.DataFrame, title: str, strategy: Optional[str] = None) -> Optional[BytesIO]:
    """
    Create a visualization based on dataframe content
    """
    if df.empty:
        return None

    plt.figure(figsize=(10, 6))

    # Simple plot selection logic - can be expanded based on data types and query intent
    if len(df.columns) >= 2:
        x_col = df.columns[0]
        y_col = df.columns[1]

        # Create bar chart - most common visualization for sales data
        plt.bar(df[x_col].astype(str), df[y_col], color='skyblue')
        plt.xlabel(x_col)
        plt.ylabel(y_col)

        # Add strategy to title if available
        if strategy:
            title = f"{title}\n({strategy})"
        plt.title(title)

        # Rotate x-labels if there are many items
        if len(df) > 5:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Save to BytesIO object for sending over Telegram
        img_data = BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        plt.close()

        return img_data

    return None
