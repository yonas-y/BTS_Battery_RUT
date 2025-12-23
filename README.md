# ⚡ Battery Remaining Usable Time (RUT) Estimation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&style=flat-square)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

This repository implements a **data-driven and model-based approach** to estimate the **Remaining Usable Time (RUT)** of BTS (Base Transceiver Station) battery banks. The approach combines **battery modeling, load forecasting, and uncertainty quantification** to provide actionable insights for predictive maintenance and energy management.

---

## 🎯 Project Objective

The goal of this project is to **automate the estimation of battery life before energy depletion**, under varying load currents and uncertain operating conditions.  

Key outcomes include:

- Predicting **battery voltage progression** until it reaches a critical cut-off voltage.  
- Estimating the **time until service interruption** (RUT).  
- Accounting for **uncertainty** in both battery behavior and load forecasts by providing **prediction intervals**.  
- Supporting proactive **maintenance planning** and **energy management**.

---

## ⚙️ Methodology

### 1. Battery Modeling

The battery voltage is modeled using a **modified Shepherd equation**, which captures the electrochemical behavior of the battery in terms of:

- Terminal voltage and open-circuit voltage  
- Internal resistance  
- Discharge current and state of charge (SoC)

The voltage prediction formula is:

```math
\hat{v}_{\text{batt}}(t) = V_0 - K \frac{Q_{B}}{Q_{B} - \int_0^t i_{\text{batt}}(t) dt} i_{\text{batt}}(t)
- R_i i_{\text{batt}}(t) + A e^{-B \int_0^t i_{\text{batt}}(t) dt}
```
Where:
- V0: Open-circuit voltage at full charge (V)
- K: Polarization constant (V/Ah)
- QB: Maximum battery capacity (Ah)
- i_batt(t): Battery current (A)
- Ri: Internal resistance (Ω)
- A, B: Exponential zone amplitude and capacity

For benchmarking, a **feedforward neural network (FNN)** is also evaluated for voltage prediction.

### 2. Load Forecasting
- Observes **daily cyclic load patterns** from a pool of users (e.g., mobile network subscribers).
- Forecasting is performed using **SARIMAX** (Seasonal ARIMA with Exogenous Regressors).
- **LSTM** models are also evaluated for comparison.

### 3. RUT Estimation
- RUT is defined as the time until battery voltage reaches the cut-off level:
- 
  ```math
  RUT = t_e - t_0
  ```
  
- Where `t0` is the current time and `te` is the time at cut-off voltage.
- The method **quantifies uncertainty via prediction intervals** (lower and upper bounds).
- This allows operators to plan maintenance **before service interruption occurs**, accounting for variability in load and battery behavior.

---

## 🧰 Tools & Frameworks
- **Python Libraries:** NumPy, SciPy, Pandas, statsmodels, scikit-learn, TensorFlow
- **Forecasting Models:** SARIMAX, LSTM 
- **Battery Models:** Modified Shepherd equation, FNN
- **Visualization:** Matplotlib, Seaborn
- **MLOps:** ZenML  

---

## 🚀 Usage
- Prepare battery capacity and load data.
- Configure model parameters in `config.py`.
- Run the main script to estimate **RUT** and generate **prediction intervals**:
  ```bash
  python main.py
  ```
- Visualize battery voltage progression and RUT uncertainty using the provided plotting functions.

---

## 📈 Key Benefits

- **Proactive maintenance**: Avoid unexpected BTS downtime.
- **Quantified uncertainty**: Provides prediction intervals instead of single deterministic values.Health indicator generation for RUL estimation.
- **Flexible modeling**: Supports different battery models and load forecasting methods.
- **Scalable**: Can be extended to larger energy storage systems.

---
## 📜 Citation

If you use this work, please cite:

```bibtex
  @article{ieee2025rut,
  title   = {Estimation of Remaining Usable Time with Uncertainty Quantification of Batteries: A Study on a Base Transceiver Station Application Using Real-Life Data.},
  author  = {Yonas Tefera, Stijn Luca, Dereje H. Woldegebreal and Peter Karsmakers},
  journal = {IEEE Access},
  volume  = {13},
  year    = {2025}
}
```

---  

## 📬 Contact & Collaboration
📧 Email: [yonas.yehualaeshet@gmail.com](mailto:yonas.yehualaeshet@gmail.com)
🐛 Issues: Open an issue in this repository

