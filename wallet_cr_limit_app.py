# Creating a Streamlit App for the Wallet Customers' Rule-Based Scorecard:

import streamlit as st
from datetime import datetime

# User-defined function to calculate the credit limit for a wallet platform customer based on defined business rules

def set_credit_limit(avg_ntxns_per_month, avg_sum_credits_per_month, median_avg_credits_per_month, businesstype='INDIVIDUAL', crb_cr_quality='Low', crb_listing='Neg', length_on_platform=0):
    """
    Calculate the credit limit for a wallet platform customer (rounded to the nearest tenth and integer) based on defined business rules.

    This function applies a hierarchical decision-making process to determine the credit limit for a wallet customer. 
    It sequentially checks multiple conditions and assigns the credit limit accordingly.

    The conditions are checked in the following order:
    1. Business Type ('INDIVIDUAL', 'SOLE_PROPRIETOR', 'UNREGISTERED', 'LIMITED_COMPANY', or 'PARTNERSHIP')
    2. CRB Listing Status.
    3. Average Number of Transactions per Month.
    4. Average Sum of Credits per Month.
    5. CRB Credit Quality (Defaulter|Lowest|Low|Moderate|High|Highest)
    6. Length of Customer on the Platform.
    7. Median of the Average Credits per Month.
    8. Customer Category (IND or BUS)
    
    Args:
    avg_ntxns_per_month (float): Average number of transactions per month.
    avg_sum_credits_per_month (float): Average sum of credits per month.
    median_avg_credits_per_month (float): Median of the average credits per month.
    businesstype (str): Type of business (INDIVIDUAL, SOLE_PROPRIETOR, UNREGISTERED, LIMITED_COMPANY, PARTNERSHIP). Defaults to 'INDIVIDUAL'.
    crb_cr_quality (str): CRB customer credit quality categorization (Defaulter|Lowest|Low|Moderate|High|Highest). Defaults to 'Low'.
    crb_listing (str): CRB listing status of the customer ('Pos' or 'Neg'). Defaults to 'Neg'.
    length_on_platform (int): Duration of the customer on the wallet platform (in months).

    Returns:
    tuple: A tuple containing the decision ('Decline' or 'Accept') and the credit limit (numeric), and a reason for decline or acceptance (str).

    Raises:
    ValueError: If any input value is invalid.

    """
    # ---------------Validation Checks--------------------
    # Validate numeric input values
    if not isinstance(avg_ntxns_per_month, (int, float)):
        raise ValueError("Average number of transactions per month must be numeric.")
    
    if not isinstance(avg_sum_credits_per_month, (int, float)):
        raise ValueError("Average sum of credits per month must be numeric.")
    
    if not isinstance(median_avg_credits_per_month, (int, float)):
        raise ValueError("Median of the average credits per month must be numeric.")
    
    if not isinstance(length_on_platform, (int, float)):
        raise ValueError("Length on platform must be numeric.")
    
    # Check 'crb_cr_quality' value
    if not isinstance(crb_cr_quality, str):
        raise ValueError("CRB credit quality value must be a string.")
    
    if not crb_cr_quality.lower() in ['defaulter', 'lowest', 'low', 'moderate', 'high', 'highest']:
        raise ValueError("CRB credit quality value must be either 'Defaulter', 'Lowest', 'Low', 'Moderate', 'High' or 'Highest'.")
    
    if not crb_listing.lower() in ['neg', 'pos']:
        raise ValueError("CRB listing can only take the values 'Neg' or 'Pos'.")
    
    # Check 'businesstype' value
    if not isinstance(businesstype, str):
        raise ValueError("Business type value must be a string.")
    
    businesstype = businesstype.upper()
    if businesstype not in ['INDIVIDUAL', 'SOLE_PROPRIETOR', 'UNREGISTERED', 'LIMITED_COMPANY', 'PARTNERSHIP']:
        raise ValueError("Business type value must be either 'INDIVIDUAL', 'SOLE_PROPRIETOR', 'UNREGISTERED', 'LIMITED_COMPANY', or 'PARTNERSHIP'.")
    
    # Determine customer category based on businesstype
    if businesstype in ['INDIVIDUAL', 'SOLE_PROPRIETOR', 'UNREGISTERED']:
        category = 'IND'
    else:
        category = 'BUS'

    # Check CRB Listing Status
    if crb_listing.lower() == 'neg':
        return 'Decline', 0, "Customer has a negative CRB listing status."
    
    # Check if average number of transactions per month is one or less
    if avg_ntxns_per_month <= 1:
        return 'Decline', 0, "Customer has < 2 average transactions per month."
    
    # Check if average sum of credit amounts per month is less than 1k
    if avg_sum_credits_per_month < 1000:
        return 'Decline', 0, "Customer has an average sum of credit amount per month < 1k."
    
    # Check CRB Credit Quality
    if crb_cr_quality.lower() == 'defaulter':
        return 'Decline', 0, "Customer categorized as a defaulter in CRB credit quality."
    # ---------------Limit Algorithm--------------------
    # Initializing the defaults for decision, credit limit and the reason for the decision
    decision = 'Decline'
    credit_limit = 0
    reason = "Eligibility criteria met. Limit based on transaction activity."
    
    # Set different limits based on category
    if category.lower() == 'ind': # -----------------------------Individual Category---------------------------------
        # Calculate credit limit based on CRB CR quality and length on platform
        if crb_cr_quality.lower() in ['lowest', 'low']:
            if length_on_platform <= 2:
                return 'Decline', 0, "Customer is <= 2 months old on the platform with low credit quality."
            elif 3 <= length_on_platform <= 5:
                credit_limit = min(0.2 * median_avg_credits_per_month, 10000)
            else:
                credit_limit = min(0.3 * median_avg_credits_per_month, 15000)
        else:  # Moderate or High or Highest
            if crb_cr_quality.lower() in ['moderate', 'high', 'highest']:
                if length_on_platform <= 1:
                    return 'Decline', 0, "Customer is <= 1 month old on the platform."
                elif 2 <= length_on_platform <= 5:
                    credit_limit = min(0.3 * median_avg_credits_per_month, 20000)
                else:
                    if avg_sum_credits_per_month < 1000:
                        credit_limit = 0
                        reason = "Customer's average sum of credit value per month does not qualify a limit."
                    elif 1000 <= avg_sum_credits_per_month <= 100000:
                        credit_limit = min(0.4 * median_avg_credits_per_month, 25000)
                    else:
                        credit_limit = min(0.5 * median_avg_credits_per_month, 30000)
    else:  # -----------------------------Business Category-------------------------------------------------------
        # Calculate credit limit based on CRB CR quality and length on platform
        if crb_cr_quality.lower() in ['lowest', 'low']:
            if length_on_platform <= 2:
                return 'Decline', 0, "Customer is <= 2 months old on the platform with low credit quality."
            elif 3 <= length_on_platform <= 5:
                credit_limit = min(0.45 * median_avg_credits_per_month, 50000)
            else:
                credit_limit = min(0.55 * median_avg_credits_per_month, 100000)
        else:  # Moderate or High or Highest
            if crb_cr_quality.lower() in ['moderate', 'high', 'highest']:
                if length_on_platform <= 1:
                    return 'Decline', 0, "Customer is <= 1 month old on the platform."
                elif 2 <= length_on_platform <= 5:
                    credit_limit = min(0.6 * median_avg_credits_per_month, 150000)
                else:
                    if avg_sum_credits_per_month < 1000:
                        credit_limit = 0
                        reason = "Customer's average sum of credit value per month does not qualify a limit."
                    elif 1000 <= avg_sum_credits_per_month <= 100000:
                        credit_limit = min(0.65 * median_avg_credits_per_month, 200000)
                    else:
                        credit_limit = min(0.7 * median_avg_credits_per_month, 350000)

    # Handle the case where the credit limit is zero
    if credit_limit > 0:
        decision = 'Accept'
    elif decision == 'Accept' and credit_limit == 0:
        reason = "Customer eligible for credit. However, average sum of credit value per month does not qualify a limit."
    
    return decision, round(credit_limit / 10, 0) * 10, reason

# Streamlit App Interface
st.header(f"Wallet Credit Limit Generator")
st.subheader(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Input Fields
avg_ntxns_per_month = st.number_input("Customer's Average Number of Transactions per Month", min_value=0.0, step=0.1)
avg_sum_credits_per_month = st.number_input("Customer's Average Sum of Credit Value per Month", min_value=0.0, step=0.1)
median_avg_credits_per_month = st.number_input("Customer's Median of Average Credits (Amounts) per Month", min_value=0.0, step=0.1)
businesstype = st.selectbox('Business Type', ['INDIVIDUAL', 'SOLE_PROPRIETOR', 'UNREGISTERED', 'LIMITED_COMPANY', 'PARTNERSHIP'])
crb_cr_quality = st.selectbox('CRB Credit Quality', ['Defaulter', 'Lowest', 'Low', 'Moderate', 'High', 'Highest'])
crb_listing = st.selectbox('CRB Listing Status', ['Pos', 'Neg'])
length_on_platform = st.number_input("Customer's Length on Wallet Platform (in months)", min_value=0, step=1)

# Calculate Credit Limit
if st.button("Calculate Credit Limit"):
    decision, limit, reason = set_credit_limit(
        avg_ntxns_per_month, 
        avg_sum_credits_per_month, 
        median_avg_credits_per_month, 
        businesstype, 
        crb_cr_quality, 
        crb_listing, 
        length_on_platform
    )
    st.write(f"**Decision:** {decision}")
    st.write(f"**Credit Limit:** {limit}")
    st.write(f"**Reason:** {reason}")


    