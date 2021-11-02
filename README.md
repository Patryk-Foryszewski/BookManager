# BookManager
Bookmanager. Recruitment task.


## Table of Contents
* [Project Description](#project-description)
* [Links](#links)
* [Authors](#authors)
* [License](#license)


##  Project Description

With free to choose Python web-framework (Django/Flask) create an application to manage bookstore.
App should allow us to manually:
* add
* edit
* import from public API Google https://www.googleapis.com/books/v1/volumes

For front-end you can use Bootstrap library.


Part one:

    Create models that have below fields:
    * title
    * author
    * date published
    * ISBN number
    * URI to book cover
    * language of publication

    Create two views:

    View of all book stored in database with ability to search by title, author,
    languge fo publication, date range (from - to). List hast to contain all information
    from the model show in the clear way (e.g. table)
    View has to allow us to manually add edit boks and show validation erros.

Part two:

    Create a view that allows to import books by key-words from API
    https://developers.google.com/books/docs/v1/using#WorkingVolumes.
    Imports must be saved in database created in part one.

Part three:

    Create REST API views that consists of list ob books with ability to search
    and filter by query strings

Part four:

    Deploy this app to public server. Free Heroku is one among of options

Part five:

    Create unittest and check if code is PEP8 compilant.

##Links

* Website avalible under http://friendly-bookstore.herokuapp.com

* API Docs - http://friendly-bookstore.herokuapp.com/api/v1/books/docs

## Authors

* Patryk Foryszewski


## License

This project is licensed under the MIT License - see the LICENSE.md file for details
