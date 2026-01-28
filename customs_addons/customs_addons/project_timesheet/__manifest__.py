# -*- coding: utf-8 -*-
{
    'name': 'Project Timesheet - Quản lý Timesheet',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module quản lý timesheet theo task',
    'description': """
Module quản lý timesheet theo công việc

Tính năng:
- Quản lý timesheet theo task
- Sử dụng account.analytic.line
- Tích hợp với project_task
- Tính toán giờ công thực tế
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
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_line_views.xml',
        'views/project_task_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
