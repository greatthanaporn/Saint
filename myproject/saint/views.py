import pandas as pd
import plotly.express as px
from django.shortcuts import render
import os

def show_graphs(request):
    # กำหนดเส้นทางไปยังไฟล์ CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'data.csv')
    
    # อ่านข้อมูลจากไฟล์ CSV
    df = pd.read_csv(csv_path)
    
    # สร้างกราฟแท่ง (Bar Chart)
    fig1 = px.histogram(df, x='Age', color='Gender', barmode='group',
                           title='จำนวนของแต่ละเพศในแต่ละช่วงอายุ')
    graph1_html = fig1.to_html(full_html=False)
    
    # สร้างกราฟวงกลม (Pie Chart)
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig2 = px.pie(gender_counts, names='Gender', values='Count',
                  title='สัดส่วนจำนวนของแต่ละเพศ')
    graph2_html = fig2.to_html(full_html=False)
    
    return render(request, 'graph.html', {'graph1_html': graph1_html, 'graph2_html': graph2_html})
