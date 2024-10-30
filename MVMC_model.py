import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import time

n=21

s1="CD"
s2="CGI"
s3="CGE"
s4="CMGI"
s5="CMGE"


N = range(1,n+1)


file= "21_instance.xlsx"

CD_df= pd.read_excel(file, sheet_name=s1, header=None)
CD = CD_df.to_numpy()

CGI_df= pd.read_excel(file, sheet_name=s2, header=None)
CGI = CGI_df.to_numpy()

CGE_df= pd.read_excel(file, sheet_name=s3, header=None)
CGE = CGE_df.to_numpy()

CMGI_df= pd.read_excel(file, sheet_name=s4, header=None)
CMGI = CMGI_df.to_numpy()

CMGE_df= pd.read_excel(file, sheet_name=s5, header=None)
CMGE = CMGE_df.to_numpy()

Pop_df= pd.read_excel(file, sheet_name="Pop", header=None)
Population = Pop_df.to_numpy()

model=gp.Model('MVMC')

x=model.addVars(N, vtype=GRB.BINARY,name="x")
s=model.addVars(N, vtype=GRB.BINARY,name="s")
f=model.addVars(N,N, lb=0, vtype=GRB.CONTINUOUS,name="f")
u=model.addVars(N,N, vtype=GRB.BINARY,name="u")
v=model.addVars(N, vtype=GRB.BINARY,name="v")
q=model.addVars(N, lb=0, vtype=GRB.CONTINUOUS,name="q")

m=model.addVars(N, vtype=GRB.BINARY,name="m")
p=model.addVars(N,N, vtype=GRB.BINARY,name="p")


print("Variables created")


model.modelSense=GRB.MINIMIZE

model.setObjective(sum(s[i]*CD[i-1] for i in N)+sum(x[i]*CGI[i-1] for i in N)+sum(u[i,j]*CGE[i-1][j-1] for i in N for j in N)+ sum(m[i]*CMGI[i-1]*1 for i in N)+sum(p[i,j]*CMGE[i-1][j-1] for i in N for j in N if j>i))


c1=model.addConstrs(x[i]+s[i]+m[i]==1 for i in N)

c2=model.addConstr(sum(v[i] for i in N)<=1)

c3=model.addConstrs(len(N)*v[i]>=q[i] for i in N )

c4=model.addConstrs(sum(f[i,j] for j in N)+x[i]==sum(f[l,i] for l in N)+q[i] for i in N)

c5=model.addConstrs(len(N)*u[i,j] >=f[i,j] for i in N for j in N)

c6=model.addConstrs(sum(u[l,i] for l in N)+v[i]==x[i] for i in N)

c7=model.addConstrs(u[i,j]<=x[i] for i in N for j in N)

c8=model.addConstrs(m[i]<=sum(p[i,j] for j in N  if j!=i) for i in N)

c9=model.addConstrs(p[i,j]<=m[i] for i in N for j in N)

c10=model.addConstrs(p[i,j]<=m[j] for i in N for j in N)

c11=model.addConstrs(p[i,j]==p[j,i] for i in N for j in N)


starting_time=time.time()

model.optimize()

print("Runtime is (seconds):", time.time()-starting_time)

grid_sum=0
minigrid_sum=0
offgrid_sum=0

for i in N:
    if round(x[i].X)==1:
        grid_sum+=Population[i-1]
    elif round(m[i].X)==1:
        minigrid_sum+=Population[i-1]
    else:
        offgrid_sum+=Population[i-1]


print("Grid cost:", sum(round(x[i].X)*CGI[i-1] for i in N)+sum(round(u[i,j].X)*CGE[i-1][j-1] for i in N for j in N), "Number of nodes:", sum(round(x[i].X) for i in N),"Total population", grid_sum)
print("Mini grid cost:", sum(round(m[i].X)*CMGI[i-1] for i in N )+sum(round(p[i,j].X)*CMGE[i-1][j-1] for i in N for j in N if j>i), "Number of nodes:", sum(round(m[i].X) for i in N), "Total population", minigrid_sum)
print("Off grid cost:", sum(round(s[i].X)*CD[i-1] for i in N), "Number of nodes:", sum(round(s[i].X) for i in N), "Total population", offgrid_sum)