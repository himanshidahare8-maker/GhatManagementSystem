# GhatNetra AI (घाट-नेत्र) - SIH 2026 Project Guide

## 1. Project Overview
- **Title**: GhatNetra AI - AI-Powered River Ghat Crowd Management and Decision Support System
- **Client**: Madhya Pradesh State Tourism Development Corporation Limited (MPSTDC)
- **Theme**: AI & Intelligent Systems
- **Location Context**: Ujjain (Ram Ghat, Shipra River), Omkareshwar, Maheshwar, Sethani Ghat.

---

## 2. Project Architecture & File Structure

```
ghat-ai/
├── videos/
│   └── crowd.mp4           # Input pre-recorded high-resolution crowd video (2560x1440)
├── yolo11n.pt              # YOLOv11 nano model weights for person detection
├── decision_engine.py      # Core AI Logic: Occupancy, Gate recommendations, Evacuation physics
├── zone_detection.py       # High-speed OpenCV Visualizer with HUD and translucent zones
├── app.py                  # Full Web Command Center Dashboard (Streamlit)
├── verify_pipeline.py      # Automated 1-frame verification test script
├── test_zone_output.jpg    # Output snapshot with bounding boxes & zones
└── SIH_PROJECT_GUIDE.md    # This complete explanation guide
```

---

## 3. How to Run the Project

### Command 1: Test Verification (1 Frame)
```powershell
& "C:\Users\HP\OneDrive\Desktop\Ghat Managnment\venv\Scripts\python.exe" verify_pipeline.py
```
*Kya hota hai:* Video ka pehla frame read karta hai, YOLO run karta hai, teeno zones mein log count karta hai aur `test_zone_output.jpg` save karta hai.

### Command 2: Run Full OpenCV Vision Window (High Speed)
```powershell
& "C:\Users\HP\OneDrive\Desktop\Ghat Managnment\venv\Scripts\python.exe" zone_detection.py
```
*Kya hota hai:* Ek desktop window khulti hai jisme video chalta hai, green bounding boxes bante hain, Zone A, B, C ke colored overlays aate hain, aur upar command center HUD mein real-time Gate 1 aur Gate 2 ke live orders dikhte hain. 'q' dabane par window band hoti hai.

### Command 3: Run Official Web Command Dashboard (Streamlit)
```powershell
& "C:\Users\HP\OneDrive\Desktop\Ghat Managnment\venv\Scripts\streamlit.exe" run app.py
```
*Kya hota hai:* Aapke browser mein (http://localhost:8501) ek MPSTDC Command Center khul jata hai. Wahan live video processing button bhi hai aur SIH Judges ke liye "What-If" Simulation Sandbox bhi hai!

---

## 4. SIH Judges ke saamne kaise explain karein (Presentation Pitch)

1. **Problem**: "Respected Judges, during festivals like Simhastha Kumbh or Mahakal Sawari, river ghats face dangerous stampede and drowning risks due to manual, reactive crowd management."
2. **Solution**: "Humne **GhatNetra AI** banaya hai jo:
   - Video feed se YOLOv11 ke zariye crowd detect karta hai.
   - Ghat ko 3 dynamic zones (Upper Entry, Central Snan, Waterfront Exit) mein divide karke zone-wise density calculate karta hai.
   - **Decision Support System** ke zariye entry gates ko automatic OPEN, CONTROLLED, ya RESTRICTED ki recommendation deta hai.
   - Physics-based formula se **Safe Evacuation Time** calculate karta hai taaki emergency aane se pehle crowd ko Narsingh Ghat ya Dutt Akhara ki taraf divert kiya ja sake."
