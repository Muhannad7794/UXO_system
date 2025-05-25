import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
file_path = "UXO_all_factors_Syria_final.csv"  # Adjust path if needed
df = pd.read_csv(file_path)


# Helper to convert string ranges (e.g., "10–20") to midpoints
def range_to_midpoint(val):
    if isinstance(val, str) and "–" in val:
        parts = val.replace(" ", "").split("–")
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return np.nan
    try:
        return float(val)
    except:
        return np.nan


# Convert 'uxo_count' and 'ordnance_age' from ranges to numeric midpoints
df["uxo_count"] = df["uxo_count"].apply(range_to_midpoint)
df["ordnance_age"] = df["ordnance_age"].apply(range_to_midpoint)

# Label encode categorical fields
label_cols = ["environmental_conditions", "ordnance_type", "ordnance_condition"]
for col in label_cols:
    df[col] = LabelEncoder().fit_transform(df[col].astype(str))

# Select features for PCA
features = [
    "environmental_conditions",
    "ordnance_type",
    "burial_depth_cm",
    "ordnance_condition",
    "ordnance_age",
    "population_estimate",
    "uxo_count",
]

# Drop rows with missing values in target features
df_clean = df[features].dropna()

# Normalize data using MinMaxScaler (0–1 range)
scaler = MinMaxScaler()
normalized = pd.DataFrame(scaler.fit_transform(df_clean), columns=features)

# Run PCA
pca = PCA()
pca_result = pca.fit(normalized)

# Create DataFrame of PCA loadings and round for readability
loadings = pd.DataFrame(
    np.round(pca.components_.T, 2),
    columns=[f"PC{i+1}" for i in range(len(features))],
    index=features,
)

# Create DataFrame of explained variance ratios and round for readability
explained_variance = pd.DataFrame(
    {
        "Principal Component": [f"PC{i+1}" for i in range(len(features))],
        "Explained Variance Ratio": np.round(pca.explained_variance_ratio_, 2),
    }
)

# Print results
print("\n=== PCA Feature Loadings (rounded) ===")
print(loadings)

print("\n=== Explained Variance by Principal Component (rounded) ===")
print(explained_variance)

# Optional: visualize PC1 loadings
plt.figure(figsize=(10, 6))
sns.barplot(x=loadings.index, y=loadings["PC1"])
plt.title("Feature Loadings on Principal Component 1")
plt.ylabel("Loading Magnitude")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
