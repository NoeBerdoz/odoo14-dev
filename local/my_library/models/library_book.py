from odoo import api, models, fields
from datetime import timedelta


class LibraryBook(models.Model):
    _name = 'library.book'  # This will be library_book in the database
    _description = 'Library Book'  # Model user-friendly title
    _order = 'date_release desc, name'  # Sort the records from the newest to the oldest, then by title
    _rec_name = 'short_name'  # Use short_name as record representation
    short_name = fields.Char('Short Title', translate=True, index=True, required=True)  # Short Book title
    name = fields.Char('Title', required=True)  # Book title
    date_release = fields.Date('Release Date')  # Book release date
    date_updated = fields.Datetime('Last Updated')  # Book time updated
    author_ids = fields.Many2many('res.partner', string='Authors')  # Book to authors, authors are partners, m2m
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        ondelete='set null',
        context={},
        domain=[],
    )
    notes = fields.Text('Internal Notes')  # Book notes
    state = fields.Selection(
        [
            ('draft', 'Not Available'),
            ('available', 'Available'),
            ('lost', 'Lost')
        ],
        'State', default="draft")  # Book state options
    # Description with HTML type field for user edition
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')  # Binary stand for a file stored
    out_of_print = fields.Boolean('Out of Print?')  # Book print status
    # Odoo v < 13 -> cost_price = fields.Float( 'Book Cost', digits=dp.get_precision('Book Price')).
    cost_price = fields.Float('Book Cost', digits='Book price')  # Book cost with decimal accuracy setting
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price')
    # Book page numbers
    pages = fields.Integer(
        'Number of Pages',
        groups='base.group_user',
        states={'lost': [('readonly', True)]},
        help='Total book page count',
        company_dependant=False
    )
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),)  # Rating, digits prm is decimal precision
    category_id = fields.Many2one('library.book.category')

    # Computed fields
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=True
    )

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<',
            '>=': '<=',
            '<': '>',
            '<=': '>='
        }

        new_op = operator_map.get(operator, operator)
        return ['date_release', new_op, value_date]

    # SQL Constraints
    _sql_constraints = [
        (
            'name_uniq',
            'UNIQUE (name)',
            'Book title must be unique.'
        ),
        (
            'positive_page',
            'CHECK(pages>0)',
            'No of pages must be positive'
        )
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past'
                )

    # Override name_get function to set display_name as name with date_release
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))

        return result


# Other class in the same document for learning simplicity
# This will be added to the res.partner model
class ResPartner(models.Model):
    _inherit = 'res.partner'  # Inheritance of res.partner model
    published_book_ids = fields.One2many(  # Book id, one book to many authors, o2m
        'library.book', 'publisher_id',
        string='Published Books'
    )
    authored_book_ids = fields.Many2many(  # many authors to many books, m2m
        'library.book',
        string='Authored Books'
    )