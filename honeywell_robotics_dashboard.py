import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Honeywell Aerospace - Production, Inventory & Robotics",
    layout="wide"
)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
with st.sidebar:
    st.title("Filter Panel")
    # Single date selection instead of a range.
    selected_date = st.date_input("Select Date", value=datetime.date(2025, 4, 5))
    selected_date_str = str(selected_date)
    
    shift = st.selectbox("Shift", ["Shift 1", "Shift 2", "Shift 3"])
    company = st.selectbox("Company", ["Company 1", "Company 2"])
    work_center = st.selectbox("Work Center", ["Assembly", "Warehouse A", "Warehouse B"])
    
    # New select box for production goal period.
    goal_period = st.selectbox("Production Goal Period", ["Weekly", "Monthly", "Quarterly", "Yearly"])

# --------------------------------------------------
# MOCK DATA SETUP
# --------------------------------------------------

# 1) Production Goals (mocked values)
production_goals = {
    "Weekly": {"goal": 3500, "actual": 3400},
    "Monthly": {"goal": 15000, "actual": 14800},
    "Quarterly": {"goal": 45000, "actual": 44000},
    "Yearly": {"goal": 180000, "actual": 175000}
}

# 2) OEE Metrics (mocked)
oee_metrics = {
    "Availability": {"value": 48, "target": 60},
    "Performance": {"value": 85, "target": 75},
    "Quality": {"value": 99, "target": 99},
    "OEE": {"value": 40, "target": 45}
}

# 3) Inventory Data
inventory = pd.DataFrame({
    "Component ID": ["ENG001", "SENS002", "VAL003", "ACT004", "CIRC005"],
    "Component Name": [
        "Engine Core", "Pressure Sensor", "Hydraulic Valve",
        "Linear Actuator", "Control Circuit"
    ],
    "Goes Into": [
        "Jet Engine", "Engine Core", "Hydraulic Assembly",
        "Wing Assembly", "Main CPU"
    ],
    "Status": ["Available", "Low", "Critical", "Available", "Low"],
    "Quantity": [120, 15, 5, 140, 18],
    "Location": ["Warehouse A", "Warehouse B", "Assembly", "Warehouse A", "Warehouse C"]
})
inventory["Reorder Threshold"] = 20
inventory["Reorder Required"] = inventory["Quantity"].apply(lambda x: "Yes" if x < 20 else "No")

# 4) Expected Deliveries Data (mocked)
expected_deliveries = pd.DataFrame({
    "Part ID": ["SENS002", "VAL003"],
    "Component Name": ["Pressure Sensor", "Hydraulic Valve"],
    "Expected Delivery": pd.to_datetime(["2025-04-10", "2025-04-12"]),
    "Order Quantity": [50, 30],
    "Supplier": ["Supplier A", "Supplier B"],
    "Status": ["On Order", "Delayed"]
})

# 5) Robotics & Automation Data
robotics_data = pd.DataFrame({
    "Robot ID": ["RB-01", "RB-02", "RB-03"],
    "Task Type": ["Load Materials", "Unload Materials", "Quality Check"],
    "Tasks Completed": [30, 25, 40],
    "Tasks In-Progress": [2, 3, 1],
    "Avg Cycle Time (min)": [3.2, 3.5, 4.0]
})

# 6) RPA Data: Convert each "Last Run" value individually and normalize (set time to 12:00 AM)
last_run_values = [pd.to_datetime(x).normalize() for x in ["2025-04-05 10:00", "2025-04-05 06:00", "2025-04-05"]]
rpa_data = pd.DataFrame({
    "RPA Task": [
        "Inventory Sync",
        "Scheduling",
        "Quality Report Generation"
    ],
    "Frequency": ["Hourly", "Every 6 Hours", "Daily"],
    "Last Run": last_run_values,
    "Status": ["Success", "Success", "Success"]
})
if shift == "Shift 2":
    rpa_data["Last Run"] = rpa_data["Last Run"] - pd.Timedelta(days=1)
elif shift == "Shift 3":
    rpa_data["Last Run"] = rpa_data["Last Run"] - pd.Timedelta(days=2)

# Additional realistic data: Production load distribution (scaled down)
production_load = pd.DataFrame({
    "Department": ["Assembly", "Manufacturing", "Packaging", "Shipping"],
    "Load": [40, 30, 20, 10]  # percentages
})

# --------------------------------------------------
# MULTI-PAGE NAVIGATION
# --------------------------------------------------
pages = ["🏠 Overview", "📦 Inventory Detail", "🛒 Ordering & Deliveries", "🤖 Robotics & Automation", "📝 Parts Transactions"]
selected_page = st.sidebar.radio("Navigate", pages)

# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------
if selected_page == "🏠 Overview":
    st.title("Honeywell Aerospace - Overview")
    st.markdown(
        f"**Filters:** Date: {selected_date_str} | Shift: {shift} | Company: {company} | Work Center: {work_center}"
    )
    st.markdown("### Production Goals")
    if goal_period in production_goals:
        goal_info = production_goals[goal_period]
        delta = goal_info["actual"] - goal_info["goal"]
        st.metric(label=f"{goal_period} Goal", value=f"{goal_info['actual']}", delta=f"{delta}")
    else:
        st.write("No goal information available.")
    st.markdown("---")
    st.subheader("Overall Equipment Effectiveness (OEE)")
    oee_cols = st.columns(4)
    for col, metric_name in zip(oee_cols, oee_metrics.keys()):
        value = oee_metrics[metric_name]["value"]
        target = oee_metrics[metric_name]["target"]
        delta_val = value - target
        col.metric(label=metric_name, value=f"{value}%", delta=f"{delta_val}%")
    st.markdown("---")
    st.subheader("Production Load Distribution")
    fig_load = px.pie(production_load, names="Department", values="Load",
                      title="Production Load Distribution",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_load, use_container_width=True)

# --------------------------------------------------
# PAGE 2: INVENTORY DETAIL
# --------------------------------------------------
elif selected_page == "📦 Inventory Detail":
    st.title("Inventory Detail")
    st.markdown(
        f"**Current Filters:** Company: {company}, Work Center: {work_center}, Date: {selected_date_str}"
    )
    fig_inventory = px.bar(
        inventory,
        x="Component Name",
        y="Quantity",
        color="Status",
        text="Quantity",
        title="Inventory Levels by Component",
        height=500
    )
    fig_inventory.update_layout(font=dict(size=14))
    st.plotly_chart(fig_inventory, use_container_width=True)
    inv_distribution = inventory.groupby("Status")["Quantity"].sum().reset_index()
    fig_inv_pie = px.pie(inv_distribution, names="Status", values="Quantity",
                         title="Inventory Distribution by Status",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_inv_pie, use_container_width=True)
    st.subheader("Detailed Component Table")
    st.dataframe(
        inventory[["Component ID", "Component Name", "Goes Into", "Status", 
                   "Quantity", "Reorder Required", "Location"]],
        height=400
    )

# --------------------------------------------------
# PAGE 3: ORDERING & DELIVERIES
# --------------------------------------------------
elif selected_page == "🛒 Ordering & Deliveries":
    st.title("Ordering & Deliveries")
    st.markdown("### Reorder Alerts & Orders")
    reorder_items = inventory[inventory["Reorder Required"] == "Yes"]
    if not reorder_items.empty:
        st.subheader("Reorder Alerts")
        st.dataframe(
            reorder_items[["Component ID", "Component Name", "Quantity", "Reorder Threshold"]],
            height=300
        )
    else:
        st.info("No components below reorder threshold at the moment.")
    st.markdown("---")
    st.subheader("Expected Deliveries")
    st.dataframe(expected_deliveries, height=300)
    st.markdown("#### Place a New Order")
    with st.form("order_form"):
        order_part = st.selectbox("Select Component", inventory["Component Name"])
        order_qty = st.number_input("Order Quantity", min_value=1, step=1)
        supplier = st.text_input("Supplier Name")
        submit_order = st.form_submit_button("Submit Order")
        if submit_order:
            st.success(f"Order placed for {order_qty} units of {order_part} from {supplier}!")

# --------------------------------------------------
# PAGE 4: ROBOTICS & AUTOMATION
# --------------------------------------------------
elif selected_page == "🤖 Robotics & Automation":
    st.title("Robotics & Automation")
    st.markdown("""
    **Integrating Robotics:**  
    Automated material handling and RPA enhance precision and efficiency in the factory.  
    - **Automated Material Handling (AMH):** Robots manage loading/unloading, reducing cycle times.  
    - **RPA:** Automates routine tasks like inventory sync, scheduling, and quality reporting.
    """)
    st.subheader("Automated Material Handling (AMH)")
    colR1, colR2 = st.columns([2, 1])
    with colR1:
        fig_robot = px.bar(
            robotics_data,
            x="Robot ID",
            y=["Tasks Completed", "Tasks In-Progress"],
            title="Robot Task Summary",
            barmode="group",
            height=400
        )
        fig_robot.update_layout(font=dict(size=14))
        st.plotly_chart(fig_robot, use_container_width=True)
    with colR2:
        st.dataframe(robotics_data, height=400)
    st.markdown("---")
    st.subheader("Robotic Process Automation (RPA) Tasks")
    st.dataframe(rpa_data, height=200)
    st.markdown("""
    > **Note:** In a real production environment, these data points are automatically updated from 
    the factory’s IoT and RPA systems to optimize operations.
    """)

# --------------------------------------------------
# PAGE 5: PARTS TRANSACTIONS
# --------------------------------------------------
elif selected_page == "📝 Parts Transactions":
    st.title("Parts Transactions")
    st.markdown("This page shows check‑in and check‑out events for each part with unique hash identification.")
    
    parts = []
    with open("parts.log", "r") as logfile:
        for line in logfile:
            if not line.strip():
                continue
            if not line.startswith("\t"):
                fields = [f.strip() for f in line.split(",")]
                current_part = {
                    "Unique Hash": fields[0],
                    "Part ID": fields[1],
                    "Part Name": fields[2],
                    "Quantity": fields[3],
                    "Supplier": fields[4],
                    "Events": []
                }
                parts.append(current_part)
            else:
                event_line = line.strip()
                ts, ev, op = event_line.split(" : ")
                current_part["Events"].append({"Timestamp": ts, "Event": ev, "Operator": op})
    
    # Build a summary of transactions per part
    summary_data = []
    for part in parts:
        check_ins = sum(1 for e in part["Events"] if e["Event"] == "IN")
        check_outs = sum(1 for e in part["Events"] if e["Event"] == "OUT")
        summary_data.append({
            "Unique Hash": part["Unique Hash"],
            "Part ID": part["Part ID"],
            "Part Name": part["Part Name"],
            "Supplier": part["Supplier"],
            "Quantity": part["Quantity"],
            "Check‑Ins": check_ins,
            "Check‑Outs": check_outs
        })
    df_parts = pd.DataFrame(summary_data)
    
    st.subheader("Parts Transaction Summary")
    st.dataframe(df_parts)
    
    st.subheader("Check‑In vs Check‑Out by Part")
    fig_parts = px.bar(df_parts, x="Part Name", y=["Check‑Ins", "Check‑Outs"],
                       barmode="group", title="Check‑In vs Check‑Out Counts")
    st.plotly_chart(fig_parts, use_container_width=True)
    
    st.subheader("Overall Check‑In vs Check‑Out Distribution")
    overall = {"Check‑Ins": df_parts["Check‑Ins"].sum(), "Check‑Outs": df_parts["Check‑Outs"].sum()}
    df_overall = pd.DataFrame(list(overall.items()), columns=["Transaction", "Count"])
    fig_overall = px.pie(df_overall, names="Transaction", values="Count",
                         title="Overall Check‑In vs Check‑Out Distribution",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_overall, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("###### Built for Honeywell Aerospace | Internal Use Only")

