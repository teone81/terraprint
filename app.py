import streamlit as st
import numpy as np
import trimesh
import rasterio
import osmnx as ox
from shapely.geometry import Polygon, box
import zipfile
import io
import os

st.set_page_config(page_title="Generatore Modelli 3D Topografici", layout="wide")

def crea_base_solida(mesh, spessore_base=10):
    """
    Funzione per creare una base estrusa e unire la mesh originale,
    chiudendo il volume per la stampa 3D (operazione booleana di unione).
    """
    # Esempio di implementazione concettuale. Nella pratica trimesh
    # utilizzerà le booleane o estruderà i bordi della mesh aperta.
    # bounding_box = mesh.bounding_box.bounds
    # base = trimesh.creation.box(...)
    # solido_finale = mesh.union(base)
    pass

def esporta_3mf(meshes_dict):
    """
    Salva un file .3mf multi-parte partendo da un dizionario di mesh
    (es. mesh separate per acqua, roccia, neve, ecc. per il multicolor).
    """
    scene = trimesh.Scene()
    
    # Aggiunge ogni singola mesh alla scena per l'inclusione nel 3MF
    for name, mesh in meshes_dict.items():
        scene.add_geometry(mesh, node_name=name)
    
    # Esporta in formato 3MF
    return scene.export(file_type='3mf')

def esporta_stl_zip(meshes_dict):
    """
    Salva le mesh in singoli file STL, impacchettandole in uno ZIP
    pronto da caricare su uno slicer.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for name, mesh in meshes_dict.items():
            stl_data = mesh.export(file_type='stl')
            zip_file.writestr(f"{name}.stl", stl_data)
    return zip_buffer.getvalue()

def main():
    st.title("🏔️ Generatore di Modelli 3D Topografici")
    st.markdown("""
    Questa applicazione elabora modelli digitali del terreno (DTM) in formato GeoTIFF 
    dal Geoportale Nazionale e sovrappone i poligoni di copertura del suolo (OSM) 
    per generare file pronti per la stampa 3D multicromatica (.3mf o set di STL).
    """)

    st.sidebar.header("⚙️ Impostazioni Modello")
    spessore = st.sidebar.slider("Spessore base (mm)", min_value=1, max_value=50, value=10)
    z_scale = st.sidebar.slider("Esagerazione asse Z", min_value=1.0, max_value=5.0, value=1.0)
    
    st.sidebar.header("🌍 Importazione OSM (Copertura Suolo)")
    suolo_acqua = st.sidebar.checkbox("Specchi d'acqua / Fiumi", value=True)
    suolo_boschi = st.sidebar.checkbox("Prati / Foreste", value=True)
    suolo_neve = st.sidebar.checkbox("Roccia / Neve", value=False)

    dtm_file = st.file_uploader("Carica il file DTM (formato .tif / .tiff)", type=['tif', 'tiff'])

    if dtm_file:
        st.info("File DTM caricato correttamente in memoria.")
        
        if st.button("Genera il Modello 3D", type="primary"):
            with st.spinner("Lettura del DTM, estrazione dati OSM e generazione mesh in corso..."):
                
                # TODO: Implementare pipeline rasterio -> trimesh completa
                # Esempio logica rasterio:
                # with rasterio.open(dtm_file) as src:
                #     band = src.read(1)
                #     bounds = src.bounds
                #
                # Esempio scaricamento osm (osmnx):
                # tags = {'water': 'lake', 'natural': 'water'}
                # area = ox.features_from_bbox(bounds.top, bounds.bottom, bounds.right, bounds.left, tags)
                
                st.success("Modello topografico 3D generato con successo!")
                
                # Mockup Dati per l'interfaccia di scaricamento
                # (Generiamo mesh solide basilari solo per dimostrare la funzione esportazione)
                dummy_mesh_terreno = trimesh.creation.box((10, 10, 1))
                dummy_mesh_acqua = trimesh.creation.box((2, 2, 0.1))
                dummy_mesh_bosco = trimesh.creation.box((3, 3, 0.2))
                
                # Strutturiamo il set multicromatico per l'export
                meshes = {
                    "terreno_base": dummy_mesh_terreno
                }
                if suolo_acqua:
                    meshes["superfici_acqua"] = dummy_mesh_acqua
                if suolo_boschi:
                    meshes["superfici_boschi"] = dummy_mesh_bosco
                
                st.markdown("### Scarica i File Geometria")
                col1, col2 = st.columns(2)
                
                # --- Bottone Download 3MF ---
                try:
                    out_3mf = esporta_3mf(meshes)
                    col1.download_button(
                        label="⬇️ Scarica File Unico (.3mf)",
                        data=out_3mf,
                        file_name="modello_topografico.3mf",
                        mime="application/vnd.ms-3mfdocument",
                        use_container_width=True
                    )
                except Exception as e:
                    col1.error("Il formato 3MF richiede dipendenze plugin per trimesh non attive.")
                
                # --- Bottone Download ZIP (STL) ---
                out_zip = esporta_stl_zip(meshes)
                col2.download_button(
                    label="⬇️ Scarica Archivio ZIP (STL separati)",
                    data=out_zip,
                    file_name="modelli_stl.zip",
                    mime="application/zip",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
