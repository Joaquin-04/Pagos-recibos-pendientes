{
    'name': 'Account Journal Pending Payments',
    'version': '1.0',
    'summary': 'Wizard to get pending payments by journal and date range',
    'description': 'Allows you to select a date range in a wizard and retrieve pending payments for a specific journal.',
    'category': 'Accounting',
    'author': 'Your Name',
    'depends': ['account'],  # Dependencia del módulo de contabilidad
    'data': [
        'views/account_journal_view.xml',  # Botón en account.journal para abrir el wizard
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
