import pandas as pd
import plotly.express as px
from django.shortcuts import render
import os

def show_graph(request):
    # กำหนดเส้นทางไปยังไฟล์ CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'data.csv')
    
    # อ่านข้อมูลจากไฟล์ CSV
    df = pd.read_csv(csv_path)
    
    # ตรวจสอบว่าคอลัมน์ที่ต้องการมีอยู่ใน DataFrame
    if 'Gender' in df.columns and 'Age' in df.columns:
        # สร้างกราฟแท่งด้วย Plotly
        fig = px.histogram(df, x='Age', color='Gender', barmode='group',
                           title='จำนวนของแต่ละเพศในแต่ละช่วงอายุ')
        
        # แปลงกราฟเป็น HTML
        graph_html = fig.to_html(full_html=False)
    else:
        graph_html = "<p>ไม่พบคอลัมน์ 'Gender' หรือ 'Age' ในไฟล์ข้อมูล</p>"
    
    return render(request, 'graph.html', {'graph_html': graph_html})
