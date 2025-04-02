import streamlit as st
import matplotlib.pyplot as plt

# Sidebar
st.sidebar.header("System Parameters")
failure_rate = st.sidebar.number_input("Machine failure rate (mu)", min_value=0.0, value=0.1, step=0.01)
repair_rate = st.sidebar.number_input("Repair rate (gamma)", min_value=0.0, value=1.0, step=0.1)
warm_standby_option = st.sidebar.selectbox("Warm standby (failures in unused components)?", ["Yes", "No"])
warm_standby = (warm_standby_option == "Yes")
n = st.sidebar.number_input("Total number of components (n)", min_value=1, value=5, step=1)
k = st.sidebar.number_input("Required to work (k)", min_value=1, value=3, step=1)
r = st.sidebar.number_input("Number of repairmen", min_value=1, value=1, step=1)

# Sidebar for exercise b
st.sidebar.header("Cost Parameters")
component_cost = st.sidebar.number_input("Cost per component", min_value=0.0, value=1.0, step=0.1)
repairman_cost = st.sidebar.number_input("Cost per repairman", min_value=0.0, value=5.0, step=0.1)
downtime_cost = st.sidebar.number_input("Cost per unit downtime", min_value=0.0, value=100.0, step=1.0)

# Titles 
st.title("k-out-of-n Maintenance System")
st.write("This app calculates the fraction of time the system is operational using a Markov model and steady-state probabilities.")

# Uptime calculation
def compute_uptime_fraction(n, k, r, failure_rate, repair_rate, warm_standby=True):
    failure_rates = []
    for i in range(n):
        if warm_standby:
            failure = (n - i) * failure_rate
        else:
            if i <= n - k:
                failure = k * failure_rate
            else:
                failure = 0
        failure_rates.append(failure)

    repair_rates = [min(i, r) * repair_rate for i in range(1, n + 1)]


    product_terms = [1.0]
    for i in range(1, n + 1):
        if repair_rates[i - 1] > 0:
            ratio = failure_rates[i - 1] / repair_rates[i - 1]
        else:
            ratio = 0
        product_terms.append(product_terms[-1] * ratio) # We multiply with last element in list

    denominator = sum(product_terms)
    pi_0 = 1 / denominator
    pi = [pi_0 * term for term in product_terms]

    max_failures_allowed = n - k
    uptime_fraction = sum(pi[i] for i in range(max_failures_allowed + 1))

    return uptime_fraction

# Results
if n >= k:
    uptime = compute_uptime_fraction(int(n), int(k), int(r), failure_rate, repair_rate, warm_standby)
    
    st.subheader("Results")
    st.write(f"Fraction of time system is up: {uptime:.4f}")
else:
    st.warning("Make sure that n ≥ k so the system is feasible.")

# Birth death process
def draw_birth_death_graph(n, k, r, warm_standby):
    fig, ax = plt.subplots(figsize=(1.6 * n, 2))

    for i in range(n + 1):
        ax.plot(i, 0, 'o', markersize=30, color='lightblue')
        ax.text(i, 0, str(i), ha='center', va='center', fontsize=12)

    # failure mu: i to i+1 
    for i in range(n):
        if warm_standby: # warmstandby
            fail_rate = n - i  # number of working components
        else:
            # cold standby: failures allowed until system is down (i <= k-1)
            fail_rate = k if i <= (k-1) else 0

        if fail_rate > 0:
            arrow_label = f"{fail_rate}μ"
            ax.annotate("",
                        xy=(i + 0.8, 0.15), xytext=(i + 0.2, 0.15), 
                        arrowprops=dict(arrowstyle="->", color="red", lw=2))
            ax.text(i + 0.5, 0.25, arrow_label, ha='center', va='bottom', fontsize=10, color='red')

    # repair gamma: i to i-1
    for i in range(1, n + 1):
        repair= min(r,i)
        arrow_label = f"{repair}γ"
        ax.annotate("",
                    xy=(i - 0.2, -0.15), xytext=(i - 0.8, -0.15), 
                    arrowprops=dict(arrowstyle="<-", color="green", lw=2))
        ax.text(i - 0.5, -0.25, arrow_label, ha='center', va='top', fontsize=10, color='green')

    ax.set_xlim(-0.5, n + 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_axis_off()
    title = "Warm Standby" if warm_standby else "Cold Standby"
    ax.set_title(title, fontsize=14)

    st.pyplot(fig)

st.subheader("Birth-Death Process Diagram")
draw_birth_death_graph(n, k, r, warm_standby)

# Text about results
st.markdown("""
**Explanation of the birth-death process:**

- Each state represents the number of broken components.
- State `0` means all components are **working**.
- State `n` means all components have **failed**.
- Arrows at the top are giving the rate of machine failure (mu).
- Arrows at the bottom are giving the rate of machine repair (gamma).
""")


## Exercise (b)
# Total cost function
def total_cost(n, k, r, failure_rate, repair_rate, warm_standby, component_cost, repairman_cost, downtime_cost):
    uptime = compute_uptime_fraction(n, k, r, failure_rate, repair_rate, warm_standby)
    return (
        n * component_cost +
        r * repairman_cost +
        (1 - uptime) * downtime_cost
    )

# Find best values given the costs
def find_optimal_config(failure_rate, repair_rate, warm_standby, component_cost, repairman_cost, downtime_cost, k):
    best_config = None
    best_cost = float('inf')

    for n_b in range(k, 100): # max amount of components set to 100
        for r_b in range(1, 15): # max amount of repairmen is set to 15 
            cost = total_cost(n_b, k, r_b, failure_rate, repair_rate,
                                warm_standby, component_cost, repairman_cost, downtime_cost)
            if cost < best_cost:
                best_cost = cost
                best_config = (n_b, r_b, cost)

    return best_config

st.subheader("Optimal Configuration (based on cost)")
optimal = find_optimal_config(failure_rate, repair_rate, warm_standby,
                              component_cost, repairman_cost, downtime_cost, int(k))

if optimal:
    opt_n, opt_r, opt_cost = optimal
    st.write(f"Optimal number of components = {opt_n}, number of repairmen = {opt_r}")
    st.write(f"Minimum total expected cost per unit time: **{opt_cost:.2f}**")
