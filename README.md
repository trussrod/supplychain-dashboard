## Supply Chain Analytics Dashboard  
**Python | Streamlit | Supabase | Plotly**  
[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-blue)](https://supplychain-kpi.onrender.com) | [![Code](https://img.shields.io/badge/Code-GitHub-black)](https://github.com/trussrod/supplychain-dashboard)  

### Key Features  
- **Automated KPI Calculation**: Computes on-time delivery rates and inventory turnover from raw CSV data  
- **Interactive Visualizations**: Sankey diagrams for shipping lanes, Plotly trend charts  
- **Cloud-Native Architecture**: Supabase PostgreSQL backend with Render hosting  
- **Data Validation**: Robust CSV schema enforcement with user-friendly error messaging  

### Technical Stack  
- **Backend**: Python (Pandas, NumPy)  
- **Frontend**: Streamlit (with custom CSS theming)  
- **Database**: Supabase (PostgreSQL)  
- **Visualization**: Plotly (Sankey, line charts)  
- **DevOps**: Render CI/CD, secrets management  

### Learning Outcomes  
✔ Built end-to-end data pipeline from CSV ingestion to cloud storage  
✔ Solved dependency conflicts in Python package management  
✔ Implemented dark/light mode responsive design  
✔ Developed reusable data validation framework  

### Project Structure  
```bash
supplychain-dashboard/
├── app.py               # Main Streamlit application
├── requirements.txt     # Dependency specs
├── generate_data.py     # Test data generator
└── .streamlit/          # Config
    └── secrets.toml     # API keys (ignored in Git)
