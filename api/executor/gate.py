"""The autonomous / manual switch. Owner: Person A.

This is the entire difference between the two modes:

    if auto_enabled and plan.fare <= threshold and not plan.violations:
        executor.run(plan)           # autonomous
    else:
        approvals.request(plan)      # manual

Build the manual path first. This is a 30-minute addition at hour 12.
"""
raise NotImplementedError("A9")
