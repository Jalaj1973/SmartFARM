# 🌾 **SmartFarm – IoT-Based Smart Agriculture & Advisory System**

**SmartFarm** is a comprehensive **IoT + ML-powered smart farming solution** that combines real-time environmental sensing, automated irrigation, crop and fertilizer recommendation, multilingual support, government scheme awareness, and smart motion detection via PIR sensors. All data and controls are accessible via a user-friendly web dashboard and the Blynk mobile app.

---

## 📦 **Key Features**

### 🛰️ **IoT-Based Monitoring & Automation**
Real-time monitoring of:
- 🌡️ Temperature & Humidity (DHT11)
- 🌱 Soil Moisture (Analog sensor)
- 🚶 PIR Motion Detection (Human/animal presence)
- 💧 Automatic irrigation via water pump (relay-controlled)
- 🔘 Manual irrigation using push button
- 📟 Local display using LCD (optional)
- 🔄 Live updates to Blynk IoT App

---

### 🧠 **Smart Advisory System**
- 🌾 **Crop Recommendation** using:
  - Soil moisture, temperature, nitrogen level (future)
- 🧪 **Fertilizer Suggestion** based on crop and soil condition

---

### 🧑‍🌾 **User Interaction & Accessibility**
- 🔐 **Login/Registration system** (with database)
- 🌍 **Multilingual Support** (e.g., Hindi, English)
- 🧑 Personalized dashboard

---

## 🧰 **Hardware Components**

| **Component**          | **Purpose**                        |
|------------------------|------------------------------------|
| ESP8266 NodeMCU        | Microcontroller with Wi-Fi         |
| DHT11                  | Temperature and Humidity sensor    |
| Soil Moisture Sensor   | Monitors soil water content        |
| Relay + Water Pump     | Automatic irrigation control       |
| Push Button            | Manual pump activation             |
| LCD (16x2 or I2C)      | Display local sensor values        |
| PIR Sensor             | Detects motion near device         |

---

## 🔌 **Pin Configuration (NodeMCU)**

| **Component**      | **Pin**             |
|--------------------|---------------------|
| DHT11              | D4                  |
| Soil Moisture      | A0                  |
| Relay              | D3                  |
| Push Button        | D7                  |
| PIR Sensor         | D5 (or any digital) |
| LCD (Optional)     | I2C or GPIO         |

---

## 🚀 **How It Works**
1. Sensors collect real-time data (moisture, temp, humidity, motion).
2. NodeMCU uploads data to **Blynk App** and web dashboard.
3. If soil moisture < threshold → relay activates water pump.
4. Motion detected by PIR:
   - Can log human presence
   - Can trigger alerts or display messages
5. Manual override available via push button.
6. LCD optionally displays live sensor readings.
7. ML model processes data to recommend optimal crop/fertilizer.
8. Government scheme data and multilingual UI enhance user access.

---

## 🌍 **Multilingual Support**

- Fully supports **Hindi and English**
- Translates:
  - Dashboard content
  - Crop/fertilizer names
  - Government schemes info

---

## 🔐 **Login & Database**

- **User registration and login**
- **User preferences**
- **History of crop recommendations**
- **Database:** MySQL

---

## 📸 **Hardware Setup**

![image](https://github.com/user-attachments/assets/67de928b-c7ed-49a2-914c-788d8a506f10)

---

## 📱 **Blynk Dashboard**

<img width="1370" alt="Screenshot 2025-06-01 at 1 50 11 PM" src="https://github.com/user-attachments/assets/4e91d11d-a205-4d21-8cd0-aecb53c7bd7f" />

---

## 💻 **Web Login + Dashboard UI**

<img width="1470" alt="Screenshot 2025-04-11 at 9 47 10 PM" src="https://github.com/user-attachments/assets/7ed4ad65-c1f4-4a7e-8d71-7e5b5de7008a" />

<img width="1470" alt="Screenshot 2025-04-11 at 9 51 06 PM" src="https://github.com/user-attachments/assets/010ca0b2-3ffd-496b-a885-2aca2caf42f5" />

<img width="1468" alt="Screenshot 2025-06-01 at 2 00 51 PM" src="https://github.com/user-attachments/assets/adf76e4d-25f6-4d91-a704-0ebff21a6c66" />

