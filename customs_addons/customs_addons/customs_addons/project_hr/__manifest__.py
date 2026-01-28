# -*- coding: utf-8 -*-
{
    'name': 'Project HR - Tích hợp Nhân sự',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module tích hợp HR với quản lý dự án',
    'description': """
Module tích hợp nhân sự với quản lý dự án

Tính năng:
- Gán nhân viên vào dự án và công việc
- Quản lý workload của nhân viên
- Tích hợp với hr.employee
- Quản lý hourly rate cho tính cost
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'hr',
        'project_core',
        'project_task',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/hr_employee_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
