# -*- coding: utf-8 -*-
{
    'name': 'Project Core - Quản lý Dự án & Milestone',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module cốt lõi quản lý dự án và milestone',
    'description': """
Module quản lý dự án và milestone cơ bản

Tính năng:
- Quản lý dự án với thông tin đầy đủ
- Quản lý milestone theo dự án
- Tích hợp chatter và activity
- Hỗ trợ timeline (cần web_gantt để hiển thị Gantt chart)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'calendar',
        # 'web_gantt',  # Optional: Cài thêm nếu muốn sử dụng Gantt view
    ],
    'data': [
        'security/ir.sequence.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_milestone_views.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
