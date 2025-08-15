import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Create a simple Plotly figure
fig_plotly = go.Figure(data=go.Bar(y=[2, 3, 1]))

# Try to save the figure using Matplotlib as the renderer
try:
    # --- FIX: Convert to Matplotlib and use savefig() ---
    # Convert the Plotly figure to a dictionary
    fig_dict = fig_plotly.to_dict()
    
    # Create a Matplotlib figure and axis
    fig_mpl, ax = plt.subplots()
    
    # Extract data and plot on the Matplotlib axis
    y_data = fig_dict['data'][0]['y']
    x_data = list(range(len(y_data)))
    ax.bar(x_data, y_data)
    
    # Save using Matplotlib's robust savefig function
    plt.savefig("test_figure.png")
    
    print("Success: Matplotlib saved the image correctly.")
except Exception as e:
    print(f"Failure: Matplotlib could not save the image.\nError: {e}")