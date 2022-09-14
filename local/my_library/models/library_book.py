from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _


# Other class in the same document to simplifed learning
# This normally should be in a proper other module
class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active  # set it to opposite


class LibraryBook(models.Model):
    _name = 'library.book'  # This will be library_book in the database
    _inherit = ['base.archive']  # Inherit abstract model base.archive
    _description = 'Library Book'  # Model user-friendly title
    _order = 'date_release desc, name'  # Sort the records from the newest to the oldest, then by title
    _rec_name = 'short_name'  # Use short_name as record representation
    short_name = fields.Char('Short Title', translate=True, index=True, required=True)  # Short Book title
    name = fields.Char('Title', required=True)  # Book title
    date_release = fields.Date('Release Date')  # Book release date
    date_updated = fields.Datetime('Last Updated')  # Book time updated
    # Relational fields
    author_ids = fields.Many2many('res.partner', string='Authors')  # Book to authors, authors are partners, m2m
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        ondelete='set null',
        context={},
        domain=[],
    )
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )

    # Provide a model dynamically
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')
        ])
        return [(x.model, x.name) for x in models]

    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document'
    )
    notes = fields.Text('Internal Notes')  # Book notes

    # Book State
    state = fields.Selection(
        [
            ('draft', 'Unavailable'),
            ('available', 'Available'),
            ('borrowed', 'Borrowed'),
            ('lost', 'Lost')
        ],
        'State', default="draft")  # Book state options

    # Check whether a state transition is allowed from the tuple structure
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft', 'available'),
            ('available', 'borrowed'),
            ('available', 'lost'),
            ('borrowed', 'lost'),
            ('lost', 'available')
        ]
        return (old_state, new_state) in allowed

    # Change the state of some books
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    # Change the state of a book to available
    def make_available(self):
        self.change_state('available')

    # Change the state of a book to lost
    def make_lost(self):
        self.change_state('lost')

    # Change the state of a book to borrowed
    def make_borrowed(self):
        self.change_state('borrowed')

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

    # Example of log button
    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS: ", all_members)
        return True


# Other class in the same document to simplified learning
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
    count_books = fields.Integer(
        'Number of Authored Books',
        compute='_compute_count_books'
    )

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)


# Other class in the same document to simplified learning
class LibraryMember(models.Model):
    _name = 'library.member'
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade',  # Deleting a partner will delete the corresponding member
        delegate=True
    )
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')



