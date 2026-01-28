# -*- coding: utf-8 -*-
{
    'name': 'Project Portal - Portal Khách hàng',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module portal cho khách hàng xem tiến độ dự án',
    'description': """
Module portal cho khách hàng

Tính năng:
- Portal cho khách hàng xem tiến độ dự án
- Xem danh sách công việc
- Xem timesheet và chi phí (nếu được phép)
- Tích hợp với portal module
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'portal',
        'project_core',
        'project_task',
        'project_timesheet',
        'project_cost',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_security.xml',
        'views/project_project_portal_templates.xml',
        'views/project_task_portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
