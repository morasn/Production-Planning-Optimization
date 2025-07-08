# Production Planning Optimization

## Table of Contents

- [Overview](#overview)
- [Importance in Production Planning](#importance-in-production-planning)
- [Features](#features)
- [Mathematical Model](#mathematical-model)
- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Contributing](#contributing)

## Overview

The **Production Optimizer** is a web-based application designed to optimize production scheduling in manufacturing environments using Integer Linear Programming (ILP). Built with Python, Streamlit, PuLP, and Pandas, this tool helps production engineers maximize profits by determining the optimal production schedule while considering machine availability, product demands, and production constraints. The application provides a user-friendly interface for inputting parameters and visualizing results, making it an invaluable tool for efficient production planning.

This project addresses the complex challenge of scheduling production across multiple machines and products, accounting for factors such as batch sizes, setup times, production rates, maintenance costs, and demand penalties. By leveraging ILP, it ensures optimal resource allocation, minimizing costs and unmet demand while maximizing profitability.

## Importance in Production Planning

In manufacturing, efficient production planning is critical to reducing costs, meeting demand, and optimizing resource utilization. The Production Optimizer addresses these needs by:

- **Maximizing Profitability**: Balances production output with costs (maintenance and penalties for unmet demand) to achieve the highest possible profit.
- **Optimizing Resource Utilization**: Ensures machines are used efficiently within their available hours, reducing idle time and overutilization.
- **Handling Complex Constraints**: Accounts for real-world constraints such as batch size limits, setup times, and machine-specific production rates.
- **Scalability and Modularity**: Supports any number of products and machines, making it adaptable to various manufacturing scenarios.
- **User-Friendly Interface**: Simplifies data input and result interpretation through an intuitive Streamlit interface, reducing the learning curve for production engineers.
- **Scenario Analysis**: Allows users to test different scenarios (e.g., machine downtime or increased demand), enabling proactive decision-making.

This tool is particularly valuable in industries where production schedules are complex, resources are limited, and demand fluctuates, such as electronics, automotive, or consumer goods manufacturing.

## Features

1. **Input Flexibility**:
   - Users can define any number of products and machines via comma-separated inputs.
   - Supports customizable parameters for products (profit, setup time, min/max batch sizes, demand, penalty costs) and machines (available hours, maintenance costs).
   - Allows specification of machine-specific production rates for each product.

2. **Optimization Model**:
   - Utilizes PuLP to formulate and solve an ILP model that maximizes profit.
   - Decision variables include the number of batches per product, machine, and batch type (min/max), and binary variables for machine assignment.
   - Accounts for unmet demand with associated penalty costs.
   - Constraints ensure realistic scheduling (e.g., one product per machine per day, adherence to available hours, batch size limits).

3. **Interactive User Interface**:
   - Built with Streamlit for a clean, responsive web interface.
   - Features dynamic data tables for inputting product and machine parameters.
   - Displays results in a clear, organized format, including production schedules, machine utilization, and total profit.

4. **Comprehensive Results**:
   - Outputs the optimization status (e.g., Optimal, Infeasible).
   - Provides detailed production summaries, including batch assignments, units produced, and unmet demand.
   - Shows machine utilization metrics (hours used vs. available and percentage utilization).

5. **Scenario Testing**:
   - Supports what-if analysis, such as simulating machine downtime (e.g., setting Machine Y's available hours to 0) or changes in product demand (e.g., tripling demand for Product B).
   - Demonstrates robustness by handling varied inputs and constraints.

6. **Modular Backend**:
   - Separates optimization logic (`Backend.py`) from the frontend (`app.py`) for maintainability and scalability.
   - Easily extensible for additional constraints or objective function modifications.

## Mathematical Model

The Production Optimizer uses an Integer Linear Programming (ILP) model to maximize profit. Below are the key components of the mathematical formulation, implemented in `Backend.py`.

### Decision Variables

- $x_{p,m,b}$: Number of batches of product $p$ on machine $m$ with batch type $b$ (min or max), integer, $\geq 0$.
- $y_{p,m,b}$: Binary variable, 1 if product $p$ is assigned to machine $m$ with batch type $b$, 0 otherwise.
- $u_p$: Unmet demand for product $p$, integer, $\geq 0$.

### Objective Function

Maximize total profit, accounting for revenue, penalty costs for unmet demand, and maintenance costs:

$\max Z = \sum_{p \in P} \left[ \text{Profit}_p \cdot \sum_{m \in M} \sum_{b \in B} x_{p,m,b} \cdot \text{BatchSize}_{p,b} - \text{Penalty}_p \cdot u_p \right] - \sum_{m \in M} \sum_{p \in P} \sum_{b \in B} \text{Maintenance}_m \cdot y_{p,m,b}$

Where:
- $P$: Set of products.
- $M$: Set of machines.
- $B$: Set of batch types (min, max).
- $\text{Profit}_p$: Profit per unit of product $p$.
- $\text{BatchSize}_{p,b}$: Batch size for product $p$ and batch type $b$.
- $\text{Penalty}_p$: Penalty cost per unmet unit of product $p$.
- $\text{Maintenance}_m$: Maintenance cost for machine $m$.

### Constraints

1. **Machine Assignment**:
   Each machine can produce at most one product per day:
   $\sum_{p \in P} \sum_{b \in B} y_{p,m,b} \leq 1 \quad \forall m \in M$

2. **Machine Time**:
   Total time (production + setup) on each machine must not exceed available hours:
   $\sum_{p \in P} \sum_{b \in B} \left( \frac{x_{p,m,b} \cdot \text{BatchSize}_{p,b}}{\text{Rate}_{p,m}} + \text{SetupTime}_p \cdot y_{p,m,b} \right) \leq \text{AvailableHours}_m \quad \forall m \in M$

3. **Batch Type Exclusivity**:
   For each product-machine pair, at most one batch type (min or max) can be used:
   $y_{p,m,\text{min}} + y_{p,m,\text{max}} \leq 1 \quad \forall (p,m) \in \text{Rates}$

4. **Batch Activation**:
   Batches are only produced if the corresponding $y$ variable is 1:
   $x_{p,m,b} \leq 50000 \cdot y_{p,m,b} \quad \forall p \in P, m \in M, b \in B$

5. **Demand Satisfaction**:
   Production plus unmet demand equals total demand:
   $\sum_{m \in M} \sum_{b \in B} x_{p,m,b} \cdot \text{BatchSize}_{p,b} + u_p = \text{Demand}_p \quad \forall p \in P$

## Prerequisites

To run the Production Optimizer, ensure you have the following installed:

- **Python**: Version 3.8 or higher.
- **Required Libraries**:
  - `streamlit`: For the web interface.
  - `pulp`: For solving the ILP model.
  - `pandas`: For data handling and table inputs.
- Install dependencies using:
  ```bash
  pip install streamlit pulp pandas
  ```

## How to Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/production-optimizer.git
   cd production-optimizer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   This will launch the web interface in your default browser.

4. **Using the Application**:
   - **Step 1: Define Machines and Products**:
     - Enter comma-separated names for machines (e.g., `W, X, Y, Z`) and products (e.g., `A, B, C`).
   - **Step 2: Enter Product Parameters**:
     - Input parameters like profit per unit, setup time, min/max batch sizes, demand, and penalty costs in the provided table.
   - **Step 3: Define Machine Parameters**:
     - Specify available hours and maintenance costs for each machine.
   - **Step 4: Define Production Rates**:
     - Enter production rates (units/hour) for each product-machine combination.
   - **Step 5: Optimize**:
     - Click the "Optimize Production" button to run the ILP model.
   - **View Results**:
     - Review the optimization status, total profit, production summary, unmet demand, and machine utilization.

## Example Usage

### Scenario 1: Normal Operations
- **Input**:
  - Machines: `W, X, Y, Z`
  - Products: `A, B, C`
  - Product Parameters (example):
    - Product A: Profit $100, Setup 30 min, Min Batch 5, Max Batch 20, Demand 150, Penalty $50
    - Product B: Profit $80, Setup 20 min, Min Batch 8, Max Batch 30, Demand 330, Penalty $40
    - Product C: Profit $120, Setup 25 min, Min Batch 4, Max Batch 15, Demand 150, Penalty $60
  - Machine Parameters:
    - Machine W: 8 hours, $100 maintenance
    - Machine X: 12 hours, $150 maintenance
    - Machine Y: 10 hours, $120 maintenance
    - Machine Z: 9 hours, $110 maintenance
  - Production Rates: Vary by product-machine combination.
- **Output**:
  - Status: Optimal
  - Total Profit: $43,820
  - Production Summary: Details batches and units produced (e.g., Product A on Machine W: 15 min batches, 75 units).
  - Unmet Demand: Lists any shortfall (e.g., 75 units unmet for Product A).
  - Machine Utilization: Shows hours used and percentage (e.g., Machine W: 7.75 hours, 96.88%).

### Scenario 2: Machine Y Breakdown
- **Input Change**: Set Machine Y's available hours to 0.
- **Output**:
  - Total Profit: $38,260
  - Production shifts to other machines (e.g., Product C only on Machine Z).
  - Machine Y: 0 hours used.

### Scenario 3: Tripled Demand for Product B
- **Input Change**: Increase Product B's demand to 990 units.
- **Output**: Adjusts batch assignments to meet new demand, with potential increases in unmet demand if constrained by machine hours.

## Project Structure

- `app.py`: Frontend Streamlit application for user interface and interaction.
- `Backend.py`: Contains the ILP model solver and result calculations.
- `requirements.txt`: Lists required Python libraries.

## Future Enhancements

- **Data Persistence**: Add support for saving and loading input configurations.
- **Advanced Constraints**: Incorporate additional constraints like labor availability or storage limits.
- **Visualization**: Include graphical outputs (e.g., Gantt charts) for production schedules.
- **API Integration**: Enable integration with external systems for real-time data input.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bug fixes.