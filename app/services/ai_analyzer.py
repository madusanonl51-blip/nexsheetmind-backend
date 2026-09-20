from app.core.models import CompareResponse, AnalysisResponse

def generate_insights(compare_response: CompareResponse) -> AnalysisResponse:
    accuracy = compare_response.accuracy_pct
    if accuracy < 90:
        severity = 'high'
    elif accuracy < 95:
        severity = 'medium'
    else:
        severity = 'low'
        
    anomalies = []
    recommendations = []
    
    for col, stats in compare_response.column_stats.items():
        total_col_comparisons = stats['matched'] + stats['mismatched']
        if total_col_comparisons > 0:
            mismatch_rate = stats['mismatched'] / total_col_comparisons
            if mismatch_rate > 0.5:
                anomalies.append(f"Column '{col}' has a high mismatch rate of {mismatch_rate*100:.1f}%.")
                
        if stats['missing_left'] > 0 and stats['matched'] == 0 and stats['mismatched'] == 0:
            anomalies.append(f"Column '{col}' is entirely missing in the first file.")
            
    if compare_response.missing_left > 0 or compare_response.missing_right > 0:
        recommendations.append("Check if the key column has duplicates or unmatched identifiers across both sheets.")
        
    if "date" in str(compare_response.data_type_distribution).lower():
        recommendations.append("Review date formats to ensure they match across both sheets, as discrepancies may be due to formatting.")
        
    if len(recommendations) == 0:
        recommendations.append("Regularly audit data sources for consistency.")
        
    summary = f"Analysis of {compare_response.total_rows} rows reveals {accuracy:.1f}% data accuracy. Found {compare_response.mismatched} row discrepancies across {len(compare_response.column_stats)} compared columns."
    
    return AnalysisResponse(
        summary=summary,
        anomalies=anomalies,
        recommendations=recommendations,
        severity=severity
    )
