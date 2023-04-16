import json
from web3 import Web3
import networkx
from networkx.generators.degree_seq import random_degree_sequence_graph, configuration_model
from networkx.algorithms.graphical import is_graphical
from networkx.utils.random_sequence import powerlaw_sequence
from random import randint
from numpy import random
import matplotlib.pyplot as plt

num_nodes = 100
exponent = 2
# Connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
#check if ethereum is connected
print(w3.is_connected())

# Replace the address with your contract address
deployed_contract_address = '0xF49CB1bCA9A9a478796ccEB28DbDb2720AcCbc1B'

# Path of the contract json file
compiled_contract_path ="build/contracts/Payment.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']
contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)


for i in range(num_nodes):
    contract.functions.registerUser(i,str(i)).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})

print(num_nodes, "nodes Succesfully Created!")


# Creating edges for the nodes that follow a power law sequence    
n, t = num_nodes, exponent
while True:  # Continue generating sequences until one of them is graphical
    seq = sorted([int(round(d)) for d in powerlaw_sequence(n, t)], reverse=True)  # Round to nearest integer to obtain DISCRETE degree sequence
    # print(seq)
    if is_graphical(seq):
        print("It is graphical")
        break
    else:
        print("NOT Graphical")

print("Sequence:", seq)

G = configuration_model(seq)    # Generating a graph with the obtained power law sequence
attempts = 1
print("Attempt", attempts,"to generate connected graph")
while (networkx.is_connected(G)==False and attempts<100):    
    G = configuration_model(seq)
    attempts=attempts+1
    print("Attempt", attempts,"to generate connected graph")
if (attempts==100):
    print("Connected Graph could not be found in 100 attempts!!")
    exit()

print("Total Edges are",len(list(G.edges)))

edges = []
for i in list(G.edges):
    edges.append((i[0], i[1]))

G = networkx.Graph(G)                               # Removing parallel edges
G.remove_edges_from(networkx.selfloop_edges(G))     # Removing self loops


edges = list(G.edges)
print("Total number of Joint Accounts:", len(edges))
for edge in edges:
    acct_1=edge[0]
    acct_2=edge[1]

    init_balance = int(random.exponential(scale = 10))

    # Using .call() first to check if createAcc() returns a success message
    if (contract.functions.createAcc(acct_1,acct_2,init_balance).call()=='Joint Account added'):
        # If account can be created successfully, execute transact() to add the account to the blockchain 
        contract.functions.createAcc(acct_1,acct_2,init_balance).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
        print("Edge added between nodes",acct_1,"and",acct_2,"with balance",init_balance)
    else:
        print("Edge already exists between nodes",acct_1,"and",acct_2)


n_successful = []
n_successful_batch = []
c = 0
batch_count = 0
for k in range(1000):       # Performing 1000 transactions
    node1=randint(0,num_nodes-1)
    node2=randint(0,num_nodes-1)

    while (node2 == node1):
        node2=randint(0,num_nodes-1)
   
    shortest_path = networkx.shortest_path(G, node1, node2)
    print("Transferring 1 coin from", node1,"to",node2)

    i = 0
    while i < len(shortest_path)-1:
        acct_1=shortest_path[i]
        acct_2=shortest_path[i+1]

        # Checking using call() if 1 coin can be sent from acct_1 to acct_2
        if(contract.functions.sendAmount(acct_1,acct_2,1).call())=='Txn Successful':
            # If enough balance exists in the joint account to transfer 1 coin, perform the transaction on the blockchain
            contract.functions.sendAmount(acct_1,acct_2,1).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
        else:
            # Joint account did not have enough balance
            print("Txn couldn't be fully complete")
            print("The shortest Path was",shortest_path)
            print("Transaction failed in the edge between", shortest_path[i],"and",shortest_path[i+1])

            # Generating the reverse path so that the transactions mid-way in the shortest path can be reverted
            reverse_path = shortest_path[i::-1]
            print("Reversing transactions in the path", reverse_path, "\n")
            j = 0
            while j < len(reverse_path) - 1:
                acct_1=reverse_path[j]
                acct_2=reverse_path[j+1]

                # Sending 1 coin in the reverse direction to backtrack the failed transaction 
                contract.functions.sendAmount(acct_1,acct_2,1).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
                j += 1
            break
        i += 1

    if (i == len(shortest_path) - 1):
        print("Txn Fully Complete!")
        print("Path of transaction was",shortest_path, "\n")
        c += 1
        batch_count += 1
    
    # Storing the ratio of successful transactions every 100 transaction to plot the graph
    if (k + 1) % 100 == 0:
        n_successful.append(c/(k+1))
        n_successful_batch.append(batch_count/100)
        batch_count=0

print("Cumulative",n_successful)
print("Batch",n_successful_batch)
print("Total number of Joint Accounts:", len(edges))

x = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
plt.title("Ratio of successful transactions")
plt.xlabel("Total number of transactions")
plt.ylabel("Fraction of successful transactions")


plt.plot(x, n_successful)  # Plot the chart
plt.savefig('cumulative.png')

plt.plot(x, n_successful_batch)  # Plot the chart
plt.savefig('batch.png')