# -*- coding: utf-8 -*-
{
    'name': 'Project Report - Báo cáo & Dashboard',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module báo cáo và dashboard cho quản lý dự án',
    'description': """
Module báo cáo và dashboard

Tính năng:
- Báo cáo pivot/graph cho dự án
- Báo cáo timesheet và chi phí
- Dashboard tổng quan
- Báo cáo PDF
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'project_core',
        'project_task',
        'project_hr',
        'project_timesheet',
        'project_cost',
    ],
    'data': [
        'reports/project_reports.xml',
        'views/project_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
