# -*- coding: utf-8 -*-
{
    'name': 'Project Task - Quản lý Công việc & Subtask',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module quản lý task và subtask với workflow',
    'description': """
Module quản lý công việc và subtask

Tính năng:
- Quản lý task với workflow đầy đủ
- Hỗ trợ subtask (parent/child)
- Tích hợp với project_core
- Tích hợp chatter và activity
- Hỗ trợ timeline (cần web_gantt để hiển thị Gantt chart)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'project_core',
        'calendar',
        # 'web_gantt',  # Optional: Cài thêm nếu muốn sử dụng Gantt view
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
