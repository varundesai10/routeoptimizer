import pandas as pd
import json
from docplex.mp.model import Model
import numpy as np
import sys

#sys.argv[1] -> input_file_name_clients, sys.argv[2] -> input file name for agents sys.argv[3] -> export file name sys.argv[4] -> solving time limit (default 100s)



#data = pd.read_json(sys.argv[1]).to_dict()
#agent_data = pd.read_json(sys.argv[2].to_dict())
print('SAMPLE')
with open(sys.argv[1]) as fp:
	data  = json.load(fp)

with open(sys.argv[2]) as fp:
	agent_data = json.load(fp)

distanceMatrix = data['distances']
#importing the set of customers with their demands
n = len(distanceMatrix)-1 #total_number_of_clients
N = [i for i in range(1, len(distanceMatrix))] #set of all customers
V = [0]+N  #set of all customers+depot
q = {i:data['demands'][i-1] for i in N} #set of demand of all customers.
c = {(i,j):distanceMatrix[i][j] for i in V for j in V if i!=j}

#inporting the set of all deliviry agents
m = len(agent_data['id'])
K = [i for i in range(1, m+1)]
C = {i:agent_data['capacities'][i-1] for i in K}


E = [(i,j,k) for i in V for j in V for k in K if i!=j]

#building optimization model
mdl = Model('CVRP')
x = mdl.binary_var_dict(E, name='x')
Q = mdl.continuous_var_dict([(i,k) for i in N for k in K], name='Q')
y = mdl.binary_var_dict([(i,k) for i in N for k in K], name='y')

mdl.minimize(mdl.sum(c[i,j]*x[i,j,k] for i,j,k in E))
#for indicator contraints
mdl.add_constraints(mdl.sum(x[i,j,k] for j in V if j != i) == y[i,k] for i in N for k in K)
#flow_constraints
mdl.add_constraints(mdl.sum(x[i,j,k] for j in V for k in K if i!=j) == 1 for i in N)
mdl.add_constraints(mdl.sum(x[i,j,k] for i in V for k in K if i!=j) == 1 for j in N)
mdl.add_constraints((mdl.sum(x[i, h, k] for i in V if i!=h) - mdl.sum(x[h, j, k] for j in V if j!=h)) == 0 for h in N for k in K)
mdl.add_constraints(mdl.sum(x[0,j,k] for j in N)==1 for k in K)
mdl.add_constraints(mdl.sum(x[i,0,k] for i in N)==1 for k in K)
#capacity_contraints
'''
mdl.add_indicator_constraints(mdl.indicator_constraint(x[i,j,k], u[i,k]+q[i] == u[j,k]) for i,j,k in E if i!=0 and j!=0)
mdl.add_constraints(u[i,k]>=q[i] for i in N for k in K)
mdl.add_constraints(u[i,k]<=Q[k] for i in N for k in K)
'''
mdl.add_indicator_constraints(mdl.indicator_constraint(y[i,k],Q[i,k]>=q[i]) for i in N for k in K)
mdl.add_indicator_constraints(mdl.indicator_constraint(y[i,k], Q[i,k]-q[i] <= C[k]) for i in N for k in K)

#definitional constraints
mdl.add_indicator_constraints(mdl.indicator_constraint(x[i,j,k], Q[j,k] == Q[i,k]-q[i]) for i in N for j in N for k in K if i!=j)
mdl.add_indicator_constraints(mdl.indicator_constraint(x[0,j,k], Q[j,k] == C[k]) for j in N for k in K)

mdl.parameters.timelimit = 100
if(sys.argv[4] != None):
	mdl.parameters.timelimit = float(sys.argv[4])

solution = mdl.solve(log_output = True)
if(solution == None):
	print('Model unsolvable. Try increasing capacities of vehicles or decreasing demands of clients')
	exit()
print(solution)
print(solution.solve_status)

if(solution == None):
	print('Model unsolvable. Try increasing capacities of vehicles or decreasing demands of clients')

#now making different graphs out of the solution set.
active_arcs = [(i,j,k) for (i,j,k) in E if x[i,j,k].solution_value > 0.9]
routes = {k:[0] for k in K}
for k in K:
	i = 0
	while(True):
		for j in V:
			if (i,j,k) in active_arcs:
				routes[k].append(j)
				i = j
				break
		if (i==0):
			break
#now replacing the indexed locations by the actual locations!
final_routes = {}
final_routes['routes'] = [[data['coords'][i] for i in routes[k]] for k in K]
final_routes['id'] = agent_data['id']

with open('{}.json'.format(sys.argv[3].split('.')[0]), 'w') as fp:
	json.dump(final_routes, fp)
	print('file saved')
'''
toBeSaved = pd.DataFrame.from_dict(final_routes)
toBeSaved.to_json(r'{}.{}'.format(sys.argv[3].split('.')[0], 'json'))
toBeSaved.to_csv(r'{}.{}'.format(sys.argv[3].split('.')[0], 'csv'))
'''
