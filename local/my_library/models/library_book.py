from odoo import models, fields


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
