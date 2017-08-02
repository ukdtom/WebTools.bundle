module.exports = function(grunt){
	grunt.loadNpmTasks('grunt-angular-gettext');
	
	grunt.initConfig({
		nggettext_extract: {
			pot: {
				files: {
					'../po/template.pot': ['../http/**/*.html', '../http/**/*.js']
					}
				},
			},
		nggettext_compile: {
			all: {
				files: {
					'../http/static/_shared/translations.js': ['../po/*.po']
					}
				},
			},
		})
};
