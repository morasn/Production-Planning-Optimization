import streamlit as st
import pulp
import pandas as pd
import Backend

st.set_page_config(
    page_title="Production Optimizer", page_icon="📦", layout="centered"
)

#  brand styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f9ff;
        font-family: 'Helvetica', sans-serif;
        color: #0089CF;
    }

    .block-container {
        padding-top: 2rem;
    }

    h1 {
        color: #0072ce;
    }

    p {
        color: #333;
    }

    .stButton > button {
        background-color: #0089CF !important;
        color: white !important;
        border: none;
        padding: 0.6em 1.2em;
        border-radius: 4px;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #0072ce !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.image("Personal Logo - Letters White .png", width=200)
st.title("Production Optimization")

st.markdown("### Step 1: Define Machines, Products, and Parameters")

products = st.text_input("Enter product names (comma-separated)", "")
machines = st.text_input("Enter machine names (comma-separated)", "")

if machines and products:
    machines = [m.strip() for m in machines.split(",")]
    products = [p.strip() for p in products.split(",")]
    batch_types = ["min", "max"]

    # Define Product Parameters
    st.markdown("### Step 2: Enter Product Parameters")
    product_df = pd.DataFrame(
        {
            "Product": products,
            "Profit per Unit": [0] * len(products),
            "Setup Time (min)": [0] * len(products),
            "Min Batch Size": [1] * len(products),
            "Max Batch Size": [1] * len(products),
            "Demand (units)": [1] * len(products),
            "Penalty Cost (per unit)": [0] * len(products),
        }
    )

    product_df = st.data_editor(product_df, num_rows="dynamic", key="product_params")

    # Extract data
    profit = {
        row["Product"]: row["Profit per Unit"] for _, row in product_df.iterrows()
    }
    setup_time = {
        row["Product"]: row["Setup Time (min)"] / 60 for _, row in product_df.iterrows()
    }
    batch_sizes = {
        (row["Product"], "min"): row["Min Batch Size"]
        for _, row in product_df.iterrows()
    }
    batch_sizes.update(
        {
            (row["Product"], "max"): row["Max Batch Size"]
            for _, row in product_df.iterrows()
        }
    )
    demand = {row["Product"]: row["Demand (units)"] for _, row in product_df.iterrows()}
    penalty_cost = {
        row["Product"]: row["Penalty Cost (per unit)"]
        for _, row in product_df.iterrows()
    }

    available_hours = {}
    maintenance_cost = {}

    # Define Machine Available Hours and Maintenance Costs
    st.markdown("### Step 3: Define Machine Available Hours and Maintenance Costs")

    machine_df = pd.DataFrame(
        {
            "Machine": machines,
            "Available Hours": [0.0] * len(machines),
            "Maintenance Cost": [0.0] * len(machines),
        }
    )

    machine_df = st.data_editor(machine_df, num_rows="dynamic", key="machine_params")

    available_hours = {
        row["Machine"]: row["Available Hours"] for _, row in machine_df.iterrows()
    }
    maintenance_cost = {
        row["Machine"]: row["Maintenance Cost"] for _, row in machine_df.iterrows()
    }

    # Define Machine Capability (Rates in units/hr)
    st.markdown("### Step 4: Define Machine Capability (Rates in units/hr)")
    rate_entries = []
    for p in products:
        for m in machines:
            rate_entries.append({"Product": p, "Machine": m, "Rate (units/hr)": ""})

    rate_df = pd.DataFrame(rate_entries)
    rate_df = st.data_editor(rate_df, key="rate_table")

    rates = {}
    for _, row in rate_df.iterrows():
        try:
            rate = float(row["Rate (units/hr)"])
            if rate > 0:
                rates[(row["Product"], row["Machine"])] = rate
        except:
            pass  # Skip if empty or invalid

        # Model Setup
    if st.button("Optimize Production"):
        [x, y, unmet, Status, Model_Objective] = Backend.Model_Solver(
            machines,
            products,
            demand,
            batch_types,
            batch_sizes,
            setup_time,
            profit,
            penalty_cost,
            rates,
            maintenance_cost,
            available_hours,
        )

        [Prod_Totals_Msg, Unmet_Summary, Machine_Hours, Machine_Utilization ] = Backend.Results_Calculating(
            x,
            y,
            unmet,
            products,
            machines,
            rates,
            batch_types,
            batch_sizes,
            setup_time,
            demand,
            available_hours,
        )

        st.markdown("### Results")
        st.write(f"**Status:** {Status}")
        st.write(f"**Total Profit:** {Model_Objective:.2f} units")


        st.markdown("### Production Summary")
        for msg in Prod_Totals_Msg:
            st.write(msg)

        st.markdown("### Total Hours per Machine")
        for i in range(len(Machine_Hours)):
            st.write(Machine_Hours[i])
            st.write(Machine_Utilization[i])
else:
    st.info("Please enter both machines and products to begin.")
