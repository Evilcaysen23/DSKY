#Mass Caculation script
import math

# Constants
Engines = 2 # Total engine count
Thrust = 716 # Thrust in kN
WetMass = 50.530 # Mass in Tons 
Isp = 251 # Specific impulse in seconds
Drymass = 22.589 # Dry mass in Tons
Desired_TWR = 1.25 # Desired Thrust-to-Weight Ratio
Gravity = 9.81 # Gravitational acceleration in m/s^2
# Function to give design parameters of a rocket
def MassCalculation(Engines, Thrust, Mass, Isp, Drymass, Desired_TWR):
    Total_Thrust = ((Engines * Thrust) * 0.1124044715) #Thrust from kN to Tonnes
    TWR = Total_Thrust / WetMass # TWR = Thrust to Weight Ratio
    Exhaust_Velocity = Isp * Gravity # Exhaust velocity in m/s
    DeltaV = Exhaust_Velocity * math.log(WetMass / Drymass) # DeltaV in m/s
    MaxMass = Total_Thrust/(Desired_TWR)
    return Total_Thrust, TWR, DeltaV, MaxMass, WetMass, Desired_TWR
print("First Stage Parameters:")
print("Total Thrust: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[0], "Tons")
print("Thrust-to-Weight Ratio: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[1])
print("Delta-V: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[2], "Meters a second")
print("Maximum Mass: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[3], "Tons")
Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass, Stage_1_WetMass, Stage_1_Desired_TWR = MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)
# Constants
Engines = 1 # Total engine count
Thrust = 790 # Thrust in kN
Drymass = 3.997 # Dry mass in Tons
WetMass = 19.753 # Mass in Tons 
Isp = 270 # Specific impulse in seconds
Desired_TWR= 0.95 # Desired Thrust-to-Weight Ratio
# Function to give design parameters of a rocket second upper stage
print("Upper Stage Parameters:")
print("Total Thrust: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[0], "Tons")
print("Thrust-to-Weight Ratio: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[1])
print("Delta-V: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[2], "Meters a second")
print("Maximum Mass: ", MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)[3], "Tons")
Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass, Stage_2_WetMass, Stage_2_Desired_TWR = MassCalculation(Engines, Thrust, WetMass, Isp, Drymass, Desired_TWR)
# Function to give design parameters of a rocket vehicle
def VehicleParameters(Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass,Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass):
    Vehicle_Thrust = Stage_1_Thrust 
    Vehicle_TWR = (Stage_1_Thrust) / (Stage_1_WetMass + Stage_2_WetMass) # Stage 1 Thrust Ratio Wet Tanks
    Vehicle_DeltaV = Stage_1_DeltaV + Stage_2_DeltaV # Total Delta-V in Meters a second
    Vehicle_MaxMass = Stage_1_MaxMass + Stage_2_MaxMass # Total Maximum Mass in Tons
    return Vehicle_Thrust, Vehicle_TWR, Vehicle_DeltaV, Vehicle_MaxMass
print("Vehicle Parameters:")
print("Total Thrust: ", VehicleParameters(Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass, Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass)[0], "Tons")
print("Thrust-to-Weight Ratio: ", VehicleParameters(Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass, Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass)[1])
print("Delta-V: ", VehicleParameters(Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass, Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass)[2], "Meters a second")
print("Maximum Mass: ", VehicleParameters(Stage_1_Thrust, Stage_1_TWR, Stage_1_DeltaV, Stage_1_MaxMass, Stage_2_Thrust, Stage_2_TWR, Stage_2_DeltaV, Stage_2_MaxMass)[3], "Tons")
print("Vehicle Mass: ", Stage_1_WetMass + Stage_2_WetMass, "Tons")
# Function to give design parameters of a rocket
#work on the function gowing foward for trajectory calculations 