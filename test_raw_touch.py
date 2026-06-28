import machine
import time

print("Starting raw touch test...")

# 1. Reset sequence for GT911 touch chip
rst = machine.Pin(40, machine.Pin.OUT)
t_int = machine.Pin(42, machine.Pin.OUT)

# Pull both low
rst.value(0)
t_int.value(0)
time.sleep_ms(20)

# Pull Reset high while INT is low (forces GT911 to I2C address 0x5D)
rst.value(1)
time.sleep_ms(10)

# Set INT back to input
t_int.init(machine.Pin.IN)
time.sleep_ms(50)

# 2. Initialize software I2C (SoftI2C) for bit-banging stability
i2c = machine.SoftI2C(sda=machine.Pin(7), scl=machine.Pin(8), freq=100000)

# Detect address
addr = 0x5D
devices = i2c.scan()
print("I2C Scan results:", [hex(d) for d in devices])
if 0x14 in devices:
    addr = 0x14
elif 0x5D in devices:
    addr = 0x5D
else:
    print("WARNING: GT911 not found in scan, trying 0x5D anyway.")

# 3. Read ID
try:
    chip_id = i2c.readfrom_mem(addr, 0x8140, 4, addrsize=16)
    print(f"Success! Verified Chip ID via raw I2C on {hex(addr)}:", chip_id)
except Exception as e:
    print(f"Could not read Chip ID on {hex(addr)}:", e)

# 4. Poll touch coordinates for 45 seconds
print(f"\nPolling touch registers on {hex(addr)} for 45 seconds...")
start_time = time.time()
while time.time() - start_time < 45:
    try:
        # 4a. Read ID register to check if bus is still alive
        chip_id = i2c.readfrom_mem(addr, 0x8140, 4, addrsize=16)
        
        # 4b. Read touch status register
        status = i2c.readfrom_mem(addr, 0x814E, 1, addrsize=16)[0]
        
        # Check if coordinates are ready (bit 7)
        if status & 0x80:
            points = status & 0x0F
            if points > 0:
                data = i2c.readfrom_mem(addr, 0x814F, 6, addrsize=16)
                x = data[0] | (data[1] << 8)
                y = data[2] | (data[3] << 8)
                print(f"RAW Python Touch -> Points: {points}, X: {x}, Y: {y}")
            # Clear status flag
            i2c.writeto_mem(addr, 0x814E, b'\x00', addrsize=16)
    except Exception as e:
        print("I2C Poll Error:", e)
        
    time.sleep_ms(50)

print("\nRaw touch test complete.")

