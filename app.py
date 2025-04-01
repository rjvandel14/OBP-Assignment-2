import streamlit as st
import matplotlib.pyplot as plt

# --- Sidebar input ---
st.sidebar.header("System Parameters")
failure_rate = st.sidebar.number_input("Machine failure rate (mu)", min_value=0.0, value=0.1, step=0.01)
repair_rate = st.sidebar.number_input("Repair rate (gamma)", min_value=0.0, value=1.0, step=0.1)
warm_standby_option = st.sidebar.selectbox("Warm standby (failures in unused components)?", ["Yes", "No"])
warm_standby = (warm_standby_option == "Yes")
n = st.sidebar.number_input("Total number of components (n)", min_value=1, value=5, step=1)
k = st.sidebar.number_input("Required to work (k)", min_value=1, value=3, step=1)
r = st.sidebar.number_input("Number of repairmen", min_value=1, value=1, step=1)

# --- Main content ---
st.title("k-out-of-n Maintenance System")
st.write("This app calculates the fraction of time the system is operational using a Markov model and steady-state probabilities.")

# --- Uptime Calculation Function ---
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

# --- Results ---
if n >= k:
    uptime = compute_uptime_fraction(int(n), int(k), int(r), failure_rate, repair_rate, warm_standby)
    
    st.subheader("Results")
    st.write(f"Fraction of time system is UP: {uptime:.4f}")
else:
    st.warning("Make sure that n ≥ k so the system is feasible.")

# --- Birth-Death Diagram ---
def draw_birth_death_graph(n, k, r, warm_standby):
    fig, ax = plt.subplots(figsize=(1.6 * n, 2))

    for i in range(n + 1):
        ax.plot(i, 0, 'o', markersize=30, color='lightblue')
        ax.text(i, 0, str(i), ha='center', va='center', fontsize=12)

    # Failure arrows (mu): i → i+1 (right)
    for i in range(n):
        if warm_standby:
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

    # Repair arrows (γ): i → i-1 (left)
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
    title = "Birth-Death Process Diagram (Warm Standby)" if warm_standby else "Birth-Death Process Diagram (Cold Standby)"
    ax.set_title(title, fontsize=14)

    st.pyplot(fig)

st.subheader("Birth-Death Process Diagram")
draw_birth_death_graph(n, k, failure_rate, repair_rate, r, warm_standby)

# --- Legend ---
st.markdown("""
**Explanation of states:**

- Each state represents the number of broken components.
- State `0` means all components are **working**.
- State `n` means all components have **failed**.
- Arrows at the top are giving the rate of machine failure (mu).
- Arrow at the bottom are giving the rate of machine repair (gamma).
""")
