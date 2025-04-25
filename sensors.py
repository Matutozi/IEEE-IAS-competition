import network
import socket
import time
import machine
from machine import Pin, ADC
import onewire
import ds18x20
import urequests
import json
import sensor_utils

# Network credentials
ssid = 'Pico Network'
password = 'networkpico'

# Pin definitions
TEMP_SENSOR_PIN = 2  
CURRENT_SENSOR_PIN = 0  
VOLTAGE_SENSOR_PIN = 0  
RELAY_PIN = 5  

# Initialize pins
relay = Pin(RELAY_PIN, Pin.OUT)
adc = ADC(0)  

# Initialize OneWire and DS18B20 temperature sensor
ds_pin = Pin(TEMP_SENSOR_PIN)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        
        max_wait = 10
        while not wlan.isconnected() and max_wait > 0:
            print('Waiting for connection...')
            if wlan.status() == network.STAT_NO_AP_FOUND:
                print("No access point found with the SSID " + ssid)
                break
            if wlan.status() == network.STAT_WRONG_PASSWORD:
                print("Password rejected by WLAN.")
                break
            if wlan.status() == network.STAT_CONNECT_FAIL:
                print("Connection failed.")
                break
            time.sleep(1)
            max_wait -= 1
    
    if wlan.isconnected():
        print('Connected to WiFi')
        print('Network config:', wlan.ifconfig())
        return True
    else:
        print('Failed to connect to WiFi')
        return False

def send_data_to_dashboard(data):
    try:
        url = "https://atlas-solar-dashboard.example.com/api/update"
        headers = {'Content-Type': 'application/json'}
        
        response = urequests.post(url, headers=headers, data=json.dumps(data))
        print("Data sent to dashboard:", response.status_code)
        response.close()
        
    except Exception as e:
        print("Failed to send data:", e)

def main():
    if not connect_wifi():
        print("WiFi connection failed. Restarting...")
        machine.reset()
    
    relay.value(0)
    
    print("ATLAS Solar Monitoring System Started")
    
    while True:
        try:
            temperature, current, voltage, power = sensor_utils.collect_sensor_data(
                ds_sensor, roms, adc
            )
            
            env_data = sensor_utils.get_environmental_data(temperature)
            
            efficiency = sensor_utils.calculate_efficiency(power, env_data["irradiance"])
            
            data = {
                "panel_data": {
                    "id": 1,
                    "temperature": temperature,
                    "voltage": voltage,
                    "current": current,
                    "power": power,
                    "efficiency": efficiency
                },
                "environmental": env_data,
                "system": {
                    "total_power": power,
                    "system_efficiency": efficiency,
                    "battery_level": 82
                }
            }
            
            print("Temperature:", temperature, "°C")
            print("Voltage:", voltage, "V")
            print("Current:", current, "A")
            print("Power:", power, "W")
            print("Efficiency:", efficiency, "%")
            
            send_data_to_dashboard(data)
            
            if temperature > 75:
                relay.value(1)
                print("Panel disconnected due to high temperature")
            elif relay.value() == 1 and temperature < 70:
                relay.value(0)
                print("Panel reconnected")
            
            time.sleep(60)
            
        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped by user")
    except Exception as e:
        print("Fatal error:", e)
        machine.reset()