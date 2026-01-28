# -*- coding: utf-8 -*-
{
    'name': 'Project AI Analytics - Đánh giá & Phân tích Tiến độ',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module AI đánh giá tiến độ, deadline và công khai thông tin',
    'description': """
Module AI Analytics cho Dự án

Tính năng:
- Theo dõi deadline theo ngày
- Công khai tiến độ và thành viên
- Tính toán tiến độ % công việc
- AI đánh giá tiến độ hoàn thành công việc được giao
- Báo cáo và phân tích tự động
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
        'project_core',
        'project_task',
        'project_hr',
        'project_timesheet',
        'project_cost',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_ai_analytics_views.xml',
        'views/project_task_views.xml',
        'views/project_project_views.xml',
        'views/public_templates.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
