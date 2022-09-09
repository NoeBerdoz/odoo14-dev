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
│   ├── controllers.py  
│   └── __init__.py  
├── demo  
│   └── demo.xml  
├── __init__.py  
├── __manifest__.py  
├── models  
│   ├── __init__.py  
│   └── models.py  
├── security  
│   └── ir.model.access.csv  
└── views  
    ├── templates.xml  
    └── views.xml  


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

When a model is modified you need to upgrade the module 

	$ env/bin/python src/odoo/odoo-bin -c .odoorc -u my_library -d odoo14-dev

Or you can upgrade it from the web interface

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
 
## View
Add a xml view in /views and fill it with Odoo xml page constructor

## Settings permissions 
Add base rules in a xml
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
and set permissions in a csv like so 
```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
acl_book,library.book default,model_library_book,,1,0,0,0
acl_book_librarian,library.book_librarian,model_library_book,group_librarian,1,1,1,1
```

# User management
The user with a user_id = 1 represent the administrator user
