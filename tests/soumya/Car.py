
#Car is the class and it will have different "Car" objects
class Car:
    
    # __init__ is the constructor and it uses the parameters/attributes- make,model,year,color to define each different "car" object
    def __init__(self,make,model,year,color):
        self.make= make
        self.model= model
        self.year= year
        self.color= color
    
    #The following are two different methods "drive" and "stop" which corresponds to two different actions
    def drive(self):
        print("This car is driving")
    
    def stop(self):
        print("This car is stopped")

    

