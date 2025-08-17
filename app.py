import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import plotly.express as px

# ---- Sayfa Yapılandırması ----
st.set_page_config(layout="wide", page_title="Türkiye Veri Portalı")

# --- Veri Yükleme ve Zenginleştirme ---
@st.cache_data
def veri_yukle_ve_hazirla():
    df = pd.read_csv('turkiye_il_verileri.csv')
    geojson_yolu = 'tr-cities-utf8.json'
    with open(geojson_yolu, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Bölge verisini ekle
    bolge_map = {
        'Adana': 'Akdeniz', 'Antalya': 'Akdeniz', 'Burdur': 'Akdeniz', 'Hatay': 'Akdeniz', 'Isparta': 'Akdeniz', 'Kahramanmaraş': 'Akdeniz', 'Mersin': 'Akdeniz', 'Osmaniye': 'Akdeniz',
        'Adıyaman': 'Güneydoğu Anadolu', 'Batman': 'Güneydoğu Anadolu', 'Diyarbakır': 'Güneydoğu Anadolu', 'Gaziantep': 'Güneydoğu Anadolu', 'Kilis': 'Güneydoğu Anadolu', 'Mardin': 'Güneydoğu Anadolu', 'Siirt': 'Güneydoğu Anadolu', 'Şanlıurfa': 'Güneydoğu Anadolu', 'Şırnak': 'Güneydoğu Anadolu',
        'Ağrı': 'Doğu Anadolu', 'Ardahan': 'Doğu Anadolu', 'Bingöl': 'Doğu Anadolu', 'Bitlis': 'Doğu Anadolu', 'Elazığ': 'Doğu Anadolu', 'Erzincan': 'Doğu Anadolu', 'Erzurum': 'Doğu Anadolu', 'Hakkâri': 'Doğu Anadolu', 'Iğdır': 'Doğu Anadolu', 'Kars': 'Doğu Anadolu', 'Malatya': 'Doğu Anadolu', 'Muş': 'Doğu Anadolu', 'Tunceli': 'Doğu Anadolu', 'Van': 'Doğu Anadolu',
        'Ankara': 'İç Anadolu', 'Aksaray': 'İç Anadolu', 'Çankırı': 'İç Anadolu', 'Eskişehir': 'İç Anadolu', 'Karaman': 'İç Anadolu', 'Kayseri': 'İç Anadolu', 'Kırıkkale': 'İç Anadolu', 'Kırşehir': 'İç Anadolu', 'Konya': 'İç Anadolu', 'Nevşehir': 'İç Anadolu', 'Niğde': 'İç Anadolu', 'Sivas': 'İç Anadolu', 'Yozgat': 'İç Anadolu',
        'Aydın': 'Ege', 'Afyonkarahisar': 'Ege', 'Denizli': 'Ege', 'İzmir': 'Ege', 'Kütahya': 'Ege', 'Manisa': 'Ege', 'Muğla': 'Ege', 'Uşak': 'Ege',
        'Amasya': 'Karadeniz', 'Artvin': 'Karadeniz', 'Bartın': 'Karadeniz', 'Bayburt': 'Karadeniz', 'Bolu': 'Karadeniz', 'Çorum': 'Karadeniz', 'Düzce': 'Karadeniz', 'Giresun': 'Karadeniz', 'Gümüşhane': 'Karadeniz', 'Karabük': 'Karadeniz', 'Kastamonu': 'Karadeniz', 'Ordu': 'Karadeniz', 'Rize': 'Karadeniz', 'Samsun': 'Karadeniz', 'Sinop': 'Karadeniz', 'Tokat': 'Karadeniz', 'Trabzon': 'Karadeniz', 'Zonguldak': 'Karadeniz',
        'Balıkesir': 'Marmara', 'Bilecik': 'Marmara', 'Bursa': 'Marmara', 'Çanakkale': 'Marmara', 'Edirne': 'Marmara', 'İstanbul': 'Marmara', 'Kırklareli': 'Marmara', 'Kocaeli': 'Marmara', 'Sakarya': 'Marmara', 'Tekirdağ': 'Marmara', 'Yalova': 'Marmara'
    }
    df['Bölge'] = df['Ad'].map(bolge_map)
    
    # Pandas verisini GeoJSON içine işleme (Tooltip için gerekli)
    df_indexed = df.set_index('Ad')
    for feature in geojson_data['features']:
        il_adi = feature['properties']['name']
        if il_adi in df_indexed.index:
            feature['properties'].update(df_indexed.loc[il_adi].to_dict())

    return df, geojson_data

# Veriyi yükle ve hazırla
df_iller, geojson_data = veri_yukle_ve_hazirla()

# --- STİL AYARLARI ---
sayi_formati = {
    'Alan_km2': '{:,.0f} km²', 'Nufus_2021': '{:,.0f}', 'Nufus_Yogunlugu': '{:,.2f}',
    'Plaka_Kodu': '{:d}', 'Telefon_Kodu': '{:.0f}', 'Rakim_m': '{:,.0f} m',
    'Toplam_Nüfus': '{:,.0f}', 'Ortalama_Rakım': '{:.0f} m', 'Ortalama_Nüfus_Yoğunluğu': '{:.2f}'
}
tablo_stili = {'font-size': '16px'}

# --- ARAYÜZ ---
if df_iller is not None:
    st.title('🇹🇷 Türkiye İl Verileri Analiz Portalı')

    # --- KENAR ÇUBUĞU (SIDEBAR) ---
    st.sidebar.title('Analiz Menüsü')
    analiz_secimi = st.sidebar.selectbox(
        'Lütfen bir analiz türü seçin:',
        ['Genel Bakış ve Harita', "Sıralamalar ve 'En'ler", 'Bölgesel Analiz', 'İlişki Analizi (Korelasyon)']
    )

    # --- ANA EKRAN ---
    if analiz_secimi == 'Genel Bakış ve Harita':
        st.header('İnteraktif Veri Haritası')

        heatmap_ayarlari = {
            'Nüfus Yoğunluğu': {'sutun': 'Nufus_Yogunlugu', 'renk': 'YlOrRd', 'efsane': 'Nüfus Yoğunluğu'},
            'Nüfus (2021)': {'sutun': 'Nufus_2021', 'renk': 'PuBuGn', 'efsane': 'Toplam Nüfus'},
            'Yüz Ölçümü': {'sutun': 'Alan_km2', 'renk': 'Greens', 'efsane': 'Yüz Ölçümü'},
            'Rakım': {'sutun': 'Rakim_m', 'renk': 'Blues', 'efsane': 'Rakım'}
        }
        
        heatmap_kriteri = st.selectbox('Haritada görmek istediğiniz veriyi seçin:', list(heatmap_ayarlari.keys()))
        secilen_ayar = heatmap_ayarlari[heatmap_kriteri]
        sutun_adi = secilen_ayar['sutun']
        
        turkiye_merkez = [39, 35]
        m = folium.Map(location=turkiye_merkez, zoom_start=6, tiles='CartoDB positron')
        
        # Zengin renkler için KANTİL ölçeği kullan
        threshold_scale = df_iller[sutun_adi].quantile([i/10 for i in range(11)]).tolist()
        
        folium.Choropleth(
            geo_data=geojson_data,
            data=df_iller,
            columns=['Ad', sutun_adi],
            key_on='feature.properties.name',
            threshold_scale=threshold_scale,
            fill_color=secilen_ayar['renk'],
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=secilen_ayar['efsane'],
            nan_fill_color="white"
        ).add_to(m)

        # --- YENİ BÖLÜM: GÖSTERGEDEKİ YAZILARI GİZLEME ---
        css_fix = """
        <style>
            .legend.leaflet-control text {
                display: none;
            }
        </style>
        """
        m.get_root().html.add_child(folium.Element(css_fix))
        # --- YENİ BÖLÜM SONU ---
        
        tooltip_sutunlar = ['name', 'Bölge', 'Nufus_2021', 'Alan_km2', 'Rakim_m', 'Nufus_Yogunlugu']
        tooltip_basliklar = ['İl:', 'Bölge:', 'Nüfus (2021):', 'Alan (km²):', 'Rakım (m):', 'Nüfus Yoğunluğu:']

        folium.features.GeoJson(
            geojson_data,
            tooltip=folium.features.GeoJsonTooltip(
                fields=tooltip_sutunlar, aliases=tooltip_basliklar,
                localize=True, sticky=False, labels=True,
                style="background-color: #F0EFEF; border: 2px solid black; border-radius: 3px; box-shadow: 3px;"
            ),
            style_function=lambda x: {'weight':0.5, 'color':'black', 'fillOpacity':0}
        ).add_to(m)
        
        with st.spinner('Harita yükleniyor...'):
            st_folium(m, width='100%', height=500, key=heatmap_kriteri)
        
        st.header("Veri Setinin Tamamı")
        st.dataframe(df_iller.style.format(sayi_formati).set_properties(**tablo_stili))
    
    elif analiz_secimi == "Sıralamalar ve 'En'ler":
        st.header("İllerin 'En'leri")
        kriter = st.selectbox('Hangi kritere göre sıralamak istersiniz?',
            ['Nüfus (En Yüksek)', 'Nüfus (En Düşük)', 'Yüz Ölçümü (En Geniş)', 'Yüz Ölçümü (En Küçük)', 'Rakım (En Yüksek)', 'Rakım (En Düşük)'])
        siralama_kriterleri = {
            'Nüfus (En Yüksek)': ('Nufus_2021', False), 'Nüfus (En Düşük)': ('Nufus_2021', True),
            'Yüz Ölçümü (En Geniş)': ('Alan_km2', False), 'Yüz Ölçümü (En Küçük)': ('Alan_km2', True),
            'Rakım (En Yüksek)': ('Rakim_m', False), 'Rakım (En Düşük)': ('Rakim_m', True)}
        sutun, artan_mi = siralama_kriterleri[kriter]
        df_sirali = df_iller.sort_values(by=sutun, ascending=artan_mi).dropna(subset=[sutun]).head(10)
        st.write(f"**{kriter} 10 İl:**")
        st.dataframe(df_sirali[['Ad', sutun]].style.format(sayi_formati).set_properties(**tablo_stili))

    elif analiz_secimi == 'Bölgesel Analiz':
        st.header("Coğrafi Bölgelere Göre Analizler")
        bolgesel_df = df_iller.groupby('Bölge').agg(
            Toplam_Nüfus=('Nufus_2021', 'sum'), Ortalama_Rakım=('Rakim_m', 'mean'),
            Ortalama_Nüfus_Yoğunluğu=('Nufus_Yogunlugu', 'mean'), İl_Sayısı=('Ad', 'count')).reset_index()
        st.write("Bölgelerin Özet Verileri:")
        st.dataframe(bolgesel_df.style.format(sayi_formati).set_properties(**tablo_stili))
        fig = px.bar(bolgesel_df.sort_values('Toplam_Nüfus', ascending=False), 
                     x='Bölge', y='Toplam_Nüfus', title='Bölgelerin Toplam Nüfusları',
                     labels={'Bölge': 'Coğrafi Bölge', 'Toplam_Nüfus': 'Toplam Nüfus'})
        st.plotly_chart(fig, use_container_width=True)

    elif analiz_secimi == 'İlişki Analizi (Korelasyon)':
        st.header("Veriler Arasındaki İlişkileri Keşfet")
        st.write("Bu bölümde, iki farklı veri arasındaki ilişkiyi bir saçılım grafiği üzerinde görebilirsiniz.")
        numeric_columns = ['Nufus_2021', 'Alan_km2', 'Nufus_Yogunlugu', 'Rakim_m', 'Plaka_Kodu']
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox('X Ekseni İçin Veri Seçin:', numeric_columns, index=4)
        with col2:
            y_axis = st.selectbox('Y Ekseni İçin Veri Seçin:', numeric_columns, index=2)
        fig = px.scatter(df_iller, x=x_axis, y=y_axis, hover_name='Ad',
                         title=f'{x_axis} ve {y_axis} Arasındaki İlişki',
                         labels={x_axis: x_axis.replace('_', ' ').title(), y_axis: y_axis.replace('_', ' ').title()})
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.title("🇹🇷 Türkiye İl Verileri Analiz Portalı")
    st.error("Veri yükleme aşamasında bir hata oluştuğu için uygulama başlatılamadı.")