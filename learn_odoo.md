# Documentation Odoo

___
By Noé Berdoz

This file stands for my notes while learning Odoo with the Odoo 14 Development cookbook

My main work on a custom module is present here:
[local/my_library](https://github.com/NoeBerdoz/odoo14-dev/tree/master/local/my_library)

# Directories Roles
The functions of the subdirectories are as follows:  
• src/: This contains the clone of Odoo itself, as well as the various third-party add-on projects (we have added Odoo source code to the next step in this recipe).  
• local/: This is used to save your instance-specific add-ons.  
• bin/: This includes various helper executable shell scripts.  
• filestore/: This is used as a file store.  
• logs/ (optional): This is used to store the server log files.  

# Debug mode
## Activate debug mode
From your odoo instance:
- Authenticate as admin
- Go to Settings menu from up-left menu
- Activate Debug mode on Developer Tools

From URL:  
-> http://localhost:8069/web#menu_id=102&action=94   
--> http://localhost:8069/web?debug=1#menu_id=102&action=94.  

Debug with assets:  
http://localhost:8069/web?debug=assets#menu_id=102&action=94.

The with assets mode won't minify the CSS and JS code, it's useful when debugging web

## Deactivate debug mode
- From the menu where you activated it
- Edit URL and add ?debug=0
- Click on the bug in the menu bar and choose *Leave developer tools*

# Modules
They are found with the __manifest__.py file inside their directory.

## Install a module
From the web interface with an administrator account 
Or from command line wiht -i parameter 
env/bin/python src/odoo/odoo-bin -d odoo14-dev -i stock,website -c .odoorc

## Uninstall a module
Do it with the web interface or with a shell command

## Creating a module from command line
Shut down your odoo server and do this command where you want the new module to be stored

    $ ../env/bin/python ../src/odoo/odoo-bin scaffold my_module

If you want to manually set the module path:
Consider the following example:

    $ ~/odoo-dev/odoo/odoo-bin scaffold my_module ~/odoo-dev/local-addons

A default template is used, but you can also set a theme template fr website with option -t:
    
    $ ~/odoo-dev/odoo/odoo-bin scaffold -t path/to/template my_module

## Creating a module manually
You need to add an __init__.py file at the root of the module telling odoo what to init
The init files are letting our module aware of the file it has to handle
The __manifest__.py file is used to create the module base information

The base tree of the module should be so:

my_module/  
├── controllers  
├── controllers.py  
│ └── __init__.py  
├── demo  
│ └── demo.xml  
├── __init__.py  
├── __manifest__.py  
├── models  
│ ├── __init__.py  
│ └── models.py  
├── security  
│ └── ir.model.access.csv  
└── views  
    ├── templates.xml  
    └── views.xml  


## Update a module
From command line:

	$ env/bin/python src/odoo/odoo-bin -c .odoorc -u my_library -d odoo14-dev

Or you can upgrade it from the web interface

## Model

The model folder is used to generate the database table for the module
You have to implement it with a class
```
from odoo import models, fields


class LibraryBook(models.Model):
    _name = 'library.book'  # This will be library_book in the database
    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )
```

To see a model structure from the GUI, activate de developer mode and go to Settings -> Technical | Database Structure | Models

When a model is modified you need to upgrade the module

When you implement a new module with a view, be aware that you need to configure permissions on the view, 
to see the view without configurations, go to the superuser mode -> debug icon -> Become superuser

Models have structural attributes, they start with an underscore '_'
*****
**_name** defines the internal global identifier (_name="library.book" -> id will be library_book)  
**_rac_name** is used to set the field that's used as a representation or title for the records, Odoo GUI will show this one for records instead of name  
**_order** is used to set the order in which the records are presented  
*****

If your model doesn't have a name field and no specification for the records name, the name in GUI will be model name and record ID like (library.book, 1)

If you want to display a special name for the records, like a combination of the name and release date you have to override the name_get() function:
```
def name_get(self):
 result = []
 for record in self:
 rec_name = "%s (%s)" % (record.name, record.date_release)
 result.append((record.id, rec_name))
 return result
```

### Fields
#### Fields type

- **Char** -> string
- **Text** -> multiline string
- **Selection** -> enum (Be aware that '0' can't be set as integer key)
- **Html** -> similar to **Text** but with rich text storage in Html format
- **Binary** -> binary files (images or documents)
- **Boolean** -> Bool
- **Date** -> Date handled as Python date object (fields.Date.today() to set current date as default)
- **Datetime** -> datetime handled as Python datetime object (fields.Date.now to set current datetime as default)
- **Integer** -> int
- **Float** -> float, their precision can be defined
- **Monetary** -> amount with currency

Default fields that shouldn't be set manually:
- **id** -> id
- **create_date** -> record creation timestamp
- **create_uid** -> user who created record
- **write_date** -> last edit timestamp
- **write_uid** -> user from last edit

Special fields:
- **_log_access=False** -> To disable the creation of the 4 log fields:  
- **active** -> only records with active set to True are visible

#### Fields attribute
- **string** -> field's title used in GUI, if not set it will show an adapted field name (first case Upper, '_' as ' ') 
- **translate** -> make the field translatable depending on user language
- **default** -> default field value
- **help** -> explanation text on field hover
- **groups** -> make field restricted to user group
- **states** -> dynamically set a state value from a selection value (states are attributes: readonly, required, invisible)
- **copy** -> set field to copy or not when record duplicated (True for m2m, False for o2m)
- **index** -> set True to create a database index (for faster searches)
- **readonly** -> readonly security permission
- **required** -> required field
- **company_dependant** -> field store different value for each company
- **group_operator** -> SQL group operator (count, count_distinct, array_agg, bool_and, bool_or, max, min, avg, sum)
- **sanitize** -> secure content from injections, used by **Html** field
  - sanitize_tags=True -> remove tags that are not part of the whitelist (default)
  - sanitize_attributes=True -> remove attributes of tags that are not part of whitelist
  - sanitize_style=True -> remove style properties that are not part of whitelist
  - strip_style=True -> remove all style elements
  - strip_class=True -> remove the class attributes

### Computed fields
Computed fields are fields that are calculated from other fields. 
Ex. total amount calculated from multiple prices and quantity.

```
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0
```

Computed fields are dynamically calculated at runtime, they are not stored
in the database. The ORM uses caching to avoid useless recalculating.

To use the ORM caching you have to use the @depends decorator to let it detect
when the value changes

Be aware that the compute function need a value for the @depends decorator to work, 
if there are conditions setting the value to NULL, il will raise an error tricky to debug.

There are many computed flags:

- **store** -> set to True to store field in the database, no needs to implement a search method.
- **compute_sudo** -> set to True to do the computation with elevated privileges
- 

### Relations
Odoo has his own ORM API

Depending on the relations between the model, the database structure will be adapted.  

Many-to-many relations don't add columns to te tables for the models,
they create an intermediate table with two columns to store the related ID's.

Odoo handles that, the intermediate table name will be by default the two related models alphabetically sorted with a '_rel' suffix

#### Relational fields:
- **many-to-one** -> commonly abbreviated m2o
- **one-to-many** -> commonly abbreviated 02m
- **many-to-one** -> commonly abbreviated m2m

#### Relational attributes:
- **ondelete** -> determines what happens when record is deleted (set null, restrict, cascade)
- **context** -> adds variable to client context
- **domain** -> search filter to limit the list of available records related
- **relation** -> only m2m, overrides the default name of intermediate table
- **comodel_name** -> target model identifier
- **column1** -> name for the m2o field
- **column2** -> name for the m2o field linking to comodel
- **inverse_name** -> only for o2m, field name in the target model for inverse many-to-one relation
- **limit** -> for o2m and m2m, limit number of records to read in GUI

#### Special relations
More than once Many2many relations between the same two models:  
Provide the relation table name for the second relation, otherwise the default name will conflict

Intermediate table with a default name > 63 characters:  
use the **relation** attribute to set a shorter name
PostgreSQL identifier limit is 63 characters, however odoo puts the identifier name liek so
<model1>_<model2>_rel_<model1>_id_<model2>_id_key


### # Hierarchy / Inheritance
Odoo provides 3 types of inheritance:
- Class inheritance (extension)
- Prototype inheritance
- Delegation inheritance

#### Class inheritance
When a model class is defined with the **_inherit** attribute
it adds modification instead of replacing.

If you add a new method by inheriting existing methods, you should 
include a **super** statement to call its version in the parent class

```
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
```

#### Prototype inheritance
Prototype inheritance copy the entire definition of the existing model.

It won't work if you use the same model name in the **_inherit** and **_name**
attributes, it will behave like a normal extension inheritance.

Prototype inheritance is rarely used in practice,
we usually use delegation inheritance as it doesn't need to duplicate data structures.

#### Delegation inheritance
When you don't want to modify an existing model, but also don't want to 
create duplicate data structures, you can use delegation inheritance.
Instead of **_inherit** it uses the **_inherits** class attributes,

Delegation inheritance **only works for fields** and **not for methods**.

```
_inherits = {'res.partner': 'partner_id'}  # Delegation inheritance, sets the parent models to inherit from
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade'  # Deleting a partner will delete the corresponding member
    )
    
    # or like this with delegation attribute  shortcut

    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade',  # Deleting a partner will delete the corresponding member
        delegate=True
    )
```

#### Abstract models
When you want to add a feature to multiple model, 
use an abstract model and inherit it to a regular model.

```
class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active  # set it to opposite
```

And then in the regular model:

```
class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']  # Inherit abstract model base.archive
```


## Base Models
- **res.partner** -> represent people, organizations, addresses

## Views
Views are built with XML within an <odoo> tag

```
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <!-- Example custom tree (list) view -->
    <record id="library_book_view_tree" model="ir.ui.view">
        <field name="name">Library Book List</field>
        <field name="model">library.book</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="date_release"/>
                <field name="short_name"/>
            </tree>
        </field>
    </record>
</odoo>
```

## Security Settings
You can define users/groups permissions on records/views

Add base rules in a xml:
```
<?xml version="1.0" encoding="UTF-8" ?>
<!-- Security rules -->
<odoo>
    <record id="group_ibrarian" model="res.groups">
        <field name="name">Librarians</field>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>
</odoo>
```
and set permissions in a csv like so:
```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
acl_book,library.book default,model_library_book,,1,0,0,0
acl_book_librarian,library.book_librarian,model_library_book,group_librarian,1,1,1,1
```

# SQL Constraints 
Models can have validations preventing them undesired data
Odoo supports two different type of constraints:

- Checked at the database level
- Checked at the server level

Database level constraints are limited to the one supported by PostgreSQL.
ex: UNIQUE, CHECK, EXCLUDE.

If they are not matching our needs, we can use Odoo server level constraints
that are made with Python.

Database level constraints
```
    _sql_constraints = [Book Category model
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
```

Server level constraints
```
    @api.constrains('date_release')
    def check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past'
                )
```


# User management
The user with a user_id = 1 represent the administrator user
