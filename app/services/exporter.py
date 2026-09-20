import os
import pandas as pd
from app.core.models import CompareResponse, AnalysisResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def export_to_excel(compare_response: CompareResponse, output_path: str) -> str:
    summary_data = {
        'Metric': ['Total Rows', 'Matched', 'Mismatched', 'Missing Left', 'Missing Right', 'Accuracy'],
        'Value': [
            compare_response.total_rows,
            compare_response.matched,
            compare_response.mismatched,
            compare_response.missing_left,
            compare_response.missing_right,
            f"{compare_response.accuracy_pct:.2f}%"
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    
    diff_data = []
    for diff in compare_response.row_diffs:
        diff_data.append({
            'Row Index': diff.row_index,
            'Column': diff.column,
            'File A Value': diff.value_a,
            'File B Value': diff.value_b,
            'Status': diff.status
        })
    df_diffs = pd.DataFrame(diff_data)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        df_diffs.to_excel(writer, sheet_name='Comparison', index=False)
        if not df_diffs.empty:
            df_mismatches = df_diffs[df_diffs['Status'] == 'mismatch']
            df_mismatches.to_excel(writer, sheet_name='Mismatches Only', index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name='Mismatches Only')
            
    return output_path

def export_to_pdf(compare_response: CompareResponse, analysis: AnalysisResponse, output_path: str) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph("NexSheetMind - Data Comparison Report", title_style))
    elements.append(Spacer(1, 12))
    
    # KPI Section
    elements.append(Paragraph("Key Metrics", styles['Heading2']))
    kpi_data = [
        ['Metric', 'Value'],
        ['Total Rows', str(compare_response.total_rows)],
        ['Matched Rows', str(compare_response.matched)],
        ['Mismatched Rows', str(compare_response.mismatched)],
        ['Accuracy', f"{compare_response.accuracy_pct:.2f}%"]
    ]
    kpi_table = Table(kpi_data)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F8EF7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 12))
    
    # Data Type Distribution
    elements.append(Paragraph("Data Type Distribution", styles['Heading2']))
    dt_data = [['Type', 'Count']]
    for dt, count in compare_response.data_type_distribution.items():
        dt_data.append([dt, str(count)])
    dt_table = Table(dt_data)
    dt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F8EF7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(dt_table)
    elements.append(Spacer(1, 12))
    
    # AI Insights
    elements.append(Paragraph("AI Insights", styles['Heading2']))
    elements.append(Paragraph(f"<b>Summary:</b> {analysis.summary}", normal_style))
    elements.append(Spacer(1, 6))
    
    elements.append(Paragraph("<b>Anomalies:</b>", normal_style))
    for anomaly in analysis.anomalies:
        elements.append(Paragraph(f"• {anomaly}", normal_style))
    elements.append(Spacer(1, 6))
    
    elements.append(Paragraph("<b>Recommendations:</b>", normal_style))
    for rec in analysis.recommendations:
        elements.append(Paragraph(f"• {rec}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Top 50 Mismatches
    elements.append(Paragraph("Top 50 Mismatches", styles['Heading2']))
    mismatch_data = [['Row Index', 'Column', 'File A', 'File B', 'Status']]
    count = 0
    for diff in compare_response.row_diffs:
        if count >= 50:
            break
        mismatch_data.append([
            diff.row_index, 
            diff.column, 
            str(diff.value_a)[:20], 
            str(diff.value_b)[:20], 
            diff.status
        ])
        count += 1
        
    if len(mismatch_data) > 1:
        m_table = Table(mismatch_data)
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F8EF7')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        elements.append(m_table)
    else:
        elements.append(Paragraph("No mismatches found.", normal_style))
        
    doc.build(elements)
    return output_path
