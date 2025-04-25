import time

VOLTAGE_DIVIDER_RATIO = 11.0
CURRENT_SENSOR_SENSITIVITY = 0.185

def read_temperature(ds_sensor, roms):
    try:
        ds_sensor.convert_temp()
        time.sleep(0.75)
        
        if roms:
            temp = ds_sensor.read_temp(roms[0])
            return round(temp, 1)
        else:
            print("No temperature sensors found")
            return 0
    except Exception as e:
        print("Temperature sensor error:", e)
        return 0

def read_current(adc):
    try:
        adc_value = adc.read()
        voltage = adc_value * (1.0 / 1023.0)
        current = (voltage - 0.5) / CURRENT_SENSOR_SENSITIVITY
        return abs(round(current, 2))
    except Exception as e:
        print("Current sensor error:", e)
        return 0

def read_voltage(adc):
    try:
        adc_value = adc.read()
        measured_voltage = adc_value * (1.0 / 1023.0)
        actual_voltage = measured_voltage * VOLTAGE_DIVIDER_RATIO
        return round(actual_voltage, 1)
    except Exception as e:
        print("Voltage sensor error:", e)
        return 0

def calculate_power(voltage, current):
    return round(voltage * current, 1)

def calculate_efficiency(power, irradiance):
    panel_area = 0.5
    theoretical_max = irradiance * panel_area
    
    if theoretical_max > 0:
        efficiency = (power / theoretical_max) * 100
        return min(round(efficiency), 100)
    else:
        return 0

def get_environmental_data(panel_temp):
    ambient_temp = panel_temp - 10
    humidity = 45
    irradiance = 876
    
    return {
        "ambient_temp": ambient_temp,
        "humidity": humidity,
        "irradiance": irradiance
    }

def collect_sensor_data(ds_sensor, roms, adc, samples=5, interval=0.5):
    temp_sum = 0
    current_sum = 0
    voltage_sum = 0
    
    for _ in range(samples):
        temp_sum += read_temperature(ds_sensor, roms)
        current_sum += read_current(adc)
        voltage_sum += read_voltage(adc)
        time.sleep(interval)
    
    avg_temp = temp_sum / samples
    avg_current = current_sum / samples
    avg_voltage = voltage_sum / samples
    avg_power = calculate_power(avg_voltage, avg_current)
    
    return avg_temp, avg_current, avg_voltage, avg_power
