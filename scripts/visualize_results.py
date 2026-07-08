import argparse
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize experiment results.")
    parser.add_argument("--input-dir", default="out", help="Directory containing CSV files")
    parser.add_argument("--output-dir", default="out/figures", help="Output directory for figures")
    return parser.parse_args()


def load_summary_files(input_dir):
    """Load all *_summary.csv files from input directory."""
    pattern = os.path.join(input_dir, "*_summary.csv")
    files = glob.glob(pattern)
    
    data = []
    for f in files:
        df = pd.read_csv(f)
        model_name = os.path.basename(f).replace("_summary.csv", "")
        df["model"] = model_name
        data.append(df)
    
    if not data:
        raise ValueError(f"No summary CSV files found in {input_dir}")
    
    return pd.concat(data, ignore_index=True)


def plot_model_comparison(df, output_dir):
    """Create bar chart comparing key metrics across models."""
    # Filter to baseline results only (no grouping columns)
    baseline = df[df["group"] == "all_runs"].copy()
    
    # Key metrics to compare
    metrics = [
        "m_final_susceptible_mean",
        "m_final_infected_mean", 
        "m_final_recovered_mean",
        "m_ever_infected_mean",
        "m_deaths_mean"
    ]
    
    # Filter to available metrics
    available_metrics = [m for m in metrics if m in baseline.columns]
    
    if not available_metrics:
        print("No baseline metrics found for comparison")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(available_metrics):
        if i >= len(axes):
            break
        ax = axes[i]
        
        # Extract metric name for title
        metric_name = metric.replace("_mean", "").replace("m_", "").replace("_", " ").title()
        
        baseline.sort_values("model", inplace=True)
        ax.bar(baseline["model"], baseline[metric], color="steelblue")
        ax.set_title(metric_name)
        ax.set_xlabel("Model")
        ax.set_ylabel("Mean Value")
        ax.tick_params(axis="x", rotation=45)
    
    # Hide unused subplots
    for i in range(len(available_metrics), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, "model_comparison.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_metric_distributions(df, output_dir):
    """Create boxplots for metric distributions."""
    # Look for columns with std values to identify metrics with distributions
    metric_cols = [col for col in df.columns if col.endswith("_std")]
    
    if not metric_cols:
        print("No distribution data found")
        return
    
    # Get base metric names
    base_metrics = sorted(set(col.replace("_std", "") for col in metric_cols))
    
    # Filter to baseline results
    baseline = df[df["group"] == "all_runs"].copy()
    
    # Create subplots
    n_metrics = min(len(base_metrics), 6)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, base_metric in enumerate(base_metrics[:6]):
        if i >= len(axes):
            break
        ax = axes[i]
        
        mean_col = f"{base_metric}_mean"
        std_col = f"{base_metric}_std"
        
        if mean_col not in baseline.columns or std_col not in baseline.columns:
            continue
        
        # Create simple error bar plot (mean ± std)
        baseline_sorted = baseline.sort_values("model")
        x_pos = range(len(baseline_sorted))
        
        ax.errorbar(
            x_pos,
            baseline_sorted[mean_col],
            yerr=baseline_sorted[std_col],
            fmt="o",
            capsize=5,
            capthick=2,
            color="darkorange"
        )
        
        metric_name = base_metric.replace("m_", "").replace("_", " ").title()
        ax.set_title(metric_name)
        ax.set_xlabel("Model")
        ax.set_ylabel("Value (mean ± std)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(baseline_sorted["model"], rotation=45, ha="right")
    
    # Hide unused subplots
    for i in range(n_metrics, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, "metric_distributions.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_correlation_heatmap(df, output_dir):
    """Create correlation heatmap for key metrics."""
    baseline = df[df["group"] == "all_runs"].copy()
    
    # Get numeric mean columns
    mean_cols = [col for col in baseline.columns if col.endswith("_mean")]
    
    if len(mean_cols) < 2:
        print("Not enough metrics for correlation analysis")
        return
    
    # Select only the mean columns
    data = baseline[mean_cols].copy()
    
    # Clean column names for display
    data.columns = [col.replace("_mean", "").replace("m_", "") for col in data.columns]
    
    # Calculate correlation
    corr = data.corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, 
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("Metric Correlations")
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_parameter_sensitivity(df, output_dir):
    """Create line plots for parameter sensitivity analysis (extended experiments)."""
    # Filter out baseline results
    extended = df[df["group"] != "all_runs"].copy()
    
    if extended.empty:
        print("No extended experiment data found")
        return
    
    # Identify grouping columns (parameter columns)
    param_cols = [col for col in extended.columns if col not in ["model", "group"] and not col.endswith("_mean") and not col.endswith("_std") and not col.endswith("_n") and not col.endswith("_p25") and not col.endswith("_p50") and not col.endswith("_p75")]
    
    if not param_cols:
        print("No parameter columns found in extended data")
        return
    
    # Get key metrics to plot
    metrics = ["m_ever_infected_mean", "m_deaths_mean", "m_ticks_mean"]
    available_metrics = [m for m in metrics if m in extended.columns]
    
    if not available_metrics:
        print("No key metrics found in extended data")
        return
    
    # For each model with extended data, create plots
    for model_name in extended["model"].unique():
        model_data = extended[extended["model"] == model_name].copy()
        
        # Use the first parameter column as x-axis
        param_col = param_cols[0]
        
        # Check if parameter is numeric
        try:
            model_data[param_col] = pd.to_numeric(model_data[param_col])
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False
        
        n_metrics = len(available_metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 4))
        if n_metrics == 1:
            axes = [axes]
        
        for i, metric in enumerate(available_metrics):
            ax = axes[i]
            
            if is_numeric:
                # Sort by parameter for line plot
                model_data_sorted = model_data.sort_values(param_col)
                ax.plot(model_data_sorted[param_col], model_data_sorted[metric], 
                        marker='o', linewidth=2, markersize=6)
                ax.set_xlabel(param_col.replace("_", " ").title())
            else:
                # Bar plot for categorical parameters
                model_data_sorted = model_data.sort_values(param_col)
                x_pos = range(len(model_data_sorted))
                ax.bar(x_pos, model_data_sorted[metric], color="coral")
                ax.set_xticks(x_pos)
                ax.set_xticklabels(model_data_sorted[param_col], rotation=45, ha="right")
                ax.set_xlabel(param_col.replace("_", " ").title())
            
            metric_name = metric.replace("_mean", "").replace("m_", "").replace("_", " ").title()
            ax.set_ylabel(metric_name)
            ax.set_title(f"{model_name}: {metric_name}")
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(output_dir, f"{model_name}_parameter_sensitivity.png")
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Saved: {output_path}")


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    print(f"Loading summary files from {args.input_dir}...")
    df = load_summary_files(args.input_dir)
    print(f"Loaded {len(df)} rows from {df['model'].nunique()} models")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_model_comparison(df, args.output_dir)
    plot_metric_distributions(df, args.output_dir)
    plot_correlation_heatmap(df, args.output_dir)
    plot_parameter_sensitivity(df, args.output_dir)
    
    print(f"\nAll figures saved to {args.output_dir}")


if __name__ == "__main__":
    main()
