import streamlit as st
import numpy as np
import time
import json
import os

# --- 💾 SISTEMA DE GUARDADO DE PROGRESO ---
ARCHIVO_DATOS = "progreso_estudiantes.json"

def cargar_progreso_global():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_progreso_usuario(nombre, datos_usuario):
    progreso_total = cargar_progreso_global()
    datos_guardar = datos_usuario.copy()
    datos_guardar["aprobados"] = list(datos_usuario["aprobados"])
    
    progreso_total[nombre.lower().strip()] = datos_guardar
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(progreso_total, f, ensure_ascii=False, indent=4)

# --- 🔊 CONFIGURACIÓN DE EFECTOS DE SONIDO SINTÉTICOS ---
def reproducir_sonido(tipo):
    sr = 12000
    t = np.linspace(0, 0.3 if tipo=="acierto" else 0.4, int(sr * (0.3 if tipo=="acierto" else 0.4)))
    frecuencia = 880 if tipo=="acierto" else 120
    if tipo == "acierto":
        onda = np.sin(2 * np.pi * frecuencia * t) * np.exp(-15 * t)
    else:
        onda = np.sign(np.sin(2 * np.pi * frecuencia * t)) * np.exp(-4 * t)
    st.audio(onda, sample_rate=sr, autoplay=True)

# --- 🧠 GENERADOR AUTOMÁTICO DE 50 MINIJUEGOS POR MATERIA ---
banco_materias = {}
materias_secundaria = {
    "Matematicas": "🧮 Matemáticas", "Historia": "🏛️ Historia",
    "Ciencias": "🔬 Ciencias", "Geografia": "🌍 Geografía"
}

for clave, texto in materias_secundaria.items():
    banco_materias[clave] = {"menu_texto": texto, "juegos": []}
    for i in range(1, 51):
        if clave == "Matematicas":
            num1, num2 = i * 2, i + 5
            banco_materias[clave]["juegos"].append({
                "titulo": f"Ecuaciones Básicas - Nivel {i}",
                "explicacion": f"Suma {num1} más {num2} para obtener el valor de X.",
                "pregunta": f"¿Cuánto vale X en: X = {num1} + {num2}?",
                "opciones": [str(num1+num2), str(num1+num2+3), str(num1+num2-2)],
                "correcta": str(num1+num2)
            })
        elif clave == "Historia":
            año = 1400 + i
            banco_materias[clave]["juegos"].append({
                "titulo": f"Línea del Tiempo - Nivel {i}",
                "explicacion": f"El año {año} pertenece a una época de grandes cambios.",
                "pregunta": f"¿A qué siglo pertenece el año {año}?",
                "opciones": ["Siglo XV", "Siglo XVI", "Siglo XVII"],
                "correcta": "Siglo XV" if año < 1500 else "Siglo XVI"
            })
        elif clave == "Ciencias":
            banco_materias[clave]["juegos"].append({
                "titulo": f"Elementos y Células - Nivel {i}",
                "explicacion": f"El hidrógeno (H) tiene exactamente 1 protón en su núcleo.",
                "pregunta": f"¿Cuántos protones tiene el Hidrógeno en el nivel {i}?",
                "opciones": ["1", "2", "3"], "correcta": "1"
            })
        elif clave == "Geografia":
            distancia = i * 100
            banco_materias[clave]["juegos"].append({
                "titulo": f"Capas Atmosféricas - Nivel {i}",
                "explicacion": f"La troposfera llega hasta los primeros kilómetros.",
                "pregunta": f"Si un cohete sube {distancia} km, ¿en qué capa está?",
                "opciones": ["Troposfera", "Estratosfera", "Espacio Exterior"],
                "correcta": "Troposfera" if distancia < 12 else "Espacio Exterior" if distancia > 50 else "Estratosfera"
            })

# --- 💾 CONFIGURACIÓN DE AVATARES ---
lista_avatares_config = {
    "👶 Recluta": {"emoji": "👶", "nivel_req": 1},
    "🧠 Estudiante": {"emoji": "🧠", "nivel_req": 2},
    "🚀 Explorador": {"emoji": "🚀", "nivel_req": 3},
    "🧙 Mago": {"emoji": "🧙", "nivel_req": 4},
    "🔥 Maestro": {"emoji": "🔥", "nivel_req": 5}
}

# --- CONTROL DE SESIÓN ---
if "usuario" not in st.session_state:
    st.session_state.usuario = {"nombre": "", "xp": 0, "nivel": 1, "aprobados": set(), "avatar_emoji": "👶", "avatar_nombre": "👶 Recluta"}

# --- INTERFAZ GRÁFICA ---
st.title("🏫 Academia de Secundaria Interactiva")

if st.session_state.usuario["nombre"] == "":
    nombre_input = st.text_input("Introduce tu nombre para comenzar o continuar tu partida:")
    if st.button("Ingresar a la Escuela 🚀"):
        if nombre_input.strip() != "":
            nombre_limpio = nombre_input.strip()
            db_global = cargar_progreso_global()
            
            if nombre_limpio.lower() in db_global:
                datos_saved = db_global[nombre_limpio.lower()]
                st.session_state.usuario = {
                    "nombre": datos_saved["nombre"],
                    "xp": datos_saved["xp"],
                    "nivel": datos_saved["nivel"],
                    "aprobados": set(datos_saved["aprobados"]),
                    "avatar_emoji": datos_saved.get("avatar_emoji", "👶"),
                    "avatar_nombre": datos_saved.get("avatar_nombre", "👶 Recluta")
                }
                st.toast(f"✨ ¡Bienvenido de vuelta, {datos_saved['nombre']}!")
            else:
                st.session_state.usuario["nombre"] = nombre_limpio
                guardar_progreso_usuario(nombre_limpio, st.session_state.usuario)
                st.toast("👋 ¡Perfil nuevo creado!")
                
            time.sleep(1)
            st.rerun()
else:
    u = st.session_state.usuario
    juegos_ganados = len(u["aprobados"])
    porcentaje = int((juegos_ganados / 200) * 100)
    
    st.sidebar.markdown("### ⚙️ Configuración")
    
    opciones_visuales_avatar = []
    mapeo_opciones = {}
    for nombre, datos in lista_avatares_config.items():
        if u["nivel"] >= datos["nivel_req"]:
            texto_visual = f"{datos['emoji']} {nombre}"
        else:
            texto_visual = f"🔒 {nombre} (Req. Nivel {datos['nivel_req']})"
        opciones_visuales_avatar.append(texto_visual)
        mapeo_opciones[texto_visual] = nombre

    indice_defecto = 0
    if u["avatar_nombre"] in lista_avatares_config:
        for idx, texto in enumerate(opciones_visuales_avatar):
            if mapeo_opciones[texto] == u["avatar_nombre"]:
                indice_defecto = idx
                break

    avatar_seleccionado = st.sidebar.selectbox("Elige tu foto de perfil:", opciones_visuales_avatar, index=indice_defecto)
    nombre_real_avatar = mapeo_opciones[avatar_seleccionado]
    requisitos = lista_avatares_config[nombre_real_avatar]
    
    if u["nivel"] >= requisitos["nivel_req"]:
        if u["avatar_emoji"] != requisitos["emoji"]:
            u["avatar_emoji"] = requisitos["emoji"]
            u["avatar_nombre"] = nombre_real_avatar
            guardar_progreso_usuario(u["nombre"], u)
    else:
        st.sidebar.error(f"⚠️ Requiere Nivel {requisitos['nivel_req']}.")

    st.sidebar.markdown("---")
    st.sidebar.html(f"<h1 style='text-align: center; font-size: 80px; margin: 0;'>{u['avatar_emoji']}</h1>")
    st.sidebar.markdown(f"### 👤 Estudiante: {u['nombre']}")
    st.sidebar.markdown(f"🌟 **Nivel {u['nivel']}** | ✨ {u['xp']} XP")
    st.sidebar.progress(juegos_ganados / 200)
    st.sidebar.caption(f"Completado: {juegos_ganados}/200 ({porcentaje}%)")
    
    if st.sidebar.button("Cerrar Sesión 🚪"):
        st.session_state.clear()
        st.rerun()
        
    materia_sel = st.selectbox("Selecciona una materia:", list(banco_materias.keys()), format_func=lambda x: materias_secundaria[x])
    
    nivel_actual = 1
    for i in range(1, 51):
        if f"{materia_sel}_{i}" not in u["aprobados"]:
            nivel_actual = i
            break
            
    if f"{materia_sel}_50" in u["aprobados"]:
        st.balloons()
        st.success("¡Completaste esta materia!")
    else:
        juego = banco_materias[materia_sel]["juegos"][nivel_actual - 1]
        st.subheader(f"📚 {juego['titulo']} ({nivel_actual}/50)")
        st.info(juego['explicacion'])
        
        respuesta = st.radio(juego['pregunta'], juego['opciones'], index=None)
        
        if st.button("Comprobar Respuesta ✔️"):
            if respuesta == juego['correcta']:
                st.session_state.usuario["aprobados"].add(f"{materia_sel}_{nivel_actual}")
                st.session_state.usuario["xp"] += 1
                
                nuevo_nivel = (st.session_state.usuario["xp"] // 50) + 1
                if nuevo_nivel > st.session_state.usuario["nivel"]:
                    st.session_state.usuario["nivel"] = nuevo_nivel
                    st.toast("🎉 ¡Subiste de nivel!")
                
                guardar_progreso_usuario(u["nombre"], st.session_state.usuario)
                st.success("¡Correcto! +1 XP")
                reproducir_sonido("acierto")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrecto. Intenta de nuevo.")
                reproducir_sonido("error")
                
