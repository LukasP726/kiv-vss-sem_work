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
        
        # Determine if this is baseline or extended based on columns
        if "group" in df.columns:
            df["experiment_type"] = "baseline"
        else:
            df["experiment_type"] = "extended"
        
        data.append(df)
    
    if not data:
        raise ValueError(f"No summary CSV files found in {input_dir}")
    
    return pd.concat(data, ignore_index=True)


def plot_model_comparison(df, output_dir):
    """Create bar chart comparing key metrics across models."""
    # Filter to baseline results only
    baseline = df[df["experiment_type"] == "baseline"].copy()
    
    if baseline.empty:
        print("No baseline data found for comparison")
        return
    
    # Get all available mean metrics (excluding n, std, p25, p50, p75)
    mean_cols = [col for col in baseline.columns if col.endswith("_mean")]
    
    # Focus on key outcome metrics
    key_metrics = ["m_ever_infected_mean", "m_deaths_mean", "m_ticks_mean", 
                   "m_final_infected_mean", "m_final_recovered_mean"]
    available_metrics = [m for m in key_metrics if m in baseline.columns]
    
    if not available_metrics:
        print("No key metrics found in baseline data")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(available_metrics):
        if i >= len(axes):
            break
        ax = axes[i]
        
        # Extract metric name for title
        metric_name = metric.replace("_mean", "").replace("m_", "").replace("_", " ").title()
        
        baseline_sorted = baseline.sort_values("model")
        ax.bar(baseline_sorted["model"], baseline_sorted[metric], color="steelblue")
        ax.set_title(metric_name)
        ax.set_xlabel("Model")
        ax.set_ylabel("Mean Value")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
    
    # Hide unused subplots
    for i in range(len(available_metrics), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, "model_comparison.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_metric_distributions(df, output_dir):
    """Create error bar plots showing mean ± std for key metrics."""
    # Filter to baseline results
    baseline = df[df["experiment_type"] == "baseline"].copy()
    
    if baseline.empty:
        print("No baseline data found for distributions")
        return
    
    # Get key metrics with std values
    key_metrics = ["m_ever_infected", "m_deaths", "m_ticks", 
                   "m_final_infected", "m_final_recovered"]
    
    available_metrics = []
    for base in key_metrics:
        mean_col = f"{base}_mean"
        std_col = f"{base}_std"
        if mean_col in baseline.columns and std_col in baseline.columns:
            available_metrics.append(base)
    
    if not available_metrics:
        print("No metrics with std data found")
        return
    
    # Create subplots
    n_metrics = len(available_metrics)
    n_cols = min(n_metrics, 3)
    n_rows = (n_metrics + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    if n_metrics == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [axes]
    axes = [ax if isinstance(ax, list) else [ax] for row in axes for ax in (row if isinstance(row, list) else [row])]
    axes = axes[:n_metrics]
    
    for i, base_metric in enumerate(available_metrics):
        ax = axes[i]
        
        mean_col = f"{base_metric}_mean"
        std_col = f"{base_metric}_std"
        
        # Create error bar plot (mean ± std)
        baseline_sorted = baseline.sort_values("model")
        x_pos = range(len(baseline_sorted))
        
        ax.errorbar(
            x_pos,
            baseline_sorted[mean_col],
            yerr=baseline_sorted[std_col],
            fmt="o",
            capsize=5,
            capthick=2,
            color="darkorange",
            linewidth=2,
            markersize=8
        )
        
        metric_name = base_metric.replace("m_", "").replace("_", " ").title()
        ax.set_title(metric_name)
        ax.set_xlabel("Model")
        ax.set_ylabel("Value (mean ± std)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(baseline_sorted["model"], rotation=45, ha="right")
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, "metric_distributions.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_correlation_heatmap(df, output_dir):
    """Create correlation heatmap for key metrics."""
    baseline = df[df["experiment_type"] == "baseline"].copy()
    
    if baseline.empty:
        print("No baseline data found for correlation analysis")
        return
    
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
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, 
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax,
                annot_kws={"size": 8}, fmt=".2f")
    ax.set_title("Metric Correlations (Baseline)")
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_parameter_sensitivity(df, output_dir):
    """Create line plots for parameter sensitivity analysis (extended experiments)."""
    # Filter to extended results
    extended = df[df["experiment_type"] == "extended"].copy()
    
    if extended.empty:
        print("No extended experiment data found")
        return
    
    # For each model with extended data, create plots
    for model_name in extended["model"].unique():
        model_data = extended[extended["model"] == model_name].copy()
        
        # Identify parameter columns (non-metric columns)
        metric_suffixes = ["_mean", "_std", "_n", "_p25", "_p50", "_p75"]
        param_cols = [col for col in model_data.columns 
                      if col not in ["model", "experiment_type"] 
                      and not any(col.endswith(suffix) for suffix in metric_suffixes)]
        
        if not param_cols:
            print(f"No parameter columns found for {model_name}")
            continue
        
        # Get available metrics
        mean_cols = [col for col in model_data.columns if col.endswith("_mean")]
        
        if not mean_cols:
            print(f"No mean metrics found for {model_name}")
            continue
        
        # Use the first parameter as x-axis
        param_col = param_cols[0]
        
        # Check if parameter is numeric
        try:
            model_data[param_col] = pd.to_numeric(model_data[param_col])
            is_numeric = True
        except (ValueError, TypeError):
            is_numeric = False
        
        # Plot top 4-6 metrics
        metrics_to_plot = mean_cols[:6]
        n_metrics = len(metrics_to_plot)
        n_cols = min(n_metrics, 2)
        n_rows = (n_metrics + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
        if n_metrics == 1:
            axes = [[axes]]
        elif n_rows == 1:
            axes = [axes]
        axes_flat = []
        for row in axes:
            if isinstance(row, list):
                axes_flat.extend(row)
            else:
                axes_flat.append(row)
        axes_flat = axes_flat[:n_metrics]
        
        for i, metric in enumerate(metrics_to_plot):
            ax = axes_flat[i]
            
            if is_numeric:
                # Sort by parameter for line plot
                model_data_sorted = model_data.sort_values(param_col)
                ax.plot(model_data_sorted[param_col], model_data_sorted[metric], 
                        marker='o', linewidth=2, markersize=6, color='steelblue')
                ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
            else:
                # Bar plot for categorical parameters
                model_data_sorted = model_data.sort_values(param_col)
                x_pos = range(len(model_data_sorted))
                ax.bar(x_pos, model_data_sorted[metric], color="coral")
                ax.set_xticks(x_pos)
                ax.set_xticklabels(model_data_sorted[param_col], rotation=45, ha="right")
                ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
            
            metric_name = metric.replace("_mean", "").replace("m_", "").replace("-", " ").replace("_", " ").title()
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
    print(f"  - Baseline experiments: {len(df[df['experiment_type'] == 'baseline'])} rows")
    print(f"  - Extended experiments: {len(df[df['experiment_type'] == 'extended'])} rows")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_model_comparison(df, args.output_dir)
    plot_metric_distributions(df, args.output_dir)
    plot_correlation_heatmap(df, args.output_dir)
    plot_parameter_sensitivity(df, args.output_dir)
    
    print(f"\nAll figures saved to {args.output_dir}")


if __name__ == "__main__":
    main()
