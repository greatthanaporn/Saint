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

    life_expectancy_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Life-Expectancy-Data-Averaged.csv')
        # อ่านข้อมูลจากไฟล์ Life Expectancy
    life_expectancy_df = pd.read_csv(life_expectancy_csv_path)
        # สร้าง Bar Chart สำหรับ Life Expectancy
    fig3 = px.bar(
        life_expectancy_df,
        x='Country',  # ประเทศบนแกน X
        y='Life_expectancy',  # อายุขัยบนแกน Y
        color='Region',  # สีแสดง Region
        title='การกระจายของ Life Expectancy ในแต่ละประเทศ',
        labels={'Life_expectancy': 'Life Expectancy', 'Country': 'Country'},  # ชื่อแกน
    )
    graph3_html = fig3.to_html(full_html=False)
    
    return render(request, 'graph.html', {'graph1_html': graph1_html, 'graph2_html': graph2_html ,'graph3_html': graph3_html})



def box(request):
    # อ่านข้อมูลจากไฟล์ CSV
    df = pd.read_csv('D:\DSTbox\Saint\myproject\saint\data\Pokemon.csv')

    # สร้างกราฟแรก
    fig1 = px.box(df, x='Generation', y='Total', title='การกระจายของ Total ในแต่ละ Generation')
    graph1 = fig1.to_html(full_html=False)

    # สร้างกราฟที่สอง
    fig2 = px.box(df, x='Legendary', y='Total', title='การกระจายของ Total ระหว่าง Pokémon ธรรมดาและ Legendary')
    graph2 = fig2.to_html(full_html=False)

    return render(request, 'boxplot.html', {'graph1': graph1, 'graph2': graph2})


