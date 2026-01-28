# -*- coding: utf-8 -*-
{
    'name': 'Project Cost - Quản lý Chi phí',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module quản lý chi phí theo timesheet và hourly rate',
    'description': """
Module quản lý chi phí dự án

Tính năng:
- Tính chi phí theo timesheet và hourly rate
- Quản lý cost theo task và project
- Tích hợp với project_timesheet và project_hr
- Báo cáo chi phí chi tiết
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'account',
        'project_core',
        'project_task',
        'project_hr',
        'project_timesheet',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_cost_views.xml',
        'views/project_task_views.xml',
        'views/project_project_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
