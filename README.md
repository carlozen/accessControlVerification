# Access Control Verification

#### Carlo Zen 864429


A simple ARBAC analyser for small policies. The program parses the specification of a role reachability problem and returns its solution.

## Implementation
The first part of the code is about the rewriting of the policies (read from the file) in lists or dictionaries.

Then in order to simplify the instances of the role reachability problem, some roles and users are removed by applying the backward slicing.

Once the useless roles are removed, the main structure of the role reachability problem is implemented by the `is_reachable` function. It's a recursive function that takes in input the user to role assignment to test and a list of configurations already tested. 

The behavior of the function can be summarized as follows:
1. base case: if the goal is in the role to users assignment data structure it means that at least one user has the target role, return 1
2. can assign role: for each role which can be assigned, try to assign that role and, if the current configuration has not already been tested, do the recursive call. If the recursive call returns 1, the goal has been reached, return 1. Otherwise, add the tested configuration to the list and remove the added role from the data structure
3. can revoke role: for each role which can be revoked, try to remove that role and, if the current configuration has not already been tested, do the recursive call. If the recursive call returns 1, the goal has been reached, return 1. Otherwise, add the tested configuration to the list and add the revoked role to the data structure
4. if no value has been returned, it's not possible to reach the goal, return 0

## To run
The code works well with policies: 1, 3, 4, 6, 7.
If tested with policy 2, it reaches the maximum recursion depth.
If tested with policies 5 and 8, after 10 minutes it is still inside the main recursive call.  

To run: `python main.py` (tested with Python 2.7.15+)
