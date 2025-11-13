WHAT WE IMPLEMENTED:
We started to implement the system by creating the backend logic 
that handles user data and club recommendations. The components we have so 
far include:

models/recommender.py - implements strategy design pattern, allowing us to 
swap different recommendation algorithms.

controllers/main_controller.py - acts as an interface between user input and 
recommender model, also simulates a user providing interest and displays 
clubs based on current strategy


HOW IT RELATES TO SYSTEM DESIGN:
This implementation is guided by our chosen high level architecture(MVC). 
The recommendation logic and data handling is our Model. The communication 
between user input and the Model is our Controller. View will be implemented 
in future versions. 