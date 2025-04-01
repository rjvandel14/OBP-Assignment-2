import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

# --- Sidebar input ---
st.sidebar.header("System Parameters")
failure_rate = st.sidebar.number_input("Failure rate (λ)", min_value=0.0, value=0.1, step=0.01)
repair_rate = st.sidebar.number_input("Repair rate (μ)", min_value=0.0, value=1.0, step=0.1)
warm_standby_option = st.sidebar.selectbox("Warm standby (failures in unused components)?", ["Yes", "No"])
warm_standby = (warm_standby_option == "Yes")
n = st.sidebar.number_input("Total number of components (n)", min_value=1, value=5, step=1)
k = st.sidebar.number_input("Required to work (k)", min_value=1, value=3, step=1)
r = st.sidebar.number_input("Number of repairmen", min_value=1, value=1, step=1)

# --- Main content ---
st.title("k-out-of-n Maintenance System")
st.write("This app calculates the **fraction of time** the system is operational based on the stationary distribution of a Markov model.")

# --- Uptime Calculation Function ---
def compute_uptime_fraction(n, k, r, failure_rate, repair_rate, warm_standby=True):
    λ = failure_rate
    μ = repair_rate

    # Step 1: Transition rates
    birth_rates = [(n - i) * λ if warm_standby else max(0, k - i) * λ for i in range(n)]
    death_rates = [min(i, r) * μ for i in range(1, n + 1)]

    # Step 2: Compute steady-state probabilities (Theorem 5.4.3)
    product_terms = [1.0]
    for i in range(1, n + 1):
        if death_rates[i - 1] > 0:
            ratio = birth_rates[i - 1] / death_rates[i - 1]
        else:
            ratio = 0
        product_terms.append(product_terms[-1] * ratio)

    denominator = sum(product_terms)
    π_0 = 1 / denominator
    π = [π_0 * term for term in product_terms]

    # Step 3: Uptime = sum of probabilities in states with ≤ (n - k) failed components
    max_failures_allowed = n - k
    uptime_fraction = sum(π[i] for i in range(max_failures_allowed + 1))

    return uptime_fraction, π

# --- Calculate and show results ---
if n >= k:
    uptime, π = compute_uptime_fraction(int(n), int(k), int(r), failure_rate, repair_rate, warm_standby)
    
    st.subheader("Results")
    st.write(f"**Fraction of time system is UP:** `{uptime:.4f}`")

    # st.bar_chart(π, use_container_width=True)
    # st.caption("Distribution of states (0 = no failures, ... up to n failed components)")

else:
    st.warning("Make sure that n ≥ k so the system is feasible.")


def draw_birth_death_graph(n, k, failure_rate, repair_rate, r, warm_standby):
    import matplotlib.pyplot as plt
    import streamlit as st

    fig, ax = plt.subplots(figsize=(1.6 * n, 2))

    # Draw state nodes
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
        arrow_label = "γ"
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

st.markdown("""
**Explanation of states:**

- Each state represents the number of broken components.
- State `0` means all components are **working**.
- State `n` means all components have **failed**.
- Arrows at the top are giving the rate of machine failure (mu).
- Arrow at the bottom are giving the rate of machine repair (gamma).
""")
