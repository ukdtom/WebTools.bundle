# How to work with translations

## Initial setup

* Install npm
* Install grunt-cli globally

Make translations directory the current one, and run:

* npm install grunt
* npm install grunt-angular-gettext

## Extraction

To update the translation template, when ever the website has been updated, do:

* Make translations directory the current directory, and run:
* run "grunt nggettext_extract"

Template file in PO directory should then be updated

After that is done, we can import it to the translation site, and notify contributers
https://poeditor.com/join/project/8uRxEmAE4M


## Compiling
To update the file named /http/static/_shared/translations.js with the translations in the po files, do the following:

* Make translations directory the current directory, and run:
* run "grunt nggettext_compile"
