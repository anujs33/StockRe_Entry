import streamlit as st
import pandas as pd

def calculate_charges(turnover, exchange):
    # STT (0.1% on buy & sell)
    stt = turnover * 0.001
    
    # Exchange Transaction Charges
    if exchange == "NSE":
        txn_charges = turnover * 0.0002970
    else:  # BSE
        txn_charges = turnover * 0.0003750
        
    # SEBI Charges (₹10 per crore)
    sebi_charges = (turnover / 10000000) * 10
    
    # Stamp Duty (0.015% or ₹1500/crore on buy side only)
    stamp_duty = min(turnover * 0.00015, (turnover / 10000000) * 1500)
    
    # GST (18% on brokerage + SEBI charges + transaction charges)
    gst = (0 + sebi_charges + txn_charges) * 0.18
    
    total_charges = stt + txn_charges + sebi_charges + stamp_duty + gst
    
    return {
        'stt': stt,
        'txn_charges': txn_charges,
        'sebi_charges': sebi_charges,
        'stamp_duty': stamp_duty,
        'gst': gst,
        'total_charges': total_charges
    }

def main():
    st.set_page_config(page_title="Stock Re-entry Calculator", layout="wide")
    
    st.title("Stock Re-entry Calculator")
    
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entry Details")
        entry_price = st.number_input("Entry Price (₹)", min_value=0.0, step=0.1)
        entry_qty = st.number_input("Entry Quantity", min_value=0, step=1)
        
        st.subheader("Exchange")
        exchange = st.radio("Select Exchange", ["NSE", "BSE"])
    
    with col2:
        st.subheader("Exit Details")
        exit_price = st.number_input("Exit Price (₹)", min_value=0.0, step=0.1)
        exit_qty = st.number_input("Exit Quantity", min_value=0, step=1)
        
        st.subheader("Holding Period")
        holding_period = st.radio("Select Holding Period", ["Short Term (< 1 year)", "Long Term (> 1 year)"])

    if st.button("Calculate Re-entry Price"):
        if entry_price and entry_qty and exit_price and exit_qty:
            # Calculate turnovers
            entry_turnover = entry_price * entry_qty
            exit_turnover = exit_price * exit_qty
            
            # Calculate charges
            entry_charges = calculate_charges(entry_turnover, exchange)
            exit_charges = calculate_charges(exit_turnover, exchange)
            
            # Calculate P&L
            gross_pl = (exit_price - entry_price) * exit_qty
            net_pl = gross_pl - (entry_charges['total_charges'] + exit_charges['total_charges'])
            
            # Calculate tax
            tax_rate = 0.20 if "Short Term" in holding_period else 0.125
            tax_amount = net_pl * tax_rate
            post_tax_pl = net_pl - tax_amount
            
            # Calculate re-entry prices
            total_amount = entry_turnover + post_tax_pl
            reentry_price = total_amount / exit_qty
            conservative_reentry_price = reentry_price * 0.99
            
            # Display results
            st.markdown("---")
            st.subheader("Calculation Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Initial Investment", f"₹{entry_turnover:,.2f}")
                st.metric("Gross P&L", f"₹{gross_pl:,.2f}")
            
            with col2:
                st.metric("Total Charges", f"₹{entry_charges['total_charges'] + exit_charges['total_charges']:,.2f}")
                st.metric(f"Tax Amount ({tax_rate*100}%)", f"₹{tax_amount:,.2f}")
            
            with col3:
                st.metric("Net P&L (after tax)", f"₹{post_tax_pl:,.2f}")
            
            st.markdown("---")
            st.subheader("Re-entry Prices")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Standard Re-entry Price", f"₹{reentry_price:,.2f}")
            with col2:
                st.metric("Conservative Re-entry Price (1% lower)", f"₹{conservative_reentry_price:,.2f}")
            
            # Show detailed charges
            with st.expander("View Detailed Charges"):
                charges_df = pd.DataFrame({
                    'Entry': [
                        entry_charges['stt'],
                        entry_charges['txn_charges'],
                        entry_charges['sebi_charges'],
                        entry_charges['stamp_duty'],
                        entry_charges['gst'],
                        entry_charges['total_charges']
                    ],
                    'Exit': [
                        exit_charges['stt'],
                        exit_charges['txn_charges'],
                        exit_charges['sebi_charges'],
                        exit_charges['stamp_duty'],
                        exit_charges['gst'],
                        exit_charges['total_charges']
                    ]
                }, index=['STT', 'Transaction Charges', 'SEBI Charges', 'Stamp Duty', 'GST', 'Total'])
                
                st.dataframe(charges_df.style.format("₹{:,.2f}"))

if __name__ == "__main__":
    main() 