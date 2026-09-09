import pandas as pd
import numpy as np

# Set random seed so results are reproducible
np.random.seed(42)

# Number of candidate records
n_samples = 1000

# Generate candidate features
required_skill_match = np.random.randint(20, 101, n_samples)
preferred_skill_match = np.random.randint(0, 101, n_samples)

# Overall skill match
total_skill_match = (
    required_skill_match * 0.7
    + preferred_skill_match * 0.3
)

matched_required_count = np.round(required_skill_match / 10).astype(int)
matched_preferred_count = np.round(preferred_skill_match / 20).astype(int)

experience_years = np.random.randint(0, 11, n_samples)
project_count = np.random.randint(0, 11, n_samples)

# Create shortlisting logic for training labels
score = (
    required_skill_match * 0.50
    + preferred_skill_match * 0.15
    + experience_years * 4
    + project_count * 2
)

# Add some randomness to make the dataset realistic
score += np.random.normal(0, 10, n_samples)

# Create target variable
shortlisted = (score >= 65).astype(int)

# Create DataFrame
data = pd.DataFrame({
    "required_skill_match": required_skill_match,
    "preferred_skill_match": preferred_skill_match,
    "total_skill_match": total_skill_match,
    "matched_required_count": matched_required_count,
    "matched_preferred_count": matched_preferred_count,
    "experience_years": experience_years,
    "project_count": project_count,
    "shortlisted": shortlisted
})

# Save dataset
data.to_csv("ml/dataset/candidate_dataset.csv", index=False)

print("Dataset generated successfully!")
print(f"Total records: {len(data)}")
print("\nClass distribution:")
print(data["shortlisted"].value_counts())
print("\nFirst 5 records:")
print(data.head())