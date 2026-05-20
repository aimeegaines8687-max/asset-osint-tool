import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyvis.network import Network
import streamlit.components.v1 as components

# ================= 模拟数据库 (实际应用时，这里改为调用 API) =================
MOCK_DATA = {
    "张三": {
        "relatives": [
            {"name": "李四", "relation": "配偶", "assets": ["上海浦东某别墅", "新加坡某公寓"]},
            {"name": "王五", "relation": "助手", "assets": ["北京朝阳区某写字楼"]}
        ],
        "companies": [
            {"name": "某贸易有限公司", "role": "实际控制人", "share": "40%", "linked_asset": "办公大楼A"},
            {"name": "某投资咨询公司", "role": "影子股东", "share": "15%", "linked_asset": "海外信托账户"}
        ],
        "locations": [
            {"name": "上海浦东某别墅", "lat": 31.2304, "lon": 121.4737, "detail": "价值 8000万，登记在李四名下"},
            {"name": "北京朝阳区某写字楼", "lat": 39.9042, "lon": 116.4074, "detail": "价值 5000万，由王五代持"},
            {"name": "办公大楼A", "lat": 31.2200, "lon": 121.4800, "detail": "企业资产，用于洗钱"}
        ]
    }
}

# ================= 核心功能函数 =================

def generate_relation_graph(target_name):
    """生成关系网络图"""
    net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    if target_name not in MOCK_DATA:
        return None
        
    data = MOCK_DATA[target_name]
    net.add_node(target_name, label=target_name, color="red", size=30)
    
    # 添加亲属及其资产
    for rel in data["relatives"]:
        net.add_node(rel["name"], label=rel["name"], color="blue")
        net.add_edge(target_name, rel["name"], label=rel["relation"])
        for asset in rel["assets"]:
            net.add_node(asset, label=asset, color="green")
            net.add_edge(rel["name"], asset, label="持有")
            
    # 添加公司及其资产
    for comp in data["companies"]:
        net.add_node(comp["name"], label=comp["name"], color="yellow")
        net.add_edge(target_name, comp["name"], label=comp["role"])
        net.add_node(comp["linked_asset"], label=comp["linked_asset"], color="green")
        net.add_edge(comp["name"], comp["linked_asset"], label="关联")
        
    net.save_graph("graph.html")
    return "graph.html"

def generate_asset_map(target_name):
    """生成资产分布地图"""
    if target_name not in MOCK_DATA:
        return None
        
    m = folium.Map(location=[35.0, 110.0], zoom_start=4)
    for loc in MOCK_DATA[target_name]["locations"]:
        folium.Marker(
            [loc["lat"], loc["lon"]], 
            popup=f"{loc['name']}: {loc['detail']}", 
            tooltip=loc['name'],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    return m

# ================= Streamlit UI 界面 =================

st.set_page_config(page_title="OSINT 资产关联分析系统", layout="wide")

st.title("🔍 地方官员不良资产关联分析系统 (OSINT Prototype)")
st.warning("⚠️ 本工具基于公开情报分析逻辑。请确保您的操作符合当地法律法规。")

target = st.text_input("请输入目标人物姓名:", placeholder="例如：张三")

if target:
    if target in MOCK_DATA:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🌐 资产控制关系图谱")
            graph_file = generate_relation_graph(target)
            components.html(open(graph_file, 'r', encoding='utf-8').read(), height=550)
            st.caption("红色：目标 | 蓝色：关联人 | 黄色：壳公司 | 绿色：实物资产")

        with col2:
            st.subheader("📍 资产物理位置分布")
            asset_map = generate_asset_map(target)
            st_folium(asset_map, width=700, height=550)
            
        st.divider()
        st.subheader("📋 资产细节明细表")
        df_assets = pd.DataFrame(MOCK_DATA[target]["locations"])
        st.table(df_assets)
        
    else:
        st.error("未在公开数据源中找到该人物的相关资产线索，请尝试其他姓名或更新数据池。")
