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
    
    # Don't concat - return list of separate dataframes to avoid column mixing
    return data


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
    
    # Flatten axes array
    if n_metrics == 1:
        axes = [[axes]]
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
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


def plot_parameter_sensitivity(extended_dfs, output_dir):
    """Create visualizations for parameter sensitivity analysis (extended experiments)."""
    if not extended_dfs:
        print("No extended experiment data found")
        return
    
    # Process each extended experiment file separately
    for model_data in extended_dfs:
        model_name = model_data["model"].iloc[0]
        
        # Identify parameter columns (non-metric columns)
        metric_suffixes = ["_mean", "_std", "_n", "_p25", "_p50", "_p75"]
        param_cols = [col for col in model_data.columns 
                      if col not in ["model", "experiment_type"] 
                      and not any(col.endswith(suffix) for suffix in metric_suffixes)]
        
        print(f"  {model_name}: {len(param_cols)} parameters: {param_cols}")
        
        if not param_cols:
            print(f"No parameter columns found for {model_name}")
            continue
        
        # Get available metrics (exclude zero-variance metrics)
        mean_cols = [col for col in model_data.columns if col.endswith("_mean")]
        non_zero_metrics = []
        for metric in mean_cols:
            std_val = model_data[metric].std()
            if std_val > 0.001:  # Has some variance
                non_zero_metrics.append(metric)
                print(f"    {metric}: std={std_val:.4f}")
        
        if not non_zero_metrics:
            print(f"No non-constant metrics found for {model_name}")
            continue
        
        # If single parameter (OFAT), use line plots
        if len(param_cols) == 1:
            param_col = param_cols[0]
            
            # Check if parameter is numeric
            try:
                model_data[param_col] = pd.to_numeric(model_data[param_col])
                is_numeric = True
            except (ValueError, TypeError):
                is_numeric = False
            
            # Plot top 4 metrics
            metrics_to_plot = non_zero_metrics[:4]
            n_metrics = len(metrics_to_plot)
            n_cols = min(n_metrics, 2)
            n_rows = (n_metrics + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
            axes = axes[:n_metrics]
            
            for i, metric in enumerate(metrics_to_plot):
                ax = axes[i]
                
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
        
        # If multiple parameters (grid), use heatmap for primary metric
        elif len(param_cols) >= 2:
            # Use the metric with highest variance as primary
            primary_metric = max(non_zero_metrics, key=lambda m: model_data[m].std())
            
            # For 2-parameter grid, create heatmap
            if len(param_cols) == 2:
                param1, param2 = param_cols[0], param_cols[1]
                
                # Create pivot table
                try:
                    pivot_data = model_data.pivot(index=param1, columns=param2, values=primary_metric)
                    
                    # Check if pivot succeeded
                    if pivot_data.empty or pivot_data.isna().all().all():
                        print(f"    Warning: Pivot table failed for {model_name}, falling back to line plot")
                        # Fall back to line plot
                        param_col = param_cols[0]
                        model_data[param_col] = pd.to_numeric(model_data[param_col], errors='coerce')
                        model_data_sorted = model_data.sort_values(param_col)
                        
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.plot(model_data_sorted[param_col], model_data_sorted[primary_metric], 
                                marker='o', linewidth=2, markersize=6, color='steelblue')
                        ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
                        metric_name = primary_metric.replace("_mean", "").replace("m_", "").replace("-", " ").replace("_", " ").title()
                        ax.set_ylabel(metric_name)
                        ax.set_title(f"{model_name}: {metric_name}")
                        ax.grid(True, alpha=0.3)
                        plt.tight_layout()
                        output_path = os.path.join(output_dir, f"{model_name}_parameter_sensitivity.png")
                    else:
                        # Create heatmap
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(pivot_data, annot=True, fmt=".1f", cmap="YlOrRd", 
                                   cbar_kws={"label": primary_metric.replace("_mean", "").replace("m_", "").replace("_", " ").title()},
                                   ax=ax)
                        ax.set_title(f"{model_name}: {primary_metric.replace('_mean', '').replace('m_', '').replace('_', ' ').title()}")
                        ax.set_xlabel(param2.replace("-", " ").replace("_", " ").title())
                        ax.set_ylabel(param1.replace("-", " ").replace("_", " ").title())
                        plt.tight_layout()
                        output_path = os.path.join(output_dir, f"{model_name}_grid_heatmap.png")
                except Exception as e:
                    print(f"    Warning: Heatmap creation failed for {model_name}: {e}")
                    # Fall back to line plot
                    param_col = param_cols[0]
                    model_data[param_col] = pd.to_numeric(model_data[param_col], errors='coerce')
                    model_data_sorted = model_data.sort_values(param_col)
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.plot(model_data_sorted[param_col], model_data_sorted[primary_metric], 
                            marker='o', linewidth=2, markersize=6, color='steelblue')
                    ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
                    metric_name = primary_metric.replace("_mean", "").replace("m_", "").replace("-", " ").replace("_", " ").title()
                    ax.set_ylabel(metric_name)
                    ax.set_title(f"{model_name}: {metric_name}")
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    output_path = os.path.join(output_dir, f"{model_name}_parameter_sensitivity.png")
                
                plt.savefig(output_path, dpi=150)
                plt.close()
                print(f"Saved: {output_path}")
            else:
                # For 3 parameters, create multiple heatmaps for each parameter pair
                if len(param_cols) == 3:
                    print(f"  Creating multi-heatmap visualization for {model_name}")
                    
                    # Get unique values for each parameter to determine which to fix
                    param_values = {}
                    for param in param_cols:
                        param_values[param] = sorted(model_data[param].unique())
                    
                    # Create figure with 3 subplots (one for each fixed parameter)
                    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
                    
                    # For each parameter, fix it and create heatmap of the other two
                    for i, fixed_param in enumerate(param_cols):
                        ax = axes[i]
                        other_params = [p for p in param_cols if p != fixed_param]
                        param1, param2 = other_params[0], other_params[1]
                        
                        # Fix the parameter to its median value (or first if categorical)
                        fixed_value = param_values[fixed_param][len(param_values[fixed_param]) // 2]
                        
                        # Filter data to fixed parameter value
                        filtered_data = model_data[model_data[fixed_param] == fixed_value].copy()
                        
                        if len(filtered_data) < 2:
                            # Try first value instead
                            fixed_value = param_values[fixed_param][0]
                            filtered_data = model_data[model_data[fixed_param] == fixed_value].copy()
                        
                        if len(filtered_data) < 2:
                            print(f"    Warning: Not enough data for fixed {fixed_param}={fixed_value}")
                            ax.text(0.5, 0.5, f"Insufficient data\nfor {fixed_param}={fixed_value}", 
                                   ha='center', va='center', transform=ax.transAxes)
                            continue
                        
                        # Create pivot table
                        try:
                            pivot_data = filtered_data.pivot(index=param1, columns=param2, values=primary_metric)
                            
                            if pivot_data.empty or pivot_data.isna().all().all():
                                print(f"    Warning: Pivot failed for {fixed_param}={fixed_value}")
                                ax.text(0.5, 0.5, f"Pivot failed", ha='center', va='center', transform=ax.transAxes)
                                continue
                            
                            # Create heatmap
                            sns.heatmap(pivot_data, annot=True, fmt=".1f", cmap="YlOrRd", 
                                       cbar_kws={"label": primary_metric.replace("_mean", "").replace("m_", "").replace("_", " ").title()},
                                       ax=ax)
                            ax.set_title(f"{fixed_param} = {fixed_value}")
                            ax.set_xlabel(param2.replace("-", " ").replace("_", " ").title())
                            ax.set_ylabel(param1.replace("-", " ").replace("_", " ").title())
                        except Exception as e:
                            print(f"    Warning: Heatmap failed for {fixed_param}={fixed_value}: {e}")
                            ax.text(0.5, 0.5, f"Error: {str(e)[:20]}...", ha='center', va='center', transform=ax.transAxes)
                    
                    plt.suptitle(f"{model_name}: {primary_metric.replace('_mean', '').replace('m_', '').replace('_', ' ').title()}", 
                                fontsize=14, fontweight='bold')
                    plt.tight_layout()
                    output_path = os.path.join(output_dir, f"{model_name}_parameter_sensitivity.png")
                    plt.savefig(output_path, dpi=150)
                    plt.close()
                    print(f"Saved: {output_path}")
                else:
                    # For >3 parameters, fall back to simple line plot
                    print(f"Warning: {model_name} has {len(param_cols)} parameters, using simplified visualization")
                    
                    # Plot primary metric vs first parameter
                    param_col = param_cols[0]
                    try:
                        model_data[param_col] = pd.to_numeric(model_data[param_col])
                        is_numeric = True
                    except (ValueError, TypeError):
                        is_numeric = False
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    
                    if is_numeric:
                        model_data_sorted = model_data.sort_values(param_col)
                        ax.plot(model_data_sorted[param_col], model_data_sorted[primary_metric], 
                                marker='o', linewidth=2, markersize=6, color='steelblue')
                        ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
                    else:
                        model_data_sorted = model_data.sort_values(param_col)
                        x_pos = range(len(model_data_sorted))
                        ax.bar(x_pos, model_data_sorted[primary_metric], color="coral")
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(model_data_sorted[param_col], rotation=45, ha="right")
                        ax.set_xlabel(param_col.replace("-", " ").replace("_", " ").title())
                    
                    metric_name = primary_metric.replace("_mean", "").replace("m_", "").replace("-", " ").replace("_", " ").title()
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
    dfs = load_summary_files(args.input_dir)
    
    # Separate baseline and extended
    baseline_dfs = [df for df in dfs if df["experiment_type"].iloc[0] == "baseline"]
    extended_dfs = [df for df in dfs if df["experiment_type"].iloc[0] == "extended"]
    
    # Concat baseline data for comparison visualizations
    if baseline_dfs:
        baseline_df = pd.concat(baseline_dfs, ignore_index=True)
        print(f"Loaded {len(baseline_df)} baseline rows from {baseline_df['model'].nunique()} models")
    else:
        baseline_df = pd.DataFrame()
        print("No baseline data found")
    
    print(f"Loaded {len(extended_dfs)} extended experiment files")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    if not baseline_df.empty:
        plot_model_comparison(baseline_df, args.output_dir)
        plot_metric_distributions(baseline_df, args.output_dir)
        plot_correlation_heatmap(baseline_df, args.output_dir)
    
    # Extended visualizations work with separate dataframes
    plot_parameter_sensitivity(extended_dfs, args.output_dir)
    
    print(f"\nAll figures saved to {args.output_dir}")


if __name__ == "__main__":
    main()
