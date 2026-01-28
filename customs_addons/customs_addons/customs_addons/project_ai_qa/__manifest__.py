# -*- coding: utf-8 -*-
{
    'name': 'Project AI Q&A - Hỏi đáp AI về Dự án',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'summary': 'Module AI hỏi đáp về dữ liệu dự án',
    'description': """
Module AI Q&A cho Dự án

Tính năng:
- Hỏi đáp về dữ liệu dự án bằng AI
- Tích hợp với các module project khác
- Chat interface để tương tác với AI
- Lưu lịch sử câu hỏi và câu trả lời
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
        'data/system_parameters.xml',
        'security/ir.model.access.csv',
        'views/project_ai_qa_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
