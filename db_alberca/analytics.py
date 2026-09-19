def calcular_kpis_dashboard(df_dash):
    """Calcula los totales generales del día a partir del DataFrame del dashboard."""
    if df_dash.empty:
        return 0, 0, 0, 0
    
    total_olimpica = df_dash['olimpica'].sum()
    total_calentamiento = df_dash['calentamiento'].sum()
    total_fosa = df_dash['fosa'].sum()
    total_general = df_dash['total_hora'].sum()
    
    return total_olimpica, total_calentamiento, total_fosa, total_general