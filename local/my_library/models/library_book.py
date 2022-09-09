from odoo import models, fields


class LibraryBook(models.Model):
    _name = 'library.book'  # This will be library_book in the database
    _description = 'Library Book'  # Model user-friendly title
    _order = 'date_release desc, name'  # Sort the records from the newest to the oldest, then by title
    _rec_name = 'short_name'  # Use short_name as record representation
    short_name = fields.Char('Short Title', required=True)  # Short Book title
    name = fields.Char('Title', required=True)  # Book title
    date_release = fields.Date('Release Date')  # Book release date
    date_updated = fields.Datetime('Last Updated')  # Book time updated
    author_ids = fields.Many2many('res.partner', string='Authors')  # Book authors, authors are partners, N to N
    notes = fields.Text('Internal Notes')  # Book notes
    state = fields.Selection(
        [
            ('draft', 'Not Availabke'),
            ('available', 'Available'),
            ('lost', 'Lost')
        ],
        'State')  # Book state options
    description = fields.Html('Description')  # Description, but why HTML ?
    cover = fields.Binary('Book Cover')  # Binary stand for a file stored
    out_of_print = fields.Boolean('Out of Print?')  # Book print status
    pages = fields.Integer('Number of Pages')  # Book page numbers
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),)  # Rating, digits prm is decimal precision

    # Override name_get function to set display_name as name with date_release
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))

        return result
