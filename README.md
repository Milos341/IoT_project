# Concrete Structures Moisture and Temperature Monitoring System

## Project Structure
- sensor_temp/ : Temperature sensor simulation
- sensor_humidity/ : Humidity sensor simulation
- controller/ : Central controller (receives data, analyzes, sends commands to actuator)
- actuator/ : Actuator simulation (executes controller commands)

## Running and Testing on Two Computers
1. Install required Python libraries (`paho-mqtt`, etc.) and copy the entire `IoT_project` folder on both computers.
2. On the first computer, run the sensors:
   - `python3 sensor_temp/main.py`
   - `python3 sensor_humidity/main.py`
3. On the second computer, run the controller and actuator:
   - `python3 controller/main.py`
   - `python3 actuator/main.py`
4. Start the MQTT broker (e.g., Mosquitto) on one computer and configure the broker's IP in all modules.
5. The controller automatically discovers the sensors (SSDP), receives data, and sends commands to the actuator when threshold values are exceeded.
6. The actuator simulates execution (outputs to the terminal).

## Note
The alarm module has been removed – only the actuator performs actions, as specified in the project.
