# k-out-of-n Maintenance System (Streamlit App)

This project implements a Streamlit app to analyze and visualize the stationary distribution of a k-out-of-n maintenance system with exponential failure and repair times.

## How to Run the App Locally

### 1. Clone the repository

```bash
git clone https://github.com/rjvandel14/OBP-Assignment-2
cd OBP-Assignment-2
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 3. Launch the Streamlit app

```bash
streamlit run app.py
```

The app will open in your browser.

## Inputs

The app requires the following inputs via the Streamlit interface:

- Failure rate (per component)
- Repair rate (per repairman)
- Number of components (n)
- Number of components required for functioning (k)
- Number of repairmen (r)
- Warm or cold standby setting
- Cost per component, repairman, and downtime

## Output

- The fraction of time the system is up (uptime)
- A birth-death diagram visualizing failure and repair transitions
- The optimal configuration (n, r) that minimizes total cost

## Author

This app was developed by Day Dortmans and Roos van Andel as part of the assignment for the course **Optimization of Business Processes**.
