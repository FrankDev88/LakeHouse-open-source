# 🚀 Local Data Lakehouse Project

Este proyecto implementa una arquitectura **DuckLake** de grado empresarial, optimizada para un despliegue ligero y eficiente en un solo nodo 

La filosofía central es **"Zero-Spark"**: Reemplazamos los pesados clústeres distribuidos por la arquitectura **DuckLake**, utilizando **DuckDB** con la extensión **DuckLake**, logrando latencias analíticas mínimas sin la sobrecarga de la JVM.

---

## 🏗️ Arquitectura del Sistema

![Arquitectura del Proyecto](arquitectura.webp)

### Diagrama Técnico (Mermaid)




## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Almacenamiento** | [MinIO](https://min.io/) | Data Lake compatible con S3 para persistencia de objetos. |
| **Motor de Cómputo** | [DuckDB](https://duckdb.org/) | Motor OLAP en memoria para procesamiento ultrarrápido. |
| **Gestor de Metadatos**| [DuckLake](https://github.com/marcelosousa/ducklake) | Extensión de DuckDB para gestión de metadatos y almacenamiento (reemplaza Delta Lake). |
| **Transformación** | [dbt](https://www.getdbt.com/) | Orquestación de lógica de negocio y linaje de datos. |
| **Orquestador** | [Airflow](https://airflow.apache.org/) | Gestión de workflows y scheduling de pipelines. |

---

## 📂 Estructura Medallion (Path-Based)

El proyecto sigue el patrón de diseño **Medallion Architecture**:

1.  **Bronze (Raw)**: Datos crudos capturados directamente del origen. Gestionado por DuckLake (`raw_lake`).
2.  **Silver (Clean)**: Datos filtrados y normalizados. Implementado mediante modelos dbt materializados en DuckLake (`silver_lake`).
3.  **Gold (Business)**: Agregaciones finales y métricas listas para consumo. Persistido y catalogado en DuckLake (`gold_lake`).

---


## 🧠 Conceptos Clave de esta Arquitectura

Para entender "cómo está el baile" en este proyecto, hay que entender la separación de roles:

### 1. El Almacén (MinIO)
Es el refrigerador. Aquí viven los datos físicos en la nube (S3). Si el motor explota, los datos están a salvo aquí, organizados por los catálogos de DuckLake.

### 2. El Catálogo (DuckLake)
Es el **Menú del Restaurante**. No contiene la comida, pero contiene las descripciones, los precios y sabe exactamente en qué parte del refrigerador está cada ingrediente. 
*   En esta arquitectura, usamos la extensión **DuckLake** para gestionar múltiples catálogos (`raw_lake`, `silver_lake`, `gold_lake`) de forma independiente.
*   Esto permite desacoplar los metadatos del motor y facilita la gestión de ambientes multicanal.

### 3. El Motor (DuckDB + DuckLake Extension)
Es el chef. Lee el menú (DuckLake), saca los ingredientes del refrigerador (MinIO), los cocina en la estufa (RAM) y te entrega el plato (Resultado del SQL).

### 4. El Orquestador de Lógica (dbt)
Es el **Libro de Recetas** y el **Capitán del Barco**. dbt no "toca" los datos, pero le dice a DuckDB exactamente en qué orden cocinar cada plato (`ref`). Él sabe que no puede haber "Gold" si antes no se terminó el "Silver".
