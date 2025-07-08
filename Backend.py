import pulp
import pandas as pd

def Model_Solver(machines, products, demand, batch_types, batch_sizes, setup_time, profit, penalty_cost, rates, maintenance_cost, available_hours):
    """Optimize the production schedule using linear programming.
    arguments:
        machines: List of machine names.
        products: List of product names.
        demand: Dictionary mapping products to their demand.
        batch_types: List of batch types (e.g., "min", "max").
        batch_sizes: Dictionary mapping (product, batch_type) to batch size.
        setup_time: Dictionary mapping products to setup time in hours.
        profit: Dictionary mapping products to profit per unit.
        penalty_cost: Dictionary mapping products to penalty cost per unmet unit.
        rates: Dictionary mapping (product, machine) to production rate (units per hour).
        maintenance_cost: Dictionary mapping machines to their maintenance cost.
        available_hours: Dictionary mapping machines to their available hours per day.
    Returns:
    
    """

    model = pulp.LpProblem("Optimal_Production_Schedule", pulp.LpMaximize)
    # Decision variables
    x = pulp.LpVariable.dicts(
        "Num_Of_Batches",
        [(p, m, b) for p in products for m in machines for b in batch_types],
        lowBound=0,
        cat="Integer",
    )
    y = pulp.LpVariable.dicts(
        "Min_Max_Assign",
        [(p, m, b) for p in products for m in machines for b in batch_types],
        cat="Binary",
    )

    # Create unmet demand variables (non-negative)
    unmet = pulp.LpVariable.dicts(
        "Unmet_Demand", products, lowBound=0, cat="Integer"
    )

    # Objective function: Maximize profit - maintenance costs
    model += (
        pulp.lpSum(
            [
                profit[p]
                * pulp.lpSum(
                    [
                        x[(p, m, b)] * batch_sizes[(p, b)]
                        for m in machines
                        for b in batch_types
                        if (p, m) in rates
                    ]
                )
                - penalty_cost[p] * unmet[p]
                for p in products
            ]
        )
        - pulp.lpSum(
            [
                maintenance_cost[m] * y[(p, m, b)]
                for p in products
                for m in machines
                for b in batch_types
                if (p, m) in rates
            ]
        ),
        "Objective_Function",
    )

    # Constraints

    for m in machines:
        # Each machine produces only one product per day
        model += (
            pulp.lpSum(
                [
                    y[(p, m, b)]
                    for p in products
                    for b in batch_types
                    if (p, m) in rates
                ]
            )
            <= 1
        )

        # Machine time constraints (production + setup)
        model += (
            pulp.lpSum(
                [
                    (
                        x[(p, m, b)] * batch_sizes[(p, b)] / rates[(p, m)]
                        + setup_time[p] * y[(p, m, b)]
                    )
                    for p in products
                    for b in batch_types
                    if (p, m) in rates
                ]
            )
            <= available_hours[m]
        )

    # Batch constraints: only one machine per product per batch type
    for p, m in rates:
        model += y[(p, m, "min")] + y[(p, m, "max")] <= 1
        for b in batch_types:
            model += x[(p, m, b)] <= 50000 * y[(p, m, b)]

    # Demand constraints to ensure production meets demand and does not exceed it
    for p in products:

        model += (
            pulp.lpSum(
                [
                    x[(p, m, b)] * batch_sizes[(p, b)]
                    for m in machines
                    for b in batch_types
                    if (p, m) in rates
                ]
            )
            + unmet[p]
            == demand[p],
            f"Meet_Demand_{p}",
        )

    model.solve()
    Status = pulp.LpStatus[model.status]
    Model_Objective = pulp.value(model.objective)
    return  x, y, unmet, Status, Model_Objective


def Results_Calculating(x, y, unmet, products, machines, rates, batch_types, batch_sizes, setup_time, demand, available_hours):
    
    ## Production totals
    Prod_Totals_Msg = []
    Prod = {p: 0 for p in products}  # Initialize production totals
    for p, m in rates:
        for b in batch_types:
            if x[(p, m, b)].varValue > 0:
                Prod_Totals_Msg.append(
                    f"Product {p} on Machine {m} with {b} Batch Size of {batch_sizes[(p, b)]} → Number of Batches: {x[(p, m, b)].varValue} → Number of Units: {x[(p, m, b)].varValue * batch_sizes[(p, b)]}"
                )
                Prod[p] += x[(p, m, b)].varValue * batch_sizes[(p, b)]
    
    ## Production Summary Messages
    Unmet_Summary = []
    for p in products:
        if unmet[p].varValue > 0:
            Unmet_Summary.append(f"Unmet Demand for {p}: {unmet[p].varValue} units, with total of {Prod[p]} out of {demand[p]}.")
        else:
            Unmet_Summary.append(f"All demand for {p} met, with total of {Prod[p]}.")
    
    ## Machine Utilization and Total Hours
    Machine_Hours = []
    Mnachine_Utilization = []
    for m in machines:
        total_hours = 0
        
        for p, m2 in rates:
            if m2 == m:
                for b in batch_types:
                    if y[(p, m, b)].varValue == 1:
                        total_hours += (
                            x[(p, m, b)].varValue
                            * batch_sizes[(p, b)]
                            / rates[(p, m)]
                            + setup_time[p]
                        )

        Utilization = total_hours / available_hours[m] * 100
        Machine_Hours.append(f"Machine {m}: {total_hours:.2f} hours out of {available_hours[m]} hours available")
        Mnachine_Utilization.append(f"Machine Utilization: {Utilization:.2f}%")

    return Prod_Totals_Msg, Unmet_Summary, Machine_Hours, Mnachine_Utilization 