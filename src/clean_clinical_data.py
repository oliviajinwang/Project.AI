import pandas as pd
import numpy as np
# from sklearn.impute import SimpleImputer

def clean_clinician_dataset(file_path, output_path="clinician_mri_clean.csv"):
    print("🚀 Starting Clinical Dataset Preprocessing Pipeline...")
    
    # 1. Load Data
    df = pd.read_csv(file_path)
    
    # 2. Establish Schema & Feature Selection
    # Drop IDs & columns that create absolute data leakage (like CDR, which is literally the diagnostic rating itself)
    # We keep MMSE, eTIV, nWBV, ASF as clinical predictors.
    columns_to_keep = ['Subject ID', 'MRI ID', 'Group', 'M/F', 'Age', 'EDUC', 'SES', 'MMSE', 'eTIV', 'nWBV', 'ASF']
    df_filtered = df[columns_to_keep].copy()
    
    # Standardize column naming convention for the frontend developer (lowercase, descriptive)
    schema_mapping = {
        'Subject ID': 'subject_id',
        'MRI ID': 'mri_id',
        'Group': 'dementia_status',
        'M/F': 'gender_male',
        'Age': 'age',
        'EDUC': 'education_years',
        'SES': 'socioeconomic_status',
        'MMSE': 'mmse_score',
        'eTIV': 'estimated_intracranial_volume',
        'nWBV': 'normalized_whole_brain_volume',
        'ASF': 'atlas_scaling_factor'
    }
    df_filtered.rename(columns=schema_mapping, inplace=True)
    
    # 3. Handle Target Variable (dementia_status)
    # Three distinct clinical states, matching the original OASIS 'Group'
    # labels exactly rather than collapsing 'Converted' (patients who
    # transitioned during the study) into 'Demented' -- that transition is
    # itself clinically meaningful and worth predicting as its own class.
    df_filtered['dementia_status'] = df_filtered['dementia_status'].map({
        'Nondemented': 0,
        'Demented': 1,
        'Converted': 2
    })
    
    # 4. Encode Categorical Features
    # Encode Gender: Male = 1, Female = 0
    df_filtered['gender_male'] = df_filtered['gender_male'].map({'M': 1, 'F': 0})
    
    # 5. Handle Missing Values (Imputation)
    print("🔍 Missing values before imputation:\n", df_filtered.isnull().sum())
    
    # SES (Socioeconomic Status) is heavily tied to education years (EDUC). 
    # Instead of a global median, we impute SES using the median score of people with the same education level.
    df_filtered['socioeconomic_status'] = df_filtered.groupby('education_years')['socioeconomic_status'].transform(
        lambda x: x.fillna(x.median() if pd.notna(x.median()) else 3.0) # Fallback to 3 if group is empty
    )
    
    # For MMSE (Mini-Mental State Exam), if any are missing, impute with the median score based on dementia status.
    df_filtered['mmse_score'] = df_filtered.groupby('dementia_status')['mmse_score'].transform(
        lambda x: x.fillna(x.median())
    )
    
    # 6. Outlier & Anomaly Detection
    # In brain metrics, true outliers are usually data-entry bugs (e.g., fractional numbers where whole numbers belong).
    # We clip values to logical medical boundaries to make sure extreme outliers don't warp your Week 2 models.
    df_filtered['mmse_score'] = df_filtered['mmse_score'].clip(0, 30) # MMSE cannot exceed 30
    df_filtered['normalized_whole_brain_volume'] = df_filtered['normalized_whole_brain_volume'].clip(0.5, 0.9)
    
    # Double check for remaining nulls
    if df_filtered.isnull().sum().sum() > 0:
        print("⚠️ Warning: Post-grouped imputation still left missing values. Applying fallback global imputer.")
        # Final safety check fallback
        for col in df_filtered.columns:
            df_filtered[col].fillna(df_filtered[col].median(), inplace=True)
            
    print("✅ Cleaned Schema Verification:\n", df_filtered.dtypes)
    print(f"📊 Final Cleaned Shape: {df_filtered.shape[0]} rows, {df_filtered.shape[1]} columns.")
    
    # 7. Export Clean Dataset
    df_filtered.to_csv(output_path, index=False)
    print(f"💾 File successfully saved to: {output_path}")
    return df_filtered

# --- Execution Block ---
if __name__ == "__main__":
    # Make sure 'dementia_dataset.csv' is saved in your project folder!
    clean_clinician_dataset('data/clinician_view_data/oasis_longitudinal.csv', 'data/clinician_view_data/clinician_mri_clean.csv')

# --- Execution Block ---
# Replace 'dementia_dataset.csv' with your local raw file filename/path
# cleaned_df = clean_clinician_dataset('dementia_dataset.csv')