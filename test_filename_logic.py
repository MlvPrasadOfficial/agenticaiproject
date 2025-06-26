#!/usr/bin/env python3

"""
Direct test of filename extraction logic
"""

import os

def test_filename_extraction():
    # Simulate the filename extraction logic from agent_status.py
    test_files = [
        "f8ed31fa-0c47-4231-b562-84e216eff2a2_heart_surgeries_dummy.csv",
        "18ffaf7b-eac0-4e8f-85a9-6e8314695fbf_sample_sales_data.csv", 
        "893567e6-de2a-42bc-9e73-dda1c3e55531_temp_test.csv"
    ]
    
    print("🔍 Testing filename extraction logic:")
    print("=" * 50)
    
    for full_filename in test_files:
        print(f"\nOriginal filename: {full_filename}")
        
        # Apply the logic from agent_status.py
        if '_' in full_filename:
            extracted_filename = full_filename.split('_', 1)[1]  # Get everything after first underscore
        else:
            extracted_filename = full_filename  # Fallback if no underscore
            
        print(f"Extracted filename: {extracted_filename}")
        
        # Check if UUID prefix was removed
        if extracted_filename != full_filename:
            print("✅ UUID prefix successfully removed")
        else:
            print("❌ No change made")

if __name__ == "__main__":
    test_filename_extraction()
