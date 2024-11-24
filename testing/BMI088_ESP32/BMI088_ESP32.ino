#include <Wire.h>

// I2C Addresses for BMI088
#define ACCEL_I2C_ADDR 0x18 // Accelerometer I2C address
#define GYRO_I2C_ADDR  0x68 // Gyroscope I2C address

// Register Addresses for Accelerometer
#define ACC_X_LSB 0x12
#define ACC_X_MSB 0x13
#define ACC_Y_LSB 0x14
#define ACC_Y_MSB 0x15
#define ACC_Z_LSB 0x16
#define ACC_Z_MSB 0x17
#define ACC_RANGE 0x41

// Register Addresses for Gyroscope
#define GYRO_X_LSB 0x02
#define GYRO_X_MSB 0x03
#define GYRO_Y_LSB 0x04
#define GYRO_Y_MSB 0x05
#define GYRO_Z_LSB 0x06
#define GYRO_Z_MSB 0x07

// Conversion constants
const float ACCEL_SCALE = 1.5 / 32768.0; // Accelerometer scale for ±6g
const float GYRO_SCALE = 250.0 / 32768.0; // Gyroscope scale for ±250 dps

// I2C Pins for ESP32-S3
#define SDA_PIN 21
#define SCL_PIN 22

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);

  // Wait for Serial to be ready
  while (!Serial) {}
  Serial.println("Initializing BMI088 Accelerometer...");

  // Perform a soft reset
  writeRegister(ACCEL_I2C_ADDR, 0x7E, 0xB6); // Soft reset
  delay(100);

  // Set accelerometer to normal mode
  writeRegister(ACCEL_I2C_ADDR, 0x7D, 0x04); // Enable accelerometer in normal mode
  delay(50);

  // Set accelerometer range to ±6g
  writeRegister(ACCEL_I2C_ADDR, ACC_RANGE, 0x03); // ±6g range
  delay(50);

  Serial.println("BMI088 Accelerometer Initialized");
}


void loop() {
  // Read accelerometer data
  int16_t accelX = readSensorData(ACCEL_I2C_ADDR, ACC_X_LSB, ACC_X_MSB);
  int16_t accelY = readSensorData(ACCEL_I2C_ADDR, ACC_Y_LSB, ACC_Y_MSB);
  int16_t accelZ = readSensorData(ACCEL_I2C_ADDR, ACC_Z_LSB, ACC_Z_MSB);

  // Convert to mg
  float accelX_mg = accelX * ACCEL_SCALE * 1000;
  float accelY_mg = accelY * ACCEL_SCALE * 1000;
  float accelZ_mg = accelZ * ACCEL_SCALE * 1000;

  // Read gyroscope data
  int16_t gyroX = readSensorData(GYRO_I2C_ADDR, GYRO_X_LSB, GYRO_X_MSB);
  int16_t gyroY = readSensorData(GYRO_I2C_ADDR, GYRO_Y_LSB, GYRO_Y_MSB);
  int16_t gyroZ = readSensorData(GYRO_I2C_ADDR, GYRO_Z_LSB, GYRO_Z_MSB);

  // Convert to degrees/second
  float gyroX_dps = gyroX * GYRO_SCALE;
  float gyroY_dps = gyroY * GYRO_SCALE;
  float gyroZ_dps = gyroZ * GYRO_SCALE;

  // Print accelerometer results (milli-g's)
  Serial.print(accelX_mg);
  Serial.print("\t");
  Serial.print(accelY_mg);
  Serial.print("\t");
  Serial.print(accelZ_mg);
  Serial.print("\t");

  // Print gryoscope results (degrees per second)
  Serial.print(gyroX_dps);
  Serial.print("\t");
  Serial.print(gyroY_dps);
  Serial.print("\t");
  Serial.println(gyroZ_dps);

  delay(10);
}

// Function to write a value to a register
void writeRegister(uint8_t deviceAddr, uint8_t regAddr, uint8_t value) {
  Wire.beginTransmission(deviceAddr);
  Wire.write(regAddr);
  Wire.write(value);
  Wire.endTransmission();
}

// Function to read 16-bit data (LSB and MSB)
int16_t readSensorData(uint8_t deviceAddr, uint8_t lsbAddr, uint8_t msbAddr) {
  uint8_t lsb = readRegister(deviceAddr, lsbAddr);
  uint8_t msb = readRegister(deviceAddr, msbAddr);
  return (int16_t)((msb << 8) | lsb);
}

// Function to read a single byte from a register
uint8_t readRegister(uint8_t deviceAddr, uint8_t regAddr) {
  Wire.beginTransmission(deviceAddr);
  Wire.write(regAddr);
  Wire.endTransmission(false); // Send a restart condition
  Wire.requestFrom(deviceAddr, (uint8_t)1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0;
}
