# 🛰️ Satellite Collision Distance Tracker

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-brightgreen?logo=streamlit)](https://satellites.streamlit.app/)

A Python + Streamlit application that calculates and visualizes the **minimum distances between satellites** using real Two-Line Element (TLE) data.  

This tool can help analyze potential conjunctions (close approaches) between satellites and visualize how their distances change over time.

---

## ✨ Features
- Fetches live **TLE orbital data** from [public NASA APIs](https://api.nasa.gov/).
- Calculates **closest distances** between satellites using [Skyfield](https://rhodesmill.org/skyfield/).
- **Overview table**: all satellite pair minimum distances with color coding.
- **Interactive table**: scrollable list of satellite pairs with a **"Show Plot"** button.
- **Plots**: visualize distance over time for a given satellite pair.
- SQLite backend for storing and querying results.

---

## 🖥️ Live Demo
👉 Try it here: [satellites.streamlit.app](https://satellites.streamlit.app/)

---
