#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 16:31:24 2023

@author: janinegantenbein
"""

import streamlit as st
import pandas as pd
import altair as alt
import json
import os
from fpdf import FPDF
from datetime import date
import datetime

#Layouts und Container
col1, col2 = st.columns(2)

with col1:
    #Titel der App
    st.title('Blutzucker-Tracker')
    
with col2:
    st.image('Blutzucker.jpg', width=220)    


# Erstelle das Hauptmenü
menu = ['Werte erfassen', 'Werte löschen', 'Archiv', 'Persönliche Daten']
choice = st.sidebar.selectbox('Menü', menu)

# Wenn das Menü "Werte erfassen" ausgewählt ist
if choice == 'Werte erfassen':
    st.subheader("Werte erfassen")
    # Erstelle die Eingabefelder für Datum, Uhrzeit und Blutzuckerwert
    datum = st.date_input('Datum')
    uhrzeit = st.time_input('Uhrzeit')
    wert = st.number_input('Blutzuckerwert')
    
    # Lese die vorhandenen Daten aus der JSON-Datei
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    
    # Speichere die Daten, wenn der Benutzer auf "Speichern" klickt
    if st.button('Speichern'):
        # Erstelle ein neues Datensatz-Objekt
        datensatz = {'Datum': str(datum), 'Uhrzeit': str(uhrzeit), 'Blutzuckerwert': wert}
        
        if wert <4 or wert >9:
            st.warning('Achtung: Der eingegebene Wert liegt ausserhalb des Referenzbereichs.', icon="🚨")
        
        # Füge den neuen Datensatz den vorhandenen Daten hinzu
        data.append(datensatz)
        
        # Speichere die aktualisierten Daten in der JSON-Datei
        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        # Erstelle ein DataFrame aus den Daten
        df = pd.DataFrame(data)
        
        # Erstelle ein Balkendiagramm mit Altair
        chart = alt.Chart(df).mark_bar(width=10).encode(x='Datum', y='Blutzuckerwert')
        st.altair_chart(chart, use_container_width=True)
    
    # Wenn es keine Daten gibt, zeige eine Nachricht an
    if len(data) == 0:
        st.write('Es sind noch keine Daten vorhanden.')
        
if choice == 'Werte löschen':
        st.subheader('Werte löschen') 
        
        # Lese die vorhandenen Daten aus der JSON-Datei
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                data = json.load(f)
        else:
            data = []
            
        #Erstelle ein DataFrame mit den Daten
        df = pd.DataFrame(data)
        
        #Zeige die Tabelle mit den Daten
        st.write(df)
        
        #Erstelle eine Auswahlliste mit verfügbaren Daten
        selected_index = st.selectbox('Wählen Sie den zu löschenden Datensatz aus:', df.index.tolist())
        
        #Zeige die ausgewählten Daten an
        st.write('Sie haben folgenden Datensatz ausgewählt:')
        st.write(df.loc[selected_index])
        
        #Wenn der Benutzer auf "Löschen" klickt, entferne ausgewählten Datensatz
        if st.button("Löschen"):
            data.pop(selected_index)
            
            #Speichere aktualisierte Daten in der JSON-Datei
            with open('data.json', 'w') as f:
                json.dump(data,f)
                
            #Zeige eine Erfolgsmeldung
            st.success('Datensatz wurde erfolgreich gelöscht.')
    
# Wenn das Menü "Archiv" ausgewählt ist
elif choice == 'Archiv':
    st.subheader("Archiv")
    # Lese die vorhandenen Daten aus der JSON-Datei
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    
    # Erstelle ein DataFrame aus den Daten
    df = pd.DataFrame(data)
    
    # Wenn es keine Daten gibt, zeige eine Nachricht an
    if len(data) == 0:
        st.write('Es sind noch keine Daten vorhanden.')
    else:
        # Zeige die Daten als Tabelle an
        st.write(df)
        
    #Funktionen für PDF-Datei erstellen
    class PDF(FPDF):
        def __init__(self, patient_name, birthdate):
            super().__init__()
            self.patient_name = patient_name
            self.birthdate = birthdate

        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Blutzuckerwerte', 0, 1, 'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Seite ' + str(self.page_no()), 0, 0, 'C')

        def add_patient_info(self):
            self.set_font('Arial', 'B', 12)
            self.cell(40, 10, 'Patientenname:', 0)
            self.set_font('Arial', '', 12)
            self.cell(0, 10, self.patient_name, 0, 1)
            self.set_font('Arial', 'B', 12)
            self.cell(40, 10, 'Geburtsdatum:', 0)
            self.set_font('Arial', '', 12)
            birthdate_str = self.birthdate.strftime("%d.%m.%Y")
            self.cell(len(birthdate_str) * 2.5, 10, birthdate_str, 0, 1)
            self.ln()

        def add_data(self, data):
            self.set_font('Arial', 'B', 12)
            for col in data.columns:
                self.cell(40, 10, col, 1)
            self.ln()
            self.set_font('Arial', '', 12)
            for _, row in data.iterrows():
                for col in data.columns:
                    self.cell(40, 10, str(row[col]), 1)
                self.ln()

    def create_pdf(data, patient_name, birthdate):
        pdf = PDF(patient_name, birthdate)
        pdf.add_page()
        pdf.add_patient_info()
        pdf.add_data(data)
        return pdf
    
    data = pd.read_json('data.json', convert_dates=['date'])
    
    #Input Formular anzeigen
    patient_name = st.text_input("Name")
    birthdate = st.date_input("Geburtsdatum:", min_value=date(1930, 1, 1))

    #PDF Datei erstellen
    if st.button('PDF herunterladen'):
        pdf = create_pdf(data, patient_name, birthdate)
        pdf_file = f'{patient_name}_{birthdate}.pdf'
        pdf.output(pdf_file)
        
        #Download-Button anzeigen
        with open(pdf_file, 'rb') as f:
            pdf_data = f.read()
        st.download_button(
            label='PDF-Datei herunterladen',
            data=pdf_data,
            file_name=pdf_file,
            mime='application/pdf'
            )    
        
#Menü Persönliche Daten
elif choice == 'Persönliche Daten':
    st.subheader("Persönliche Daten")
    # Persönliche Daten erfassen
    name = st.text_input('Name')
    birthdate = st.date_input('Geburtsdatum', min_value=datetime.date(1930, 1, 1))
    height = st.number_input('Grösse (in cm)', value=0, min_value=0, max_value=None)
    weight = st.number_input('Gewicht (in kg)', value=0, min_value=0, max_value=None)

    # Button zum Speichern der persönlichen Daten
    if st.button('Speichern'):
        st.write(f"Name: {name}")
        st.write(f"Geburtsdatum: {birthdate}")
        st.write(f"Grösse: {height} cm")
        st.write(f"Gewicht: {weight} kg")    
    