# Smart_Vehicle_Parking_Management_System
A modern, fully digital parking solution built using Python (Flask), MySQL, HTML, CSS, and a clean UI. This project automates the entire workflow of parking operations from vehicle entry to billing making the process fast, secure, and error-free.
Smart Parking System

A web-based automated vehicle parking management system built using Flask (Python), MySQL, HTML/CSS, designed to streamline parking operations, reduce manual work, and provide real-time monitoring of entries, exits, billing, and occupancy.

**Overview**

The Smart Parking System digitizes the complete parking workflow from vehicle entry to final billing. It automatically assigns slots, generates unique tokens, calculates charges using timestamps, and updates occupancy across multiple locations. A modern dashboard provides administrators real-time insights including today’s stats, earnings, recent entries, and place-wise occupancy.

Features
Vehicle Entry

Enter user details, vehicle type, number, and place

Automatic slot allocation based on availability

Instant 3-digit unique token generation

Stores all data securely in MySQL

Vehicle Exit & Billing

Token-based record retrieval

Calculates duration and charges (Bike: ₹1/min, Car: ₹3/min)

Frees slot and updates occupancy

Generates a digital parking receipt

**Dashboard**

Today’s stats (cars, bikes, totals)

Daily earnings calculation

Recent vehicle entries (details masked)

Parking occupancy displayed place-wise

Additional Modules

Lost token assistance

Parking rates page

Token check page

Help desk and support info

**Technologies Used**

Frontend: HTML, CSS

Backend: Python Flask

Database: MySQL

Logic: Flask routing, SQL queries, timestamp-based billing

**Database Tables**

places – list of parking locations and capacity

parking_slots – individual slots mapped to places

vehicle_entry – stores entry records, timestamps, and tokens

vehicle_exit – stores exit timestamps and billing details

**How It Works**

User fills entry form → system assigns slot → token issued

Vehicle exits → token entered → bill calculated

Slot freed → system updates all stats automatically

Dashboard displays real-time data for admins

**Purpose**

The system reduces manual workload, eliminates errors, improves accuracy, and provides a much faster and smarter parking experience.
