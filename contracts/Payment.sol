// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract Payment {

  //Total Node Count i.e 100
  uint public total_nodes=0;

  //2D array to keep track of Adjancency list  (Dynamic)
  uint[][] public adj_list;

  /*This will track the balances in each edge ->
     eg-  4-5 => 5 Ether
          5-4 => 5 Ether so on
  */ 
  mapping(string => int256) bal;


  function registerUser(uint user_id, string memory user_name) public{
    total_nodes+=1;
    //Pushing a particular 1D adjacency array for a node
    uint[] memory single_list = new uint[](0);
    adj_list.push(single_list);
  }

  //Balace to sent from an exponential distribution from python
  function createAcc(uint user_1, uint user_2, int256 balance) public returns(string memory){
    
    // If already a connection exist between them
    for(uint i=0;i<adj_list[user_1].length;i++){
      
      //Account already exists
      if(adj_list[user_1][i] == user_2)
        return "Account already exists";
    }

    //Adding to the adjacency list of both
    adj_list[user_1].push(user_2);
    adj_list[user_2].push(user_1);


    /* Map storing the mapping of balances
      4->5 = 5 in this format 
    */

    bal[string(abi.encodePacked(toString(user_1), "->", toString(user_2)))] = int256(uint(balance)/uint(2));
    bal[string(abi.encodePacked(toString(user_2), "->", toString(user_1)))] = int256(uint(balance)/uint(2));

    return "Joint Account added";
  }

  function getbalance(uint user_1, uint user_2) public returns (int256){
    return bal[string(abi.encodePacked(toString(user_1), "->", toString(user_2)))];
  }
  
  function sendAmount(uint user_1, uint user_2, int256 money) public returns (string memory){
    /*Todo -  Check money > 0
              Do a BFS traversal to find the shortest path thus checking the money on the path 
              as we go
                Once Path is found -- Backtrack path and update the balances

              As msg in teams - One can find the next shortest path by not inputting
              the final node(user2) in visited array
    */
  if (bal[string(abi.encodePacked(toString(user_1), "->", toString(user_2)))]-money<0)
  {
    return "Txn Failed due to Negative Balance";
  }
   else {
   bal[string(abi.encodePacked(toString(user_1), "->", toString(user_2)))]-=money; 
   bal[string(abi.encodePacked(toString(user_2), "->", toString(user_1)))]+=money;
   return "Txn Successful";
   }
  } 

  function closeAccount(uint user_1, uint user_2) public{
    
    uint i =0;
    //To traverse to delete user2 from the adj_list of user1 
    while (i < adj_list[user_1].length) {
      if (adj_list[user_1][i] == user_2) {
        adj_list[user_1][i] = adj_list[user_1][adj_list[user_1].length-1];
        adj_list[user_1].pop();
        break;
      }
      i++;
    }
    i=0;
    while (i < adj_list[user_2].length) {
      if (adj_list[user_2][i] == user_1) {
        adj_list[user_2][i] = adj_list[user_2][adj_list[user_2].length-1];
        adj_list[user_2].pop();
        break;
      }
      i++;
    }

    //Deleting the edge mappings from the edge->balance map

    //COndition to check if account existed
    if (i!=adj_list[user_2].length)
    {
      delete bal[string(abi.encodePacked(toString(user_1), "->", toString(user_2)))];
      delete bal[string(abi.encodePacked(toString(user_2), "->", toString(user_1)))];
    }

  }


function toString(uint value) internal pure returns (string memory) {
      // Special case for 0
        if (value == 0) {
            return "0";
        }

        // Determine the number of digits in the value
        uint digits = 0;
        for (uint i = value; i > 0; i /= 10) {
            digits++;
        }

        // Allocate a buffer to store the string
        bytes memory buffer = new bytes(digits);

        // Convert each digit to a character and store it in the buffer
        for (uint i = digits; i > 0; i--) {
            buffer[--digits] = bytes1(uint8(value % 10) + 48);
            value /= 10;
        }

        // Return the resulting string
        return string(buffer);
    }
}