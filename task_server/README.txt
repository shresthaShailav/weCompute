Taskserver for a WeCompute Client.
Ideally There should have been no server, but because most agent connected to the internet is behind a NAT, we need to : 
    1. Create a Hole punching mechanism
    OR
    2. Create a publich reachable resource
    (Both of which requires a server)


TaskServer DOES NOT perform any computation itself.
It simply manages taskQueue for the differnt clients that are connected throughout the internet.
