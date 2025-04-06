import streamlit as st
import json
import re
import pandas as pd
import io
from datetime import datetime

# Заголовок приложения
st.title("📄 Визуализация анализа правоотношений")
st.write("Вставьте JSON-результат анализа правоотношений для визуализации")

# Текстовое поле для ввода JSON
input_json = st.text_area(
    "Введите JSON для визуализации", 
    height=300,
    placeholder="Вставьте JSON-результат здесь..."
)

if input_json:
    try:
        # Пытаемся распарсить JSON
        result = json.loads(input_json)
        
        # Обрабатываем и выводим результат
        all_rights_data = []
        all_duties_data = []
        all_goals = []
        all_objects = []
        all_subjects = []

        for relation in result:
            with st.expander(f"Источник описания правоотношения: {relation.get('источник', 'Не указан')}"):
                st.markdown(f"**Источник:** {relation.get('источник', 'Не указан')}")
                st.markdown(f"**Фрагмент текста:** _{relation.get('фрагмент_текста', 'Не указан')}_")
                
                # Блок "Потребности и цели"
                st.subheader("Потребности-цели")
                for goal in relation.get('правоотношение', {}).get('потребности_цели', []):
                    st.markdown(f"- {goal}")
                    all_goals.append(goal)
                
                # Разделение на две колонки: Объекты и Субъекты
                cols = st.columns(2)
                
                with cols[0]:
                    st.subheader("Предметы")
                    for obj in relation.get('правоотношение', {}).get('объекты', []):
                        st.markdown(f"- {obj}")
                        all_objects.append(obj)
                
                with cols[1]:
                    st.subheader("Субъекты")
                    for subj in relation.get('правоотношение', {}).get('субъекты', []):
                        st.markdown(f"""
                        - **{subj.get('название', 'Не указано')}** ({subj.get('тип', 'Не указан')})
                        """)
                        all_subjects.append(f"{subj.get('название', 'Не указано')} ({subj.get('тип', 'Не указан')})")
                
                # Таблица прав
                st.subheader("Права")
                rights_data = []
                for right in relation.get('правоотношение', {}).get('права', []):
                    for obligation in right.get('встречные_обязанности', []):
                        rights_data.append({
                            "Источник": relation.get('источник', 'Не указан'),
                            "Субъект права": right.get('субъект_права', {}).get('название', 'Не указан'),
                            "Право": right.get('описание_права', 'Не указано'),
                            "Встречная обязанность": obligation.get('описание_обязанности', 'Не указана'),
                            "Субъект обязательств": obligation.get('субъект_обязанности', {}).get('название', 'Не указан')
                        })
                rights_df = pd.DataFrame(rights_data)
                st.dataframe(rights_df, use_container_width=True)
                all_rights_data.extend(rights_data)
                
                # Таблица обязанностей
                st.subheader("Обязанности")
                duties_data = []
                for duty in relation.get('правоотношение', {}).get('обязанности', []):
                    for right in duty.get('обеспечиваемые_права', []):
                        duties_data.append({
                            "Источник": relation.get('источник', 'Не указан'),
                            "Субъект обязательств": duty.get('субъект_обязанности', {}).get('название', 'Не указан'),
                            "Обязанность": duty.get('описание_обязанности', 'Не указано'),
                            "Обеспечивает право": right.get('описание_права', 'Не указано'),
                            "Субъект права": right.get('субъект_права', {}).get('название', 'Не указан')
                        })
                duties_df = pd.DataFrame(duties_data)
                st.dataframe(duties_df, use_container_width=True)
                all_duties_data.extend(duties_data)

        # Кнопка для экспорта в Excel
        if st.button("Сформировать и скачать Excel файл"):
            # Создаем Pandas DataFrames
            rights_df = pd.DataFrame(all_rights_data)
            duties_df = pd.DataFrame(all_duties_data)
            goals_df = pd.DataFrame({"Потребности и цели": all_goals})
            objects_df = pd.DataFrame({"Предметы": all_objects})
            subjects_df = pd.DataFrame({"Субъекты": all_subjects})

            # Создаем Excel writer
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                rights_df.to_excel(writer, sheet_name='Права', index=False)
                duties_df.to_excel(writer, sheet_name='Обязанности', index=False)
                goals_df.to_excel(writer, sheet_name='Потребности-цели', index=False)
                objects_df.to_excel(writer, sheet_name='Предметы (объекты)', index=False)
                subjects_df.to_excel(writer, sheet_name='Субъекты', index=False)

            # Формируем имя файла
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"анализ_правоотношений_{now}.xlsx"

            # Предлагаем файл для скачивания
            st.download_button(
                label="Скачать сведения в Excel",
                data=excel_buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.ms-excel"
            )

    except json.JSONDecodeError as e:
        st.error(f"Ошибка: неверный формат JSON. Проверьте введенные данные. Детали ошибки: {e}")
    except Exception as e:
        st.error(f"Ошибка при обработке данных: {str(e)}")
